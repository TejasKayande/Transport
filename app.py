
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Database.db'
app.secret_key = 'a3f1b4e2d7c9a8735b1a93d8e0f2a7b6'

from models import db
from models import Client
from models import Driver
from models import User
from models import Order
from models import Bid

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

def close_expired_bids():
    """Automatically selects the lowest bid and closes expired orders."""
    expired_orders = Order.query.filter(Order.bidding_end_time <= datetime.utcnow(), Order.status == "pending").all()

    for order in expired_orders:
        if order.bids:
            winning_bid = min(order.bids, key=lambda bid: bid.bid_price)
            order.winning_bid_id = winning_bid.id
            order.status = "closed"
        else:
            order.status = "expired"  # No bids were placed

    db.session.commit()

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


@app.route("/biddings")
def biddings():
    if not isRegistered() or session.get('role') != "Driver":
        flash("Only drivers can view bids!", "error")
        return redirect('/')

    close_expired_bids()

    open_orders = Order.query.all()
    return render_template("bidding.html", orders=open_orders)


@app.route("/place_bid/<int:order_id>", methods=['GET', 'POST'])
def place_bid(order_id):
    if not isRegistered() or session.get('role') != "Driver":
        flash("Only drivers can place bids!", "error")
        return redirect('/')

    order = Order.query.get(order_id)

    if not order:
        flash("Order not found!", "error")
        return redirect(url_for('bidding'))

    if order.bidding_end_time <= datetime.utcnow():
        flash("Bidding for this order has ended!", "error")
        return redirect(url_for('biddings'))

    if request.method == 'POST':
        bid_price = request.form['bid_price']
        driver_id = session.get('user_id')

        lowest_bid = db.session.query(db.func.min(Bid.bid_price)).filter(Bid.order_id == order_id).scalar()
        if request.method == 'POST':
            try:
                bid_price = float(request.form['bid_price'])  # Convert input to float
            except ValueError:
                flash("Invalid bid amount! Please enter a valid number.", "error")

                return redirect(url_for('place_bid', order_id=order_id))

        if lowest_bid is not None and bid_price >= float(lowest_bid):
            flash(f"Your bid must be lower than the current lowest bid: ${lowest_bid:.2f}", "error")
            return redirect(url_for('place_bid', order_id=order_id))

        new_bid = Bid(order_id=order_id, driver_id=driver_id, bid_price=bid_price)
        db.session.add(new_bid)
        db.session.commit()

        flash("Your bid has been placed successfully!", "success")
        return redirect(url_for('biddings'))

    return render_template("place_bid.html", order=order)


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
        dimension     = request.form['dimensions']
        origin        = request.form['origin']
        destination   = request.form['destination']
        note          = request.form['notes']

        bidding_end_time = datetime.utcnow() + timedelta(hours=24)

        new_order = Order(client_id=session.get('user_id'), total_price=0.0, 
                          shipment_type=shipment_type, weight=weight, dimension=dimension, 
                          origin=origin, destination=destination, note=note, status="pending",
                          bidding_end_time=bidding_end_time)

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
