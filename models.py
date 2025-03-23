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

class Bid(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    order_id   = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    driver_id  = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)
    bid_price  = db.Column(db.Float, nullable=False)
    bid_time   = db.Column(db.DateTime, default=datetime.utcnow)

    # Fix: Explicitly define the foreign key relationship
    order = db.relationship('Order', back_populates="bids", foreign_keys=[order_id])
    driver = db.relationship('Driver', backref=db.backref('bids', lazy=True))

class Order(db.Model):
    id               = db.Column(db.Integer, primary_key=True)
    shipment_type    = db.Column(db.String(50), nullable=False)
    weight           = db.Column(db.Integer, nullable=False)
    dimension        = db.Column(db.String(10), nullable=False)
    origin           = db.Column(db.String(50), nullable=False)
    destination      = db.Column(db.String(50), nullable=False)
    note             = db.Column(db.String(200), nullable=True, default="")
    
    client_id        = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    order_date       = db.Column(db.DateTime, default=datetime.utcnow)
    total_price      = db.Column(db.Float, nullable=False)
    status           = db.Column(db.String(50), default="pending")
    
    bidding_end_time = db.Column(db.DateTime, nullable=False)
    winning_bid_id   = db.Column(db.Integer, db.ForeignKey('bid.id'), nullable=True)

    bids = db.relationship('Bid', back_populates="order", foreign_keys=[Bid.order_id])
    winning_bid = db.relationship('Bid', foreign_keys=[winning_bid_id], uselist=False)

    client = db.relationship('Client', backref=db.backref('orders', lazy=True))
