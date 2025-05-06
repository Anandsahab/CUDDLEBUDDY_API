from app import app, db, User

with app.app_context():
    # Check if the user already exists
    existing_user = User.query.filter_by(username='sar').first()
    if existing_user:
        print(f"User 'sar' already exists, updating password")
        existing_user.set_password('password123')
    else:
        # Create a new user
        new_user = User(username='sar', email='sar@example.com')
        new_user.set_password('password123')
        db.session.add(new_user)
    
    # Commit the changes
    db.session.commit()
    print("User 'sar' with password 'password123' is ready to use") 