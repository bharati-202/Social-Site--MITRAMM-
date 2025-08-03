# How to Fix the Migration Error

The error you're seeing is due to an inconsistent migration history. The `account.0001_initial` migration (from django-allauth) is applied before its dependency `accounts.0001_initial` (your custom user model).

## Solution

Follow these steps to fix the issue:

1. **Delete the database file**:
   ```
   # On Windows
   del db.sqlite3
   
   # On macOS/Linux
   rm db.sqlite3
   ```

2. **Run migrations in the correct order**:
   ```
   python manage.py migrate auth
   python manage.py migrate accounts
   python manage.py migrate contenttypes
   python manage.py migrate admin
   python manage.py migrate sessions
   python manage.py migrate account
   python manage.py migrate socialaccount
   python manage.py migrate posts
   python manage.py migrate friends
   ```

3. **Create a superuser** (optional):
   ```
   python manage.py createsuperuser
   ```

4. **Start the development server**:
   ```
   python manage.py runserver
   ```

## Why This Happens

This issue occurs because django-allauth's migrations depend on your custom user model, but they were applied before your custom user model's migrations. By deleting the database and applying migrations in the correct order, we ensure that dependencies are satisfied.

## Alternative Solution

If you want to keep your existing data, you can try:

1. **Fake the accounts migration**:
   ```
   python manage.py migrate accounts 0001_initial --fake
   ```

2. **Then run all migrations**:
   ```
   python manage.py migrate
   ```

However, this approach might lead to other issues, so the clean approach (deleting the database) is recommended for development environments. 