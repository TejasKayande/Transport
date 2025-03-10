from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Driver(db.Model):
    id    = db.Column(db.Integer, primary_key=True)
    name  = db.Column(db.String(100), nullable=False) 
    email = db.Column(db.String(100), unique=True, nullable=False) 


class Client(db.Model):
    id    = db.Column(db.Integer, primary_key=True)
    name  = db.Column(db.String(100), nullable=False) 
    email = db.Column(db.String(100), unique=True, nullable=False) 