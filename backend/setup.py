#!/usr/bin/env python
"""
PesaPlan Setup Script
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pesaplan.settings.development')
    django.setup()

def run_migrations():
    """Run database migrations"""
    print("Running database migrations...")
    execute_from_command_line(['manage.py', 'migrate'])

def create_superuser():
    """Create superuser"""
    print("Creating superuser...")
    execute_from_command_line(['manage.py', 'create_superuser'])

def collect_static():
    """Collect static files"""
    print("Collecting static files...")
    execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])

def main():
    """Main setup function"""
    print("Setting up PesaPlan...")
    
    try:
        setup_django()
        run_migrations()
        collect_static()
        
        print("\n" + "="*50)
        print("PesaPlan setup completed successfully!")
        print("="*50)
        print("\nNext steps:")
        print("1. Create a superuser: python manage.py create_superuser")
        print("2. Start the development server: python manage.py runserver")
        print("3. Access the admin panel at: http://localhost:8000/admin/")
        print("4. API documentation at: http://localhost:8000/api/v1/")
        print("\nFor production deployment:")
        print("1. Copy env.example to .env and configure your settings")
        print("2. Run: docker-compose up -d")
        
    except Exception as e:
        print(f"Setup failed: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
