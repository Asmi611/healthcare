# healthcare - MVP Flask Starter (Hackathon-ready)

## Goal
Starter project for the Healthcare MVP: appointment → prescription → pharmacy pipeline.

## Quick start (Windows CMD)
1. Open CMD and `cd` to the folder where you want the project.
2. Create project folder and virtualenv (optional via GUI):
   ```
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   set FLASK_APP=run.py
   set FLASK_ENV=development
   flask run
   ```
3. The app will run on http://127.0.0.1:5000 by default.

## Structure generated
- app/: application package
  - templates/: HTML templates (base, login, signup, dashboards)
  - static/: CSS, JS, images (logo copied if provided)
- run.py: entrypoint
- requirements.txt

Customize DB credentials in `.env` or update config in `app/config.py`.


## Initialize database (MySQL)
1. Start MySQL server and create user if needed.
2. Run SQL script: `mysql -u root -p < docs/init_db.sql`
3. Update `.env` with DB credentials or edit app/db.py defaults.
