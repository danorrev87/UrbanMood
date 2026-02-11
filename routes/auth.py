from flask import Blueprint, request, jsonify, session, redirect, render_template, render_template_string
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
import secrets
from datetime import datetime, date
from functools import wraps
from db import SessionLocal
from models import User, UserRole, InvitationToken, InvitationPurpose, Rutina, WorkoutLog, RutinaEjercicio, RutinaUser
from config import config
try:
    from mailersend.emails import NewEmail as Email
except ImportError:
    from mailersend import Email

auth_bp = Blueprint('auth', __name__)

INVITE_TEMPLATE = """
<!doctype html><title>Set Password</title>
<h2>Crear contraseña</h2>
<form method=post>
  <input type=password name=password placeholder="Nueva contraseña" required minlength=8>
  <button type=submit>Guardar</button>
</form>
"""

def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'uid' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return wrapper

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    # Accept either JSON or form data
    if request.is_json:
        data = request.get_json() or {}
        email = (data.get('email') or '').strip().lower()
        password = data.get('password') or ''
    else:
        email = (request.form.get('email') or '').strip().lower()
        password = request.form.get('password') or ''
    with SessionLocal() as db:
        user = db.query(User).filter(User.email == email, User.is_active == True).first()
        if not user or not user.password_hash or not bcrypt.verify(password, user.password_hash):
            if request.is_json:
                return jsonify({"success": False, "message": "Credenciales inválidas"}), 401
            # form submit -> re-render with message (simplistic)
            return render_template('login.html', error="Credenciales inválidas"), 401
        session['uid'] = user.id
        session['role'] = user.role.value
    if user.role == UserRole.admin:
        redirect_url = '/admin/users'
    elif user.role == UserRole.coach:
        redirect_url = '/admin/rutinas'
    else:
        redirect_url = '/mi-rutina'
    if request.is_json:
        return jsonify({"success": True, "redirect": redirect_url})
    return redirect(redirect_url)

@auth_bp.route('/logout', methods=['POST','GET'])
def logout():
    session.clear()
    if request.method == 'GET':
        return redirect('/')
    return jsonify({"success": True})

@auth_bp.route('/me')
def me():
    if 'uid' not in session:
        return jsonify({"authenticated": False})
    return jsonify({"authenticated": True, "role": session.get('role')})

@auth_bp.route('/invite/<token>', methods=['GET', 'POST'])
def accept_invite(token):
    with SessionLocal() as db:
        invite = db.query(InvitationToken).filter(InvitationToken.token==token, InvitationToken.invalidated==False).first()
        if not invite or invite.used_at or invite.expires_at < datetime.utcnow():
            return "Token inválido o expirado", 400
        user = invite.user
        if request.method == 'POST':
            password = request.form.get('password')
            if not password or len(password) < 8:
                return "Contraseña inválida", 400
            user.password_hash = bcrypt.hash(password)
            user.is_active = True
            invite.used_at = datetime.utcnow()
            db.commit()
            return redirect('/')
        return render_template_string(INVITE_TEMPLATE)

