
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Database.db'
app.secret_key = 'a3f1b4e2d7c9a8735b1a93d8e0f2a7b6'


from models import db
from models import Client
from models import Driver
from models import User

db.init_app(app)


with app.app_context():
    db.create_all()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            flash("Login successful!", "success")
            return redirect('/')
        else:
            flash("Invalid email or password!", "error")

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        role = request.form['role']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if passwords match
        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect('/register')

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please log in.", "error")
            return redirect('/login')

        # Hash the password before storing
        hashed_password = generate_password_hash(password)

        # Create new user
        new_user = User(name=name, email=email, role=role, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! You can now log in.", "success")
        return redirect('/login')

    return render_template('register.html')



@app.route("/")
def home():
    return render_template('index.html')

@app.route("/services")
def services():
    return render_template('services.html')

@app.route("/tracking")
def tracking():
    return render_template('tracking.html')

@app.route("/quote")
def quote():
    return render_template('quote.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/contact")
def contact():
    return render_template('contact.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8888", debug=True)
