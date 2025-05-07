🐾 CUDDLE BUDDY – Pet Service Management System
CUDDLE BUDDY is a comprehensive full-stack web application developed to streamline the management of pet appointments, service bookings, and order processing. Designed with pet service businesses in mind, it leverages the power of Flask 🐍 for backend development and Django 🎯 for frontend administration, creating a seamless and scalable solution for both users and administrators.

✨ Key Features
🔐 User Registration & Login with Role Management
Supports secure user authentication with two distinct roles:

Admin 👩‍💼 / 👨‍💼: Full access to all system data and administrative controls

Regular User 🧑‍🤝‍🧑: Can book appointments, services, and manage orders

📅 Book & Manage Appointments
Users can conveniently schedule appointments for their pets, while admins can view, update, and manage these appointments in real time.

🛁 Pet Service Bookings
Provides an interface to browse and book various pet-related services such as grooming, training, or vet consultations.

📦 Order Management System
Users can place, view, and cancel product or service orders. Admins oversee and manage the fulfillment and status of all orders.

📊 Admin Dashboard
A powerful Django-based dashboard offering visibility and control over all key components, including users, services, appointments, and transactions.

🔗 RESTful API Endpoints
Clean, modular API endpoints built with Flask to ensure seamless integration and efficient data communication between frontend and backend.

🔐 Secure Authentication & Session Management
Incorporates Flask-Login for session control and Werkzeug for password hashing, ensuring data privacy and user security.

🌐 CORS Protection
Configured to enable secure communication across origins, safeguarding the platform during cross-domain interactions.

🧰 Technology Stack
🧠 Backend:

Flask (API development)

SQLAlchemy (ORM)

SQLite (Lightweight database)

🎨 Frontend & Admin Panel:

Django (Frontend templating and admin interface)

HTML, CSS, JavaScript

Bootstrap (Responsive UI design)

🔐 Authentication & Security:

Flask-Login

Werkzeug (Password encryption)

🛠️ Additional Tools:

Jinja2 (Flask templating)

CORS Middleware

🐶 Why Choose CUDDLE BUDDY?
Whether you're a pet clinic, grooming salon, or a multi-service pet care business, CUDDLE BUDDY offers a user-friendly and professional-grade solution to manage daily operations, improve customer service, and ensure pets get the care they deserve—all through one intuitive platform.



STEPS FOR RUNNING THIS::
To get started with the CUDDLE BUDDY – Pet Service Management System, first ensure that you have the necessary prerequisites installed: Git, Python 3.7 or higher, pip (Python package manager), and optionally SQLite3 (if not already bundled with your Python installation). It's also recommended to use a virtual environment such as venv for dependency management.

Begin by cloning the project repository using the command:
git clone https://github.com/your-username/cuddle-buddy.git, and navigate into the project directory with cd cuddle-buddy. If you're working on a system with virtual environments, set one up using python -m venv venv, then activate it with source venv/bin/activate on macOS/Linux or venv\Scripts\activate on Windows.

Next, install the required dependencies using pip install -r requirements.txt. If the project maintains separate requirements for backend and frontend, you may need to run pip install -r backend/requirements.txt and pip install -r frontend/requirements.txt individually. Once the environment is ready, initialize the SQLite database by navigating to the backend directory and running a setup script like python setup_db.py, or manually creating the necessary tables.

Switching to the frontend directory, run python manage.py migrate to set up Django's database schema. To access the Django admin dashboard, create a superuser with python manage.py createsuperuser and follow the prompts to enter a username, email, and password.

To run the application locally, first start the Flask API by running flask run inside the backend directory. This will launch the backend at http://127.0.0.1:5000/. Then, in the frontend directory, start the Django development server using python manage.py runserver, which will host the frontend and admin dashboard at http://127.0.0.1:8000/.

At this point, you can access the full application: users can interact with pet services and appointments via the frontend, while administrators can manage the system through the Django admin interface. The Flask backend provides RESTful APIs to handle all core functionalities, and the system is now ready for testing, development, or deployment..

