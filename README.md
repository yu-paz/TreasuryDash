# TreasuryDash
A full-stack web application for managing chapter finances, built with Python and Flask.

**Live demo:** 
https://treasurydash.onrender.com

## Features

- **Transaction tracking** — add, edit, and delete income and expense records
- **Budget categories** — set spending limits per category with live progress tracking
- **Dashboard** — real-time balance, income vs expense charts, and spending breakdown
- **User authentication** — secure login with hashed passwords
- **Invite-only registration** — officers must enter an invite code to create an account

## Tech Stack

- **Backend** — Python, Flask, SQLAlchemy
- **Database** — SQLite
- **Frontend** — Jinja2 templates, Bootstrap 5, Chart.js
- **Auth** — Flask-Login, Flask-Bcrypt

## Environment Variables

For production, set these as environment variables:

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Flask session secret key |
| `INVITE_CODE` | Code required to register a new account |

## Project Structure

├── app.py              # Flask routes and database models
├── requirements.txt    # Python dependencies
├── render.yaml         # Render deployment configuration
└── templates/
    ├── base.html       # Shared layout and navigation
    ├── index.html      # Dashboard
    ├── categories.html # Budget categories
    ├── edit.html       # Edit transaction
    ├── login.html      # Login page
    └── register.html   # Registration page
