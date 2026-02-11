from flask import Blueprint, request, jsonify, render_template, redirect, send_from_directory
from db import SessionLocal
from models import User, UserRole, InvitationToken, InvitationPurpose, Clase, Rutina, Ejercicio, RutinaEjercicio, BodySection, Sucursal, RutinaUser
from routes.auth import send_invitation_email
from utils.audit import log_action
from datetime import datetime
import secrets
import os

admin_bp = Blueprint('admin', __name__)


def deactivate_user_routines(db, user_id):
    """Deactivate all active routine assignments for a user."""
    db.query(RutinaUser).filter(
        RutinaUser.user_id == user_id,
        RutinaUser.is_active == True
    ).update({'is_active': False})

# Simple decorator placeholder
from functools import wraps
from flask import session

def require_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get('role') != UserRole.admin.value:
            return jsonify({"success": False, "message": "No autorizado"}), 403
        return f(*args, **kwargs)
    return wrapper

def require_coach_or_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get('role') not in (UserRole.admin.value, UserRole.coach.value):
            return jsonify({"success": False, "message": "No autorizado"}), 403
        return f(*args, **kwargs)
    return wrapper

@admin_bp.route('/admin/users', methods=['GET'])
@require_admin
def list_users():
    with SessionLocal() as db:
        users = db.query(User).order_by(User.created_at.desc()).all()
        return render_template('admin_users.html', users=users)

@admin_bp.route('/admin/users/create', methods=['POST'])
@require_admin
def create_user():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    name = data.get('name') or ''
    role = data.get('role') or 'user'
    if role not in [r.value for r in UserRole]:
        return jsonify({"success": False, "message": "Rol inválido"}), 400
    with SessionLocal() as db:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            return jsonify({"success": False, "message": "Usuario ya existe"}), 400
        user = User(email=email, name=name, role=UserRole(role), is_active=False)
        db.add(user)
        db.flush()
        token = secrets.token_urlsafe(32)
        invite = InvitationToken(user_id=user.id, token=token, purpose=InvitationPurpose.invite, expires_at=InvitationToken.new_expiry())
        db.add(invite)
        log_action(db, 'create_user', 'user', user.id, {'email': email})
        db.commit()
        send_invitation_email(email, token)
        return jsonify({"success": True, "user_id": user.id})

