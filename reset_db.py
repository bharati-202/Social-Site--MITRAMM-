import os
import sys
import subprocess

def run_command(command):
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"Error: {result.stderr}")
    return result.returncode

def main():
    # Delete the database file
    db_file = "db.sqlite3"
    if os.path.exists(db_file):
        print(f"Deleting database file: {db_file}")
        os.remove(db_file)
    
    # Run migrations in the correct order
    commands = [
        "python manage.py makemigrations accounts",
        "python manage.py makemigrations posts",
        "python manage.py makemigrations friends",
        "python manage.py migrate auth",
        "python manage.py migrate accounts",
        "python manage.py migrate contenttypes",
        "python manage.py migrate admin",
        "python manage.py migrate sessions",
        "python manage.py migrate account",
        "python manage.py migrate socialaccount",
        "python manage.py migrate posts",
        "python manage.py migrate friends",
    ]
    
    for command in commands:
        if run_command(command) != 0:
            print(f"Error running command: {command}")
            sys.exit(1)
    
    print("Database reset and migrations applied successfully!")

if __name__ == "__main__":
    main() 