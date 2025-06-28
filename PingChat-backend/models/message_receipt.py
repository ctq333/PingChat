from extensions import db

class MessageReceipt(db.Model):
    __tablename__ = 'message_receipts'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    message_id = db.Column(db.BigInteger, db.ForeignKey('messages.id'), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    delivered_time = db.Column(db.DateTime)
    read_time = db.Column(db.DateTime)