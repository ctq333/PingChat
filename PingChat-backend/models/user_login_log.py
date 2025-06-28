from extensions import db
from sqlalchemy.sql import func

class UserLoginLog(db.Model):
    __tablename__ = 'user_login_logs'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    login_time = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    ip_address = db.Column(db.String(64))
    device_info = db.Column(db.String(128))
    success = db.Column(db.Boolean, default=True)