# ============================================================================
# PASSWORD RESET FLOW
# ============================================================================

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'GET':
        return render_template('forgot_password.html')

    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    if not email:
        return jsonify({"success": False, "message": "Email requerido"}), 400

    with SessionLocal() as db:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            # Don't reveal whether email exists
            return jsonify({"success": True, "message": "Si el email existe, recibirás un enlace de recuperación."})

        # Invalidate any previous reset tokens
        old_tokens = db.query(InvitationToken).filter(
            InvitationToken.user_id == user.id,
            InvitationToken.purpose == InvitationPurpose.reset,
            InvitationToken.used_at == None,
            InvitationToken.invalidated == False
        ).all()
        for t in old_tokens:
            t.invalidated = True

        token = secrets.token_urlsafe(32)
        reset_token = InvitationToken(
            user_id=user.id,
            token=token,
            purpose=InvitationPurpose.reset,
            expires_at=InvitationToken.new_expiry(hours=24)
        )
        db.add(reset_token)
        db.commit()

        send_reset_email(email, token)

    return jsonify({"success": True, "message": "Si el email existe, recibirás un enlace de recuperación."})

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    with SessionLocal() as db:
        invite = db.query(InvitationToken).filter(
            InvitationToken.token == token,
            InvitationToken.purpose == InvitationPurpose.reset,
            InvitationToken.invalidated == False
        ).first()

        if not invite or invite.used_at or invite.expires_at < datetime.utcnow():
            if request.method == 'GET':
                return render_template('reset_password.html', error="Este enlace ha expirado o ya fue utilizado.")
            return jsonify({"success": False, "message": "Token inválido o expirado"}), 400

        if request.method == 'GET':
            return render_template('reset_password.html', error=None)

        data = request.get_json() or {}
        password = data.get('password') or ''
        if len(password) < 8:
            return jsonify({"success": False, "message": "La contraseña debe tener al menos 8 caracteres"}), 400

        user = invite.user
        user.password_hash = bcrypt.hash(password)
        invite.used_at = datetime.utcnow()
        db.commit()

        return jsonify({"success": True, "message": "Contraseña actualizada. Redirigiendo al login..."})

# ============================================================================
# USER-FACING ROUTINE VIEW
# ============================================================================

@auth_bp.route('/mi-rutina')
@require_auth
def mi_rutina():
    with SessionLocal() as db:
        rutinas = db.query(Rutina).join(RutinaUser).filter(
            RutinaUser.user_id == session['uid'],
            RutinaUser.is_active == True,
            Rutina.is_active == True
        ).order_by(Rutina.created_at.desc()).all()

        today = date.today()
        completed_logs = db.query(WorkoutLog.rutina_ejercicio_id).filter(
            WorkoutLog.user_id == session['uid'],
            WorkoutLog.date == today,
            WorkoutLog.completed == True
        ).all()
        completed_ids = {row[0] for row in completed_logs}

        return render_template(
            'mi_rutina.html',
            rutinas=rutinas,
            completed_ids=completed_ids,
            today=today
        )

@auth_bp.route('/mi-rutina/toggle', methods=['POST'])
@require_auth
def toggle_exercise():
    data = request.get_json() or {}
    re_id = data.get('rutina_ejercicio_id')
    if not re_id:
        return jsonify({"success": False, "message": "rutina_ejercicio_id requerido"}), 400

    today = date.today()
    uid = session['uid']

    with SessionLocal() as db:
        # Verify the exercise belongs to the user's active routine
        re = db.query(RutinaEjercicio).join(Rutina).join(RutinaUser).filter(
            RutinaEjercicio.id == re_id,
            RutinaUser.user_id == uid,
            RutinaUser.is_active == True,
            Rutina.is_active == True
        ).first()
        if not re:
            return jsonify({"success": False, "message": "Ejercicio no encontrado"}), 404

        existing = db.query(WorkoutLog).filter(
            WorkoutLog.user_id == uid,
            WorkoutLog.rutina_ejercicio_id == re_id,
            WorkoutLog.date == today
        ).first()

        if existing:
            db.delete(existing)
            db.commit()
            return jsonify({"success": True, "completed": False})
        else:
            log = WorkoutLog(
                user_id=uid,
                rutina_ejercicio_id=re_id,
                date=today,
                completed=True
            )
            db.add(log)
            db.commit()
            return jsonify({"success": True, "completed": True})

