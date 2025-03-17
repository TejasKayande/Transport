from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(100), nullable=False)
    email    = db.Column(db.String(100), unique=True, nullable=False)
    role     = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    client = db.relationship("Client", back_populates="user", uselist=False)
    driver = db.relationship("Driver", back_populates="user", uselist=False)

class Driver(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

    # relation
    user = db.relationship("User", back_populates="driver")


class Client(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

    # relation
    user = db.relationship("User", back_populates="client")


class Order(db.Model):
    id          = db.Column(db.Integer, primary_key=True)

    shipment_type = db.Column(db.String(50), nullable=False)
    weight        = db.Column(db.Integer, nullable=False)
    dimention     = db.Column(db.String(10), nullable=False)
    origin        = db.Column(db.String(50), nullable=False)
    destination   = db.Column(db.String(50), nullable=False)
    note          = db.Column(db.String(200), nullable=True, default="")

    user_id     = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    order_date  = db.Column(db.DateTime, default=datetime.now)

    total_price = db.Column(db.Float, nullable=False)
    status      = db.Column(db.String(50), default="pending")

    client = db.relationship('Client', backref=db.backref('orders', lazy=True))