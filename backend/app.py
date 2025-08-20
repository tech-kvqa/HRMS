# app.py
import eventlet
eventlet.monkey_patch()

from flask import Flask, request, jsonify, render_template, send_file, make_response, Response
from flask_cors import CORS
from models import *
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
import os
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image, ImageDraw, ImageFont
import pdfplumber
import re
from io import BytesIO, StringIO
from masking import encrypt_bytes, decrypt_bytes, mask_aadhaar_in_text, mask_pan_in_text, encrypt, mask_email, mask_phone, decrypt
import io
import mimetypes
import base64
import fitz
import cv2
import numpy as np
from PyPDF2 import PdfReader, PdfWriter
import logging
import time
from reportlab.lib.pagesizes import letter, A4, A3, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
import pandas as pd
import csv
from sqlalchemy import func
import matplotlib.pyplot as plt
from weasyprint import HTML
from dotenv import load_dotenv

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

app = Flask(__name__, template_folder='templates')

socketio = SocketIO(app, cors_allowed_origins="*")

CORS(app)

load_dotenv()

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///hrms.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

UPLOAD_FOLDER_Final = "uploads/final_docs"
os.makedirs(UPLOAD_FOLDER_Final, exist_ok=True)

password = os.environ.get('EMAIL_PASS')
username = os.environ.get('EMAIL_USER')

MAIL_CONFIG = {
    'MAIL_SERVER': 'smtp.gmail.com',
    'MAIL_PORT': 587,
    'MAIL_USERNAME': username,
    'MAIL_PASSWORD': password,
    'MAIL_USE_TLS': True
}

# BASE_URL = "http://localhost:5000"
BASE_URL = "https://hrms-ocfa.onrender.com"

logging.basicConfig(level=logging.DEBUG)

# def send_consent_email(recipient_email, consent_url):
#     body = f"Dear Employee,\n\nPlease review and submit your consent using the following secure link:\n{consent_url}\n\nThank you."
#     msg = MIMEText(body)
#     msg['Subject'] = 'Consent Request - HRMS'
#     msg['From'] = MAIL_CONFIG['MAIL_USERNAME']
#     msg['To'] = recipient_email

#     try:
#         with smtplib.SMTP(MAIL_CONFIG['MAIL_SERVER'], MAIL_CONFIG['MAIL_PORT']) as server:
#             if MAIL_CONFIG.get('MAIL_USE_TLS'):
#                 server.starttls()
#             server.login(MAIL_CONFIG['MAIL_USERNAME'], MAIL_CONFIG['MAIL_PASSWORD'])
#             server.send_message(msg)
#     except Exception as e:
#         print(f"Error sending email: {e}")

# # --- API ROUTES ---

# @app.route('/api/employees', methods=['POST'])
# def add_employee():
#     print("🔥 Received POST /api/employees request")
#     try:
#         data = request.json
#         employee = Employee(
#             name=data['name'],
#             email=data['email'],
#             department=data['department'],
#             designation=data.get('designation'),
#             preferred_language=data.get('preferred_language', 'en')
#         )
#         db.session.add(employee)
#         db.session.commit()

#         consent_url = f"{BASE_URL}/consent/{employee.id}"
#         send_consent_email(employee.email, consent_url)

#         return jsonify({"message": "Employee added and consent email sent."}), 201

#     except Exception as e:
#         print(f"Error in /api/employees: {e}")
#         return jsonify({"error": str(e)}), 500


# @app.route('/api/purposes', methods=['POST'])
# def create_purpose():
#     data = request.json
#     purpose = Purpose(
#         name=data['name'],
#         description=data.get('description'),
#         departments=data.get('departments', ''),
#         language=data.get('language', 'en')
#     )
#     db.session.add(purpose)
#     db.session.commit()
#     return jsonify({"message": "Purpose added"}), 201

# @app.route('/api/employees', methods=['GET'])
# def list_employees():
#     employees = Employee.query.all()
#     return jsonify([{
#         "id": e.id,
#         "name": e.name,
#         "email": e.email,
#         "department": e.department,
#         "designation": e.designation,
#         "consent_status": e.consent_status
#     } for e in employees])

# # --- Consent Form ---

# @app.route('/consent/<employee_id>', methods=['GET', 'POST'])
# def serve_consent_form(employee_id):
#     employee = Employee.query.get(employee_id)
#     if not employee:
#         return "Invalid employee link", 404

#     purposes = Purpose.query.filter(Purpose.language == employee.preferred_language).all()

#     if request.method == 'POST':
#         selected_ids = request.form.getlist('purpose_ids')
#         for pid in selected_ids:
#             consent = ConsentRecord(employee_id=employee_id, purpose_id=pid, consent_given=True)
#             db.session.add(consent)

#         employee.consent_status = 'Given'
#         db.session.commit()
#         return "Consent submitted successfully."

#     return render_template('consent_form.html', purposes=purposes, lang=employee.preferred_language)

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)

