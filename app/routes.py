
# app/routes.py
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash,
    current_app, g, session, jsonify
)
from .db import get_db_connection
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask import send_file
from io import BytesIO
from datetime import datetime
from flask import send_file
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

bp = Blueprint('main', __name__)


# ---------------- LOGIN REQUIRED DECORATOR ----------------
def login_required(view_func):
    """Simple session-based login checker (fallback)."""
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapped_view
# ----------------------------------------------------------


# Home
@bp.route('/')
def home():
    return render_template('home.html')


# --- AUTH ROUTES ---
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, email, password_hash, role FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()
        if user and user.get('password_hash') and check_password_hash(user['password_hash'], password):
            session.clear()
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_role'] = user['role']
            flash('Logged in successfully.', 'success')
            if user['role'] == 'doctor':
                return redirect(url_for('main.doctor_dashboard'))
            elif user['role'] == 'pharmacy':
                return redirect(url_for('main.pharmacy_dashboard'))
            else:
                return redirect(url_for('main.patient_dashboard'))
        else:
            flash('Invalid credentials.', 'danger')
    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'info')
    return redirect(url_for('main.home'))


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        role = request.form.get('role') or 'patient'

        password_hash = generate_password_hash(password)
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO users (name, role, email, password_hash, phone)
                   VALUES (%s, %s, %s, %s, %s)""",
                (full_name, role, email, password_hash, phone)
            )
            conn.commit()
            flash('Account created successfully. You can now login.', 'success')
            return redirect(url_for('main.login'))
        except mysql.connector.Error as e:
            current_app.logger.error('DB error on signup: %s', e)
            flash('An error occurred while creating account (maybe email exists).', 'danger')
        finally:
            cursor.close()

    return render_template('auth/signup.html')


# --- PATIENT ---
@bp.route('/patient/dashboard')
@login_required
def patient_dashboard():
    user_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""SELECT a.id, a.date, a.time, a.status, d.name as doctor_name
                      FROM appointments a
                      LEFT JOIN users d ON d.id = a.doctor_id
                      WHERE a.patient_id = %s""", (user_id,))
    appointments = cursor.fetchall()
    cursor.close()
    return render_template('patient/dashboard.html', appointments=appointments)


@bp.route('/appointments/book', methods=['GET', 'POST'])
@login_required
def book_appointment():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, email FROM users WHERE role='doctor' LIMIT 50")
    doctors = cursor.fetchall()
    cursor.close()

    if request.method == 'POST':
        patient_id = session.get('user_id')
        doctor_id = request.form.get('doctor_id')
        date = request.form.get('date')
        time = request.form.get('time')
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO appointments (patient_id, doctor_id, date, time, status) VALUES (%s,%s,%s,%s,%s)",
                           (patient_id, doctor_id, date, time, 'pending'))
            conn.commit()
            flash('Appointment booked successfully.', 'success')
            return redirect(url_for('main.patient_dashboard'))
        except mysql.connector.Error as e:
            current_app.logger.error('DB error booking appointment: %s', e)
            flash('Error booking appointment.', 'danger')
        finally:
            cursor.close()

    return render_template('patient/book_appointment.html', doctors=doctors)


