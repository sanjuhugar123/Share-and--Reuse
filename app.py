import os
import random
from datetime import datetime, timedelta
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for, flash,
    session, jsonify, current_app, send_from_directory
)
from werkzeug.utils import secure_filename
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
import json
import urllib.request
import urllib.error

from config import Config
from models import (
    db, User, Organization, Donation, FoodDetail,
    ClothesDetail, DonationAssignment, ReportFeedback
)
from matching import (
    haversine_distance, estimate_transit_time_minutes,
    find_matching_organizations
)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)

    # Auth helper decorators
    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('login', next=request.url))
            return f(*args, **kwargs)
        return decorated_function

    def role_required(allowed_roles):
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if 'user_id' not in session:
                    flash('Please log in first.', 'warning')
                    return redirect(url_for('login'))
                user = User.query.get(session['user_id'])
                if not user or user.role not in allowed_roles:
                    flash('Access denied. You do not have permission for this section.', 'danger')
                    return redirect(url_for('index'))
                return f(*args, **kwargs)
            return decorated_function
        return decorator

    @app.context_processor
    def inject_user():
        current_user = None
        current_org = None
        urgent_count = 0
        if 'user_id' in session:
            current_user = User.query.get(session['user_id'])
            if current_user and current_user.role == 'organization':
                current_org = Organization.query.filter_by(user_id=current_user.id).first()
                # Count active urgent food listings
                now = datetime.utcnow()
                urgent_count = Donation.query.join(FoodDetail).filter(
                    Donation.category == 'food',
                    Donation.status == 'available',
                    FoodDetail.expiry_deadline <= now + timedelta(hours=4),
                    FoodDetail.expiry_deadline > now
                ).count()
        return dict(current_user=current_user, current_org=current_org, urgent_food_count=urgent_count)

    # Utility: Check allowed file extensions
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

    def reset_serializer():
        return URLSafeTimedSerializer(app.config['SECRET_KEY'], salt='password-reset')

    @app.route('/forgot-password', methods=['GET', 'POST'])
    def forgot_password():
        if request.method == 'POST':
            email = request.form.get('email', '').strip().lower()
            user = User.query.filter(db.func.lower(User.email) == email).first()
            if user:
                token = reset_serializer().dumps(user.email)
                reset_url = url_for('reset_password', token=token, _external=True)
                # Local demo flow: show a signed, expiring link. Configure SMTP to email this in production.
                flash('Password reset link (valid for 30 minutes): ' + reset_url, 'info')
            else:
                flash('If an account exists for that email, a reset link has been created.', 'info')
            return redirect(url_for('forgot_password'))
        return render_template('forgot_password.html')

    @app.route('/reset-password/<token>', methods=['GET', 'POST'])
    def reset_password(token):
        try:
            email = reset_serializer().loads(token, max_age=1800)
        except SignatureExpired:
            flash('That reset link has expired. Request a new one.', 'warning')
            return redirect(url_for('forgot_password'))
        except BadSignature:
            flash('That reset link is invalid. Request a new one.', 'danger')
            return redirect(url_for('forgot_password'))
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('Account not found. Request a new reset link.', 'warning')
            return redirect(url_for('forgot_password'))
        if request.method == 'POST':
            password = request.form.get('password', '')
            confirm = request.form.get('confirm_password', '')
            if len(password) < 8:
                flash('Choose a password with at least 8 characters.', 'danger')
            elif password != confirm:
                flash('Passwords do not match.', 'danger')
            else:
                user.set_password(password)
                db.session.commit()
                flash('Password updated. You can now sign in.', 'success')
                return redirect(url_for('login'))
        return render_template('reset_password.html')

    @app.route('/api/classify-food', methods=['POST'])
    @login_required
    @role_required(['donor'])
    def classify_food_image():
        image = request.files.get('image')
        if not image or not image.filename or not allowed_file(image.filename):
            return jsonify(error='Choose a supported image first.'), 400
        endpoint = app.config.get('FOOD_CLASSIFIER_URL')
        if not endpoint:
            return jsonify(error='AI image checking is not configured. Set FOOD_CLASSIFIER_URL and FOOD_CLASSIFIER_TOKEN.'), 503
        payload = image.read()
        if len(payload) > 8 * 1024 * 1024:
            return jsonify(error='Image must be 8 MB or smaller.'), 413
        headers = {'Content-Type': image.mimetype or 'application/octet-stream'}
        token = app.config.get('FOOD_CLASSIFIER_TOKEN')
        if token:
            headers['Authorization'] = 'Bearer ' + token
        try:
            req = urllib.request.Request(endpoint, data=payload, headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=20) as response:
                result = json.loads(response.read().decode('utf-8'))
            # Hugging Face image-classification response: [{label, score}, ...]
            predictions = result if isinstance(result, list) else result.get('predictions', [])
            food_terms = ('food', 'dish', 'meal', 'fruit', 'vegetable', 'bread', 'meat', 'produce', 'grocery', 'pizza', 'salad')
            best = max(predictions, key=lambda item: float(item.get('score', 0)), default={})
            label = str(best.get('label', 'unknown'))
            is_food = any(term in label.lower() for term in food_terms)
            return jsonify(is_food=is_food, label=label, confidence=round(float(best.get('score', 0)), 3))
        except (urllib.error.URLError, TimeoutError, ValueError, TypeError) as exc:
            app.logger.warning('Food classification failed: %s', exc)
            return jsonify(error='AI image check failed. Try again or continue with a manual review.'), 502

    # ==========================================
    # PUBLIC ROUTES
    # ==========================================

    @app.route('/')
    def index():
        # Impact counters
        total_donations = Donation.query.count()
        completed_donations = Donation.query.filter_by(status='completed').count()
        total_food_kg = db.session.query(db.func.sum(Donation.quantity)).filter(
            Donation.category == 'food', Donation.status == 'completed'
        ).scalar() or 0.0
        total_clothes_pcs = db.session.query(db.func.sum(Donation.quantity)).filter(
            Donation.category == 'clothes', Donation.status == 'completed'
        ).scalar() or 0.0
        verified_orgs_count = Organization.query.filter_by(is_verified=True).count()

        # Recent active donations
        recent_donations = Donation.query.filter_by(status='available').order_by(
            Donation.created_at.desc()
        ).limit(6).all()

        return render_template(
            'index.html',
            total_donations=total_donations,
            completed_donations=completed_donations,
            total_food_kg=round(total_food_kg, 1),
            total_clothes_pcs=int(total_clothes_pcs),
            verified_orgs_count=verified_orgs_count,
            recent_donations=recent_donations
        )

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            if user:
                if user.role == 'donor':
                    return redirect(url_for('donor_dashboard'))
                elif user.role == 'organization':
                    return redirect(url_for('org_dashboard'))
                elif user.role == 'admin':
                    return redirect(url_for('admin_dashboard'))

        if request.method == 'POST':
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')

            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                if not user.is_active:
                    flash('Your account has been deactivated. Please contact support.', 'danger')
                    return redirect(url_for('login'))

                session['user_id'] = user.id
                session['user_role'] = user.role
                session['user_name'] = user.full_name
                flash(f'Welcome back, {user.full_name}!', 'success')

                # Redirect based on role
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                if user.role == 'donor':
                    return redirect(url_for('donor_dashboard'))
                elif user.role == 'organization':
                    return redirect(url_for('org_dashboard'))
                elif user.role == 'admin':
                    return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid email or password. Please try again.', 'danger')

        return render_template('login.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            role = request.form.get('role', 'donor')
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            full_name = request.form.get('full_name', '').strip()
            phone = request.form.get('phone', '').strip()
            address = request.form.get('address', '').strip()
            city = request.form.get('city', 'Bagalkote').strip()
            
            try:
                lat = float(request.form.get('latitude', 16.1853))
                lon = float(request.form.get('longitude', 75.6968))
            except ValueError:
                lat, lon = 16.1853, 75.6968

            if User.query.filter_by(email=email).first():
                flash('An account with this email already exists. Please log in.', 'warning')
                return redirect(url_for('register'))

            user = User(
                email=email,
                full_name=full_name,
                phone=phone,
                role=role,
                address=address,
                city=city,
                latitude=lat,
                longitude=lon,
                is_active=True
            )
            user.set_password(password)

            if role == 'donor':
                user.donor_type = request.form.get('donor_type', 'person')
                db.session.add(user)
                db.session.commit()
                flash('Donor registration successful! Please log in.', 'success')
                return redirect(url_for('login'))

            elif role == 'organization':
                db.session.add(user)
                db.session.flush()

                org_name = request.form.get('org_name', full_name).strip()
                org_type = request.form.get('org_type', 'ngo')
                registration_no = request.form.get('registration_no', '').strip()
                description = request.form.get('description', '').strip()
                accepts_food = 'accepts_food' in request.form
                accepts_clothes = 'accepts_clothes' in request.form
                accepts_damaged_clothes = 'accepts_damaged_clothes' in request.form
                capacity_note = request.form.get('capacity_note', '').strip()

                org = Organization(
                    user_id=user.id,
                    org_name=org_name,
                    org_type=org_type,
                    registration_no=registration_no,
                    description=description,
                    accepts_food=accepts_food,
                    accepts_clothes=accepts_clothes,
                    accepts_damaged_clothes=accepts_damaged_clothes,
                    capacity_note=capacity_note,
                    is_verified=False  # Requires admin review
                )
                db.session.add(org)
                db.session.commit()
                flash('Organization registered successfully! It will be reviewed by Admin shortly.', 'info')
                return redirect(url_for('login'))

        return render_template('register.html')

    @app.route('/logout')
    def logout():
        session.clear()
        flash('You have been logged out successfully.', 'info')
        return redirect(url_for('index'))

    # ==========================================
    # DONOR ROUTES
    # ==========================================

    @app.route('/donor/dashboard')
    @login_required
    @role_required(['donor'])
    def donor_dashboard():
        user = User.query.get(session['user_id'])
        donations = Donation.query.filter_by(donor_id=user.id).order_by(
            Donation.created_at.desc()
        ).all()

        total_food_kg = sum(d.quantity for d in donations if d.category == 'food' and d.status == 'completed')
        total_clothes_pcs = sum(d.quantity for d in donations if d.category == 'clothes' and d.status == 'completed')
        active_count = sum(1 for d in donations if d.status in ['available', 'accepted', 'in_transit'])
        completed_count = sum(1 for d in donations if d.status == 'completed')

        return render_template(
            'donor_dashboard.html',
            donations=donations,
            total_food_kg=round(total_food_kg, 1),
            total_clothes_pcs=int(total_clothes_pcs),
            active_count=active_count,
            completed_count=completed_count
        )

    @app.route('/donor/create-donation', methods=['GET', 'POST'])
    @login_required
    @role_required(['donor'])
    def create_donation():
        user = User.query.get(session['user_id'])

        if request.method == 'POST':
            category = request.form.get('category', 'food')
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            quantity = float(request.form.get('quantity', 1.0))
            quantity_unit = request.form.get('quantity_unit', 'kg')
            pickup_address = request.form.get('pickup_address', user.address).strip()
            city = request.form.get('city', user.city).strip()
            
            try:
                lat = float(request.form.get('latitude', user.latitude or 16.1853))
                lon = float(request.form.get('longitude', user.longitude or 75.6968))
            except ValueError:
                lat, lon = 16.1853, 75.6968

            # Handle image upload
            image_url = None
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(f"don_{int(datetime.utcnow().timestamp())}_{file.filename}")
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    image_url = f"/static/uploads/{filename}"

            # Default fallback images if none uploaded
            if not image_url:
                if category == 'food':
                    image_url = 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=600&auto=format&fit=crop&q=80'
                else:
                    image_url = 'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=600&auto=format&fit=crop&q=80'

            # 4-digit pickup OTP verification pin
            verification_pin = str(random.randint(1000, 9999))

            donation = Donation(
                donor_id=user.id,
                title=title,
                category=category,
                description=description,
                quantity=quantity,
                quantity_unit=quantity_unit,
                status='available',
                pickup_address=pickup_address,
                city=city,
                latitude=lat,
                longitude=lon,
                image_url=image_url,
                verification_pin=verification_pin
            )
            db.session.add(donation)
            db.session.flush()

            # Process Food Specifics
            if category == 'food':
                food_type = request.form.get('food_type', 'cooked')
                storage_condition = request.form.get('storage_condition', 'ambient')
                allergen_info = request.form.get('allergen_info', '').strip()
                
                prep_str = request.form.get('preparation_time')
                expiry_str = request.form.get('expiry_deadline')
                
                prep_time = datetime.fromisoformat(prep_str) if prep_str else datetime.utcnow()
                if expiry_str:
                    expiry_deadline = datetime.fromisoformat(expiry_str)
                else:
                    # Default: 4 hours from now for cooked food, 24 hours for others
                    default_hours = 4 if food_type == 'cooked' else 24
                    expiry_deadline = datetime.utcnow() + timedelta(hours=default_hours)

                # Flag as urgent if deadline is within 4 hours
                hours_left = (expiry_deadline - datetime.utcnow()).total_seconds() / 3600.0
                is_urgent = hours_left <= 4.0

                food_detail = FoodDetail(
                    donation_id=donation.id,
                    food_type=food_type,
                    preparation_time=prep_time,
                    expiry_deadline=expiry_deadline,
                    storage_condition=storage_condition,
                    allergen_info=allergen_info,
                    is_urgent=is_urgent
                )
                db.session.add(food_detail)

            # Process Clothes Specifics
            elif category == 'clothes':
                clothes_type = request.form.get('clothes_type', 'mixed')
                condition = request.form.get('condition', 'reusable')
                target_age_group = request.form.get('target_age_group', 'all')
                clean_washed = 'clean_washed' in request.form

                clothes_detail = ClothesDetail(
                    donation_id=donation.id,
                    clothes_type=clothes_type,
                    condition=condition,
                    target_age_group=target_age_group,
                    clean_washed=clean_washed
                )
                db.session.add(clothes_detail)

            db.session.commit()
            flash('Donation created successfully! Finding nearby matching organizations...', 'success')
            return redirect(url_for('nearby_orgs', donation_id=donation.id))

        # Default expiry suggestion (4 hours from now)
        suggested_expiry = (datetime.utcnow() + timedelta(hours=4)).strftime('%Y-%m-%dT%H:%M')
        suggested_prep = datetime.utcnow().strftime('%Y-%m-%dT%H:%M')

        return render_template(
            'create_donation.html',
            user=user,
            suggested_expiry=suggested_expiry,
            suggested_prep=suggested_prep
        )

    @app.route('/donor/donation/<int:donation_id>/nearby')
    @login_required
    def nearby_orgs(donation_id):
        donation = Donation.query.get_or_404(donation_id)
        matches = find_matching_organizations(donation)
        return render_template('nearby_orgs.html', donation=donation, matches=matches)

    @app.route('/donor/donation/<int:donation_id>/request-org/<int:org_id>', methods=['POST'])
    @login_required
    @role_required(['donor'])
    def request_organization(donation_id, org_id):
        donation = Donation.query.get_or_404(donation_id)
        org = Organization.query.get_or_404(org_id)

        if donation.status != 'available':
            flash('This donation is already accepted or in transit.', 'warning')
            return redirect(url_for('donation_detail', donation_id=donation.id))

        # Create or update assignment
        assignment = DonationAssignment.query.filter_by(donation_id=donation.id).first()
        if not assignment:
            assignment = DonationAssignment(
                donation_id=donation.id,
                organization_id=org.id,
                status='assigned',
                notes=f"Direct request initiated by donor to {org.org_name}."
            )
            db.session.add(assignment)
        else:
            assignment.organization_id = org.id
            assignment.status = 'assigned'

        donation.status = 'requested'
        db.session.commit()
        flash(f'Direct pickup request sent to {org.org_name}! They have been notified.', 'success')
        return redirect(url_for('donation_detail', donation_id=donation.id))

    @app.route('/donor/donation/<int:donation_id>/cancel', methods=['POST'])
    @login_required
    def cancel_donation(donation_id):
        donation = Donation.query.get_or_404(donation_id)
        if donation.donor_id != session['user_id'] and session.get('user_role') != 'admin':
            flash('Unauthorized action.', 'danger')
            return redirect(url_for('donor_dashboard'))

        donation.status = 'cancelled'
        db.session.commit()
        flash('Donation has been cancelled.', 'info')
        return redirect(url_for('donor_dashboard'))

    # ==========================================
    # ORGANIZATION ROUTES
    # ==========================================

    @app.route('/organization/dashboard')
    @login_required
    @role_required(['organization'])
    def org_dashboard():
        user = User.query.get(session['user_id'])
        org = Organization.query.filter_by(user_id=user.id).first_or_404()

        category_filter = request.args.get('category', 'all')
        urgency_filter = request.args.get('urgent', 'all')

        # Find all available or requested-to-this-org donations
        query = Donation.query.filter(
            (Donation.status == 'available') |
            ((Donation.status == 'requested') & (Donation.assignment.has(organization_id=org.id)))
        )

        if category_filter == 'food':
            query = query.filter(Donation.category == 'food')
        elif category_filter == 'clothes':
            query = query.filter(Donation.category == 'clothes')

        available_donations = query.order_by(Donation.created_at.desc()).all()

        # Compute distances & suitability for this org
        donation_cards = []
        now = datetime.utcnow()

        for don in available_donations:
            # Check capability match
            if don.category == 'food' and not org.accepts_food:
                continue
            if don.category == 'clothes':
                if don.clothes_detail and don.clothes_detail.condition == 'damaged_recycling':
                    if not (org.accepts_damaged_clothes or org.org_type == 'recycler'):
                        continue
                elif not org.accepts_clothes:
                    continue

            dist = haversine_distance(user.latitude, user.longitude, don.latitude, don.longitude)
            transit_mins = estimate_transit_time_minutes(dist)

            # Urgency check
            is_urgent = False
            hours_left = None
            if don.category == 'food' and don.food_detail:
                diff = (don.food_detail.expiry_deadline - now).total_seconds() / 3600.0
                hours_left = max(0.0, round(diff, 1))
                if hours_left <= 4.0:
                    is_urgent = True

            if urgency_filter == 'yes' and not is_urgent:
                continue

            donation_cards.append({
                'donation': don,
                'distance_km': dist,
                'transit_mins': transit_mins,
                'is_urgent': is_urgent,
                'hours_left': hours_left
            })

        # Sort: Urgent food first, then shortest distance
        donation_cards.sort(key=lambda x: (not x['is_urgent'], x['distance_km']))

        # Org active pickups
        active_pickups_count = DonationAssignment.query.filter(
            DonationAssignment.organization_id == org.id,
            DonationAssignment.status.in_(['accepted', 'in_transit'])
        ).count()

        completed_pickups_count = DonationAssignment.query.filter(
            DonationAssignment.organization_id == org.id,
            DonationAssignment.status == 'completed'
        ).count()

        return render_template(
            'org_dashboard.html',
            org=org,
            donation_cards=donation_cards,
            active_pickups_count=active_pickups_count,
            completed_pickups_count=completed_pickups_count,
            category_filter=category_filter,
            urgency_filter=urgency_filter
        )

    @app.route('/organization/accept-donation/<int:donation_id>', methods=['POST'])
    @login_required
    @role_required(['organization'])
    def accept_donation(donation_id):
        user = User.query.get(session['user_id'])
        org = Organization.query.filter_by(user_id=user.id).first_or_404()
        donation = Donation.query.get_or_404(donation_id)

        if not org.is_verified:
            flash('Your organization is pending verification by Admin. You cannot accept donations yet.', 'warning')
            return redirect(url_for('org_dashboard'))

        if donation.status not in ['available', 'requested']:
            flash('This donation is no longer available.', 'warning')
            return redirect(url_for('org_dashboard'))

        volunteer_name = request.form.get('volunteer_name', user.full_name).strip()
        volunteer_phone = request.form.get('volunteer_phone', user.phone).strip()
        pickup_time_str = request.form.get('pickup_time')
        notes = request.form.get('notes', '').strip()

        if pickup_time_str:
            scheduled_time = datetime.fromisoformat(pickup_time_str)
        else:
            scheduled_time = datetime.utcnow() + timedelta(hours=1)

        assignment = DonationAssignment.query.filter_by(donation_id=donation.id).first()
        if not assignment:
            assignment = DonationAssignment(
                donation_id=donation.id,
                organization_id=org.id
            )
            db.session.add(assignment)

        assignment.organization_id = org.id
        assignment.status = 'accepted'
        assignment.scheduled_pickup_time = scheduled_time
        assignment.volunteer_name = volunteer_name
        assignment.volunteer_phone = volunteer_phone
        assignment.notes = notes

        donation.status = 'accepted'
        db.session.commit()

        flash(f'Donation successfully accepted! Scheduled pickup for {scheduled_time.strftime("%d %b, %I:%M %p")}.', 'success')
        return redirect(url_for('accepted_pickups'))

    @app.route('/organization/pickups')
    @login_required
    @role_required(['organization'])
    def accepted_pickups():
        user = User.query.get(session['user_id'])
        org = Organization.query.filter_by(user_id=user.id).first_or_404()

        assignments = DonationAssignment.query.filter(
            DonationAssignment.organization_id == org.id
        ).order_by(DonationAssignment.created_at.desc()).all()

        return render_template('accepted_pickups.html', assignments=assignments, org=org)

    @app.route('/organization/update-pickup-status/<int:assignment_id>', methods=['POST'])
    @login_required
    @role_required(['organization'])
    def update_pickup_status(assignment_id):
        assignment = DonationAssignment.query.get_or_404(assignment_id)
        new_status = request.form.get('status')
        pin_entered = request.form.get('verification_pin', '').strip()

        if new_status == 'in_transit':
            assignment.status = 'in_transit'
            assignment.donation.status = 'in_transit'
            db.session.commit()
            flash('Status updated: Volunteer is out for pickup!', 'info')

        elif new_status == 'completed':
            # Verify OTP PIN provided by donor
            if pin_entered != assignment.donation.verification_pin:
                flash('Incorrect Verification PIN! Please ask the donor for their 4-digit pickup PIN.', 'danger')
                return redirect(url_for('accepted_pickups'))

            assignment.status = 'completed'
            assignment.actual_pickup_time = datetime.utcnow()
            assignment.donation.status = 'completed'
            assignment.donation.completed_at = datetime.utcnow()
            db.session.commit()
            flash('Donation verified and marked completed! Thank you for reducing waste.', 'success')

        return redirect(url_for('accepted_pickups'))

    # ==========================================
    # DETAILS, HISTORY & CERTIFICATE
    # ==========================================

    @app.route('/donation/<int:donation_id>')
    def donation_detail(donation_id):
        donation = Donation.query.get_or_404(donation_id)
        matches = find_matching_organizations(donation) if donation.status == 'available' else []
        return render_template('donation_detail.html', donation=donation, matches=matches)

    @app.route('/history')
    @login_required
    def donation_history():
        user = User.query.get(session['user_id'])
        if user.role == 'donor':
            donations = Donation.query.filter_by(donor_id=user.id).order_by(Donation.created_at.desc()).all()
        elif user.role == 'organization':
            org = Organization.query.filter_by(user_id=user.id).first()
            if org:
                donations = [a.donation for a in org.assignments]
            else:
                donations = []
        else: # admin
            donations = Donation.query.order_by(Donation.created_at.desc()).all()

        return render_template('donation_history.html', donations=donations)

    @app.route('/certificate/<int:donation_id>')
    @login_required
    def certificate(donation_id):
        donation = Donation.query.get_or_404(donation_id)
        if donation.status != 'completed':
            flash('Certificate is only available for completed donations.', 'info')
            return redirect(url_for('donation_detail', donation_id=donation.id))
        return render_template('certificate.html', donation=donation)

    # ==========================================
    # ADMIN ROUTES
    # ==========================================

    @app.route('/admin/dashboard')
    @login_required
    @role_required(['admin'])
    def admin_dashboard():
        # Summary counts
        total_users = User.query.count()
        total_donors = User.query.filter_by(role='donor').count()
        total_orgs = Organization.query.count()
        pending_orgs = Organization.query.filter_by(is_verified=False).all()
        
        total_donations = Donation.query.count()
        completed_donations = Donation.query.filter_by(status='completed').count()
        food_donations = Donation.query.filter_by(category='food').count()
        clothes_donations = Donation.query.filter_by(category='clothes').count()

        total_food_kg = db.session.query(db.func.sum(Donation.quantity)).filter(
            Donation.category == 'food', Donation.status == 'completed'
        ).scalar() or 0.0

        total_clothes_pcs = db.session.query(db.func.sum(Donation.quantity)).filter(
            Donation.category == 'clothes', Donation.status == 'completed'
        ).scalar() or 0.0

        recent_reports = ReportFeedback.query.order_by(ReportFeedback.created_at.desc()).limit(10).all()
        recent_donations = Donation.query.order_by(Donation.created_at.desc()).limit(10).all()
        users_list = User.query.order_by(User.created_at.desc()).limit(15).all()

        return render_template(
            'admin_dashboard.html',
            total_users=total_users,
            total_donors=total_donors,
            total_orgs=total_orgs,
            pending_orgs=pending_orgs,
            total_donations=total_donations,
            completed_donations=completed_donations,
            food_donations=food_donations,
            clothes_donations=clothes_donations,
            total_food_kg=round(total_food_kg, 1),
            total_clothes_pcs=int(total_clothes_pcs),
            recent_reports=recent_reports,
            recent_donations=recent_donations,
            users_list=users_list
        )

    @app.route('/admin/verify-org/<int:org_id>', methods=['POST'])
    @login_required
    @role_required(['admin'])
    def verify_organization(org_id):
        org = Organization.query.get_or_404(org_id)
        action = request.form.get('action', 'approve')

        if action == 'approve':
            org.is_verified = True
            org.verified_at = datetime.utcnow()
            flash(f'Organization "{org.org_name}" has been verified and approved!', 'success')
        elif action == 'reject':
            org.is_verified = False
            flash(f'Organization "{org.org_name}" verification request rejected.', 'warning')

        db.session.commit()
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/toggle-user/<int:user_id>', methods=['POST'])
    @login_required
    @role_required(['admin'])
    def toggle_user(user_id):
        user = User.query.get_or_404(user_id)
        if user.role == 'admin':
            flash('Cannot modify admin status.', 'danger')
            return redirect(url_for('admin_dashboard'))

        user.is_active = not user.is_active
        db.session.commit()
        status_str = "activated" if user.is_active else "deactivated"
        flash(f'User {user.full_name} has been {status_str}.', 'info')
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/resolve-report/<int:report_id>', methods=['POST'])
    @login_required
    @role_required(['admin'])
    def resolve_report(report_id):
        report = ReportFeedback.query.get_or_404(report_id)
        response_text = request.form.get('admin_response', 'Addressed by admin.').strip()

        report.status = 'resolved'
        report.admin_response = response_text
        db.session.commit()
        flash('Report resolved and response recorded.', 'success')
        return redirect(url_for('admin_dashboard'))

    # ==========================================
    # REPORTING & COMPLAINTS
    # ==========================================

    @app.route('/report/new', methods=['GET', 'POST'])
    @login_required
    def report_issue():
        if request.method == 'POST':
            report_type = request.form.get('report_type', 'complaint')
            subject = request.form.get('subject', '').strip()
            message = request.form.get('message', '').strip()
            donation_id = request.form.get('donation_id')

            report = ReportFeedback(
                reporter_id=session['user_id'],
                donation_id=int(donation_id) if donation_id else None,
                report_type=report_type,
                subject=subject,
                message=message,
                status='pending'
            )
            db.session.add(report)
            db.session.commit()
            flash('Your report/feedback has been submitted to the admin team.', 'success')
            return redirect(url_for('index'))

        donation_id = request.args.get('donation_id')
        return render_template('report_issue.html', donation_id=donation_id)

    # ==========================================
    # JSON APIs (For Leaflet Map & Realtime feeds)
    # ==========================================

    @app.route('/api/organizations/locations')
    def api_org_locations():
        orgs = Organization.query.join(User).filter(
            Organization.is_verified == True,
            User.is_active == True
        ).all()
        return jsonify([org.to_dict() for org in orgs])

    @app.route('/api/donations/locations')
    def api_donation_locations():
        donations = Donation.query.filter_by(status='available').all()
        data = []
        for d in donations:
            data.append({
                'id': d.id,
                'title': d.title,
                'category': d.category,
                'quantity': f"{d.quantity} {d.quantity_unit}",
                'latitude': d.latitude,
                'longitude': d.longitude,
                'address': d.pickup_address,
                'city': d.city,
                'image_url': d.image_url,
                'is_urgent': d.food_detail.is_urgent if d.food_detail 
            else False
            })
        return jsonify(data)

    return app



# Vercel entry point
app = create_app()

if __name__ == "__main__":
    app.run(
        debug=True,
        use_reloader=False,
        host='0.0.0.0',
        port=5000
    )
