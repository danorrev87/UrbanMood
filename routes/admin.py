from flask import Blueprint, request, jsonify, render_template, redirect
from db import SessionLocal
from models import User, UserRole, InvitationToken, InvitationPurpose, Clase
from routes.auth import send_invitation_email
from datetime import datetime
import secrets

admin_bp = Blueprint('admin', __name__)

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
        return render_template('admin_user_detail.html', user=user)

# --- Placeholder section routes ---
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
        db.commit()
        return jsonify({"success": True})

@admin_bp.route('/admin/clases/<int:clase_id>', methods=['DELETE'])
@require_admin
def delete_clase(clase_id):
    with SessionLocal() as db:
        clase = db.query(Clase).filter(Clase.id==clase_id).first()
        if not clase:
            return jsonify({"success": False, "message": "No existe"}), 404
        db.delete(clase)
        db.commit()
        return jsonify({"success": True})

@admin_bp.route('/admin/rutinas')
@require_admin
def admin_rutinas():
    return render_template('admin_section_placeholder.html', title='Rutinas', description='Gestión de rutinas próximamente')

@admin_bp.route('/admin/sucursales')
@require_admin
def admin_sucursales():
    return render_template('admin_section_placeholder.html', title='Sucursales', description='Gestión de sucursales próximamente')

@admin_bp.route('/admin/entrenadores')
@require_admin
def admin_entrenadores():
    return render_template('admin_section_placeholder.html', title='Entrenadores', description='Gestión de entrenadores próximamente')
