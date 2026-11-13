from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'donor', 'organization', 'admin'
    
    # Specific to Donors: 'person', 'hotel', 'function_hall', 'college', 'company'
    donor_type = db.Column(db.String(50), nullable=True)
    
    # Location
    address = db.Column(db.String(255), nullable=False, default='')
    city = db.Column(db.String(100), nullable=False, default='Bagalkote')
    latitude = db.Column(db.Float, nullable=True, default=16.1853)   # Default Bagalkote coords
    longitude = db.Column(db.Float, nullable=True, default=75.6968)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    donations = db.relationship('Donation', backref='donor', lazy=True, cascade='all, delete-orphan')
    organization = db.relationship('Organization', backref='user', uselist=False, cascade='all, delete-orphan')
    reports_submitted = db.relationship('ReportFeedback', foreign_keys='ReportFeedback.reporter_id', backref='reporter', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'role': self.role,
            'donor_type': self.donor_type,
            'address': self.address,
            'city': self.city,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'is_active': self.is_active
        }


class Organization(db.Model):
    __tablename__ = 'organizations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    org_name = db.Column(db.String(150), nullable=False)
    # Types: 'ngo', 'orphanage', 'old_age_home', 'food_bank', 'recycler'
    org_type = db.Column(db.String(50), nullable=False)
    registration_no = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Acceptance criteria
    accepts_food = db.Column(db.Boolean, default=True)
    accepts_clothes = db.Column(db.Boolean, default=True)
    # Important: Damaged clothes routed to recycling / upcycling
    accepts_damaged_clothes = db.Column(db.Boolean, default=False)
    
    capacity_note = db.Column(db.String(255), nullable=True) # e.g. "Can serve up to 100 people per day"
    
    is_verified = db.Column(db.Boolean, default=False)  # Admin verifies
    verified_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    assignments = db.relationship('DonationAssignment', backref='organization', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'org_name': self.org_name,
            'org_type': self.org_type,
            'registration_no': self.registration_no,
            'description': self.description,
            'accepts_food': self.accepts_food,
            'accepts_clothes': self.accepts_clothes,
            'accepts_damaged_clothes': self.accepts_damaged_clothes,
            'capacity_note': self.capacity_note,
            'is_verified': self.is_verified,
            'city': self.user.city if self.user else '',
            'address': self.user.address if self.user else '',
            'phone': self.user.phone if self.user else '',
            'latitude': self.user.latitude if self.user else 0.0,
            'longitude': self.user.longitude if self.user else 0.0
        }


class Donation(db.Model):
    __tablename__ = 'donations'
    
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(20), nullable=False)  # 'food' or 'clothes'
    description = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    quantity_unit = db.Column(db.String(50), nullable=False)  # 'kg', 'servings', 'pieces', 'boxes'
    
    # Status lifecycle: 'available', 'accepted', 'in_transit', 'completed', 'cancelled', 'expired'
    status = db.Column(db.String(30), default='available', index=True)
    
    pickup_address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False, default='Bagalkote')
    latitude = db.Column(db.Float, nullable=False, default=16.1853)
    longitude = db.Column(db.Float, nullable=False, default=75.6968)
    image_url = db.Column(db.String(255), nullable=True)
    
    # 4-digit verification PIN generated for secure physical pickup confirmation
    verification_pin = db.Column(db.String(10), nullable=False, default='1234')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Detailed category relations
    food_detail = db.relationship('FoodDetail', backref='donation', uselist=False, cascade='all, delete-orphan')
    clothes_detail = db.relationship('ClothesDetail', backref='donation', uselist=False, cascade='all, delete-orphan')
    assignment = db.relationship('DonationAssignment', backref='donation', uselist=False, cascade='all, delete-orphan')

    def is_food(self):
        return self.category == 'food'
        
    def is_clothes(self):
        return self.category == 'clothes'


class FoodDetail(db.Model):
    __tablename__ = 'food_details'
    
    id = db.Column(db.Integer, primary_key=True)
    donation_id = db.Column(db.Integer, db.ForeignKey('donations.id', ondelete='CASCADE'), nullable=False, unique=True)
    # 'cooked', 'packaged', 'bakery', 'raw_produce'
    food_type = db.Column(db.String(50), nullable=False)
    preparation_time = db.Column(db.DateTime, nullable=True)
    expiry_deadline = db.Column(db.DateTime, nullable=False)  # Key for urgent food matching
    # 'hot', 'ambient', 'refrigerated', 'frozen'
    storage_condition = db.Column(db.String(50), nullable=False, default='ambient')
    allergen_info = db.Column(db.String(255), nullable=True)
    is_urgent = db.Column(db.Boolean, default=False)
    
    @property
    def hours_remaining(self):
        if not self.expiry_deadline:
            return 0
        diff = self.expiry_deadline - datetime.utcnow()
        hours = diff.total_seconds() / 3600.0
        return max(0.0, round(hours, 1))

    @property
    def is_expired(self):
        if not self.expiry_deadline:
            return False
        return datetime.utcnow() > self.expiry_deadline


class ClothesDetail(db.Model):
    __tablename__ = 'clothes_details'
    
    id = db.Column(db.Integer, primary_key=True)
    donation_id = db.Column(db.Integer, db.ForeignKey('donations.id', ondelete='CASCADE'), nullable=False, unique=True)
    # 'men', 'women', 'kids', 'winterwear', 'mixed'
    clothes_type = db.Column(db.String(50), nullable=False)
    # 'reusable' (good for NGOs/Orphanages) or 'damaged_recycling' (for Recycling organizations)
    condition = db.Column(db.String(50), nullable=False, default='reusable')
    target_age_group = db.Column(db.String(50), nullable=False, default='all')
    clean_washed = db.Column(db.Boolean, default=True)


class DonationAssignment(db.Model):
    __tablename__ = 'donation_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    donation_id = db.Column(db.Integer, db.ForeignKey('donations.id', ondelete='CASCADE'), nullable=False, unique=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    # 'assigned', 'accepted', 'in_transit', 'completed', 'rejected'
    status = db.Column(db.String(30), default='accepted')
    scheduled_pickup_time = db.Column(db.DateTime, nullable=True)
    actual_pickup_time = db.Column(db.DateTime, nullable=True)
    volunteer_name = db.Column(db.String(100), nullable=True)
    volunteer_phone = db.Column(db.String(20), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ReportFeedback(db.Model):
    __tablename__ = 'reports_feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    reported_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    donation_id = db.Column(db.Integer, db.ForeignKey('donations.id', ondelete='SET NULL'), nullable=True)
    report_type = db.Column(db.String(50), nullable=False)  # 'complaint', 'food_quality', 'no_show', 'feedback'
    subject = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'resolved', 'dismissed'
    admin_response = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
