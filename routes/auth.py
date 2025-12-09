from flask import Blueprint, request, jsonify, session, redirect, render_template, render_template_string
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
import secrets
from datetime import datetime
from db import SessionLocal
from models import User, UserRole, InvitationToken, InvitationPurpose
from config import config
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
    redirect_url = '/admin/users' if user.role == UserRole.admin else '/'
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

# Utility to send invite email

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
