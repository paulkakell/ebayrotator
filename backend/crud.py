from sqlalchemy.orm import Session
from app import models

def log_error(db: Session, step: str, message: str, sku: str = None):
    error = models.ErrorLog(step=step, message=message, sku=sku)
    db.add(error)
    db.commit()

def update_rotation_status(db: Session, sku: str, success: bool):
    status = models.RotationStatus(last_sku=sku, success=success)
    db.add(status)
    db.commit()

def get_settings(db: Session):
    return {s.key: s.value for s in db.query(models.Setting).all()}

def set_setting(db: Session, key: str, value: str):
    existing = db.query(models.Setting).filter_by(key=key).first()
    if existing:
        existing.value = value
    else:
        new_setting = models.Setting(key=key, value=value)
        db.add(new_setting)
    db.commit()
