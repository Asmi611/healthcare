## Goal
Starter project for the Healthcare MVP: appointment → prescription → pharmacy pipeline.
# HealthConnect(Healthcare Appointment & Prescription MVP)
A streamlined healthcare workflow platform where **patients book appointments**, **doctors approve & prescribe**, and **pharmacies fulfill prescriptions**.  
Built as a fast MVP for showcasing full-stack development skills across Flask, MySQL, HTML/CSS/JS.
## Features
### Doctor Portal
- View pending & approved appointments  
- Approve / reject patient appointments  
- Create digital prescriptions  
- Generate prescription PDFs (ReportLab)

### Patient Portal
- Book appointments with available doctors  
- Receive notifications  
- View prescriptions & download PDFs  
- Track prescription status

### Pharmacy Portal
- View all prescriptions  
- Mark prescriptions as Ready or Delivered  
- Notify patients automatically

### Authentication
- Secure login/signup for doctor, patient, pharmacy  
- Password hashing  
- Session-based access control  
- Role-based dashboards
## Tech Stack
### Backend
- **Python Flask**
- **MySQL** (local or cloud)
- ReportLab (PDF generation)

### Frontend
- HTML5, CSS3, JS  
- Responsive Dashboard UI  

### Architecture
- MVC-inspired Flask structure  
- Clean modular routes  
- SQL schema + initialization scripts  
- Notifications system
## Folder Structure
healthcare/
│── app/
│ ├── init.py
│ ├── routes.py
│ ├── db.py
│ ├── static/
│ │ ├── css/
│ │ ├── js/
│ │ └── images/
│ └── templates/
│ ├── auth/
│ ├── doctor/
│ ├── patient/
│ ├── pharmacy/
│ └── base.html
│── docs/
│ ├── init_db.sql
│ └── schema.sql
│── run.py
│── requirements.txt
│── .gitignore
│── README.md
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
