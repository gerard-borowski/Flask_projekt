from . import db
from flask_login import UserMixin
from sqlalchemy import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150),unique=True)
    password = db.Column(db.String(150))
    plec = db.Column(db.String(20))
    admin = db.Column(db.Boolean)
    reviews = db.relationship("Review")


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(250))
    id_user = db.Column(db.Integer, db.ForeignKey("user.id"))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    status = db.Column(db.String(50))
