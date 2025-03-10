from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'client' or 'driver'
    password = db.Column(db.String(255), nullable=False)  # Store hashed passwords

class Driver(db.Model):
    id    = db.Column(db.Integer, primary_key=True)
    name  = db.Column(db.String(100), nullable=False) 
    email = db.Column(db.String(100), unique=True, nullable=False) 


class Client(db.Model):
    id    = db.Column(db.Integer, primary_key=True)
    name  = db.Column(db.String(100), nullable=False) 
    email = db.Column(db.String(100), unique=True, nullable=False) 