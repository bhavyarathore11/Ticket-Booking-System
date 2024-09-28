from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tickets.db'
db = SQLAlchemy(app)
from models import User
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('home'))
    return render_template('login.html')
from models import Event

@app.route('/home')
def home():
    events = Event.query.all()
    return render_template('tickets.html', events=events)


from models import Booking


@app.route('/book/<int:event_id>', methods=['GET', 'POST'])
def book(event_id):
    if request.method == 'POST':
        tickets = int(request.form['tickets'])
        event = Event.query.get_or_404(event_id)

        if event.tickets_available >= tickets:
            event.tickets_available -= tickets
            booking = Booking(user_id=session['user_id'], event_id=event_id, tickets_booked=tickets)
            db.session.add(booking)
            db.session.commit()
            return redirect(url_for('home'))
        else:
            return "Not enough tickets available."
    event = Event.query.get(event_id)
    return render_template('book.html', event=event)


import stripe

stripe.api_key = 'your_stripe_secret_key'

@app.route('/payment', methods=['POST'])
def payment():
    amount = request.form['amount']
    intent = stripe.PaymentIntent.create(
        amount=int(amount) * 100,  # Stripe accepts amounts in cents
        currency='usd',
    )
    return render_template('payment.html', client_secret=intent['client_secret'])

from flask_mail import Mail, Message

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_email_password'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

def send_confirmation_email(user_email, event_name, tickets):
    msg = Message('Ticket Booking Confirmation', sender='your_email@gmail.com', recipients=[user_email])
    msg.body = f"You have successfully booked {tickets} tickets for {event_name}."
    mail.send(msg)

@app.route('/confirm', methods=['POST'])
def confirm_booking():
    user_email = request.form['email']
    event_name = request.form['event']
    tickets = request.form['tickets']
    send_confirmation_email(user_email, event_name, tickets)
    return "Confirmation email sent!"

@app.route('/my_bookings')
def my_bookings():
    user_id = session['user_id']
    bookings = Booking.query.filter_by(user_id=user_id).all()
    return render_template('my_bookings.html', bookings=bookings)
