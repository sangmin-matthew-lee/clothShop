# Cloth Shop (Django)

A simple e-commerce demo built with Django 4.2, featuring product browsing, search, checkout/tracking, and a lightweight seasonal recommendation chatbot.

## Features
- Product browse/search, detail pages, and featured items on the homepage.
- Checkout flow storing orders plus status updates (tracks, cancel, return).
- Contact form submission storage.
- Simple heuristic chatbot that suggests products by user intent/season.
- Admin site for managing catalog and orders.

## Prerequisites
- Python 3.9+
- pipenv (or use `pip install django==4.2.9` in a virtualenv)

## Setup
1) Clone and enter the project:
```bash
git clone https://github.com/sangmin-matthew-lee/clothShop.git
cd clothShop/ecomm
```
2) Install dependencies and activate the environment:
```bash
pipenv install
pipenv shell
# or: python3 -m venv venv && source venv/bin/activate && pip install django==4.2.9
```
3) Apply migrations and create an admin user:
```bash
python manage.py migrate
python manage.py createsuperuser
```
4) Run the dev server:
```bash
python manage.py runserver
```
Visit http://127.0.0.1:8000/ for the shop and http://127.0.0.1:8000/admin/ for admin.

## Project layout
- `ecomm_app/` – project settings/urls.
- `shopping/` – shop app (models, views, templates, chatbot).
- `accounts/` – auth-related code if extended.
- `media/` – uploaded product images (ignored by git).
- `mydatabase/` – SQLite database file (ignored by git).

## Notes
- Default database uses SQLite (`NAME = "mydatabase"`). You can point to another path or engine in `ecomm_app/settings.py`.
- SECRET_KEY/DEBUG are hard-coded for development; move to environment variables before any production use.
- Static/media directories are ignored by git; ensure the `media/` folder exists when uploading images.
