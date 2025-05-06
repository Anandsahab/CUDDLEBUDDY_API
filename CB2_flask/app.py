from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
import requests
import logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask application
app = Flask(__name__)
# Set secret key for session security
app.config['SECRET_KEY'] = 'your-secret-key-here'
# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Enable CORS for all routes
app.config['CORS_HEADERS'] = 'Content-Type'

# Handle CORS for API routes
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# Initialize SQLAlchemy
db = SQLAlchemy(app)
# Initialize Flask-Login
login_manager = LoginManager(app)
# Set the login view for unauthorized users
login_manager.login_view = 'login'

# Helper function for page-specific flash messages
def flash_page(message, category, page_key):
    """Flash a message for a specific page only"""
    if 'page_flashes' not in session:
        session['page_flashes'] = {}
    
    if page_key not in session['page_flashes']:
        session['page_flashes'][page_key] = []
    
    session['page_flashes'][page_key].append({
        'message': message,
        'category': category
    })

# Helper function to get and clear page-specific flash messages
def get_flashed_messages_for_page(page_key):
    """Get and clear flash messages for a specific page"""
    if 'page_flashes' in session and page_key in session['page_flashes']:
        messages = session['page_flashes'][page_key]
        del session['page_flashes'][page_key]
        return messages
    return []

# Database Models
class User(UserMixin, db.Model):
    """User model for patients"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    
    def set_password(self, password):
        """Create hashed password for new user"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check hashed password for login"""
        return check_password_hash(self.password_hash, password)

class Message(db.Model):
    """Model for storing messages from users"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    # timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    # read = db.Column(db.Boolean, default=False)
   #  timestamp = db.Column(db.DateTime, default=datetime.utcnow)
   
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    persons = db.Column(db.Integer, nullable=False)
    # timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Admin(UserMixin,db.Model):
    "Admin model"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email= db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        """Create hashed password for new user"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check hashed password for login"""
        return check_password_hash(self.password_hash, password)

class PetBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pet_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    pet_type = db.Column(db.String(50), nullable=False)
    breed = db.Column(db.String(100), nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    
    admin = Admin.query.get(int(user_id))
    if admin:
       return admin
    


    user = User.query.get(int(user_id))
    if user:
        return user
    # Then try Doctor model
    # return Doctor.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, Admin):
            flash('You need to be logged in as an admin to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
@app.route('/')
def index():
    """Render homepage"""
    app.logger.debug(f'current_user: {current_user.is_authenticated}')
    if "username" in session:
        return render_template('index.html', username=session['username'])
    return render_template('index.html')

# Routes for User Authentication

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    # Get page-specific messages for login page
    page_flashes = get_flashed_messages_for_page('login')
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        app.logger.debug(f"Login attempt for username: {username}")
        
        # Find user by username
        admin = Admin.query.filter_by(username=username).first()
        if admin:
            app.logger.debug(f"Found admin user: {admin.username}")
            password_check = admin.check_password(password)
            app.logger.debug(f"Admin password check result: {password_check}")
            if password_check:
                login_user(admin)
                app.logger.debug(f"Admin login successful")
                return redirect(url_for('admin_dashboard'))

        user = User.query.filter_by(username=username).first()
        if user:
            app.logger.debug(f"Found regular user: {user.username}")
            password_check = user.check_password(password)
            app.logger.debug(f"User password check result: {password_check}")
            if password_check:
                login_user(user)
                app.logger.debug(f"User login successful")
                return redirect(url_for('index'))
        
        app.logger.debug(f"Login failed for username: {username}")
        flash_page('Invalid username or password', 'danger', 'login')
        return redirect(url_for('login'))
    
    return render_template('login.html', page_flashes=page_flashes)

@app.route('/admin_dashboard')
@admin_required
def admin_dashboard():

   return render_template('admin_dashboard.html')
   
   
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user registration"""
    # Get page-specific messages for signup page
    page_flashes = get_flashed_messages_for_page('signup')
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validate passwords match
        if password != confirm_password:
            flash_page('Passwords do not match', 'danger', 'signup')
            return redirect(url_for('signup'))

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash_page('Username already exists', 'danger', 'signup')
            return redirect(url_for('signup'))
        
        #check if email already exists
        if User.query.filter_by(email=email).first():
           flash_page('Email already exists', 'danger', 'signup')
           return redirect(url_for('signup'))

        # Create new user with hashed password
        user = User(
            username=username,
            email=email
        )
        user.set_password(password)
        flash_page('Registration successful', 'success', 'login')
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html', page_flashes=page_flashes)

@app.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    session.pop('username', None)
    logout_user()
    return redirect(url_for('login'))



# @app.route('/')
# def ind():
#     if 'user_id' in session:
#         # user = User.query.get(session['user_id'])
#         return render_template('index.html')
#     return render_template('index.html')

@app.route("/dd")
def dd():
  return render_template("dd1.html")

@app.route("/cd")
def cd():
  return render_template("cd1.html")

@app.route("/bd")
def bd():
  return render_template("bd1.html")

@app.route("/fd")
def fd():
  return render_template("fd1.html")

@app.route("/hd")
def hd():
  return render_template("hd1.html")

@app.route("/rd")
def rd():
  return render_template("rd1.html")

@app.route("/about")
def about():
  return render_template("about.html")

@app.route("/contact")
@login_required
def contact():
  return render_template("contact.html")



   #  def __repr__(self):
   #      return f'<Message {self.id} from {self.name}>'
    

# @app.route('/send_message', methods=['POST'])
# def send_message():
#     """Handle message submission from the contact form"""
#     name = request.form.get('name')
#     email = request.form.get('email')
#     subject = request.form.get('subject')
#     message = request.form.get('message')

#     # Create a new Message instance
#     new_message = Message(name=name, email=email, subject=subject, message=message)
#     try:
#         # Add the message to the database
#         db.session.add(new_message)
#         db.session.commit()
#         flash('Your message has been sent successfully!', 'success')
#     except Exception as e:
#         db.session.rollback()  # Rollback the session in case of error
#         flash('An error occurred while sending your message. Please try again.', 'error')
#         app.logger.error(f'Error saving message: {e}')  # Log the error for debugging

#     return redirect(url_for('contact'))
@app.route('/send_message', methods=['POST'])
def send_message():
    """Handle message submission from the contact form"""
    try:
        # Validate that all required fields are present
        if not all([
            request.form.get('name'),
            request.form.get('email'),
            request.form.get('subject'),
            request.form.get('message')
        ]):
            flash('All fields are required', 'error')
            return redirect(url_for('appointment'))

        # Create a new Message instance
        new_message = Message(
            name=request.form.get('name'),
            email=request.form.get('email'),
            subject=request.form.get('subject'),
            message=request.form.get('message')
        )

        # Add and commit the message to the database
        db.session.add(new_message)
        db.session.commit()
        
        flash('Your message has been sent successfully!', 'success')
        return redirect(url_for('contact'))

    except Exception as e:
        db.session.rollback()
        flash('Appointment Booked Successfully')
        app.logger.error(f'Error booking appointment: {str(e)}')
        return redirect(url_for('appointment'))

@app.route('/messages')
@login_required  # Optional: require login to view messages
def messages():
    """Display all messages"""
    all_messages = Message.query.all()
    return render_template('messages.html', messages=all_messages)


# @app.route("/profile")
# @login_required
# def profile():
#    new_appointment = Appointment.query.filter(Appointment.email==current_user.email).all()
#    return render_template("profile.html",
#         new_appointment=new_appointment)


@app.route("/booking")
@login_required
def booking():
   return render_template("booking.html")

@app.route('/book_pet', methods=['POST'])
@login_required
def book_pet():
    try:
        # Get form data
        pet_name = request.form.get('pet_name')
        email = request.form.get('email')
        pet_type = request.form.get('pet_type')
        breed = request.form.get('breed')
        address = request.form.get('address')
        payment_method = request.form.get('payment_method')
        
        # Validate form data
        if not all([pet_name, email, pet_type, breed, address, payment_method]):
            flash("All fields are required", "error")
            return redirect(url_for('booking'))
        
        # Create new booking
        new_booking = PetBooking(
            pet_name=pet_name,
            email=email,
            pet_type=pet_type,
            breed=breed,
            address=address,
            payment_method=payment_method,
            user_id=current_user.id
        )
        
        # Save to database
        db.session.add(new_booking)
        db.session.commit()
        
        flash('Pet booked successfully! We will contact you soon.', 'success')
        return redirect(url_for('booking'))
        
    except Exception as e:
        db.session.rollback()
        flash('Pet booked successfully! We will contact you soon.','error')
        app.logger.error(f'Error booking pet: {str(e)}')
        return redirect(url_for('booking'))
    

@app.route('/appointment')
@login_required
def appointment():
    """Render appointment page with minimum date set to today"""
    # Get page-specific messages for appointment page
    page_flashes = get_flashed_messages_for_page('appointment')
    today = datetime.today().strftime('%Y-%m-%d')
    return render_template("appointment.html", today=today, page_flashes=page_flashes)
# 1. First ensure proper imports at the top
# from datetime import datetime, timedelta

# 2. Replace or update your Appointment model to ensure all fields are properly defined

# 3. Update your book_appointment route to properly handle the data
# @app.route('/book_appointment', methods=['POST'])
# def book_appointment():
#     try:
#         # Get form data with proper error handling
#         name = request.form.get('name')
#         email = request.form.get('email')
#         phone = request.form.get('phone')
#         date = request.form.get('date')
#         time = request.form.get('time')
#         persons = request.form.get('persons')

#         # Convert date and time strings to proper Python objects
#         appointment_date = datetime.strptime(date, '%Y-%m-%d').date()
#         appointment_time = datetime.strptime(time, '%H:%M').time()
#         persons = int(persons)

#         # Create and save the appointment
#         new_appointment = Appointment(
#             name=name,
#             email=email,
#             phone=phone,
#             date=appointment_date,
#             time=appointment_time,
#             persons=persons
#         )

#         # Add and commit to database
#         db.session.add(new_appointment)
#         db.session.commit()
        
#         flash('Appointment booked successfully!', 'success')
#         return redirect(url_for('appointment'))

#     except Exception as e:
#         db.session.rollback()
#         flash('Error booking appointment. Please try again.', 'error')
#         return redirect(url_for('appointment'))

# @app.route('/book_appointment', methods=['POST'])
# def book_appointment():
#     # Get form data
#     name = request.form.get('name')
#     email = request.form.get('email')
#     phone = request.form.get('phone')
#     date = request.form.get('date')
#     time = request.form.get('time')
#     persons = request.form.get('persons')

#     # Basic validation
#     if not all([name, email, phone, persons,date,time]):
#         flash('All fields are required', 'error')
#         return redirect(url_for('appointment'))

#     try:
#         # Convert date and time strings to proper Python objects
#         appointment_date = datetime.strptime(date, '%d-%m-%Y').date()
#         appointment_time = datetime.strptime(time, '%H:%M').time()
#         persons_count = int(persons)

#         new_appointment = Appointment(
#             name=name,
#             email=email,
#             phone=phone,
#             date=appointment_date,
#             time=appointment_time,
#             persons=persons_count
#         )

        
#         db.session.add(new_appointment)
#         db.session.commit()

#         flash('Appointment booked successfully!', 'success')
#         return redirect(url_for('appointment'))

#     except ValueError as ve:
#         db.session.rollback()
#         flash('Invalid date or time format', 'error')
#         app.logger.error(f'validation error: {str(ve)}')
#         return redirect(url_for('appointment'))

@app.route('/book_appointment', methods=['POST'])
def book_appointment():
    # Get form data
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    date = request.form.get('date')
    time = request.form.get('time')
    persons = request.form.get('persons')

    # Debug logging
    app.logger.debug(f"Received form data: date={date}, time={time}")

    # Basic validation
    if not all([name, email, phone, date, time, persons]):
        flash_page('All fields are required', 'danger', 'appointment')
        return redirect(url_for('appointment'))

    try:
        # Convert date and time strings to proper Python objects
        # Expecting date in YYYY-MM-DD format from HTML5 date input
        appointment_date = datetime.strptime(date, '%Y-%m-%d').date()
        appointment_time = datetime.strptime(time, '%H:%M').time()
        persons_count = int(persons)

        # Validate number of persons
        if persons_count <= 0:
            flash_page('Number of persons must be greater than 0', 'danger', 'appointment')
            return redirect(url_for('appointment'))

        new_appointment = Appointment(
            name=name,
            email=email,
            phone=phone,
            date=appointment_date,
            time=appointment_time,
            persons=persons_count
        )
        
        db.session.add(new_appointment)
        db.session.commit()

        flash_page('Appointment booked successfully!', 'success', 'appointment')
        return redirect(url_for('appointment'))

    except ValueError as ve:
        db.session.rollback()
        flash_page('Invalid date or time format. Please use the date and time pickers provided.', 'danger', 'appointment')
        app.logger.error(f'Validation error: {str(ve)}')
        return redirect(url_for('appointment'))
    except Exception as e:
        db.session.rollback()
        flash_page('An error occurred while booking your appointment. Please try again.', 'danger', 'appointment')
        app.logger.error(f'Error booking appointment: {str(e)}')
        return redirect(url_for('appointment'))
# 4. Add this at the bottom of your file to ensure database tables are created
with app.app_context():
    db.create_all()


@app.route("/blog")
def blog():
  return render_template("blog.html")

@app.route('/shihtzu')
def shihtzu():
   return render_template("shihtzu.html")

@app.route('/maltese')
def maltese():
   return render_template("maltese.html")

@app.route('/labrador')
def labrador():
   return render_template("labrador.html")


@app.route('/burmila')
def burmila():
   return render_template("burmila.html")


@app.route('/birman')
def birman():
   return render_template("birman.html")


@app.route('/york')
def york():
   return render_template("york.html")

@app.route('/hawk')
def hawk():
   return render_template("hawk.html")


@app.route('/owl')
def owl():
   return render_template("owl.html")


@app.route('/lovebirds')
def lovebirds():
   return render_template("lovebirds.html")

@app.route('/splittin')
def splittin():
   return render_template("splittin.html")

@app.route('/cici')
def cici():
   return render_template("cici.html")

@app.route('/butterfly')
def butterfly():
   return render_template("butterfly.html")

@app.route('/blanc')
def blanc():
   return render_template("blanc.html")

@app.route('/dutch')
def dutch():
   return render_template("dutch.html")

@app.route('/satin')
def satin():
   return render_template("satin.html")

@app.route('/saddlebred')
def saddlebred():
   return render_template("saddlebred.html")

@app.route('/fell')
def fell():
   return render_template("fell.html")

@app.route('/arabian')
def arabian():
   return render_template("arabian.html")















@app.route('/forgot-password')
def forgot_password():
    # Your forgot password logic here
    pass

@app.route('/google-login')
def google_login():
    # Your Google OAuth logic here
    pass

@app.route('/book')  # or whatever URL you want to use
def book():
    return render_template('booking.html')  # Make sure this matches your template name



with app.app_context():
     db.create_all()
     if Admin.query.count() == 0:
        admin = Admin(username='Bandar', email='admin@example.com')
        admin.set_password('Kaju')
        db.session.add(admin)
        db.session.commit()
        print("Created admin user: Bandar/Kaju")
     else:
        # Check if admin exists but might have password issues
        admin = Admin.query.filter_by(username='Bandar').first()
        if admin:
            # Reset the password to ensure it's correct
            admin.set_password('Kaju')
            db.session.commit()
            print("Reset admin user password")





@app.route('/api/login', methods=['POST'])
def api_login():
    """API endpoint for user login"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    app.logger.debug(f"API login attempt for username: {username}")
    
    # Find user by username
    admin = Admin.query.filter_by(username=username).first()
    if admin:
        app.logger.debug(f"Found admin user: {admin.username}")
        app.logger.debug(f"Admin password hash: {admin.password_hash}")
        password_check = admin.check_password(password)
        app.logger.debug(f"Admin password check result: {password_check}")
        if password_check:
            app.logger.debug(f"Admin login successful")
            # Return a JWT token for authentication
            return jsonify({
                'success': True,
                'user_id': admin.id,
                'username': admin.username,
                'email': admin.email,
                'is_admin': True,
                'auth_source': 'flask'
            })
    
    user = User.query.filter_by(username=username).first()
    if user:
        app.logger.debug(f"Found regular user: {user.username}")
        app.logger.debug(f"User password hash: {user.password_hash}")
        password_check = user.check_password(password)
        app.logger.debug(f"User password check result: {password_check}")
        if password_check:
            app.logger.debug(f"User login successful")
            return jsonify({
                'success': True,
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'is_admin': False,
                'auth_source': 'flask'
            })
    
    app.logger.debug(f"Login failed for username: {username}")
    return jsonify({
        'success': False,
        'error': 'Invalid username or password'
    }), 401


# Update your signup route with enhanced debugging
@app.route('/api/signup', methods=['POST'])
def api_signup():
    try:
        data = request.get_json()

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if not all([username, email, password, confirm_password]):
            return jsonify({'success': False, 'error': 'All fields are required'}), 400

        if password != confirm_password:
            return jsonify({'success': False, 'error': 'Passwords do not match'}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'error': 'Username already exists'}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'error': 'Email already exists'}), 400

        user = User(
            username=username,
            email=email
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Signup successful',
            'user_id': user.id,
            'username': user.username,
            'email': user.email
        }), 201

    except Exception as e:
        app.logger.error(f"Signup error: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

# Add the appointment API endpoint below the other API endpoints

@app.route('/api/appointment', methods=['POST'])
def api_book_appointment():
    """API endpoint for booking appointments"""
    try:
        data = request.get_json()
        
        # Extract appointment details from request
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        date_str = data.get('date') 
        time_str = data.get('time')
        persons = data.get('persons')
        
        # Validate required fields
        if not all([name, email, phone, date_str, time_str, persons]):
            return jsonify({
                'success': False, 
                'error': 'All fields are required'
            }), 400
            
        # Parse date and time
        try:
            # Expecting date in format DD-MM-YYYY or YYYY-MM-DD
            if '-' in date_str:
                if len(date_str.split('-')[0]) == 4:  # YYYY-MM-DD
                    appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                else:  # DD-MM-YYYY
                    appointment_date = datetime.strptime(date_str, '%d-%m-%Y').date()
            else:
                return jsonify({'success': False, 'error': 'Invalid date format'}), 400
                
            # Parse time (expecting HH:MM format)
            appointment_time = datetime.strptime(time_str, '%H:%M').time()
        except ValueError as e:
            return jsonify({
                'success': False, 
                'error': f'Invalid date or time format: {str(e)}'
            }), 400
            
        # Create new appointment
        new_appointment = Appointment(
            name=name,
            email=email,
            phone=phone,
            date=appointment_date,
            time=appointment_time,
            persons=int(persons)
        )
        
        # Save to database
        db.session.add(new_appointment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Appointment booked successfully',
            'appointment_id': new_appointment.id,
            'name': name,
            'date': date_str,
            'time': time_str
        }), 201
            
    except Exception as e:
        app.logger.error(f"Appointment booking error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False, 
            'error': f'Internal server error: {str(e)}'
        }), 500

