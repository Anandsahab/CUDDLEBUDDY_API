from app import app, db, User, Admin
from werkzeug.security import generate_password_hash, check_password_hash

# Function to test a user login
def test_user_login(username, password):
    with app.app_context():
        # Try to find the user
        admin = Admin.query.filter_by(username=username).first()
        if admin:
            print(f"Found admin user: {admin.username}")
            print(f"Password hash: {admin.password_hash}")
            result = admin.check_password(password)
            print(f"Password check result: {result}")
            return result
        
        user = User.query.filter_by(username=username).first()
        if user:
            print(f"Found regular user: {user.username}")
            print(f"Password hash: {user.password_hash}")
            result = user.check_password(password)
            print(f"Password check result: {result}")
            return result
        
        print(f"No user found with username: {username}")
        return False

# Create a test user if needed
def create_test_user():
    with app.app_context():
        if not User.query.filter_by(username="testuser").first():
            user = User(username="testuser", email="test@example.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
            print("Created test user: testuser/password123")

# Create a test admin if needed
def create_test_admin():
    with app.app_context():
        if not Admin.query.filter_by(username="testadmin").first():
            admin = Admin(username="testadmin", email="testadmin@example.com")
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()
            print("Created test admin: testadmin/admin123")

# List all users in the database
def list_all_users():
    with app.app_context():
        print("\nAll Admin users:")
        admins = Admin.query.all()
        for admin in admins:
            print(f"Admin: {admin.username}, Email: {admin.email}")
        
        print("\nAll Regular users:")
        users = User.query.all()
        for user in users:
            print(f"User: {user.username}, Email: {user.email}")

if __name__ == "__main__":
    # Create test users
    create_test_user()
    create_test_admin()
    
    # List all users
    list_all_users()
    
    # Test logins
    print("\nTesting admin login with correct password:")
    test_user_login("testadmin", "admin123")
    
    print("\nTesting admin login with incorrect password:")
    test_user_login("testadmin", "wrongpassword")
    
    print("\nTesting regular user login with correct password:")
    test_user_login("testuser", "password123")
    
    print("\nTesting regular user login with incorrect password:")
    test_user_login("testuser", "wrongpassword")
    
    # Test the default admin
    print("\nTesting default admin (Bandar):")
    test_user_login("Bandar", "Kaju") 