def insert_dummy_data():
    colleagues_data = [
        {"name": "Alice Johnson", "email": "22dp1000105@ds.study.iitm.ac.in",
            "department": "IT", "designation": "Analyst"},
        {"name": "Anurag Kumar", "email": "akanuragkumar75@gmail.com",
            "department": "Developer", "designation": "Developer"},
        # {"name": "Mail Tester", "email": "test-tx0rvz4ke@srv1.mail-tester.com",
        #     "department": "Developer", "designation": "Developer"},
        {"name": "Sethi", "email": "tech@kvqaindia.com",
            "department": "Developer", "designation": "Developer"},
    ]

    for data in colleagues_data:
        existing_colleague = Colleagues.query.filter_by(
            email=data['email']).first()
        if not existing_colleague:  # Only insert if email doesn't exist
            colleague = Colleagues(
                name=data['name'], email=data['email'], department=data['department'], designation=data['designation'])
            db.session.add(colleague)

    questions_data = [
        {"question_text": "What is phishing?", "options": [
            "A method of fishing",
            "An attempt to obtain sensitive information by pretending to be a trustworthy entity",
            "A type of computer virus",
            "A software update"],
         "answer": "An attempt to obtain sensitive information by pretending to be a trustworthy entity"},

        {"question_text": "Which of the following is a common method used in phishing attacks?", "options": [
            "Phone calls",
            "Text messages (SMS)",
            "Emails",
            "All of the above"],
         "answer": "All of the above"},

        {"question_text": "What is a common sign of a phishing email?", "options": [
            "Professional formatting",
            "Misspellings and grammatical errors",
            "A personal greeting using your name",
            "A recognizable sender email address"],
         "answer": "Misspellings and grammatical errors"},

        {"question_text": "What should you do if you receive an email asking for your personal information?", "options": [
            "Reply with the information requested",
            "Click on any links in the email",
            "Verify the sender’s email address and contact the company directly",
            "Ignore it and delete it"],
         "answer": "Verify the sender’s email address and contact the company directly"},

        {"question_text": "Which of these can be a red flag in a phishing attempt?", "options": [
            "Urgent requests for action",
            "Generic greetings (e.g., 'Dear Customer')",
            "Unexpected attachments",
            "All of the above"],
         "answer": "All of the above"},

        {"question_text": "Which of the following is a safe practice when handling emails?", "options": [
            "Open attachments from unknown senders",
            "Hover over links to check their destination before clicking",
            "Use the same password for all accounts",
            "Share personal information over email if requested"],
         "answer": "Hover over links to check their destination before clicking"},

        {"question_text": "What does a phishing website often look like?", "options": [
            "Identical to a legitimate site but with a slightly different URL",
            "Always has a secure connection (https)",
            "Contains a lot of advertisements",
            "Usually has a recognizable logo"],
         "answer": "Identical to a legitimate site but with a slightly different URL"},

        {"question_text": "Which of these is NOT a typical feature of a phishing email?", "options": [
            "Spelling mistakes",
            "A legitimate sender’s email address",
            "An urgent tone",
            "Unsolicited attachments"],
         "answer": "A legitimate sender’s email address"},

        {"question_text": "What is 'whaling' in the context of phishing?", "options": [
            "Phishing targeting high-profile individuals like executives",
            "A type of fishing gear",
            "A phishing method that uses social engineering",
            "Phishing that targets small businesses"],
         "answer": "Phishing targeting high-profile individuals like executives"},

        {"question_text": "How can you protect yourself from phishing attacks?", "options": [
            "Use strong, unique passwords for each account",
            "Enable two-factor authentication",
            "Regularly update software and antivirus programs",
            "All of the above"],
         "answer": "All of the above"},

        {"question_text": "True or False: Phishing attacks only target large organizations.", "options": [
            "True",
            "False"],
         "answer": "False"},

        {"question_text": "What should you do if you suspect you've been a victim of phishing?", "options": [
            "Ignore it; it's not a big deal",
            "Change your passwords immediately and report the incident",
            "Forward the email to your friends",
            "Contact your ISP to complain"],
         "answer": "Change your passwords immediately and report the incident"},

        {"question_text": "Which of the following are key features of a phishing website?", "options": [
            "A URL with strange characters or an incorrect domain name",
            "A site that asks for sensitive data such as passwords or credit card numbers",
            "Poor design or errors on the website",
            "All of the above"],
         "answer": "All of the above"},

        {"question_text": "What role does social engineering play in phishing?", "options": [
            "It’s a method to catch fish",
            "It exploits human psychology to manipulate individuals",
            "It refers to the technology used in phishing attacks",
            "It’s a way to create secure passwords"],
         "answer": "It exploits human psychology to manipulate individuals"},

        {"question_text": "Why is it important to keep software and systems updated?", "options": [
            "To make them look nice",
            "To protect against known vulnerabilities that phishing attacks can exploit",
            "To ensure compatibility with older systems",
            "It’s not important"],
         "answer": "To protect against known vulnerabilities that phishing attacks can exploit"},

        {"question_text": "What is the best way to verify the legitimacy of an email you receive that looks suspicious?", "options": [
            "Reply to the email with questions about the sender’s request",
            "Call the organization using a number from their official website",
            "Click on any included links to verify the information",
            "Forward the email to your friends for their opinions"],
         "answer": "Call the organization using a number from their official website"},

        {"question_text": "What is the first step you should take if you think you’ve fallen for a phishing scam?", "options": [
            "Change your passwords immediately",
            "Ignore the situation and hope it resolves itself",
            "Report it to the phishing site’s customer service",
            "Continue using your account to monitor for unusual activity"],
         "answer": "Change your passwords immediately"},

        {"question_text": "Why should you avoid using public Wi-Fi for logging into sensitive accounts?", "options": [
            "Public Wi-Fi can expose your information to man-in-the-middle attacks",
            "It makes your accounts more secure",
            "It is less likely to be monitored for phishing attempts",
            "Public Wi-Fi networks are designed to prevent phishing"],
         "answer": "Public Wi-Fi can expose your information to man-in-the-middle attacks"},

        {"question_text": "What is 'vishing'?", "options": [
            "Phishing attacks that use voice calls to trick people into sharing personal information",
            "Phishing attacks that occur through email",
            "Phishing attacks via social media",
            "Phishing attacks that target websites with high traffic"],
         "answer": "Phishing attacks that use voice calls to trick people into sharing personal information"},

        {"question_text": "How can attackers disguise a malicious link in a phishing email?", "options": [
            "By using a URL shortener",
            "By embedding the link in an image or button",
            "By using a legitimate-looking URL with a misspelling",
            "All of the above"],
         "answer": "All of the above"},

        {"question_text": "What does 'smishing' refer to?", "options": [
            "Phishing attempts via email",
            "Phishing attempts via text message",
            "Phishing attempts via social media",
            "Phishing attacks that involve fake invoices"],
         "answer": "Phishing attempts via text message"},

        {"question_text": "True or False: You should report phishing attempts to your InfoSec and IT team.", "options": [
            "True",
            "False"],
         "answer": "True"},

        {"question_text": "Which of the following is a common risk of not keeping your software up to date?", "options": [
            "Increased system performance",
            "Exposure to known security vulnerabilities",
            "Reduced software license costs",
            "Faster application load times"],
         "answer": "Exposure to known security vulnerabilities"},

        {"question_text": "What type of information might a phishing attack seek?", "options": [
            "Your favorite movie",
            "Your phone’s wallpaper",
            "Passwords, credit card numbers, or personal information.",
            "Your preferred vacation destination"],
         "answer": "Passwords, credit card numbers, or personal information."},

        {"question_text": "Which of the following is a common sign that a link may be malicious?", "options": [
            "The URL contains a long string of random numbers and letters",
            "The link takes you to a well-known website",
            "The link begins with “https://”",
            "The link ends in '.com'"],
         "answer": "The URL contains a long string of random numbers and letters"},
    ]

    for data in questions_data:
        existing_question = Questions.query.filter_by(
            question_text=data['question_text']).first()
        if not existing_question:
            question = Questions(question_text=data['question_text'],
                                 options=data['options'], answer=data['answer'])
            db.session.add(question)

    db.session.commit()


def send_welcome_email(recipient_email, upload_url):
    body = f"""
    Dear Employee,

    Welcome to the organization!

    Please upload your required documents using the following secure link:
    {upload_url}

    Thank you.
    """
    msg = MIMEText(body)
    msg['Subject'] = 'Welcome to HRMS - Document Upload'
    msg['From'] = MAIL_CONFIG['MAIL_USERNAME']
    msg['To'] = recipient_email

    try:
        with smtplib.SMTP(MAIL_CONFIG['MAIL_SERVER'], MAIL_CONFIG['MAIL_PORT']) as server:
            if MAIL_CONFIG.get('MAIL_USE_TLS'):
                server.starttls()
            server.login(MAIL_CONFIG['MAIL_USERNAME'], MAIL_CONFIG['MAIL_PASSWORD'])
            server.send_message(msg)
    except Exception as e:
        print(f"Error sending welcome email: {e}")

def send_consent_email(recipient_email, employee_name, consent_url):
    body = f"""
    Dear {employee_name},

    Please review and submit the consent form using the following secure link:
    {consent_url}

    Thank you.
    """
    msg = MIMEText(body)
    msg['Subject'] = 'Consent Form Required'
    msg['From'] = MAIL_CONFIG['MAIL_USERNAME']
    msg['To'] = recipient_email

    try:
        with smtplib.SMTP(MAIL_CONFIG['MAIL_SERVER'], MAIL_CONFIG['MAIL_PORT']) as server:
            if MAIL_CONFIG.get('MAIL_USE_TLS'):
                server.starttls()
            server.login(MAIL_CONFIG['MAIL_USERNAME'], MAIL_CONFIG['MAIL_PASSWORD'])
            server.send_message(msg)
    except Exception as e:
        print(f"Error sending consent email: {e}")

def create_and_emit_notification(emp, notif_type, message):
    notif = Notification(emp_id=emp.id, type=notif_type, message=message)
    db.session.add(notif)
    db.session.commit()

    # Emit the actual DB row so frontend gets id + is_read etc.
    payload = {
        'id': notif.id,
        'emp_id': notif.emp_id,
        'type': notif.type,
        'message': notif.message,
        'is_read': notif.is_read,
        'created_at': notif.created_at.strftime("%Y-%m-%d %H:%M:%S")
    }
    socketio.emit('new_notification', payload)
    return notif

def send_final_email_with_attachments(recipient_email, employee_name, attachments):
    body = f"""
    Dear {employee_name},

    Please find attached your final documents including the NDA and Offer Letter.

    Kindly review them at your earliest convenience.

    Thank you.
    """

    # Create multipart email
    msg = MIMEMultipart()
    msg['Subject'] = 'Final Documents - NDA & Offer Letter'
    msg['From'] = MAIL_CONFIG['MAIL_USERNAME']
    msg['To'] = recipient_email

    # Add body
    msg.attach(MIMEText(body, 'plain'))

    # Attach files
    for filepath in attachments:
        with open(filepath, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(filepath))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(filepath)}"'
            msg.attach(part)

    try:
        with smtplib.SMTP(MAIL_CONFIG['MAIL_SERVER'], MAIL_CONFIG['MAIL_PORT']) as server:
            if MAIL_CONFIG.get('MAIL_USE_TLS'):
                server.starttls()
            server.login(MAIL_CONFIG['MAIL_USERNAME'], MAIL_CONFIG['MAIL_PASSWORD'])
            server.send_message(msg)
    except Exception as e:
        print(f"Error sending final documents email: {e}")
        raise