# --- DOCTOR ---
@bp.route('/doctor/dashboard')
@login_required
def doctor_dashboard():
    # Only allow doctors
    if session.get('user_role') != 'doctor':
        flash('Access denied: doctor only area.', 'danger')
        return redirect(url_for('main.home'))

    # DEBUG: print session info to console
    current_app.logger.debug("DEBUG: session user_id = %s user_name = %s user_role = %s",
                             session.get('user_id'), session.get('user_name'), session.get('user_role'))

    conn = get_db_connection()
    pending = []
    approved = []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT a.id, a.date, a.time, a.status, p.name as patient_name, p.email as patient_email
               FROM appointments a
               LEFT JOIN users p ON p.id = a.patient_id
               WHERE a.doctor_id = %s AND a.status IN ('pending')""",
            (session.get('user_id'),)
        )
        pending = cursor.fetchall()

        cursor.execute(
            """SELECT a.id, a.date, a.time, a.status, p.name as patient_name, p.email as patient_email
               FROM appointments a
               LEFT JOIN users p ON p.id = a.patient_id
               WHERE a.doctor_id = %s AND a.status IN ('approved')""",
            (session.get('user_id'),)
        )
        approved = cursor.fetchall()
    except Exception as e:
        current_app.logger.error("Error fetching appointments for doctor_dashboard: %s", e)
        flash("Could not load appointments right now.", "danger")
    finally:
        try: cursor.close()
        except: pass
        try: conn.close()
        except: pass

    return render_template('doctor/dashboard.html', pending=pending, approved=approved)


@bp.route('/appointments/<int:appointment_id>/approve', methods=['POST'])
@login_required
def approve_appointment(appointment_id):
    if session.get('user_role') != 'doctor':
        flash('Access denied: doctor only area.', 'danger')
        return redirect(url_for('main.home'))

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE appointments SET status=%s WHERE id=%s AND doctor_id=%s", ('approved', appointment_id, session.get('user_id')))
        conn.commit()
        flash('Appointment approved.', 'success')
    except Exception as e:
        current_app.logger.error('Error approving appointment: %s', e)
        flash('Could not approve appointment.', 'danger')
    finally:
        try: cur.close()
        except: pass
        try: conn.close()
        except: pass

    return redirect(url_for('main.doctor_dashboard'))


@bp.route('/appointments/<int:appointment_id>/reject', methods=['POST'])
@login_required
def reject_appointment(appointment_id):
    if session.get('user_role') != 'doctor':
        flash('Access denied: doctor only area.', 'danger')
        return redirect(url_for('main.home'))

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE appointments SET status=%s WHERE id=%s AND doctor_id=%s", ('rejected', appointment_id, session.get('user_id')))
        conn.commit()
        flash('Appointment rejected.', 'info')
    except Exception as e:
        current_app.logger.error('Error rejecting appointment: %s', e)
        flash('Could not reject appointment.', 'danger')
    finally:
        try: cur.close()
        except: pass
        try: conn.close()
        except: pass

    return redirect(url_for('main.doctor_dashboard'))


@bp.route('/pharmacy/dashboard')
@login_required
def pharmacy_dashboard():
    return render_template('pharmacy/dashboard.html')


@bp.route('/appointments/<int:appointment_id>/prescribe', methods=['GET','POST'])
@login_required
def create_prescription(appointment_id):
    if session.get('user_role') != 'doctor':
        flash('Access denied: doctor only area.', 'danger')
        return redirect(url_for('main.home'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""SELECT a.id, a.date, a.time, a.status, p.id as patient_id, p.name as patient_name, p.email as patient_email
                      FROM appointments a
                      LEFT JOIN users p ON p.id = a.patient_id
                      WHERE a.id = %s AND a.doctor_id = %s""", (appointment_id, session.get('user_id')))
    appt = cursor.fetchone()
    cursor.close()

    if not appt:
        flash('Appointment not found or not assigned to you.', 'danger')
        return redirect(url_for('main.doctor_dashboard'))

    if request.method == 'POST':
        medicines = request.form.get('medicines')
        diagnosis = request.form.get('diagnosis')

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO prescriptions (appointment_id, doctor_id, patient_id, medicines, diagnosis) VALUES (%s,%s,%s,%s,%s)",
                        (appointment_id, session.get('user_id'), appt['patient_id'], medicines, diagnosis))
            cur.execute("UPDATE appointments SET status=%s WHERE id=%s", ('prescribed', appointment_id))
            msg = f'Your prescription for appointment #{appointment_id} is ready.'
            cur.execute("INSERT INTO notifications (user_id, message, is_read, created_at) VALUES (%s,%s,0,NOW())",
                        (appt['patient_id'], msg))
            conn.commit()
            flash('Prescription created and patient notified.', 'success')
        except Exception as e:
            current_app.logger.error('Error creating prescription: %s', e)
            flash('Could not create prescription.', 'danger')
        finally:
            try: cur.close()
            except: pass
            try: conn.close()
            except: pass

        return redirect(url_for('main.doctor_dashboard'))

    return render_template('doctor/prescribe.html', appt=appt)

