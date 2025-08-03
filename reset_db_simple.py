import os
import subprocess

# Delete the database file
db_file = "db.sqlite3"
if os.path.exists(db_file):
    print(f"Deleting database file: {db_file}")
    os.remove(db_file)

# Run migrations
print("Running migrations...")
subprocess.run("python manage.py migrate", shell=True) 