# def extract_data_from_file(file_bytes, filename):
#     """Extract PAN, Aadhaar, contact number, and address from PDF or Image."""
#     extracted_text = ""

#     if filename.lower().endswith('.pdf'):
#         with pdfplumber.open(BytesIO(file_bytes)) as pdf:
#             for page in pdf.pages:
#                 extracted_text += page.extract_text() or ""
#     else:
#         image = Image.open(BytesIO(file_bytes))
#         extracted_text = pytesseract.image_to_string(image)

#     # Patterns
#     pan = re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', extracted_text)
#     aadhaar = re.search(r'\b[0-9]{4}\s[0-9]{4}\s[0-9]{4}\b', extracted_text)
#     phone = re.search(r'\b[6-9]\d{9}\b', extracted_text)
#     address = None  # Could add NLP-based extraction if required

#     return {
#         "pan": pan.group(0) if pan else None,
#         "aadhaar": aadhaar.group(0) if aadhaar else None,
#         "phone": phone.group(0) if phone else None,
#         "address": address
#     }


def extract_data_from_file(file_bytes, filename):
    """Extract PAN, Aadhaar, contact number, and address from PDF or Image."""
    extracted_text = ""

    if filename.lower().endswith('.pdf'):
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text
                else:
                    # Fallback to OCR for scanned pages
                    im = page.to_image(resolution=300).original
                    extracted_text += pytesseract.image_to_string(im)
    else:
        image = Image.open(BytesIO(file_bytes))
        extracted_text = pytesseract.image_to_string(image)

    # Patterns
    pan = re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', extracted_text)
    aadhaar = re.search(r'\b[0-9]{4}\s?[0-9]{4}\s?[0-9]{4}\b', extracted_text)
    phone = re.search(r'\b[6-9]\d{9}\b', extracted_text)
    address = None  # Could add NLP-based extraction if required

    return {
        "pan": pan.group(0) if pan else None,
        "aadhaar": aadhaar.group(0) if aadhaar else None,
        "phone": phone.group(0) if phone else None,
        "address": address
    }

@app.route('/api/employees', methods=['POST'])
def add_employee():
    print("POST /api/employees called")
    data = request.json

    employee = Employee(
        name=data['name'],
        email=data['email'],
        department=data['department'],
        designation=data.get('designation'),
        preferred_language=data.get('preferred_language', 'en'),
        onboarding_stage='welcome_sent'
    )
    db.session.add(employee)
    db.session.commit()

    # upload_url = f"http://localhost:8080/upload/{employee.id}"
    upload_url = f"https://hrms-gamma-rosy.vercel.app/upload/{employee.id}"
    send_welcome_email(employee.email, upload_url)

    return jsonify({"message": "Employee added and welcome email sent."}), 201

@app.route("/api/employees", methods=["GET"])
def get_employees():
    employees = Employee.query.all()
    results = []
    for emp in employees:
        results.append({
            "id": emp.id,
            "name": emp.name,
            "email": emp.email,
            "department": emp.department,
            "designation": emp.designation,
            "consent_status": emp.consent_status,
            "pan_number": mask_pan_in_text(decrypt(emp.pan_number)),
            "aadhaar_number": mask_aadhaar_in_text(decrypt(emp.aadhaar_number)),
            "contact_number": mask_phone(decrypt(emp.contact_number))
        })
    return jsonify(results)

@app.route('/api/employees/<int:emp_id>/send-consent', methods=['POST'])
def send_consent_form(emp_id):
    employee = db.session.get(Employee, emp_id)
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404

    # consent_link = f"http://localhost:8080/consent/{emp_id}"
    consent_link = f"https://hrms-gamma-rosy.vercel.app/consent/{emp_id}"

    send_consent_email(employee.email, employee.name, consent_link)

    return jsonify({'message': 'Consent form email sent'})

@app.route('/api/employees/<int:employee_id>/consent', methods=['POST'])
def submit_consent(employee_id):
    """
    Handles consent form submission by the employee.
    """
    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404

    data = request.json
    accepted = data.get("accepted", False)

    if not accepted:
        return jsonify({"error": "Consent not accepted"}), 400

    # Update employee status
    employee.consent_status = 'Submitted'
    employee.onboarding_stage = 'consent_submitted'
    db.session.commit()

    # Create persistent notification
    msg = f"✅ Consent submitted by {employee.name}"
    create_and_emit_notification(employee, 'consent_submitted', msg)

    # Emit real-time socket event to admins
    socketio.emit('consent_submitted', {
        'employee_id': employee.id,
        'employee_name': employee.name
    })

    return jsonify({"message": "Consent form submitted successfully"}), 200

# get all notifications (ordered newest first)
@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    notifs = Notification.query.order_by(Notification.created_at.desc()).all()
    result = [{
        'id': n.id,
        'emp_id': n.emp_id,
        'type': n.type,
        'message': n.message,
        'is_read': n.is_read,
        'created_at': n.created_at.strftime("%Y-%m-%d %H:%M:%S")
    } for n in notifs]
    return jsonify(result)

# mark as read
@app.route('/api/notifications/<int:notif_id>/read', methods=['PATCH'])
def mark_notification_as_read(notif_id):
    notif = Notification.query.get_or_404(notif_id)
    notif.is_read = True
    db.session.commit()
    return jsonify({'message': 'marked as read', 'id': notif.id})

@app.route('/api/employees/<int:emp_id>/send-final-email', methods=['POST'])
def send_final_documents(emp_id):
    employee = db.session.get(Employee, emp_id)
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404

    if 'nda' not in request.files or 'offer_letter' not in request.files:
        return jsonify({'error': 'Both NDA and Offer Letter are required'}), 400

    nda_file = request.files['nda']
    offer_file = request.files['offer_letter']

    # Save files temporarily for emailing
    nda_path = os.path.join(UPLOAD_FOLDER, f"{employee.name}_NDA_{nda_file.filename}")
    offer_path = os.path.join(UPLOAD_FOLDER, f"{employee.name}_Offer_{offer_file.filename}")
    nda_file.save(nda_path)
    offer_file.save(offer_path)

    print("FILES RECEIVED:", request.files)
    print("FORM RECEIVED:", request.form)

    # Get or create EmployeeSensitive record
    sensitive = EmployeeSensitive.query.filter_by(employee_id=employee.id).first()
    if not sensitive:
        sensitive = EmployeeSensitive(employee_id=employee.id)
        db.session.add(sensitive)

    # Encrypt and store NDA file in DB (binary-safe)
    nda_file.seek(0)
    nda_bytes = nda_file.read()
    sensitive.nda_file_enc = encrypt_bytes(nda_bytes)
    sensitive.nda_filename = nda_file.filename  # Store original filename

    # Encrypt and store Offer Letter file in DB (binary-safe)
    offer_file.seek(0)
    offer_bytes = offer_file.read()
    sensitive.offer_letter_file_enc = encrypt_bytes(offer_bytes)
    sensitive.offer_letter_filename = offer_file.filename  # Store original filename

    db.session.commit()

    # Send email with attachments
    send_final_email_with_attachments(
        employee.email,
        employee.name,
        [nda_path, offer_path]
    )

    # Emit final_sent notification
    msg = f"📨 Final documents sent to {employee.name}"
    create_and_emit_notification(employee, 'final_sent', msg)

    return jsonify({'message': 'Final documents sent successfully and stored in database'})

@app.route('/employee_sensitive', methods=['GET'])
def get_employee_sensitive():
    data = EmployeeSensitive.query.all()
    result = [{
        'employee_id': d.employee_id,
        # 'pan': d.pan_file_enc,
        'pan_name': d.pan_filename,
        # 'aadhar': d.aadhaar_file_enc,
        'aadhar_name': d.aadhaar_filename,
        # 'phtograph': d.photo_file_enc,
        'phtograph': d.photo_filename,
        # 'nda': d.nda_file_enc,
        'nda': d.nda_filename,
        # 'offer_letter': d.offer_letter_file_enc,
        'offer_letter': d.offer_letter_filename,
        # 'education_file': d.education_docs_file_enc,
        'education_file': d.education_docs_filename,
        'created_at': d.created_at,
        'updated_at': d.updated_at
    } for d in data]

    return jsonify(result)



