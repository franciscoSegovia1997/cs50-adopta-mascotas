# Adopta Mascotas

A **learning project developed as my final project for the CS50 course**. Adopta Mascotas is a Flask web application for managing a pet adoption catalog.

The application supports account registration and sign-in, pet and pet-type records, adoption registration, and an adoption list. Its interface is in Spanish.

## Features

- Register and sign in to an account.
- Browse pets and filter them by type.
- Add pet types and register pets with a name, age, description, and photo.
- Record an adoption and view its associated adopter details.
- Review the adoption list.

## Technology

- Python and Flask
- SQLite, accessed through the `cs50` SQL library
- Flask-Session and Flask-WTF
- Jinja templates
- Bootstrap 5 and Font Awesome

## Run locally

### Requirements

- Python 3
- `pip`

### Setup

From the project directory, create and activate a virtual environment.

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Set a local session secret. For example:

**macOS / Linux**

```bash
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
```

**Windows PowerShell**

```powershell
$env:SECRET_KEY = python -c "import secrets; print(secrets.token_hex(32))"
```

Initialize the local database and demo account:

```bash
python seed.py
```

The seed script creates the database from `schema.sql` if it does not exist, adds the `Perro` and `Gato` types, and creates this local demo account:

- **Username:** `admin`
- **Password:** `admin123`

Start the application:

```bash
python app.py
```

Then open <http://127.0.0.1:5000>. You can also register a new account. After signing in, add a pet and upload a photo to try the adoption flow.

## Project structure

```text
.
├── app.py                 # Flask routes and application setup
├── forms.py               # Flask-WTF form definitions
├── helpers.py             # Login and error-page helpers
├── schema.sql             # SQLite schema
├── seed.py                # Local demo data setup
├── requirements.txt       # Python dependencies
├── static/
│   ├── styles.css
│   └── uploads/           # User-uploaded pet photos (local runtime data)
└── templates/             # Jinja HTML templates
```

## Data and security notes

This is a **local learning project**, not a production deployment. The database, uploaded photos, and filesystem session data are local runtime files and are excluded from Git. The application creates the database and upload directory when needed; run `python seed.py` to create the demo account and pet types.

The sample records in the existing local database are fictional. A fresh clone creates its own database through the setup steps above.