@bp.route('/appointments/<int:appointment_id>/prescription_pdf', methods=['GET'])
@login_required
def prescription_pdf(appointment_id):
    """
    Generate prescription PDF. Robust to whether prescriptions.created_at exists.
    """
    user_id = session.get('user_id')
    user_role = session.get('user_role')

    current_app.logger.debug("prescription_pdf called: appointment_id=%s user_id=%s role=%s",
                             appointment_id, user_id, user_role)

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        # Check if the prescriptions.created_at column exists in current DB
        cur.execute("""
            SELECT COUNT(*) AS cnt
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'prescriptions'
              AND COLUMN_NAME = 'created_at'
        """)
        row = cur.fetchone()
        has_created_at = bool(row and row.get('cnt', 0) > 0)
        current_app.logger.debug("prescriptions.created_at exists: %s", has_created_at)

        # Build SELECT dynamically depending on presence of created_at
        select_cols = [
            "pr.id AS prescription_id",
            "pr.medicines",
            "pr.diagnosis",
        ]
        if has_created_at:
            select_cols.append("pr.created_at")
        select_cols += [
            "a.id AS appointment_id",
            "a.date AS appt_date",
            "a.time AS appt_time",
            "d.id AS doctor_id",
            "d.name AS doctor_name",
            "d.email AS doctor_email",
            "p.id AS patient_id",
            "p.name AS patient_name",
            "p.email AS patient_email"
        ]
        query = "SELECT " + ", ".join(select_cols) + """
            FROM prescriptions pr
            JOIN appointments a ON a.id = pr.appointment_id
            JOIN users d ON d.id = pr.doctor_id
            JOIN users p ON p.id = pr.patient_id
            WHERE pr.appointment_id = %s
            LIMIT 1
        """
        cur.execute(query, (appointment_id,))
        pr = cur.fetchone()

        current_app.logger.debug("DB prescription fetch result: %s", bool(pr))
        if not pr:
            current_app.logger.warning("No prescription found for appointment %s", appointment_id)
            flash("No prescription found for that appointment.", "warning")
            return redirect(url_for('main.doctor_dashboard') if user_role == 'doctor' else url_for('main.patient_dashboard'))

        # Security: only doctor who created or patient owning it (or pharmacy) may download
        if user_role == 'doctor' and user_id != pr['doctor_id']:
            current_app.logger.warning("Doctor %s tried to access prescription for doctor %s", user_id, pr['doctor_id'])
            flash("Access denied.", "danger")
            return redirect(url_for('main.doctor_dashboard'))

        if user_role == 'patient' and user_id != pr['patient_id']:
            current_app.logger.warning("Patient %s tried to access prescription for patient %s", user_id, pr['patient_id'])
            flash("Access denied.", "danger")
            return redirect(url_for('main.patient_dashboard'))

        if user_role not in ('doctor', 'patient', 'pharmacy'):
            current_app.logger.warning("User role %s not permitted to download prescription", user_role)
            flash("Access denied.", "danger")
            return redirect(url_for('main.home'))

        # Build PDF in-memory
        buffer = BytesIO()
        page_width, page_height = A4
        c = canvas.Canvas(buffer, pagesize=A4)

        # Header
        clinic_name = "MVP Healthcare"
        c.setFont("Helvetica-Bold", 16)
        c.drawString(20*mm, page_height - 20*mm, clinic_name)
        c.setFont("Helvetica", 9)
        c.drawString(20*mm, page_height - 26*mm, "Digital Prescription")
        c.line(20*mm, page_height - 27*mm, page_width - 20*mm, page_height - 27*mm)

        # Metadata
        y = page_height - 36*mm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(20*mm, y, f"Prescription ID: {pr['prescription_id']}")
        c.setFont("Helvetica", 10)

        # created_at fallback: prefer pr['created_at'] if present, else NOW()
        created_at = pr.get('created_at') if 'created_at' in pr else None
        if not created_at:
            created_at = datetime.now()
        created_str = created_at.strftime("%Y-%m-%d %H:%M") if hasattr(created_at, 'strftime') else str(created_at)
        c.drawRightString(page_width - 20*mm, y, "Date: " + created_str)

        y -= 8*mm
        c.setFont("Helvetica-Bold", 11)
        c.drawString(20*mm, y, "Patient:")
        c.setFont("Helvetica", 10)
        c.drawString(40*mm, y, f"{pr['patient_name']}   ({pr['patient_email']})")

        y -= 6*mm
        c.setFont("Helvetica-Bold", 11)
        c.drawString(20*mm, y, "Doctor:")
        c.setFont("Helvetica", 10)
        c.drawString(40*mm, y, f"{pr['doctor_name']}   ({pr['doctor_email']})")

        y -= 8*mm
        c.setFont("Helvetica-Bold", 11)
        c.drawString(20*mm, y, "Appointment:")
        c.setFont("Helvetica", 10)
        appt_dt = ""
        if pr.get('appt_date'):
            appt_dt = str(pr['appt_date'])
        if pr.get('appt_time'):
            appt_dt += " " + str(pr['appt_time'])
        c.drawString(40*mm, y, appt_dt)

        # Medicines (wrap)
        y -= 12*mm
        c.setFont("Helvetica-Bold", 11)
        c.drawString(20*mm, y, "Medicines / Rx:")
        y -= 6*mm
        c.setFont("Helvetica", 10)
        meds_text = (pr.get('medicines') or "No medicines listed.").strip()
        max_chars = 90
        for paragraph in meds_text.split("\n"):
            while len(paragraph) > max_chars:
                split_at = paragraph.rfind(" ", 0, max_chars)
                if split_at <= 0:
                    split_at = max_chars
                c.drawString(22*mm, y, paragraph[:split_at])
                paragraph = paragraph[split_at:].lstrip()
                y -= 6*mm
                if y < 30*mm:
                    c.showPage()
                    y = page_height - 30*mm
                    c.setFont("Helvetica", 10)
            c.drawString(22*mm, y, paragraph)
            y -= 6*mm
            if y < 30*mm:
                c.showPage()
                y = page_height - 30*mm
                c.setFont("Helvetica", 10)

        # Diagnosis / Notes
        y -= 4*mm
        c.setFont("Helvetica-Bold", 11)
        c.drawString(20*mm, y, "Diagnosis / Notes:")
        y -= 6*mm
        c.setFont("Helvetica", 10)
        diag_text = (pr.get('diagnosis') or "No diagnosis provided.").strip()
        paragraph = diag_text
        while paragraph:
            if len(paragraph) <= max_chars:
                c.drawString(22*mm, y, paragraph)
                y -= 6*mm
                break
            split_at = paragraph.rfind(" ", 0, max_chars)
            if split_at <= 0:
                split_at = max_chars
            c.drawString(22*mm, y, paragraph[:split_at])
            paragraph = paragraph[split_at:].lstrip()
            y -= 6*mm
            if y < 30*mm:
                c.showPage()
                y = page_height - 30*mm
                c.setFont("Helvetica", 10)

        # Signature block
        if y < 80*mm:
            c.showPage()
            y = page_height - 30*mm
        y -= 20*mm
        c.setFont("Helvetica", 10)
        c.drawString(20*mm, y, "Doctor signature:")
        c.line(60*mm, y, 120*mm, y)
        y -= 6*mm
        c.setFont("Helvetica-Oblique", 9)
        c.drawString(20*mm, y, "This is a digitally generated prescription.")

        c.showPage()
        c.save()
        buffer.seek(0)

        filename = f"prescription_{pr['prescription_id']}.pdf"
        current_app.logger.info("Returning prescription PDF %s for appointment %s to user %s",
                                filename, appointment_id, user_id)
        return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name=filename)

    except Exception as exc:
        current_app.logger.exception("Error generating prescription PDF for appointment %s: %s", appointment_id, exc)
        flash("Could not generate PDF.", "danger")
        return redirect(url_for('main.doctor_dashboard') if session.get('user_role') == 'doctor' else url_for('main.patient_dashboard'))
    finally:
        try:
            cur.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass


@bp.route('/notifications')
@login_required
def notifications():
    user_id = session.get('user_id')
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, message, is_read, created_at FROM notifications WHERE user_id=%s ORDER BY created_at DESC LIMIT 50", (user_id,))
    notes = cur.fetchall()
    cur.close()
    return jsonify(notes)


@bp.route('/notifications/mark_read', methods=['POST'])
@login_required
def mark_notifications_read():
    user_id = session.get('user_id')
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE notifications SET is_read=1 WHERE user_id=%s", (user_id,))
        conn.commit()
        return jsonify({'ok': True})
    except Exception as e:
        current_app.logger.error('Mark read error: %s', e)
        return jsonify({'ok': False}), 500
    finally:
        try: cur.close()
        except: pass
        try: conn.close()
        except: pass


# Register blueprint with the Flask app
def init_routes(app):
    app.register_blueprint(bp)