def extract_data_from_file(file_bytes, filename):
    text_content = ""
    ext = filename.rsplit('.', 1)[1].lower()

    if ext == 'pdf':
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                text_content += page.extract_text() or ""
    elif ext in ['jpg', 'jpeg', 'png']:
        img = Image.open(io.BytesIO(file_bytes))
        text_content = pytesseract.image_to_string(img)

    # Regex patterns for PAN & Aadhaar
    pan_pattern = r"\b([A-Z]{5}[0-9]{4}[A-Z])\b"
    aadhaar_pattern = r"\b\d{4}\s\d{4}\s\d{4}\b"

    pan = re.search(pan_pattern, text_content)
    aadhaar = re.search(aadhaar_pattern, text_content)

    return {
        "pan": pan.group(1) if pan else None,
        "aadhaar": aadhaar.group(0) if aadhaar else None
    }

def preprocess_image_for_ocr(image):
    """Preprocess image to improve OCR accuracy."""
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    gray = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)  # Increase contrast
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    thresh = cv2.medianBlur(thresh, 3)  # Denoise
    return Image.fromarray(thresh)

def normalize_ocr_text(text):
    """Fix common OCR misreads and strip non-ASCII noise."""
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Remove weird chars
    text = text.replace('O', '0').replace('o', '0')
    text = text.replace('I', '1').replace('l', '1')
    return text

