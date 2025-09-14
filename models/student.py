from database import db
from datetime import datetime
from sqlalchemy import Index
import re

class Student(db.Model):
    """Student model with required fields and business logic"""
    
    __tablename__ = 'students'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Required fields
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False)
    
    # Calculated fields (updated by business logic)
    highest_intake = db.Column(db.String(50), nullable=True)
    highest_status = db.Column(db.String(100), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    applications = db.relationship('Application', backref='student', lazy=True, cascade='all, delete-orphan')
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_student_email', 'email'),
        Index('idx_student_phone', 'phone'),
    )
    
    def __repr__(self):
        return f'<Student {self.name} ({self.email})>'
    
    def to_dict(self):
        """Convert student to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'highest_intake': self.highest_intake,
            'highest_status': self.highest_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'applications_count': len(self.applications)
        }
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone):
        """Validate phone format (basic validation)"""
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        # Check if it has 10-15 digits
        return 10 <= len(digits_only) <= 15
    
    def validate(self):
        """Validate student data"""
        errors = []
        
        if not self.name or not self.name.strip():
            errors.append("Name is required")
        elif len(self.name.strip()) < 2:
            errors.append("Name must be at least 2 characters long")
        
        if not self.email or not self.email.strip():
            errors.append("Email is required")
        elif not self.validate_email(self.email):
            errors.append("Invalid email format")
        
        if not self.phone or not self.phone.strip():
            errors.append("Phone is required")
        elif not self.validate_phone(self.phone):
            errors.append("Invalid phone format")
        
        return errors
