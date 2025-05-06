import os
import django

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Annaproject.settings')
django.setup()

# Now import Django models
from django.contrib.auth.models import User

# Check if admin exists
admin_username = 'Bandar'
admin_email = 'admin@example.com'
admin_password = 'Kaju'

try:
    # Try to get the admin user
    admin = User.objects.filter(username=admin_username).first()
    
    if admin:
        print(f"Admin user '{admin_username}' exists")
        # Reset password for existing admin
        admin.set_password(admin_password)
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()
        print(f"Password reset to '{admin_password}' and admin privileges granted")
    else:
        # Create a new admin user
        User.objects.create_superuser(
            username=admin_username,
            email=admin_email,
            password=admin_password
        )
        print(f"Created admin user '{admin_username}' with password '{admin_password}'")
    
    print("Admin user setup complete. Please try to log in now.")
    
except Exception as e:
    print(f"Error: {e}")
    print("Please run this script from the Django project directory") 