@auth_bp.route('/mi-rutina/history')
@require_auth
def workout_history():
    uid = session['uid']
    page_size = 30
    offset = request.args.get('offset', 0, type=int)

    with SessionLocal() as db:
        from sqlalchemy import func

        rutinas = db.query(Rutina).join(RutinaUser).filter(
            RutinaUser.user_id == uid,
            RutinaUser.is_active == True,
            Rutina.is_active == True
        ).all()
        total_exercises = sum(len(r.ejercicios) for r in rutinas)

        logs = db.query(
            WorkoutLog.date,
            func.count(WorkoutLog.id).label('completed')
        ).filter(
            WorkoutLog.user_id == uid,
            WorkoutLog.completed == True
        ).group_by(WorkoutLog.date).order_by(WorkoutLog.date.desc()).offset(offset).limit(page_size + 1).all()

        has_more = len(logs) > page_size
        logs = logs[:page_size]

        history = [
            {
                "date": row.date.isoformat(),
                "total": total_exercises,
                "completed": row.completed
            }
            for row in logs
        ]

        return jsonify({"history": history, "has_more": has_more, "next_offset": offset + page_size if has_more else None})

@auth_bp.route('/mi-rutina/history/<date_str>')
@require_auth
def workout_history_detail(date_str):
    uid = session['uid']
    try:
        target_date = date.fromisoformat(date_str)
    except ValueError:
        return jsonify({"success": False, "message": "Fecha inválida"}), 400

    with SessionLocal() as db:
        logs = db.query(WorkoutLog).filter(
            WorkoutLog.user_id == uid,
            WorkoutLog.date == target_date,
            WorkoutLog.completed == True
        ).all()

        exercises = []
        for log in logs:
            re = log.rutina_ejercicio
            ej = re.ejercicio
            exercises.append({
                "name": ej.name,
                "body_section": ej.body_section.value,
                "image_url": ej.image_url,
                "series": re.series,
                "repeticiones": re.repeticiones,
                "peso": re.peso,
                "descanso": re.descanso,
            })

        return jsonify({"date": date_str, "exercises": exercises})

# ============================================================================
# EMAIL UTILITIES
# ============================================================================

def send_invitation_email(email_to: str, token: str):
    if not config.MAILERSEND_API_KEY:
        print(f"[INVITE LINK] https://urbanmood.net/invite/{token}")
        return
    mailer = Email(config.MAILERSEND_API_KEY)
    mail_body = {}
    mail_from = {"name": config.MAIL_FROM_NAME, "email": config.MAIL_FROM_EMAIL}
    recipients = [{"name": email_to, "email": email_to}]
    subject = "Invitación UrbanMood"
    html_content = f"""
    <p>Te invitamos a crear tu cuenta UrbanMood.</p>
    <p><a href='https://urbanmood.net/invite/{token}'>Crear contraseña</a> (expira en 72h)</p>
    """
    mailer.set_mail_from(mail_from, mail_body)
    mailer.set_mail_to(recipients, mail_body)
    mailer.set_subject(subject, mail_body)
    mailer.set_html_content(html_content, mail_body)
    mailer.send(mail_body)

def send_reset_email(email_to: str, token: str):
    if not config.MAILERSEND_API_KEY:
        print(f"[RESET LINK] https://urbanmood.net/reset-password/{token}")
        return
    mailer = Email(config.MAILERSEND_API_KEY)
    mail_body = {}
    mail_from = {"name": config.MAIL_FROM_NAME, "email": config.MAIL_FROM_EMAIL}
    recipients = [{"name": email_to, "email": email_to}]
    subject = "Restablecer contraseña - UrbanMood"
    html_content = f"""
    <p>Recibimos una solicitud para restablecer tu contraseña.</p>
    <p><a href='https://urbanmood.net/reset-password/{token}'>Restablecer contraseña</a> (expira en 24h)</p>
    <p>Si no solicitaste este cambio, podés ignorar este email.</p>
    """
    mailer.set_mail_from(mail_from, mail_body)
    mailer.set_mail_to(recipients, mail_body)
    mailer.set_subject(subject, mail_body)
    mailer.set_html_content(html_content, mail_body)
    mailer.send(mail_body)