def extract_aadhaar_and_pan(file_bytes, filename):
    extracted_text = ""

    # Handle PDFs
    if filename.lower().endswith('.pdf'):
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text
                else:
                    im = page.to_image(resolution=300).original
                    extracted_text += pytesseract.image_to_string(im)
    else:
        # Handle images
        image = Image.open(BytesIO(file_bytes))
        extracted_text = pytesseract.image_to_string(image)

    # Normalize before matching
    extracted_text = normalize_ocr_text(extracted_text)

    # PAN regex
    pan_match = re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', extracted_text)

    # Aadhaar regex
    aadhaar_match = re.search(r'\b\d{4}\s?\d{4}\s?\d{4}\b', extracted_text)

    # Fallback for Aadhaar with preprocessing if not found
    if not aadhaar_match:
        if filename.lower().endswith('.pdf'):
            with pdfplumber.open(BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    im = page.to_image(resolution=300).original
                    im = preprocess_image_for_ocr(im)
                    text = normalize_ocr_text(pytesseract.image_to_string(im))
                    aadhaar_match = re.search(r'\b\d{4}\s?\d{4}\s?\d{4}\b', text)
                    if aadhaar_match:
                        break
        else:
            image = Image.open(BytesIO(file_bytes))
            image = preprocess_image_for_ocr(image)
            text = normalize_ocr_text(pytesseract.image_to_string(image))
            aadhaar_match = re.search(r'\b\d{4}\s?\d{4}\s?\d{4}\b', text)

    # Clean Aadhaar (remove spaces)
    aadhaar_number = re.sub(r'\s+', '', aadhaar_match.group(0)) if aadhaar_match else None
    pan_number = pan_match.group(0) if pan_match else None

    return aadhaar_number, pan_number

@app.route('/api/employees/<int:employee_id>/upload', methods=['POST'])
def upload_documents(employee_id):
    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404

    sensitive = EmployeeSensitive.query.filter_by(employee_id=employee_id).first()
    if not sensitive:
        sensitive = EmployeeSensitive(employee_id=employee_id)
        db.session.add(sensitive)

    # Encrypt contact info
    if 'contact_number' in request.form:
        employee.contact_number = encrypt(request.form['contact_number'])
    if 'contact_address' in request.form:
        employee.contact_address = encrypt(request.form['contact_address'])

    # Process each file
    for field in ['pan', 'aadhaar', 'photo', 'nda', 'offer_letter', 'education_docs']:
        file = request.files.get(field)
        if file:
            file_bytes = file.read()

            # Extract PAN/Aadhaar for pan/aadhaar fields
            if field in ['pan', 'aadhaar']:
                extracted_text = ""

                if file.filename.lower().endswith('.pdf'):
                    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
                        for page in pdf.pages:
                            text = page.extract_text()
                            if text:
                                extracted_text += text
                            else:
                                # OCR for scanned PDF pages
                                im = page.to_image(resolution=300).original
                                extracted_text += pytesseract.image_to_string(im)
                else:
                    # Image file
                    image = Image.open(BytesIO(file_bytes))
                    extracted_text = pytesseract.image_to_string(image)

                # Regex to find PAN/Aadhaar
                pan_match = re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', extracted_text)
                aadhaar_match = re.search(r'\b[0-9]{4}\s?[0-9]{4}\s?[0-9]{4}\b', extracted_text)

                if pan_match:
                    employee.pan_number = encrypt(pan_match.group(0))
                if aadhaar_match:
                    employee.aadhaar_number = encrypt(aadhaar_match.group(0))

            # Encrypt and save file
            encrypted_file = encrypt_bytes(file_bytes)
            setattr(sensitive, f"{field}_file_enc", encrypted_file)
            setattr(sensitive, f"{field}_filename", file.filename)

    employee.document_uploaded = True
    employee.onboarding_stage = 'documents_uploaded'
    db.session.commit()

    create_and_emit_notification(employee, 'document_uploaded', f"📄 Documents uploaded by {employee.name}")

    socketio.emit('document_uploaded', {
        'employee_id': employee.id,
        'employee_name': employee.name
    })

    return jsonify({"message": "Files uploaded, encrypted, and saved."}), 200


@app.route('/api/employees/<int:employee_id>/preview/<string:doc_type>', methods=['GET'])
def preview_document(employee_id, doc_type):
    # --- Unified regex patterns ---
    PAN_REGEX = r"[A-Z]{5}\d{4}[A-Z]"
    # AADHAAR_REGEX = r"(?:\d[0O]){4}\D{0,3}(?:\d[0O]){4}\D{0,3}(?:\d[0O]){4}"
    AADHAAR_REGEX = r"\b\d{4}\s?\d{4}\s?\d{4}\b"
    PATTERNS = [PAN_REGEX, AADHAAR_REGEX]

    sensitive = EmployeeSensitive.query.filter_by(employee_id=employee_id).first()
    if not sensitive:
        return jsonify({"error": "No documents found"}), 404

    enc_data = getattr(sensitive, f"{doc_type}_file_enc", None)
    filename = getattr(sensitive, f"{doc_type}_filename", None)
    if not enc_data or not filename:
        return jsonify({"error": f"{doc_type} not uploaded"}), 404

    # Decrypt file
    file_bytes = decrypt_bytes(enc_data)
    mime_type, _ = mimetypes.guess_type(filename)
    if not mime_type:
        mime_type = "application/octet-stream"

    # ==========================================================
    # 1. Handle PDF masking
    # ==========================================================
    if mime_type == "application/pdf":
        doc = fitz.open(stream=file_bytes, filetype="pdf")

        for page in doc:
            found = False
            words = page.get_text("words")  # (x0, y0, x1, y1, word, block_no, line_no, word_no)

            # --- Text-based masking ---
            from collections import defaultdict
            lines = defaultdict(list)
            for w in words:
                x0, y0, x1, y1, word_text, block_no, line_no, _ = w
                lines[(block_no, line_no)].append((x0, y0, x1, y1, word_text))

            for _, line_words in lines.items():
                line_text = "".join(word for (_, _, _, _, word) in line_words)
                line_text_spaced = " ".join(word for (_, _, _, _, word) in line_words)
                print("Extracted line:", line_text_spaced)

                for pattern in PATTERNS:
                    if re.search(pattern, line_text) or re.search(pattern, line_text_spaced):
                        for (x0, y0, x1, y1, _) in line_words:
                            rect = fitz.Rect(x0, y0, x1, y1)
                            page.add_redact_annot(rect, fill=(0, 0, 0))
                        found = True

            # --- OCR-based masking for scanned PDFs ---
            if not found:
                pix = page.get_pixmap(dpi=300)
                img = Image.open(io.BytesIO(pix.tobytes()))
                ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
                # mask_aadhaar_chunks(ocr_data, page=page, scale_x=scale_x, scale_y=scale_y)
                ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
                pdf_width, pdf_height = page.rect.width, page.rect.height
                scale_x, scale_y = pdf_width / img.width, pdf_height / img.height
                mask_aadhaar_chunks(ocr_data, page=page, scale_x=scale_x, scale_y=scale_y)


                pdf_width, pdf_height = page.rect.width, page.rect.height
                scale_x, scale_y = pdf_width / img.width, pdf_height / img.height

                for i, ocr_text in enumerate(ocr_data["text"]):
                    if not ocr_text.strip():
                        continue
                    for pattern in PATTERNS:
                        if re.search(pattern, ocr_text):
                            x, y, w, h = (ocr_data["left"][i], ocr_data["top"][i],
                                          ocr_data["width"][i], ocr_data["height"][i])
                            rect = fitz.Rect(x * scale_x, y * scale_y,
                                             (x + w) * scale_x, (y + h) * scale_y)
                            page.add_redact_annot(rect, fill=(0, 0, 0))
                            break  # avoid duplicate masking

            page.apply_redactions()

        file_bytes = doc.write(garbage=4, deflate=True)

    # ==========================================================
    # 2. Handle image masking
    # ==========================================================
    elif mime_type.startswith("image/"):
        img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
        # ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        # draw = ImageDraw.Draw(img)
        ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        draw = ImageDraw.Draw(img)
        mask_aadhaar_chunks(ocr_data, draw=draw)

        for i, text in enumerate(ocr_data["text"]):
            if not text.strip():
                continue
            for pattern in PATTERNS:
                if re.search(pattern, text):
                    x, y, w, h = (ocr_data["left"][i], ocr_data["top"][i],
                                  ocr_data["width"][i], ocr_data["height"][i])
                    draw.rectangle([x, y, x + w, y + h], fill="black")
                    break  # avoid masking same word twice

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        file_bytes = buf.getvalue()

    # ==========================================================
    # 3. Return masked file
    # ==========================================================
    return jsonify({
        "file_base64": base64.b64encode(file_bytes).decode(),
        "mime_type": mime_type
    })

# --- OCR-based masking for Aadhaar (handles split chunks) ---
def mask_aadhaar_chunks(ocr_data, page=None, draw=None, scale_x=1, scale_y=1):
    words = []
    for i, text in enumerate(ocr_data["text"]):
        if text.strip() and text.strip().isdigit() and len(text.strip()) == 4:
            words.append((i, text.strip()))
        else:
            words.append((i, None))

    # Scan sliding window of 3 consecutive 4-digit tokens
    for i in range(len(words) - 2):
        if words[i][1] and words[i+1][1] and words[i+2][1]:
            candidate = " ".join([words[i][1], words[i+1][1], words[i+2][1]])
            if re.fullmatch(r"\d{4}\s\d{4}\s\d{4}", candidate):
                # Redact all 3 boxes
                for j in [i, i+1, i+2]:
                    idx = words[j][0]
                    x, y, w, h = (ocr_data["left"][idx], ocr_data["top"][idx],
                                  ocr_data["width"][idx], ocr_data["height"][idx])
                    if page:  # PDF mode
                        rect = fitz.Rect(x * scale_x, y * scale_y,
                                         (x + w) * scale_x, (y + h) * scale_y)
                        page.add_redact_annot(rect, fill=(0, 0, 0))
                    elif draw:  # Image mode
                        draw.rectangle([x, y, x + w, y + h], fill="black")


@app.route("/api/employees/<int:id>/info", methods=["GET"])
def get_employee_info(id):
    emp = Employee.query.get_or_404(id)
    return jsonify({
        "id": emp.id,
        "name": emp.name,
        "email": emp.email,
        "department": emp.department,
        "designation": emp.designation,
        "pan_number": mask_pan_in_text(decrypt(emp.pan_number)),
        "aadhaar_number": mask_aadhaar_in_text(decrypt(emp.aadhaar_number)),
        "contact_number": mask_phone(decrypt(emp.contact_number))
    })


## Training Code

emailed_candidates = []

@app.route('/api/send_email', methods=['GET', 'POST'])
def send_email():

    request_data = request.json
    selected_department = request_data.get('department')

    if not selected_department:
        return jsonify({'error': 'No department selected'}), 400

     # Create a training session record
    colleagues = Colleagues.query.all()
    training_session = TrainingSession(
        department=selected_department,
        total_recipients=len(colleagues),
        created_by="Admin"  # Or take from request_data['created_by']
    )
    db.session.add(training_session)
    db.session.commit()

    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    signature_image_path = ''

    if selected_department == 'HR, Information Security, Training and TMG':
        with open(os.path.join(templates_dir, 'hr_email_template.html')) as f:
            email_template = f.read()
        action_name = "Update Payroll Information"
        email_subject = "Important: Update Your Payroll Information for Q4"
        # signature_image_path = os.path.join('templates', 'hr_signature.jpeg')

    elif selected_department == 'Sales and Marketing, Finance, Admin':
        with open(os.path.join(templates_dir, 'accounts_email_template.html')) as f:
            email_template = f.read()
        action_name = "Update Credentials"
        email_subject = "Reminder: Update Your Credentials for Compliance"
        # signature_image_path = os.path.join(
        #     'templates', 'sales_signature.jpeg')

    elif selected_department == 'Developer and Product Development':
        with open(os.path.join(templates_dir, 'developer_template.html')) as f:
            email_template = f.read()
            action_name = "Download Security Patch"
            email_subject = "Immediate Action Required: Security Patch Deployment for Development Tools"
            # signature_image_path = os.path.join(
            #     'templates', 'product_development_signature.jpeg')

    elif selected_department == 'Leadership':
        with open(os.path.join(templates_dir, 'leadership_template.html')) as f:
            email_template = f.read()
            action_name = "Review Strategic Plan"
            email_subject = "Urgent: Strategic Plan Review for Q4 - Action Required"
            # signature_image_path = os.path.join(
            #     'templates', 'leadership_signature.jpeg')
    # else:
    #     with open(os.path.join(templates_dir, 'email_template.html')) as f:
    #         email_template = f.read()
    #     action_name = "Complete Action"
    #     email_subject = "Action Required: Complete Task"  # Default subject

    
    EmailedCandidate.query.delete()
    db.session.commit()

    colleagues = Colleagues.query.all()

    # from_email = os.getenv('Email_Username')
    # password = os.getenv('Password')

    # from_email = os.getenv('Email_Username')
    # password = os.getenv('Password')

    from_email = MAIL_CONFIG['MAIL_USERNAME']
    password = MAIL_CONFIG['MAIL_PASSWORD']

    for colleague in colleagues:
        # tracking_link = f"https://phishing-mail-application.onrender.com/phishing_test/{colleague.id}"
        # tracking_link = f"https://phishing-mail-frontend.vercel.app/phishing_test/{colleague.id}"
        # tracking_link = f"http://localhost:8080/phishing_test/{colleague.id}"
        # tracking_link = f"http://35.182.29.153/api/phish_intermediate/{colleague.id}"
        # tracking_link = f"http://127.0.0.1:5000/api/phish_intermediate/{colleague.id}"
        tracking_link = f"https://hrms-ocfa.onrender.com/api/phish_intermediate/{colleague.id}"
        # tracking_link = f"https://phishing-application-demo.vercel.app/phishing_test/{colleague.id}"

        print(f"Generated tracking link for {colleague.name}: {tracking_link}")

        to_email = colleague.email
        msg = MIMEMultipart('related')
        msg['Subject'] = email_subject
        msg['From'] = from_email
        msg['To'] = to_email

        body = email_template.replace("{{recipient_name}}", colleague.name)
        body = body.replace("{{action_link}}", tracking_link)
        body = body.replace("{{action_name}}", action_name)
        body = body.replace("{{email_subject}}", email_subject)
        body = body.replace("{{statement_link}}", tracking_link)

        html_content = f"""
        <html>
            <body>
                {body}
            </body>
        </html>
        """
        msg.attach(MIMEText(html_content, 'html'))

        # signature_image_path = os.path.join('templates', 'Capture.JPG')
        # with open(signature_image_path, 'rb') as img_file:
        #     img = MIMEImage(img_file.read())
        #     img.add_header('Content-ID', '<signature_image>')
        #     msg.attach(img)

        # Attach logo image
        logo_image_path = os.path.join(templates_dir, 'Icici Bank.png')
        with open(logo_image_path, 'rb') as img_file:
            img = MIMEImage(img_file.read())
            img.add_header('Content-ID', '<logo_image>')
            msg.attach(img)

        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(from_email, password)
                server.send_message(msg)
            print(f"Email sent to {colleague.email}")
            # with smtplib.SMTP('smtpout.secureserver.net', 587) as server:
            #     server.starttls()
            #     server.login(from_email, password)
            #     server.send_message(msg)
            # print(f"Email sent to {colleague.email}")

            # with smtplib.SMTP('smtp.bizmail.yahoo.com', 587) as server:
            #     server.starttls()
            #     server.login(from_email, password)
            #     server.send_message(msg)
            # print(f"Email sent to {colleague.email}")

            # emailed_candidates.append({
            #     'name': colleague.name,
            #     'email': colleague.email,
            #     'designation': colleague.designation
            emailed_candidate = EmailedCandidate(
                name=colleague.name,
                email=colleague.email,
                designation=colleague.designation
            )
            db.session.add(emailed_candidate)
            print("Emailed candidates list after sending:", emailed_candidates)

        except Exception as e:
            print(f"Failed to send email to {colleague.email}: {str(e)}")
    
    db.session.commit()

    return jsonify({
        'message': 'Phishing emails sent to colleagues.',
        'training_session_id': training_session.id
        })


@app.route('/api/phishing_test/<int:colleague_id>', methods=['GET'])
def phishing_test(colleague_id):
    print(f'Phishing test accessed for colleague ID: {colleague_id}')

    colleague = Colleagues.query.get(colleague_id)
    if not colleague:
        return jsonify({'error': 'Colleague not found.'}), 404

    return jsonify({'message': 'Tracking link accessed successfully', 'colleague_id': colleague_id})
    # return redirect(f'https://kvphishing.netlify.app/phishing_test/{colleague_id}')


@app.route('/api/generate_emailed_candidates_report', methods=['GET', 'POST'])
def generate_emailed_candidates_report():
    candidates = EmailedCandidate.query.all()

    if not candidates:
        print("No candidates in emailed_candidates:",
              candidates)
        return jsonify({'error': 'No successfully emailed candidates.'}), 400

    print("Generating CSV for:", candidates)

    try:
        csv_file_path = "emailed_candidates_report.csv"
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['name', 'email', 'designation']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for c in candidates:
                writer.writerow({
                    'name': c.name,
                    'email': c.email,
                    'designation': c.designation
                })

        return send_file(csv_file_path, as_attachment=True)
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/users')
def users():
    user = Colleagues.query.all()
    return jsonify([{'id': u.id, 'name': u.name, 'email': u.email, 'department': u.department, 'designation': u.designation} for u in user])


@app.route('/api/phising_click/<int:colleague_id>', methods=['POST'])
def phising_click(colleague_id):
    print(f'Received request for colleague ID: {colleague_id}')
    colleague = Colleagues.query.get(colleague_id)
    if not colleague:
        return jsonify({'error': 'Colleague not found.'}), 404

    report = Reports.query.filter_by(colleague_id=colleague_id).first()
    if report:
        report.clicked = True
    else:
        report = Reports(colleague_id=colleague_id,
                         clicked=True, answered=False, answers={})
        db.session.add(report)
    db.session.commit()

    candidate_data = {
        'id': colleague.id,
        'name': colleague.name,
        'email': colleague.email,
        'department': colleague.department,
        'designation': colleague.designation
    }

    return jsonify({'message': 'Click recorded', 'candidate': candidate_data})


@app.route('/api/reports', methods=['GET'])
def get_reports():
    reports = Reports.query.all()
    report_data = [{'id': r.id, 'colleague_id': r.colleague_id, 'clicked': r.clicked,
                    'answered': r.answered, 'answers': r.answers, 'status': r.status, 'score': r.score, 'completion_date': r.completion_date} for r in reports]
    return jsonify(report_data)


@app.route('/api/phishing_opened/<int:colleague_id>', methods=['GET'])
def phishing_opened(colleague_id):
    report = Reports.query.filter_by(colleague_id=colleague_id).first()
    print(
        f'Processing click for colleague ID: {colleague_id} | Existing report: {report}')

    if report:
        report.clicked = True
        print(f'Updated existing report for ID {colleague_id} to clicked=True')
    else:
        report = Reports(colleague_id=colleague_id,
                         clicked=True, answered=False, answers={})
        db.session.add(report)
        print(f'Created new report for ID {colleague_id} with clicked=True')

    db.session.commit()
    return jsonify({'message': 'Thank you for participating in our phishing awareness program.', 'showPopup': True})


def evaluate_answers(submitted_answers, correct_answers, questions):
    score = 0
    total_questions = len(questions)

    for i, submitted_answer in enumerate(submitted_answers):
        question_id = questions[i]['id']  # Get the question ID
        correct_answer = correct_answers.get(question_id, None)

        if correct_answer:
            # Normalize and compare answers
            submitted_answer = str(submitted_answer).strip().lower()
            correct_answer = str(correct_answer).strip().lower()

            print(
                f"Comparing submitted: '{submitted_answer}' with correct: '{correct_answer}'")

            if submitted_answer == correct_answer:
                score += 1

    return (score / total_questions) * 100 if total_questions > 0 else 0

@app.route('/api/phish_intermediate/<int:colleague_id>', methods=['GET'])
def phish_intermediate(colleague_id):
    colleague = Colleagues.query.get(colleague_id)
    if not colleague:
        return "Invalid link.", 404
    return render_template('intermediate_page.html', colleague_id=colleague_id)



@app.route('/api/submit_answers/<int:colleague_id>', methods=['POST'])
def submit_answers(colleague_id):
    data = request.get_json()
    report = Reports.query.filter_by(colleague_id=colleague_id).first()

    if report and report.clicked:
        report.answered = True
        report.answers = data['answers']

        # We need to store the correct answers with the corresponding question IDs
        correct_answers = {question['id']: question['answer']
                           for question in data['questions']}  # Using the received questions with answers

        # Evaluate the score using the submitted answers and the corresponding correct answers
        report.score = evaluate_answers(
            data['answers'], correct_answers, data['questions'])
        print(report.score)
        report.status = "Completed" if report.score >= 70 else "Pending"
        report.completion_date = datetime.now()
        db.session.commit()

        # study_material_link = f"http://localhost:8080/study-material/{colleague_id}"
        study_material_link = f"https://hrms-gamma-rosy.vercel.app/study-material/{colleague_id}"
        # study_material_link = f"http://35.182.29.153/study-material/{colleague_id}"
        # study_material_link = f"https://phishing-application-demo.vercel.app/study-material/{colleague_id}"

        if report.score >= 70:
            subject = "Congratulations on Completing the Training Program!"
            body = f"Dear {report.colleague.name},\n\nYou have successfully completed the training program with a score of {report.score}%."
        else:
            subject = "Reattempt the Training Program"
            body = f"""Dear {report.colleague.name},<br><br>
                    Unfortunately, you did not pass the training program. Please reattempt it by following the link provided:<br><br>
                    <a href="{study_material_link}">Reattempt</a><br><br>
                    Score: {report.score}%."""

        send_result_email(report.colleague.email, subject, body)

        return jsonify({'message': 'Answers submitted successfully.', 'score': report.score})

    return jsonify({'error': 'User did not click the phishing link.'}), 400


@app.route('/api/generate_reports', methods=['GET', 'POST'])
def generate_reports():
    try:
        reports = Reports.query.all()
        report_data = []

        for report in reports:
            colleague = Colleagues.query.get(report.colleague_id)
            report_entry = {
                'Colleague Name': colleague.name,
                'Colleague Email': colleague.email,
                'Department': colleague.department,
                'Designation': colleague.designation,
                'Link Clicked': 'Yes' if report.clicked else 'No',
                # 'Answered': report.answered,
                'Score': report.score,
                'Status': report.status,
                'Completion Date': report.completion_date.strftime('%Y-%m-%d') if report.completion_date else None,
            }
            report_data.append(report_entry)

        csv_file_path = "candidate_reports.csv"
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Colleague Name', 'Colleague Email', 'Department',
                          'Designation', 'Link Clicked', 'Score',
                          'Status', 'Completion Date']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for data in report_data:
                writer.writerow(data)

        return send_file(csv_file_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download_report/<int:colleague_id>', methods=['GET'])
def download_report(colleague_id):
    report = Reports.query.filter_by(colleague_id=colleague_id).first()
    colleague = Colleagues.query.get(colleague_id)

    if not report or not colleague:
        return jsonify({'error': 'Report or colleague not found.'}), 404

    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=letter)

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(100, 770, "Phishing Awareness Report")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, 740, f"Report for: {colleague.name}")
    pdf.drawString(100, 720, f"Email: {colleague.email}")
    pdf.drawString(100, 700, f"Department: {colleague.department}")

    pdf.setLineWidth(1)
    pdf.line(100, 690, 500, 690)

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(100, 670, "Phishing Email Status:")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(120, 650, f"Clicked: {'Yes' if report.clicked else 'No'}")
    pdf.drawString(120, 630, f"Answered: {'Yes' if report.answered else 'No'}")

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(100, 600, "Answers Provided:")

    pdf.setFont("Helvetica", 12)
    y_position = 580
    if report.answers:
        for i, answer in enumerate(report.answers, start=1):
            pdf.drawString(120, y_position, f"Q{i}: {answer}")
            y_position -= 20
    else:
        pdf.drawString(120, y_position, "No answers submitted")
        y_position -= 20

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(100, y_position - 20, "Overall Performance:")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(120, y_position - 40,
                   f"Score: {report.score if report.score else 0}")

    pdf.setFont("Helvetica-Oblique", 10)
    pdf.drawString(100, 50, "Generated on: " +
                   datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    pdf.showPage()
    pdf.save()
    pdf_buffer.seek(0)

    return send_file(pdf_buffer, as_attachment=True, download_name=f'report_{colleague_id}.pdf', mimetype='application/pdf')

@app.route('/api/upload_colleagues_data', methods=['POST'])
def upload_colleagues_data():
    try:
        Reports.query.delete()
        # Clear existing data in the colleagues table
        Colleagues.query.delete()  # This will also delete related reports due to cascade delete
        
        file = request.files.get('file')
        if file and file.filename.endswith('.xlsx'):
            # Read Excel file
            df = pd.read_excel(file)
            
            # Check if the expected columns are present in the file
            required_columns = {'Full Name', 'Work Email', 'Department', 'Job Title'}
            if not required_columns.issubset(df.columns):
                return jsonify({'message': 'Invalid file structure. Ensure columns are correct.'}), 400

            # Iterate through each row in the dataframe and add to the database
            for _, row in df.iterrows():
                if pd.isna(row['Full Name']) or pd.isna(row['Work Email']) or pd.isna(row['Department']) or pd.isna(row['Job Title']):
                    continue  # Skip rows with any missing required data

                colleague = Colleagues(
                    name=row['Full Name'],
                    email=row['Work Email'],
                    department=row['Department'],
                    designation=row['Job Title']
                )
                db.session.add(colleague)

            db.session.commit()
            return jsonify({'message': 'Data uploaded successfully'}), 200
        else:
            return jsonify({'message': 'Invalid file format. Please upload an .xlsx file.'}), 400

    except Exception as e:
        db.session.rollback()
        print("Error uploading data:", e)
        return jsonify({'message': f'Error processing file: {str(e)}'}), 500

@app.route('/api/questions', methods=['GET'])
def get_questions():
    questions = Questions.query.all()
    return jsonify([{
        'id': question.id,
        'question_text': question.question_text,
        'options': question.options,
        'answer': question.answer
    } for question in questions])


@app.route('/api/questions/<int:question_id>', methods=['GET'])
def get_question(question_id):
    question = Questions.query.get(question_id)
    if question:
        return jsonify({
            'id': question.id,
            'question_text': question.question_text,
            'options': question.options,
            'answer': question.answer
        })
    return jsonify({'error': 'Question not found!'}), 404


@app.route('/api/questions', methods=['POST'])
def add_question():
    data = request.json
    new_question = Questions(
        question_text=data['question_text'],
        options=data['options'],
        answer=data['answer']
    )
    db.session.add(new_question)
    db.session.commit()
    return jsonify({'message': 'Question added!', 'id': new_question.id}), 201


@app.route('/api/questions/<int:question_id>', methods=['PUT'])
def update_question(question_id):
    print(f"Updating question ID: {question_id}")
    data = request.json
    print(f"Received data: {data}")

    question = Questions.query.get(question_id)
    if not question:
        return jsonify({'error': 'Question not found!'}), 404

    question.question_text = data['question_text']
    question.options = data['options']
    question.answer = data['answer']
    db.session.commit()
    return jsonify({'message': 'Question updated!'})


@app.route('/api/questions/<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    question = Questions.query.get(question_id)
    if not question:
        return jsonify({'error': 'Question not found!'}), 404

    db.session.delete(question)
    db.session.commit()
    return jsonify({'message': 'Question deleted!'})

@app.route('/api/download-certificate/<int:colleague_id>', methods=['GET'])
def download_certificate(colleague_id):
    try:
        # Query the database for the colleague
        colleague = Colleagues.query.get(colleague_id)
        report = Reports.query.filter_by(colleague_id=colleague_id).first()

        if not colleague or report.status != "Completed" or report.score < 70:
            return jsonify({"error": "Certificate not available for this colleague"}), 400

        # Ensure that colleague.name is a string and pass it along with the score
        certificate_path = generate_certificate(colleague.name, report.score)

        if certificate_path is None:
            return jsonify({"error": "Certificate generation failed"}), 500

        # Use send_file with download_name specified
        return send_file(certificate_path, as_attachment=True, mimetype='application/pdf', download_name=f"certificate_{colleague.name}.pdf")

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Failed to download certificate"}), 500


def generate_certificate(candidate_name, score):
    try:
        candidate_name_safe = candidate_name.replace(" ", "_")
        pdf_file_path = f"certificate_{candidate_name_safe}.pdf"

        # Check if the directory exists, create if not
        if not os.path.exists("certificates"):
            os.makedirs("certificates")

        pdf_file_path = os.path.join("certificates", pdf_file_path)

        document = SimpleDocTemplate(pdf_file_path, pagesize=letter)
        styles = getSampleStyleSheet()

        content = []

        title = Paragraph("Certificate of Completion", styles['Title'])
        content.append(title)
        content.append(Spacer(1, 20))

        name = Paragraph(
            f"This certifies that <b>{candidate_name}</b>", styles['Normal'])
        content.append(name)
        content.append(Spacer(1, 20))

        score_paragraph = Paragraph(
            f"Has successfully completed the quiz with a score of <b>{score}%</b>.", styles['Normal'])
        content.append(score_paragraph)
        content.append(Spacer(1, 20))

        footer = Paragraph("Thank you for your participation!", styles['Normal'])
        content.append(footer)

        document.build(content)
        print(f"Generated PDF at: {pdf_file_path}")

        return pdf_file_path

    except Exception as e:
        print(f"Error generating certificate: {e}")
        return None


@app.route('/api/update_report_status/<colleague_id>', methods=['POST'])
def update_report_status(colleague_id):
    data = request.get_json()
    score = data.get('score')

    if score is None:
        return jsonify({'error': 'Score is required'}), 400

    try:
        # Log the incoming data
        print(
            f"Updating report for colleague_id: {colleague_id} with score: {score}")

        # Fetch the report for the given colleague_id
        report = Reports.query.filter_by(colleague_id=colleague_id).first()

        if report:
            report.score = score
            db.session.commit()
            return jsonify({'message': 'Score updated successfully'})
        else:
            return jsonify({'error': 'Report not found'}), 404
    except Exception as e:
        print(f"Error updating report: {e}")  # Log the error to console
        return jsonify({'error': str(e)}), 500


@app.route('/api/send_result_email', methods=['POST'])
def send_result_email():
    data = request.get_json()

    colleague_email = data.get('colleague_id')
    subject = data.get('subject')
    body = data.get('body')

    if colleague_email and subject and body:
        send_result_email(colleague_email, subject, body)
        return jsonify({'message': 'Email sent successfully.'}), 200
    else:
        return jsonify({'error': 'Missing required fields.'}), 400


def send_result_email(colleague_email, subject, body):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    from_email = MAIL_CONFIG['MAIL_USERNAME']
    password = MAIL_CONFIG['MAIL_PASSWORD']

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = colleague_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(from_email, password)
            server.sendmail(from_email, colleague_email, msg.as_string())
        print(f"Email sent to {colleague_email}")

    except Exception as e:
        print(f"Failed to send email to {colleague_email}: {str(e)}")


@app.route('/api/send_reminder/<int:report_id>', methods=['POST'])
def send_reminder(report_id):
    report = Reports.query.get(report_id)
    if report:

        if report.status in ['Pending', 'Training Completed']:
            smtp_server = 'smtp.gmail.com'
            smtp_port = 587
            from_email = MAIL_CONFIG['MAIL_USERNAME']
            password = MAIL_CONFIG['MAIL_PASSWORD']

            colleague_email = report.colleague.email
            colleague_id = report.colleague_id

            # study_material_link = f"http://localhost:8080/study-material/{colleague_id}"
            study_material_link = f"https://hrms-gamma-rosy.vercel.app/study-material/{colleague_id}"
            # study_material_link = f"http://35.182.29.153/study-material/{colleague_id}"
            # study_material_link = f"https://phishing-application-demo.vercel.app/study-material/{colleague_id}"

            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = colleague_email
            msg['Subject'] = "Reminder: Complete Your Training"

            # body = f"Dear {report.colleague.name},\n\nThis is a reminder to complete your training."

            body = f"""
            Dear {report.colleague.name},<br><br>
            This is a reminder to complete your training.<br><br>
            Please click the link below to access the study material:<br>
            <a href="{study_material_link}">Study Material</a><br><br>
            """
            msg.attach(MIMEText(body, 'html'))

            try:
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(from_email, password)
                    server.send_message(msg)
                return jsonify({"message": "Reminder email sent successfully!"}), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        else:
            return jsonify({"message": "Status is not Pending or Training Completed."}), 400
    else:
        return jsonify({"message": "Report not found."}), 404


@app.route('/api/get_random_questions', methods=['GET'])
def get_random_questions():
    try:
        # Fetch 10 random questions from the database
        questions = Questions.query.order_by(func.random()).limit(10).all()
        questions_data = [{
            'id': question.id,
            'question_text': question.question_text,
            'options': question.options,
            'answer': question.answer
        } for question in questions]

        return jsonify({'questions': questions_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/get_all_reports', methods=['GET'])
def get_all_reports():
    try:
        reports = Reports.query.all()
        report_data = [{'id': r.id, 'colleague_id': r.colleague_id, 'clicked': r.clicked,
                        'answered': r.answered, 'answers': r.answers, 'status': r.status, 'score': r.score, 'completion_date': r.completion_date} for r in reports]
        return jsonify({'reports': report_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/delete_colleagues_data', methods=['Delete'])
def delete_colleagues_data():
    try:
        num_deleted = Colleagues.query.delete()
        db.session.commit()
        return jsonify({"message": "Colleagues data successfully deleted."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

def generate_pie_chart(data, labels, colors):
    fig, ax = plt.subplots()
    ax.pie(data, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
    ax.axis('equal')
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    plt.close(fig)
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    return img_base64

@app.route('/api/generate_reports_pdf')
def generate_styled_report():
    reports = Reports.query.all()
    total_recipients = EmailedCandidate.query.count()
    fail_count = Reports.query.filter_by(clicked=True).count()
    did_not_click_count = total_recipients - fail_count
    pass_count = len(reports) - fail_count
    clicked_only = Reports.query.filter(Reports.clicked == True, Reports.answered == False).count()
    clicked_and_answered = Reports.query.filter(Reports.clicked == True, Reports.answered == True).count()
    repeat_offender = db.session.query(Reports.colleague_id).filter_by(clicked=True).group_by(Reports.colleague_id).having(func.count(Reports.id) > 1).count()

    summary = [
        {'label': 'Total Recipients (Emailed)', 'value': total_recipients},
        {'label': 'Fail', 'value': fail_count},
        {'label': 'Pass', 'value': pass_count},
        {'label': 'Clicked Only', 'value': clicked_only},
        {'label': 'Clicked & Submitted Data', 'value': clicked_and_answered},
        {'label': 'Repeat Offender', 'value': repeat_offender}
    ]

    # 3 charts: Pass/Fail, Clicked vs Not, Clicked Only vs Clicked&Submitted
    chart1 = generate_pie_chart([fail_count, pass_count], ['Fail', 'Pass'], ['#e74c3c', '#2ecc71'])
    chart2 = generate_pie_chart([clicked_only, clicked_and_answered], ['Clicked Only', 'Clicked & Submitted'], ['#f39c12', '#3498db'])
    # chart3 = generate_pie_chart([len(reports) - fail_count, fail_count], ['Did Not Click', 'Clicked'], ['#2ecc71', '#e74c3c'])
    chart3 = generate_pie_chart(
        [did_not_click_count, fail_count],
        ['Did Not Click', 'Clicked'],
        ['#2ecc71', '#e74c3c']
    )
    charts = [chart1, chart2, chart3]

    candidate_reports = []
    for report in reports:
        colleague = Colleagues.query.get(report.colleague_id)
        candidate_reports.append({
            'id': report.id,
            'name': colleague.name if colleague else 'Unknown',
            'clicked': 'Yes' if report.clicked else 'No',
            'answered': 'Yes' if report.answered else 'No',
            'score': f"{report.score}%" if report.score else '0%',
            'status': report.status,
            'completion_date': report.completion_date.strftime('%Y-%m-%d') if report.completion_date else '-'
        })

    company_logo_path = os.path.abspath(os.path.join('static', 'Xploit2Secure.png'))
    company_logo_path = company_logo_path.replace('\\', '/')
    company_logo_url = f'file:///{company_logo_path}'
    print(f"Company logo absolute file URL: {company_logo_url}")
    rendered_html = render_template(
        'phishing_report.html',
        summary=summary,
        charts=charts,
        reports=candidate_reports,
        company_logo=company_logo_url
    )

    # pdf = HTML(string=rendered_html).write_pdf()
    pdf = HTML(string=rendered_html, base_url=os.path.abspath(".")).write_pdf()
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=styled_report.pdf'
    return response


@app.route('/api/training_sessions', methods=['GET'])
def get_training_sessions():
    sessions = TrainingSession.query.all()
    return jsonify([{
        'id': s.id,
        'department': s.department,
        'conducted_on': s.conducted_on.strftime("%Y-%m-%d %H:%M:%S"),
        'total_recipients': s.total_recipients,
        'created_by': s.created_by
    } for s in sessions])

@app.route('/api/training-sessions/csv', methods=['GET'])
def download_training_sessions_csv():
    sessions = TrainingSession.query.all()

    if not sessions:
        return Response("No training sessions found.", mimetype="text/plain")

    si = StringIO()
    writer = csv.writer(si)

    headers = [column.name for column in TrainingSession.__table__.columns]
    writer.writerow(headers)

    for session in sessions:
        row = []
        for col in headers:
            value = getattr(session, col)

            if col == "conducted_on" and value:
                # Ensure proper datetime formatting
                if isinstance(value, datetime):
                    value = value.strftime("%d-%m-%Y")
                else:
                    try:
                        dt = datetime.strptime(str(value), "%Y-%m-%d %H:%M:%S")
                        value = dt.strftime("%d-%m-%Y")
                    except:
                        value = str(value)

                # ✅ Force Excel to keep as text
                value = f"{value}"

            row.append(value)
        writer.writerow(row)

    output = si.getvalue()
    si.close()

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=training_sessions.csv"}
    )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        insert_dummy_data()
    socketio.run(app, debug=True)