# Add API endpoint to get all appointments for a specific email
@app.route('/api/appointments/<email>', methods=['GET'])
def api_get_appointments(email):
    """API endpoint to get all appointments for an email"""
    try:
        appointments = Appointment.query.filter_by(email=email).order_by(Appointment.date.desc(), Appointment.time.desc()).all()
        
        appointments_list = []
        for appointment in appointments:
            appointments_list.append({
                'id': appointment.id,
                'name': appointment.name,
                'email': appointment.email,
                'phone': appointment.phone,
                'date': appointment.date.strftime('%Y-%m-%d'),
                'time': appointment.time.strftime('%H:%M'),
                'persons': appointment.persons
            })
            
        return jsonify({
            'success': True,
            'appointments': appointments_list
        })
        
    except Exception as e:
        app.logger.error(f"Error getting appointments: {str(e)}", exc_info=True)
        return jsonify({
            'success': False, 
            'error': f'Internal server error: {str(e)}'
        }), 500

# Add API endpoint to update an appointment
@app.route('/api/appointment/<int:appointment_id>', methods=['PUT'])
def api_update_appointment(appointment_id):
    """API endpoint to update an existing appointment"""
    try:
        # Get the appointment from the database
        appointment = Appointment.query.get(appointment_id)
        
        if not appointment:
            return jsonify({
                'success': False,
                'error': 'Appointment not found'
            }), 404
            
        # Get the data from the request
        data = request.get_json()
        
        # Extract appointment details from request
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        date_str = data.get('date')
        time_str = data.get('time')
        persons = data.get('persons')
        
        # Validate required fields
        if not all([name, email, phone, date_str, time_str, persons]):
            return jsonify({
                'success': False,
                'error': 'All fields are required'
            }), 400
            
        # Parse date and time
        try:
            # Expecting date in format DD-MM-YYYY or YYYY-MM-DD
            if '-' in date_str:
                if len(date_str.split('-')[0]) == 4:  # YYYY-MM-DD
                    appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                else:  # DD-MM-YYYY
                    appointment_date = datetime.strptime(date_str, '%d-%m-%Y').date()
            else:
                return jsonify({'success': False, 'error': 'Invalid date format'}), 400
                
            # Parse time (expecting HH:MM format)
            appointment_time = datetime.strptime(time_str, '%H:%M').time()
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': f'Invalid date or time format: {str(e)}'
            }), 400
            
        # Update the appointment
        appointment.name = name
        appointment.email = email
        appointment.phone = phone
        appointment.date = appointment_date
        appointment.time = appointment_time
        appointment.persons = int(persons)
        
        # Save to database
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Appointment updated successfully',
            'appointment_id': appointment.id
        })
            
    except Exception as e:
        app.logger.error(f"Appointment update error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

# API endpoint for sending contact messages
@app.route('/api/contact', methods=['POST'])
def api_send_message():
    """API endpoint for sending contact messages"""
    try:
        # Get data from request
        data = request.get_json()
        
        # Extract message details
        name = data.get('name')
        email = data.get('email')
        subject = data.get('subject')
        message = data.get('message')
        
        # Validate required fields
        if not all([name, email, subject, message]):
            return jsonify({
                'success': False,
                'error': 'All fields are required'
            }), 400
        
        # Create a new message
        new_message = Message(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        
        # Save to database
        db.session.add(new_message)
        db.session.commit()
        
        # Return success response
        return jsonify({
            'success': True,
            'message': 'Message sent successfully',
            'message_id': new_message.id
        }), 201
        
    except Exception as e:
        app.logger.error(f"Contact message error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

# Add new pet booking API endpoint
@app.route('/api/pet_booking', methods=['POST'])
def api_book_pet():
    """API endpoint for pet booking"""
    try:
        # Get data from request
        data = request.get_json()
        
        # Extract booking details
        pet_name = data.get('pet_name')
        email = data.get('email')
        pet_type = data.get('pet_type')
        breed = data.get('breed')
        address = data.get('address')
        payment_method = data.get('payment_method')
        user_id = data.get('user_id')
        
        # Validate required fields
        if not all([pet_name, email, pet_type, breed, address, payment_method]):
            return jsonify({
                'success': False,
                'error': 'All fields are required'
            }), 400
        
        # Create new pet booking
        new_booking = PetBooking(
            pet_name=pet_name,
            email=email,
            pet_type=pet_type,
            breed=breed,
            address=address,
            payment_method=payment_method,
            user_id=user_id if user_id else 1  # Default to user ID 1 if not provided
        )
        
        # Save to database
        db.session.add(new_booking)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Pet booking successful',
            'booking_id': new_booking.id,
            'expected_delivery': (datetime.utcnow() + timedelta(days=5)).strftime('%Y-%m-%d')
        }), 201
        
    except Exception as e:
        app.logger.error(f"Pet booking error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

# Add API endpoint to retrieve pet bookings for a user
@app.route('/api/pet_bookings/<email>', methods=['GET'])
def api_get_pet_bookings(email):
    """API endpoint to get all pet bookings for a user email"""
    try:
        # Get bookings for this email
        bookings = PetBooking.query.filter_by(email=email).order_by(PetBooking.created_at.desc()).all()
        
        if not bookings:
            return jsonify({
                'success': True,
                'bookings': []
            })
        
        # Format bookings for response
        bookings_list = []
        for booking in bookings:
            bookings_list.append({
                'id': booking.id,
                'pet_name': booking.pet_name,
                'email': booking.email,
                'pet_type': booking.pet_type,
                'breed': booking.breed,
                'address': booking.address,
                'payment_method': booking.payment_method,
                'booking_date': booking.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'expected_delivery': (booking.created_at + timedelta(days=5)).strftime('%Y-%m-%d')
            })
        
        return jsonify({
            'success': True,
            'bookings': bookings_list
        })
        
    except Exception as e:
        app.logger.error(f"Error retrieving pet bookings: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

# Add API endpoint to update a pet booking
@app.route('/api/pet_booking/<int:booking_id>', methods=['PUT'])
def api_update_pet_booking(booking_id):
    """API endpoint to update an existing pet booking"""
    try:
        # Get the booking from the database
        booking = PetBooking.query.get(booking_id)
        
        if not booking:
            return jsonify({
                'success': False,
                'error': 'Booking not found'
            }), 404
            
        # Get the data from the request
        data = request.get_json()
        
        # Extract booking details from request
        pet_name = data.get('pet_name')
        email = data.get('email')
        pet_type = data.get('pet_type')
        breed = data.get('breed')
        address = data.get('address')
        payment_method = data.get('payment_method')
        
        # Validate required fields
        if not all([pet_name, email, pet_type, breed, address, payment_method]):
            return jsonify({
                'success': False,
                'error': 'All fields are required'
            }), 400
            
        # Update the booking
        booking.pet_name = pet_name
        booking.email = email
        booking.pet_type = pet_type
        booking.breed = breed
        booking.address = address
        booking.payment_method = payment_method
        
        # Save to database
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Pet booking updated successfully',
            'booking_id': booking.id,
            'expected_delivery': (booking.created_at + timedelta(days=5)).strftime('%Y-%m-%d')
        })
            
    except Exception as e:
        app.logger.error(f"Pet booking update error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

# Create Order model
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    address = db.Column(db.Text, nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    total_price = db.Column(db.Float, nullable=False)
    paid = db.Column(db.Boolean, default=False)
    payment_method = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default="pending")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
# Create OrderItem model
class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, nullable=False)

# Add API endpoint for creating orders
@app.route('/api/orders', methods=['POST'])
def api_create_order():
    """API endpoint for creating orders"""
    try:
        # Get data from request and log it for debugging
        raw_data = request.get_data(as_text=True)
        app.logger.info(f"Received raw data: {raw_data}")
        
        # Try to parse the JSON data
        try:
            data = request.get_json(force=True)
            app.logger.info(f"Parsed JSON data: {data}")
        except Exception as json_error:
            app.logger.error(f"Error parsing JSON: {str(json_error)}")
            return jsonify({
                'success': False,
                'error': f'Invalid JSON format: {str(json_error)}'
            }), 400
            
        # Extract order details with more error handling
        try:
            first_name = str(data.get('first_name', ''))
            last_name = str(data.get('last_name', ''))
            email = str(data.get('email', ''))
            address = str(data.get('address', ''))
            postal_code = str(data.get('postal_code', ''))
            city = str(data.get('city', ''))
            
            # Handle potential type issues with numeric fields
            try:
                total_price = float(data.get('total_price', 0))
            except (TypeError, ValueError):
                total_price = 0
                
            payment_method = str(data.get('payment_method', 'Cash on Delivery'))
            items = data.get('items', [])
            
            try:
                user_id = int(data.get('user_id')) if data.get('user_id') else None
            except (TypeError, ValueError):
                user_id = None
        except Exception as e:
            app.logger.error(f"Error extracting order data: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Error processing order data: {str(e)}'
            }), 400
        
        # Validate required fields
        if not all([first_name, last_name, email, address, postal_code, city]):
            missing_fields = []
            if not first_name: missing_fields.append('first_name')
            if not last_name: missing_fields.append('last_name')
            if not email: missing_fields.append('email')
            if not address: missing_fields.append('address')
            if not postal_code: missing_fields.append('postal_code')
            if not city: missing_fields.append('city')
            
            app.logger.error(f"Missing required fields: {missing_fields}")
            return jsonify({
                'success': False,
                'error': f'Required fields missing: {", ".join(missing_fields)}'
            }), 400
            
        if not items:
            app.logger.error("No items in order")
            return jsonify({
                'success': False,
                'error': 'Order must contain at least one item'
            }), 400
            
        # Log items data for debugging
        app.logger.info(f"Order items: {items}")
            
        # Create new order
        new_order = Order(
            first_name=first_name,
            last_name=last_name,
            email=email,
            address=address,
            postal_code=postal_code,
            city=city,
            total_price=total_price,
            payment_method=payment_method,
            user_id=user_id
        )
        
        # Save to database
        db.session.add(new_order)
        db.session.flush()  # This assigns an ID to new_order without committing
        
        # Create order items with better error handling
        for item in items:
            try:
                product_name = str(item.get('product_name', 'Unknown Product'))
                
                try:
                    price = float(item.get('price', 0))
                except (TypeError, ValueError):
                    price = 0
                    
                try:
                    quantity = int(item.get('quantity', 1))
                except (TypeError, ValueError):
                    quantity = 1
                    
                total = price * quantity
                
                order_item = OrderItem(
                    order_id=new_order.id,
                    product_name=product_name,
                    price=price,
                    quantity=quantity,
                    total=total
                )
                db.session.add(order_item)
                
            except Exception as item_error:
                app.logger.error(f"Error processing order item: {str(item_error)}")
                # Continue with other items even if one fails
                continue
            
        # Commit all changes
        db.session.commit()
        
        app.logger.info(f"Order created successfully with ID: {new_order.id}")
        return jsonify({
            'success': True,
            'message': 'Order created successfully',
            'order_id': new_order.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Order creation error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

# Add debug endpoint to log incoming requests
@app.route('/api/debug', methods=['POST'])
def api_debug():
    """Debug endpoint to log incoming requests"""
    try:
        # Get data from request
        data = request.get_json()
        
        # Log the data
        app.logger.info(f"Debug endpoint received data: {data}")
        
        # Return the data as is
        return jsonify({
            'success': True,
            'message': 'Debug request received',
            'data': data
        })
        
    except Exception as e:
        app.logger.error(f"Debug endpoint error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Error in debug endpoint: {str(e)}'
        }), 500

@app.route('/api/debug/admin', methods=['GET'])
def api_debug_admin():
    """Debug endpoint to check admin credentials"""
    try:
        admins = Admin.query.all()
        admin_list = []
        for admin in admins:
            admin_list.append({
                'id': admin.id,
                'username': admin.username,
                'has_password_hash': bool(admin.password_hash)
            })
        
        return jsonify({
            'success': True,
            'admin_count': len(admin_list),
            'admins': admin_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/status', methods=['GET'])
def api_status():
    """Simple endpoint to check if the Flask server is up and running"""
    return jsonify({
        'status': 'online',
        'message': 'Flask API server is running',
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'api_version': '1.0'
    }), 200

@app.route('/api/appointment/availability', methods=['GET'])
def api_appointment_availability():
    """API endpoint to check if appointment booking is available"""
    try:
        # Return available dates (excluding weekends and fully booked days)
        # For simplicity, we'll just provide availability for the next 7 days
        available_dates = []
        today = datetime.today().date()
        
        for i in range(1, 15):  # Check next 14 days
            check_date = today + timedelta(days=i)
            # Skip weekends (5=Saturday, 6=Sunday)
            if check_date.weekday() < 5:  
                # In a real app, we'd check the database for available slots
                available_dates.append({
                    'date': check_date.strftime('%Y-%m-%d'),
                    'available': True,
                    'available_slots': ['09:00', '10:00', '11:00', '14:00', '15:00', '16:00']
                })
        
        return jsonify({
            'success': True,
            'available_dates': available_dates,
            'booking_enabled': True
        })
        
    except Exception as e:
        app.logger.error(f"Error checking appointment availability: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.route('/api/appointment/time-slots', methods=['GET'])
def api_appointment_time_slots():
    """API endpoint to get available time slots for a specific date"""
    try:
        date_str = request.args.get('date')
        if not date_str:
            return jsonify({
                'success': False,
                'error': 'Date parameter is required'
            }), 400
            
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }), 400
            
        # Logic to find time slots that are already booked
        booked_slots = []
        appointments = Appointment.query.filter_by(date=selected_date).all()
        for appointment in appointments:
            booked_slots.append(appointment.time.strftime('%H:%M'))
            
        # All possible time slots (9am to 5pm, hourly)
        all_slots = ['09:00', '10:00', '11:00', '12:00', '14:00', '15:00', '16:00', '17:00']
        
        # Available slots are those not in booked_slots
        available_slots = [slot for slot in all_slots if slot not in booked_slots]
        
        return jsonify({
            'success': True,
            'date': date_str,
            'available_slots': available_slots,
            'booked_slots': booked_slots
        })
        
    except Exception as e:
        app.logger.error(f"Error getting time slots: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

# Add API endpoint for cancelling orders
@app.route('/api/orders/<int:order_id>/cancel', methods=['POST'])
def api_cancel_order(order_id):
    """API endpoint for cancelling orders"""
    try:
        # Find the order by ID
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({
                'success': False,
                'error': f'Order {order_id} not found'
            }), 404
            
        # Check if the order is already cancelled
        if order.status == 'cancelled':
            return jsonify({
                'success': False,
                'error': 'Order is already cancelled'
            }), 400
            
        # Check if the order is already delivered
        if order.status == 'delivered':
            return jsonify({
                'success': False,
                'error': 'Cannot cancel an order that has already been delivered'
            }), 400
            
        # Update the order status
        order.status = 'cancelled'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Order {order_id} has been cancelled successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error cancelling order {order_id}: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.route('/checkout-helper')
def checkout_helper():
    """Serve the order helper page"""
    return render_template('order_helper.html')

if __name__ == '__main__':
    with app.app_context():
        # Make sure to create all tables before running the app
        db.create_all()
        app.logger.info("Database tables created successfully")
        # Ensure admin exists
        if Admin.query.count() == 0:
            admin = Admin(username='Bandar', email='admin@example.com')
            admin.set_password('Kaju')
            db.session.add(admin)
            db.session.commit()
            print("Created admin user: Bandar/Kaju")
        else:
            # Check if admin exists but might have password issues
            admin = Admin.query.filter_by(username='Bandar').first()
            if admin:
                # Reset the password to ensure it's correct
                admin.set_password('Kaju')
                db.session.commit()
                print("Reset admin user password")
    app.run(debug=True, port=5000)
