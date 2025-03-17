
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
from models import Order

db.init_app(app)

with app.app_context():
    db.create_all()


def isRegistered():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if not user:
            session.clear()
            return False
        return True
    return False

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        email    = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            session['user_id'] = user.id
            session['role']    = user.role

            flash("Login successful!", "success")

            return redirect('/')
        else:
            flash("Invalid email or password!", "error")

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name             = request.form['name']
        email            = request.form['email']
        role             = request.form['role']
        password         = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect('/register')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please log in.", "error")
            return redirect('/login')

        hashed_password = generate_password_hash(password)

        new_user = User(name=name, email=email, role=role, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        if role == "Client":
            db.session.add(Client(id=new_user.id))

        if role == "Driver":
            db.session.add(Driver(id=new_user.id))

        db.session.commit()

        flash("Registration successful! You can now log in.", "success")

        return redirect('/login')

    return render_template('register.html')


@app.route("/admin")
def admin():

    if "user_id" not in session or session.get("role") != "Admin":
        flash("Access Denied! Only admins have access to admin panel", "error")
        return redirect(url_for("login"))

    total_orders    = Order.query.count()
    total_shipments = 0
    total_users     = User.query.count()
    return render_template('admin.html', total_orders=total_orders, 
                           total_shipments=total_shipments, total_users=total_users)


@app.route('/manage-orders', methods=['GET', 'POST'])
def manage_orders():
    if "user_id" not in session or session.get("role") != "Admin":
        flash("Access Denied! Only admins can manage orders.", "error")
        return redirect(url_for("login"))

    session.pop('_flashes', None)

    orders = Order.query.all()

    if request.method == 'POST':
        order_id = request.form['order_id']
        new_status = request.form['status']
        order = Order.query.get(order_id)
        if order:
            order.status = new_status
            db.session.commit()
            flash("Order status updated successfully!", "success")

    return render_template('manageorders.html', orders=orders)

@app.route('/delete-order', methods=['POST'])
def delete_order():
    if "user_id" not in session or session.get("role") != "Admin":
        flash("Access Denied! Only admins can manage orders.", "error")
        return redirect(url_for("login"))

    order_id = request.form['order_id']
    order = Order.query.get(order_id)
    if order:
        db.session.delete(order)
        db.session.commit()
        flash("Order deleted successfully!", "success")
    else:
        flash("Order not found!", "error")

    return redirect('/manage-orders')

@app.route("/manage-users", methods=["GET", "POST"])
def manage_users():
    if "user_id" not in session or session.get("role") != "Admin":
        flash("Access Denied! Only admins can manage users.", "error")
        return redirect(url_for("login"))

    users = User.query.all()

    if request.method == "POST":
        user_id = request.form.get("user_id")
        action = request.form.get("action")

        user = User.query.get(user_id)

        if action == "delete":
            if user:
                db.session.delete(user)
                db.session.commit()
                flash("User deleted successfully!", "success")

        elif action == "update_role":
            new_role = request.form.get("new_role")
            if user and new_role in ["Admin", "Client", "Driver"]:
                user.role = new_role
                db.session.commit()
                flash("User role updated successfully!", "success")

        return redirect(url_for("manage_users"))

    return render_template("manageusers.html", users=users)


@app.route("/tracking")
def tracking():

    if not isRegistered():
        flash("You must login first before accessing the tracking page!")
        return render_template('login.html')

    return render_template('tracking.html')

@app.route("/quote", methods=['GET', 'POST'])
def quote():

    if not isRegistered():
        flash("You must login first before accessing the Quotes page!")
        return render_template('login.html')

    if request.method == 'POST':

        shipment_type = request.form['shipment_type']
        weight        = request.form['weight']
        dimention     = request.form['dimensions']
        origin        = request.form['origin']
        destination   = request.form['destination']
        note          = request.form['notes']

        new_order = Order(user_id=session.get('user_id'), total_price=0.0, 
                          shipment_type=shipment_type, weight=weight, dimention=dimention, 
                          origin=origin, destination=destination, note=note)

        db.session.add(new_order)
        db.session.commit()

        flash("Your Order was Successfully recorded!")

        return render_template('index.html')

    return render_template('quote.html')


@app.route("/services")
def services():
    return render_template('services.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/contact")
def contact():
    return render_template('contact.html')


@app.route("/")
def home():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8888", debug=True)
