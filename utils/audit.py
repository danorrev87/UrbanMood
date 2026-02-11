import json
from flask import session
from models.audit import AuditLog

def log_action(db, action, entity=None, entity_id=None, meta=None):
    """Log an admin action. Reads user_id from flask session."""
    log = AuditLog(
        user_id=session.get('uid'),
        action=action,
        entity=entity,
        entity_id=entity_id,
        meta=json.dumps(meta, default=str) if meta else None
    )
    db.add(log)
