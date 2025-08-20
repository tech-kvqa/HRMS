# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

def gen_id():
    return str(uuid.uuid4())

# class Employee(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(120))
#     email = db.Column(db.String(120), unique=True)
#     department = db.Column(db.String(120))
#     designation = db.Column(db.String(120))
#     preferred_language = db.Column(db.String(10), default='en')
#     consent_status = db.Column(db.String(50), default='Pending')
#     document_uploaded = db.Column(db.Boolean, default=False)
#     onboarding_stage = db.Column(db.String(50), default='welcome_sent')  # new

class Employee(db.Model):
    __tablename__ = 'employee'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    department = db.Column(db.String(120))
    designation = db.Column(db.String(120))
    preferred_language = db.Column(db.String(10), default='en')
    consent_status = db.Column(db.String(50), default='Pending')
    document_uploaded = db.Column(db.Boolean, default=False)
    onboarding_stage = db.Column(db.String(50), default='welcome_sent')

    # Extracted from uploaded docs
    pan_number = db.Column(db.String(50))
    aadhaar_number = db.Column(db.String(50))
    contact_number = db.Column(db.String(50))
    contact_address = db.Column(db.Text)


# class EmployeeSensitive(db.Model):
#     __tablename__ = 'employee_sensitive'

#     id = db.Column(db.Integer, primary_key=True)
#     employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False, unique=True)

#     # Encrypted file storage (AES CBC)
#     pan_file_enc = db.Column(db.Text)      # base64-encoded AES ciphertext
#     aadhaar_file_enc = db.Column(db.Text)
#     photo_file_enc = db.Column(db.Text)
#     nda_file_enc = db.Column(db.Text)
#     offer_letter_file_enc = db.Column(db.Text)
#     education_docs_enc = db.Column(db.Text)

#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class EmployeeSensitive(db.Model):
    __tablename__ = 'employee_sensitive'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False, unique=True)

    # Encrypted file storage (AES CBC)
    pan_file_enc = db.Column(db.Text)
    aadhaar_file_enc = db.Column(db.Text)
    photo_file_enc = db.Column(db.Text)
    nda_file_enc = db.Column(db.Text)
    offer_letter_file_enc = db.Column(db.Text)
    education_docs_file_enc = db.Column(db.Text)

    # Store original filenames for MIME detection
    pan_filename = db.Column(db.String(255))
    aadhaar_filename = db.Column(db.String(255))
    photo_filename = db.Column(db.String(255))
    nda_filename = db.Column(db.String(255))
    offer_letter_filename = db.Column(db.String(255))
    education_docs_filename = db.Column(db.String(255))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)



class Purpose(db.Model):
    id = db.Column(db.String, primary_key=True, default=gen_id)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    departments = db.Column(db.String)  # Comma-separated string
    language = db.Column(db.String(10), default='en')

class ConsentRecord(db.Model):
    id = db.Column(db.String, primary_key=True, default=gen_id)
    employee_id = db.Column(db.String, db.ForeignKey('employee.id'))
    purpose_id = db.Column(db.String, db.ForeignKey('purpose.id'))
    consent_given = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String, db.ForeignKey('employee.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)       # e.g. 'document_uploaded', 'consent_submitted'
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Colleagues(db.Model):
    __tablename__ = 'colleagues'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(100), nullable=False)
    reports = db.relationship(
        'Reports',
        back_populates='colleague',  # Use back_populates here
        cascade="all, delete",
        passive_deletes=True
    )


class Reports(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    colleague_id = db.Column(db.Integer, db.ForeignKey('colleagues.id', ondelete='CASCADE'), nullable=False)
    clicked = db.Column(db.Boolean, default=False)
    answered = db.Column(db.Boolean, default=False)
    answers = db.Column(db.PickleType)
    score = db.Column(db.Float)
    status = db.Column(db.String(50), default="Pending")
    completion_date = db.Column(db.DateTime)

    # Use back_populates here as well to explicitly link the two relationships
    colleague = db.relationship('Colleagues', back_populates='reports')

    def to_dict(self):
        return {
            "id": self.id,
            "colleague": {
                "name": self.colleague.name,
                "email": self.colleague.email
            },
            "score": self.score,
            "status": self.status,
            "answers": self.answers,
            "answered": self.answered,
            "clicked": self.clicked,
            "completion_date": self.completion_date.strftime('%Y-%m-%d') if self.completion_date else None
        }



class Questions(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(255), nullable=False)
    options = db.Column(db.JSON, nullable=False)
    answer = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "question_text": self.question_text,
            "options": self.options,
            "answer": self.answer
        }
    
class EmailedCandidate(db.Model):
    __tablename__ = 'emailed_candidates'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(100), nullable=False)

class TrainingSession(db.Model):
    __tablename__ = 'training_sessions'
    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String(100), nullable=False)
    conducted_on = db.Column(db.DateTime, default=datetime.utcnow)
    total_recipients = db.Column(db.Integer, nullable=False)
    created_by = db.Column(db.String(100))  # Optional: who initiated training


