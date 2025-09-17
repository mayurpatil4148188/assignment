from app.extensions import db
from datetime import datetime
from sqlalchemy import Index, ForeignKey
import re
from dateutil import parser

class Application(db.Model):
    """Application model with status hierarchy and business logic"""
    
    __tablename__ = 'applications'
    
    # Status hierarchy with weightage (higher number = higher priority)
    STATUS_HIERARCHY = {
        'Building Application': 1,
        'Application Submitted to University': 2,
        'Offer Received': 3,
        'Offer Accepted by Student': 4,
        'Visa Approved': 5,
        'Dropped': 0  # Lowest priority
    }
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key
    student_id = db.Column(db.Integer, ForeignKey('students.id'), nullable=False)
    
    # Required fields
    university_name = db.Column(db.String(255), nullable=False)
    program_name = db.Column(db.String(255), nullable=False)
    intake = db.Column(db.String(50), nullable=False)  # Format: Jan 2026, Feb 2026, etc.
    status = db.Column(db.String(100), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_application_student_id', 'student_id'),
        Index('idx_application_status', 'status'),
        Index('idx_application_intake', 'intake'),
    )
    
    def __repr__(self):
        return f'<Application {self.university_name} - {self.program_name} ({self.status})>'
    
    def to_dict(self):
        """Convert application to dictionary"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'university_name': self.university_name,
            'program_name': self.program_name,
            'intake': self.intake,
            'status': self.status,
            'status_weight': self.get_status_weight(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_status_weight(self):
        """Get the weight of the current status"""
        return self.STATUS_HIERARCHY.get(self.status, 0)
    
    @staticmethod
    def get_valid_statuses():
        """Get list of valid statuses"""
        return list(Application.STATUS_HIERARCHY.keys())
    
    @staticmethod
    def validate_intake_format(intake):
        """Validate intake format (e.g., Jan 2026, Feb 2026)"""
        if not intake or not intake.strip():
            return False
        
        # Pattern for month year format
        pattern = r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}$'
        return re.match(pattern, intake.strip(), re.IGNORECASE) is not None
    
    @staticmethod
    def parse_intake_date(intake):
        """Parse intake string to datetime for comparison"""
        try:
            # Convert to standard format for parsing
            intake_clean = intake.strip()
            return parser.parse(intake_clean)
        except (ValueError, TypeError):
            return None
    
    def validate(self):
        """Validate application data"""
        errors = []
        
        if not self.university_name or not self.university_name.strip():
            errors.append("University name is required")
        elif len(self.university_name.strip()) < 2:
            errors.append("University name must be at least 2 characters long")
        
        if not self.program_name or not self.program_name.strip():
            errors.append("Program name is required")
        elif len(self.program_name.strip()) < 2:
            errors.append("Program name must be at least 2 characters long")
        
        if not self.intake or not self.intake.strip():
            errors.append("Intake is required")
        elif not self.validate_intake_format(self.intake):
            errors.append("Invalid intake format. Use format like 'Jan 2026', 'Feb 2026'")
        
        if not self.status or not self.status.strip():
            errors.append("Status is required")
        elif self.status not in self.get_valid_statuses():
            errors.append(f"Invalid status. Valid statuses are: {', '.join(self.get_valid_statuses())}")
        
        return errors