@admin_bp.route('/admin/users/<int:user_id>/update', methods=['PATCH'])
@require_admin
def update_user(user_id):
    data = request.get_json() or {}
    with SessionLocal() as db:
        user = db.query(User).filter(User.id==user_id).first()
        if not user:
            return jsonify({"success": False, "message": "No existe"}), 404
        if user.role == UserRole.admin:
            admin_count = db.query(User).filter(User.role==UserRole.admin).count()
            if ((data.get('role') and data.get('role') != 'admin') or (data.get('is_active') is False)) and admin_count == 1:
                return jsonify({"success": False, "message": "No se puede cambiar/eliminar el último admin"}), 400
        if 'name' in data and data['name']:
            user.name = data['name']
        if 'phone' in data:
            user.phone = data['phone'] or None
        if 'birth_date' in data:
            bd = data.get('birth_date') or None
            if bd:
                try:
                    user.birth_date = datetime.strptime(bd, '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({"success": False, "message": "Fecha inválida (YYYY-MM-DD)"}), 400
            else:
                user.birth_date = None
        if 'address' in data:
            user.address = (data.get('address') or '').strip() or None
        if 'gender' in data:
            # Accept any provided value (UI controls list) but limit length
            gval = (data.get('gender') or '').strip()
            if len(gval) > 40:
                return jsonify({"success": False, "message": "Genero demasiado largo"}), 400
            user.gender = gval or None
        if 'role' in data and data['role'] in [r.value for r in UserRole]:
            user.role = UserRole(data['role'])
        if 'is_active' in data:
            user.is_active = bool(data['is_active'])
        if 'preferred_location_id' in data:
            loc_id = data.get('preferred_location_id')
            user.preferred_location_id = int(loc_id) if loc_id else None
        log_action(db, 'update_user', 'user', user_id, data)
        db.commit()
        return jsonify({"success": True})

@admin_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@require_admin
def delete_user(user_id):
    with SessionLocal() as db:
        user = db.query(User).filter(User.id==user_id).first()
        if not user:
            return jsonify({"success": False, "message": "No existe"}), 404
        # Disallow self-delete for now
        from flask import session as flask_session
        if user.id == flask_session.get('uid'):
            return jsonify({"success": False, "message": "No puedes eliminar tu propia cuenta"}), 400
        if user.role == UserRole.admin:
            admin_count = db.query(User).filter(User.role==UserRole.admin).count()
            if admin_count == 1:
                return jsonify({"success": False, "message": "No se puede eliminar el último admin"}), 400
        log_action(db, 'delete_user', 'user', user_id, {'email': user.email})
        db.delete(user)
        db.commit()
        return jsonify({"success": True})

@admin_bp.route('/admin/users/<int:user_id>', methods=['GET'])
@require_admin
def user_detail(user_id):
    with SessionLocal() as db:
        user = db.query(User).filter(User.id==user_id).first()
        if not user:
            return jsonify({"success": False, "message": "No existe"}), 404
        sucursales = db.query(Sucursal).filter(Sucursal.is_active == True).order_by(Sucursal.name).all()
        # Current active routine assignment
        active_assignment = db.query(RutinaUser).filter(
            RutinaUser.user_id == user_id,
            RutinaUser.is_active == True
        ).first()
        # All available routines for the dropdown
        rutinas = db.query(Rutina).filter(Rutina.is_active == True).order_by(Rutina.name).all()
        return render_template('admin_user_detail.html', user=user, sucursales=sucursales,
                               active_assignment=active_assignment, rutinas=rutinas)

@admin_bp.route('/admin/users/<int:user_id>/assign-rutina', methods=['PATCH'])
@require_admin
def assign_rutina_to_user(user_id):
    """Assign or unassign a routine to/from a user."""
    data = request.get_json() or {}
    rutina_id = data.get('rutina_id')

    with SessionLocal() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({"success": False, "message": "Usuario no existe"}), 404

        # Deactivate current assignments
        deactivate_user_routines(db, user_id)

        if rutina_id:
            rutina = db.query(Rutina).filter(Rutina.id == rutina_id).first()
            if not rutina:
                return jsonify({"success": False, "message": "Rutina no existe"}), 404

            # Check if assignment already exists (reactivate)
            existing = db.query(RutinaUser).filter(
                RutinaUser.rutina_id == rutina_id,
                RutinaUser.user_id == user_id
            ).first()
            if existing:
                existing.is_active = True
            else:
                assignment = RutinaUser(rutina_id=rutina_id, user_id=user_id, is_active=True)
                db.add(assignment)

            log_action(db, 'assign_rutina', 'user', user_id, {'rutina_id': rutina_id})
            db.commit()
            return jsonify({"success": True, "rutina_name": rutina.name})
        else:
            log_action(db, 'unassign_rutina', 'user', user_id)
            db.commit()
            return jsonify({"success": True, "rutina_name": None})

# ============================================================================
# CLASES ROUTES
# ============================================================================

@admin_bp.route('/admin/clases', methods=['GET'])
@require_admin
def list_clases():
    with SessionLocal() as db:
        clases = db.query(Clase).order_by(Clase.created_at.desc()).all()
        return render_template('admin_clases.html', clases=clases)

@admin_bp.route('/admin/clases', methods=['POST'])
@require_admin
def create_clase():
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    description = (data.get('description') or '').strip() or None
    if not name:
        return jsonify({"success": False, "message": "Nombre requerido"}), 400
    if len(name) > 120:
        return jsonify({"success": False, "message": "Nombre demasiado largo"}), 400
    with SessionLocal() as db:
        exists = db.query(Clase).filter(Clase.name == name).first()
        if exists:
            return jsonify({"success": False, "message": "Clase ya existe"}), 400
        clase = Clase(name=name, description=description)
        db.add(clase)
        db.flush()
        log_action(db, 'create_clase', 'clase', clase.id)
        db.commit()
        return jsonify({"success": True, "id": clase.id})

@admin_bp.route('/admin/clases/<int:clase_id>', methods=['PATCH'])
@require_admin
def update_clase(clase_id):
    data = request.get_json() or {}
    with SessionLocal() as db:
        clase = db.query(Clase).filter(Clase.id==clase_id).first()
        if not clase:
            return jsonify({"success": False, "message": "No existe"}), 404
        if 'name' in data:
            new_name = (data.get('name') or '').strip()
            if not new_name:
                return jsonify({"success": False, "message": "Nombre requerido"}), 400
            if len(new_name) > 120:
                return jsonify({"success": False, "message": "Nombre demasiado largo"}), 400
            clash = db.query(Clase).filter(Clase.name==new_name, Clase.id!=clase.id).first()
            if clash:
                return jsonify({"success": False, "message": "Nombre ya usado"}), 400
            clase.name = new_name
        if 'description' in data:
            desc = (data.get('description') or '').strip() or None
            clase.description = desc
        if 'is_active' in data:
            clase.is_active = bool(data.get('is_active'))
        log_action(db, 'update_clase', 'clase', clase_id)
        db.commit()
        return jsonify({"success": True})

@admin_bp.route('/admin/clases/<int:clase_id>', methods=['DELETE'])
@require_admin
def delete_clase(clase_id):
    with SessionLocal() as db:
        clase = db.query(Clase).filter(Clase.id==clase_id).first()
        if not clase:
            return jsonify({"success": False, "message": "No existe"}), 404
        log_action(db, 'delete_clase', 'clase', clase_id)
        db.delete(clase)
        db.commit()
        return jsonify({"success": True})

# ============================================================================
# SUCURSALES ROUTES
# ============================================================================

@admin_bp.route('/admin/sucursales', methods=['GET'])
@require_admin
def admin_sucursales():
    with SessionLocal() as db:
        sucursales = db.query(Sucursal).order_by(Sucursal.created_at.desc()).all()
        return render_template('admin_sucursales.html', sucursales=sucursales)

@admin_bp.route('/admin/sucursales', methods=['POST'])
@require_admin
def create_sucursal():
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({"success": False, "message": "Nombre requerido"}), 400
    if len(name) > 120:
        return jsonify({"success": False, "message": "Nombre demasiado largo"}), 400
    with SessionLocal() as db:
        exists = db.query(Sucursal).filter(Sucursal.name == name).first()
        if exists:
            return jsonify({"success": False, "message": "Sucursal ya existe"}), 400
        sucursal = Sucursal(
            name=name,
            address=(data.get('address') or '').strip() or None,
            phone=(data.get('phone') or '').strip() or None
        )
        db.add(sucursal)
        db.flush()
        log_action(db, 'create_sucursal', 'sucursal', sucursal.id, {'name': name})
        db.commit()
        return jsonify({"success": True, "id": sucursal.id})

@admin_bp.route('/admin/sucursales/<int:sucursal_id>', methods=['PATCH'])
@require_admin
def update_sucursal(sucursal_id):
    data = request.get_json() or {}
    with SessionLocal() as db:
        sucursal = db.query(Sucursal).filter(Sucursal.id == sucursal_id).first()
        if not sucursal:
            return jsonify({"success": False, "message": "No existe"}), 404
        if 'name' in data:
            new_name = (data.get('name') or '').strip()
            if not new_name:
                return jsonify({"success": False, "message": "Nombre requerido"}), 400
            clash = db.query(Sucursal).filter(Sucursal.name == new_name, Sucursal.id != sucursal.id).first()
            if clash:
                return jsonify({"success": False, "message": "Nombre ya usado"}), 400
            sucursal.name = new_name
        if 'address' in data:
            sucursal.address = (data.get('address') or '').strip() or None
        if 'phone' in data:
            sucursal.phone = (data.get('phone') or '').strip() or None
        if 'is_active' in data:
            sucursal.is_active = bool(data.get('is_active'))
        log_action(db, 'update_sucursal', 'sucursal', sucursal_id, data)
        db.commit()
        return jsonify({"success": True})

@admin_bp.route('/admin/sucursales/<int:sucursal_id>', methods=['DELETE'])
@require_admin
def delete_sucursal(sucursal_id):
    with SessionLocal() as db:
        sucursal = db.query(Sucursal).filter(Sucursal.id == sucursal_id).first()
        if not sucursal:
            return jsonify({"success": False, "message": "No existe"}), 404
        log_action(db, 'delete_sucursal', 'sucursal', sucursal_id, {'name': sucursal.name})
        db.delete(sucursal)
        db.commit()
        return jsonify({"success": True})

# ============================================================================
# ENTRENADORES ROUTES
# ============================================================================

@admin_bp.route('/admin/entrenadores', methods=['GET'])
@require_admin
def admin_entrenadores():
    with SessionLocal() as db:
        coaches = db.query(User).filter(User.role == UserRole.coach).order_by(User.name).all()
        # Annotate each coach with stats
        coach_data = []
        for coach in coaches:
            rutinas_count = db.query(Rutina).filter(Rutina.created_by_coach_id == coach.id).count()
            users_count = db.query(RutinaUser.user_id).join(Rutina).filter(
                Rutina.created_by_coach_id == coach.id,
                RutinaUser.is_active == True
            ).distinct().count()
            coach.rutinas_count = rutinas_count
            coach.users_count = users_count
            coach_data.append(coach)

        total_rutinas = db.query(Rutina).filter(
            Rutina.created_by_coach_id.in_([c.id for c in coaches])
        ).count() if coaches else 0

        regular_users = db.query(User).filter(User.role == UserRole.user, User.is_active == True).order_by(User.name).all()

        return render_template('admin_entrenadores.html',
            coaches=coach_data,
            total_rutinas=total_rutinas,
            regular_users=regular_users
        )

@admin_bp.route('/admin/entrenadores/<int:user_id>/promote', methods=['POST'])
@require_admin
def promote_to_coach(user_id):
    with SessionLocal() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({"success": False, "message": "Usuario no encontrado"}), 404
        if user.role == UserRole.coach:
            return jsonify({"success": False, "message": "Ya es coach"}), 400
        if user.role == UserRole.admin:
            return jsonify({"success": False, "message": "No se puede cambiar un admin a coach"}), 400
        user.role = UserRole.coach
        log_action(db, 'promote_coach', 'user', user_id, {'email': user.email})
        db.commit()
        return jsonify({"success": True})

@admin_bp.route('/admin/entrenadores/<int:user_id>/demote', methods=['POST'])
@require_admin
def demote_from_coach(user_id):
    with SessionLocal() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({"success": False, "message": "Usuario no encontrado"}), 404
        if user.role != UserRole.coach:
            return jsonify({"success": False, "message": "No es coach"}), 400
        user.role = UserRole.user
        log_action(db, 'demote_coach', 'user', user_id, {'email': user.email})
        db.commit()
        return jsonify({"success": True})

# ============================================================================
# AUDIT LOG ROUTE
# ============================================================================

@admin_bp.route('/admin/audit', methods=['GET'])
@require_admin
def admin_audit():
    from models.audit import AuditLog
    page = request.args.get('page', 1, type=int)
    action_filter = request.args.get('action', '').strip()
    per_page = 50

    with SessionLocal() as db:
        query = db.query(AuditLog).order_by(AuditLog.created_at.desc())

        if action_filter:
            query = query.filter(AuditLog.action == action_filter)

        total = query.count()
        total_pages = max(1, (total + per_page - 1) // per_page)
        page = min(page, total_pages)

        logs = query.offset((page - 1) * per_page).limit(per_page).all()

        # Get distinct actions for filter dropdown
        actions = [r[0] for r in db.query(AuditLog.action).distinct().order_by(AuditLog.action).all()]

        return render_template('admin_audit.html',
            logs=logs,
            page=page,
            total_pages=total_pages,
            actions=actions,
            current_filter=action_filter
        )

# ============================================================================
# RUTINAS ROUTES
# ============================================================================

@admin_bp.route('/admin/rutinas', methods=['GET'])
@require_coach_or_admin
def list_rutinas():
    """List all routines with user and coach information"""
    with SessionLocal() as db:
        from sqlalchemy.orm import joinedload
        rutinas = db.query(Rutina).options(
            joinedload(Rutina.assigned_users).joinedload(RutinaUser.user)
        ).order_by(Rutina.created_at.desc()).all()
        # Show all users (any role can have a routine assigned)
        users = db.query(User).filter(User.is_active == True).order_by(User.name).all()
        coaches = db.query(User).filter(User.role.in_([UserRole.coach, UserRole.admin])).order_by(User.name).all()
        return render_template('admin_rutinas.html', rutinas=rutinas, users=users, coaches=coaches)

@admin_bp.route('/admin/rutinas/create', methods=['POST'])
@require_coach_or_admin
def create_rutina():
    """Create a new routine and assign to selected users"""
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    description = (data.get('description') or '').strip()
    user_ids = data.get('user_ids', [])

    if not name:
        return jsonify({"success": False, "message": "El nombre es requerido"}), 400
    if not user_ids:
        return jsonify({"success": False, "message": "Debe seleccionar al menos un usuario"}), 400

    with SessionLocal() as db:
        # Get current coach from session
        coach_id = session.get('uid')
        if not coach_id:
            return jsonify({"success": False, "message": "Sesión inválida"}), 401

        rutina = Rutina(
            name=name,
            description=description or None,
            created_by_coach_id=coach_id,
            is_active=True
        )
        db.add(rutina)
        db.flush()

        for uid in user_ids:
            user = db.query(User).filter(User.id == uid).first()
            if not user:
                continue
            # Deactivate previous active assignments for this user
            deactivate_user_routines(db, uid)
            assignment = RutinaUser(rutina_id=rutina.id, user_id=uid, is_active=True)
            db.add(assignment)

        log_action(db, 'create_rutina', 'rutina', rutina.id, {'user_ids': user_ids})
        db.commit()
        return jsonify({"success": True, "rutina_id": rutina.id})

@admin_bp.route('/admin/rutinas/<int:rutina_id>', methods=['GET'])
@require_coach_or_admin
def get_rutina(rutina_id):
    """Get routine details with exercises"""
    with SessionLocal() as db:
        rutina = db.query(Rutina).filter(Rutina.id == rutina_id).first()
        if not rutina:
            return jsonify({"success": False, "message": "Rutina no existe"}), 404
        return jsonify({"success": True, "rutina": rutina.to_dict(include_ejercicios=True)})

@admin_bp.route('/admin/rutinas/<int:rutina_id>/update', methods=['PATCH'])
@require_coach_or_admin
def update_rutina(rutina_id):
    """Update routine basic information and user assignments"""
    data = request.get_json() or {}

    with SessionLocal() as db:
        rutina = db.query(Rutina).filter(Rutina.id == rutina_id).first()
        if not rutina:
            return jsonify({"success": False, "message": "Rutina no existe"}), 404

        if 'name' in data and data['name']:
            rutina.name = data['name'].strip()
        if 'description' in data:
            rutina.description = (data['description'] or '').strip() or None
        if 'user_ids' in data:
            new_user_ids = set(data['user_ids'])
            current_assignments = {au.user_id: au for au in rutina.assigned_users}
            current_user_ids = set(current_assignments.keys())

            # Remove users no longer in list
            for uid in current_user_ids - new_user_ids:
                db.delete(current_assignments[uid])

            # Add new users
            for uid in new_user_ids - current_user_ids:
                user = db.query(User).filter(User.id == uid).first()
                if not user:
                    continue
                deactivate_user_routines(db, uid)
                assignment = RutinaUser(rutina_id=rutina.id, user_id=uid, is_active=True)
                db.add(assignment)

            # Ensure existing assignments for users still in list are active
            for uid in new_user_ids & current_user_ids:
                if not current_assignments[uid].is_active:
                    deactivate_user_routines(db, uid)
                    current_assignments[uid].is_active = True
        if 'is_active' in data:
            rutina.is_active = bool(data['is_active'])
        if 'start_date' in data:
            start_date = data.get('start_date') or None
            if start_date:
                try:
                    rutina.start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({"success": False, "message": "Fecha inicio inválida"}), 400
            else:
                rutina.start_date = None
        if 'end_date' in data:
            end_date = data.get('end_date') or None
            if end_date:
                try:
                    rutina.end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({"success": False, "message": "Fecha fin inválida"}), 400
            else:
                rutina.end_date = None

        log_action(db, 'update_rutina', 'rutina', rutina_id)
        db.commit()
        return jsonify({"success": True})

@admin_bp.route('/admin/rutinas/<int:rutina_id>', methods=['DELETE'])
@require_coach_or_admin
def delete_rutina(rutina_id):
    """Delete a routine"""
    with SessionLocal() as db:
        rutina = db.query(Rutina).filter(Rutina.id == rutina_id).first()
        if not rutina:
            return jsonify({"success": False, "message": "Rutina no existe"}), 404
        log_action(db, 'delete_rutina', 'rutina', rutina_id)
        db.delete(rutina)
        db.commit()
        return jsonify({"success": True})

# ============================================================================
# EJERCICIOS (Exercise Catalog) ROUTES
# ============================================================================

@admin_bp.route('/admin/ejercicios', methods=['GET'])
@require_coach_or_admin
def list_ejercicios():
    """List all exercises, optionally filtered by body section"""
    body_section = request.args.get('body_section')
    search = request.args.get('search', '').strip()

    with SessionLocal() as db:
        query = db.query(Ejercicio).filter(Ejercicio.is_active == True)

        if body_section and body_section in [bs.value for bs in BodySection]:
            query = query.filter(Ejercicio.body_section == BodySection(body_section))

        if search:
            query = query.filter(Ejercicio.name.ilike(f'%{search}%'))

        ejercicios = query.order_by(Ejercicio.name).all()
        return jsonify({"success": True, "ejercicios": [e.to_dict() for e in ejercicios]})

# ============================================================================
# RUTINA-EJERCICIO (Exercise Assignment) ROUTES
# ============================================================================

@admin_bp.route('/admin/rutinas/<int:rutina_id>/ejercicios', methods=['POST'])
@require_coach_or_admin
def add_ejercicio_to_rutina(rutina_id):
    """Add an exercise to a routine with configuration"""
    data = request.get_json() or {}
    ejercicio_id = data.get('ejercicio_id')

    if not ejercicio_id:
        return jsonify({"success": False, "message": "Ejercicio ID requerido"}), 400

    with SessionLocal() as db:
        rutina = db.query(Rutina).filter(Rutina.id == rutina_id).first()
        if not rutina:
            return jsonify({"success": False, "message": "Rutina no existe"}), 404

        ejercicio = db.query(Ejercicio).filter(Ejercicio.id == ejercicio_id).first()
        if not ejercicio:
            return jsonify({"success": False, "message": "Ejercicio no existe"}), 404

        # Check if already added
        existing = db.query(RutinaEjercicio).filter(
            RutinaEjercicio.rutina_id == rutina_id,
            RutinaEjercicio.ejercicio_id == ejercicio_id
        ).first()
        if existing:
            return jsonify({"success": False, "message": "Ejercicio ya está en la rutina"}), 400

        # Get max orden
        max_orden = db.query(RutinaEjercicio).filter(
            RutinaEjercicio.rutina_id == rutina_id
        ).count()

        rutina_ejercicio = RutinaEjercicio(
            rutina_id=rutina_id,
            ejercicio_id=ejercicio_id,
            series=data.get('series', 3),
            repeticiones=data.get('repeticiones'),
            peso=data.get('peso'),
            descanso=data.get('descanso'),
            notas=data.get('notas'),
            orden=max_orden
        )
        db.add(rutina_ejercicio)
        db.commit()
        db.refresh(rutina_ejercicio)
        return jsonify({"success": True, "rutina_ejercicio": rutina_ejercicio.to_dict()})

@admin_bp.route('/admin/rutinas/<int:rutina_id>/ejercicios/<int:re_id>', methods=['PATCH'])
@require_coach_or_admin
def update_rutina_ejercicio(rutina_id, re_id):
    """Update exercise configuration in a routine"""
    data = request.get_json() or {}

    with SessionLocal() as db:
        re = db.query(RutinaEjercicio).filter(
            RutinaEjercicio.id == re_id,
            RutinaEjercicio.rutina_id == rutina_id
        ).first()
        if not re:
            return jsonify({"success": False, "message": "Ejercicio no encontrado en rutina"}), 404

        if 'series' in data:
            re.series = int(data['series']) if data['series'] else 3
        if 'repeticiones' in data:
            re.repeticiones = (data['repeticiones'] or '').strip() or None
        if 'peso' in data:
            re.peso = (data['peso'] or '').strip() or None
        if 'descanso' in data:
            re.descanso = (data['descanso'] or '').strip() or None
        if 'notas' in data:
            re.notas = (data['notas'] or '').strip() or None
        if 'orden' in data:
            re.orden = int(data['orden'])

        db.commit()
        return jsonify({"success": True})

@admin_bp.route('/admin/rutinas/<int:rutina_id>/ejercicios/<int:re_id>', methods=['DELETE'])
@require_coach_or_admin
def remove_ejercicio_from_rutina(rutina_id, re_id):
    """Remove an exercise from a routine"""
    with SessionLocal() as db:
        re = db.query(RutinaEjercicio).filter(
            RutinaEjercicio.id == re_id,
            RutinaEjercicio.rutina_id == rutina_id
        ).first()
        if not re:
            return jsonify({"success": False, "message": "Ejercicio no encontrado"}), 404

        db.delete(re)
        db.commit()
        return jsonify({"success": True})

@admin_bp.route('/admin/rutinas/<int:rutina_id>/ejercicios/reorder', methods=['POST'])
@require_coach_or_admin
def reorder_ejercicios(rutina_id):
    """Reorder exercises in a routine"""
    data = request.get_json() or {}
    order = data.get('order', [])  # List of rutina_ejercicio IDs in new order

    if not isinstance(order, list):
        return jsonify({"success": False, "message": "Order debe ser una lista"}), 400

    with SessionLocal() as db:
        for idx, re_id in enumerate(order):
            re = db.query(RutinaEjercicio).filter(
                RutinaEjercicio.id == re_id,
                RutinaEjercicio.rutina_id == rutina_id
            ).first()
            if re:
                re.orden = idx
        db.commit()
        return jsonify({"success": True})

# ============================================================================
# IMAGE ORGANIZER ROUTES
# ============================================================================

@admin_bp.route('/admin/image-organizer')
@require_admin
def image_organizer():
    """Serve the image organizer tool"""
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    return send_from_directory(static_dir, 'image_organizer_v2.html')

@admin_bp.route('/admin/ejercicios/organized', methods=['GET'])
@require_admin
def get_organized_ejercicios():
    """Get all exercises organized by body section with their images"""
    with SessionLocal() as db:
        ejercicios = db.query(Ejercicio).filter(Ejercicio.is_active == True).order_by(Ejercicio.id).all()

        # Group by body section
        organized = {}
        for ej in ejercicios:
            section = ej.body_section.value
            if section not in organized:
                organized[section] = []
            organized[section].append({
                'id': ej.id,
                'name': ej.name,
                'image_url': ej.image_url,
                'body_section': section
            })

        return jsonify({"success": True, "exercises": organized})
