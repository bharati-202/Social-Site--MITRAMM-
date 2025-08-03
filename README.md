# Social Networking Site

A modern social networking platform built with Django.

## Features

- User authentication and profiles
- Post creation and sharing
- Friend connections
- News feed
- Like and comment system
- User search functionality

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows:
```bash
venv\Scripts\activate
```
- Unix/MacOS:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

7. Visit http://127.0.0.1:8000/ in your browser

## Project Structure

- `social_network/` - Main project directory
- `accounts/` - User authentication and profiles
- `posts/` - Post creation and management
- `friends/` - Friend connections and requests
- `templates/` - HTML templates
- `static/` - CSS, JavaScript, and images 