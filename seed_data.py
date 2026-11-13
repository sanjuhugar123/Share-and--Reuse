from datetime import datetime, timedelta
from app import create_app
from models import db, User, Organization, Donation, FoodDetail, ClothesDetail, DonationAssignment, ReportFeedback

def seed_database():
    app = create_app()
    with app.app_context():
        # Clear existing tables
        db.drop_all()
        db.create_all()
        
        print("[*] Seeding Users...")
        
        # 1. Admin
        admin = User(
            email='admin@shareandreuse.org',
            full_name='System Administrator',
            phone='9876543210',
            role='admin',
            donor_type=None,
            address='Administrative Hub, DC Office Road',
            city='Bagalkote',
            latitude=16.1853,
            longitude=75.6968,
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)

        # 2. Donors
        donor1 = User(
            email='basaveshwar.hotel@gmail.com',
            full_name='Hotel Basaveshwar Grand',
            phone='9448123456',
            role='donor',
            donor_type='hotel',
            address='Near Bus Stand, Station Road',
            city='Bagalkote',
            latitude=16.1820,
            longitude=75.6940,
            is_active=True
        )
        donor1.set_password('donor123')
        db.session.add(donor1)

        donor2 = User(
            email='royalpalace.events@gmail.com',
            full_name='Royal Palace Function Hall',
            phone='9880123987',
            role='donor',
            donor_type='function_hall',
            address='Vidyagiri 4th Cross',
            city='Bagalkote',
            latitude=16.1750,
            longitude=75.6880,
            is_active=True
        )
        donor2.set_password('donor123')
        db.session.add(donor2)

        donor3 = User(
            email='bvvs.hostel@bvvs.edu',
            full_name='BVVS Campus Central Mess',
            phone='9900554433',
            role='donor',
            donor_type='college',
            address='BVV Sangha Campus, Vidyagiri',
            city='Bagalkote',
            latitude=16.1720,
            longitude=75.6850,
            is_active=True
        )
        donor3.set_password('donor123')
        db.session.add(donor3)

        donor4 = User(
            email='rajesh.sharma@gmail.com',
            full_name='Rajesh K. Sharma',
            phone='9741238901',
            role='donor',
            donor_type='person',
            address='House #42, Sector 8, Navanagar',
            city='Bagalkote',
            latitude=16.1680,
            longitude=75.6600,
            is_active=True
        )
        donor4.set_password('donor123')
        db.session.add(donor4)

        # 3. Organizations (Users + Org profiles)
        # Org 1: Orphanage
        org_user1 = User(
            email='snehadheepa.orphanage@gmail.com',
            full_name='Sneha Deepa Children Home',
            phone='9844001122',
            role='organization',
            address='Plot 15, Sector 12, Navanagar',
            city='Bagalkote',
            latitude=16.1640,
            longitude=75.6580,
            is_active=True
        )
        org_user1.set_password('org123')
        db.session.add(org_user1)
        db.session.flush()

        org1 = Organization(
            user_id=org_user1.id,
            org_name='Sneha Deepa Children Home',
            org_type='orphanage',
            registration_no='TR-BGK-2018-094',
            description='Dedicated shelter supporting 65 orphaned and vulnerable children with nutrition, education, and healthcare.',
            accepts_food=True,
            accepts_clothes=True,
            accepts_damaged_clothes=False,
            capacity_note='65 children dining capacity',
            is_verified=True,
            verified_at=datetime.utcnow() - timedelta(days=60)
        )
        db.session.add(org1)

        # Org 2: Food Distribution Network
        org_user2 = User(
            email='annapurna.seva@gmail.com',
            full_name='Annapurna Food Redistribution Network',
            phone='9740118833',
            role='organization',
            address='APMC Yard Road, Ward 5',
            city='Bagalkote',
            latitude=16.1890,
            longitude=75.7010,
            is_active=True
        )
        org_user2.set_password('org123')
        db.session.add(org_user2)
        db.session.flush()

        org2 = Organization(
            user_id=org_user2.id,
            org_name='Annapurna Food Redistribution Network',
            org_type='food_bank',
            registration_no='NGO-BGK-2020-512',
            description='Mobile food rescue team equipped with insulated food transport vans. Serving slums and daily wage workers.',
            accepts_food=True,
            accepts_clothes=False,
            accepts_damaged_clothes=False,
            capacity_note='Can collect and redistribute up to 350 kg food daily',
            is_verified=True,
            verified_at=datetime.utcnow() - timedelta(days=45)
        )
        db.session.add(org2)

        # Org 3: Old Age Home
        org_user3 = User(
            email='mathruchhaya.elderly@gmail.com',
            full_name='Mathru Chhaya Vrudhashrama',
            phone='9449887766',
            role='organization',
            address='Near Kalidas Nagar, Vidyagiri',
            city='Bagalkote',
            latitude=16.1770,
            longitude=75.6900,
            is_active=True
        )
        org_user3.set_password('org123')
        db.session.add(org_user3)
        db.session.flush()

        org3 = Organization(
            user_id=org_user3.id,
            org_name='Mathru Chhaya Old Age Home',
            org_type='old_age_home',
            registration_no='TR-BGK-2015-112',
            description='Provides peaceful, caring residential sanctuary for 48 senior citizens.',
            accepts_food=True,
            accepts_clothes=True,
            accepts_damaged_clothes=False,
            capacity_note='48 senior residents',
            is_verified=True,
            verified_at=datetime.utcnow() - timedelta(days=90)
        )
        db.session.add(org3)

        # Org 4: Textile Recycling Organization
        org_user4 = User(
            email='greenweave.recycling@gmail.com',
            full_name='GreenWeave Upcycling & Textile Recycling',
            phone='9988223344',
            role='organization',
            address='Plot 88, KIADB Industrial Area',
            city='Bagalkote',
            latitude=16.1950,
            longitude=75.7150,
            is_active=True
        )
        org_user4.set_password('org123')
        db.session.add(org_user4)
        db.session.flush()

        org4 = Organization(
            user_id=org_user4.id,
            org_name='GreenWeave Upcycling & Textile Recycling',
            org_type='recycler',
            registration_no='MSME-KA-02-0045182',
            description='Eco-friendly textile recycling unit transforming torn/scrap fabrics into industrial mats, insulation pads, and upcycled bags.',
            accepts_food=False,
            accepts_clothes=True,
            accepts_damaged_clothes=True,  # Key for damaged clothes!
            capacity_note='500 kg weekly processing capacity',
            is_verified=True,
            verified_at=datetime.utcnow() - timedelta(days=30)
        )
        db.session.add(org4)

        # Org 5: Pending NGO for Admin Verification demo
        org_user5 = User(
            email='karuna.seva@outlook.com',
            full_name='Karuna Seva Rural Trust',
            phone='9123456780',
            role='organization',
            address='Cross 3, Extension Colony, Navanagar',
            city='Bagalkote',
            latitude=16.1600,
            longitude=75.6520,
            is_active=True
        )
        org_user5.set_password('org123')
        db.session.add(org_user5)
        db.session.flush()

        org5 = Organization(
            user_id=org_user5.id,
            org_name='Karuna Seva Rural Trust',
            org_type='ngo',
            registration_no='TR-KA-2026-PENDING-08',
            description='Grassroots social service trust active in village welfare and child schooling support.',
            accepts_food=True,
            accepts_clothes=True,
            accepts_damaged_clothes=False,
            capacity_note='Serves around 80 rural families',
            is_verified=False,  # Unverified!
            verified_at=None
        )
        db.session.add(org5)

        db.session.commit()
        print("[*] Seeding Donations & Details...")

        now = datetime.utcnow()

        # Donation 1: Urgent Surplus Food (Wedding/Hotel surplus - expires in 3 hours!)
        d1 = Donation(
            donor_id=donor1.id,
            title='Surplus Veg Pulao, Dal & Paneer Curry',
            category='food',
            description='Freshly cooked hot meals from lunch banquet. Kept in clean food-grade hot cases. Extremely hygienic and nutritious.',
            quantity=18.0,
            quantity_unit='kg',
            status='available',
            pickup_address='Hotel Basaveshwar Grand, Station Road',
            city='Bagalkote',
            latitude=16.1820,
            longitude=75.6940,
            image_url='https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=600&auto=format&fit=crop&q=80',
            verification_pin='8492',
            created_at=now - timedelta(minutes=40)
        )
        db.session.add(d1)
        db.session.flush()

        fd1 = FoodDetail(
            donation_id=d1.id,
            food_type='cooked',
            preparation_time=now - timedelta(hours=2),
            expiry_deadline=now + timedelta(hours=3, minutes=30),  # < 4 hours remaining -> Urgent!
            storage_condition='hot',
            allergen_info='Contains dairy (paneer). Vegetarian only.',
            is_urgent=True
        )
        db.session.add(fd1)

        # Donation 2: Packed food items / dry ration from College Mess
        d2 = Donation(
            donor_id=donor3.id,
            title='Unopened Packaged Rice, Wheat Flour & Biscuits',
            category='food',
            description='Surplus dry grocery items and biscuit cartons stored safely before college vacation break.',
            quantity=35.0,
            quantity_unit='kg',
            status='available',
            pickup_address='BVVS Central Mess Store, Vidyagiri',
            city='Bagalkote',
            latitude=16.1720,
            longitude=75.6850,
            image_url='https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=600&auto=format&fit=crop&q=80',
            verification_pin='4321',
            created_at=now - timedelta(hours=3)
        )
        db.session.add(d2)
        db.session.flush()

        fd2 = FoodDetail(
            donation_id=d2.id,
            food_type='packaged',
            preparation_time=now - timedelta(days=2),
            expiry_deadline=now + timedelta(days=15),
            storage_condition='ambient',
            allergen_info='Gluten (Wheat)',
            is_urgent=False
        )
        db.session.add(fd2)

        # Donation 3: Reusable Clothes for Children & Adults
        d3 = Donation(
            donor_id=donor4.id,
            title='Clean Children Sweaters, Jackets & T-Shirts',
            category='clothes',
            description='Gentle used winter sweaters, hoodies, and t-shirts for ages 5-14. All items washed, sanitized, and neatly folded in 2 bags.',
            quantity=28.0,
            quantity_unit='pieces',
            status='available',
            pickup_address='House #42, Sector 8, Navanagar',
            city='Bagalkote',
            latitude=16.1680,
            longitude=75.6600,
            image_url='https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=600&auto=format&fit=crop&q=80',
            verification_pin='7723',
            created_at=now - timedelta(hours=5)
        )
        db.session.add(d3)
        db.session.flush()

        cd3 = ClothesDetail(
            donation_id=d3.id,
            clothes_type='kids',
            condition='reusable',
            target_age_group='children',
            clean_washed=True
        )
        db.session.add(cd3)

        # Donation 4: Damaged / Scrap Textiles from Function Hall (Target for Recycler)
        d4 = Donation(
            donor_id=donor2.id,
            title='Torn Stage Drapes, Fabric Cuts & Stage Linen Scrap',
            category='clothes',
            description='Surplus damaged stage backdrop fabrics, torn drapes, and linen scrap not suitable for wear. Clean but damaged, ideal for textile recycling/upcycling.',
            quantity=45.0,
            quantity_unit='kg',
            status='available',
            pickup_address='Royal Palace Function Hall, Vidyagiri 4th Cross',
            city='Bagalkote',
            latitude=16.1750,
            longitude=75.6880,
            image_url='https://images.unsplash.com/photo-1558769132-cb1aea458c5e?w=600&auto=format&fit=crop&q=80',
            verification_pin='9012',
            created_at=now - timedelta(hours=6)
        )
        db.session.add(d4)
        db.session.flush()

        cd4 = ClothesDetail(
            donation_id=d4.id,
            clothes_type='mixed',
            condition='damaged_recycling',
            target_age_group='all',
            clean_washed=True
        )
        db.session.add(cd4)

        # Donation 5: In-Transit / Accepted Donation (For showing active pickups in Org Dashboard)
        d5 = Donation(
            donor_id=donor2.id,
            title='Dinner Buffet Surplus - Chapati, Sabzi & Kheer',
            category='food',
            description='Surplus from family reception dinner. 40 servings packed in aluminium foil trays.',
            quantity=15.0,
            quantity_unit='kg',
            status='accepted',
            pickup_address='Royal Palace Function Hall, Vidyagiri 4th Cross',
            city='Bagalkote',
            latitude=16.1750,
            longitude=75.6880,
            image_url='https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=600&auto=format&fit=crop&q=80',
            verification_pin='3658',
            created_at=now - timedelta(hours=1, minutes=30)
        )
        db.session.add(d5)
        db.session.flush()

        fd5 = FoodDetail(
            donation_id=d5.id,
            food_type='cooked',
            preparation_time=now - timedelta(hours=3),
            expiry_deadline=now + timedelta(hours=4),
            storage_condition='hot',
            allergen_info='Milk / Dairy',
            is_urgent=True
        )
        db.session.add(fd5)

        assign5 = DonationAssignment(
            donation_id=d5.id,
            organization_id=org2.id,  # Annapurna Food Network
            status='accepted',
            scheduled_pickup_time=now + timedelta(minutes=45),
            volunteer_name='Ramesh Patil',
            volunteer_phone='9740118833',
            notes='Van #KA-29-M-1402 dispatched with thermal containers.'
        )
        db.session.add(assign5)

        # Donation 6: Completed Donation (For Donation History & Impact Certificate)
        d6 = Donation(
            donor_id=donor1.id,
            title='Fresh Morning Bakery Buns, Bread & Sandwiches',
            category='food',
            description='Daily fresh morning stock excess. Distributed successfully to children home.',
            quantity=12.0,
            quantity_unit='kg',
            status='completed',
            pickup_address='Hotel Basaveshwar Grand, Station Road',
            city='Bagalkote',
            latitude=16.1820,
            longitude=75.6940,
            image_url='https://images.unsplash.com/photo-1509440159596-0249088772ff?w=600&auto=format&fit=crop&q=80',
            verification_pin='5519',
            created_at=now - timedelta(days=2),
            completed_at=now - timedelta(days=2, hours=-2)
        )
        db.session.add(d6)
        db.session.flush()

        fd6 = FoodDetail(
            donation_id=d6.id,
            food_type='bakery',
            preparation_time=now - timedelta(days=2, hours=3),
            expiry_deadline=now - timedelta(days=1),
            storage_condition='ambient',
            allergen_info='Wheat/Gluten',
            is_urgent=False
        )
        db.session.add(fd6)

        assign6 = DonationAssignment(
            donation_id=d6.id,
            organization_id=org1.id,  # Sneha Deepa Children Home
            status='completed',
            scheduled_pickup_time=now - timedelta(days=2, hours=1),
            actual_pickup_time=now - timedelta(days=2),
            volunteer_name='Sunita M.',
            volunteer_phone='9844001122',
            notes='Successfully picked up and served as evening snacks to all 65 children.'
        )
        db.session.add(assign6)

        # Donation 7: Completed Clothes Donation
        d7 = Donation(
            donor_id=donor4.id,
            title='Sarees, Dhotis and Blankets for Senior Citizens',
            category='clothes',
            description='Donated gently worn traditional attire and 15 warm blankets for elderly care.',
            quantity=25.0,
            quantity_unit='pieces',
            status='completed',
            pickup_address='House #42, Sector 8, Navanagar',
            city='Bagalkote',
            latitude=16.1680,
            longitude=75.6600,
            image_url='https://images.unsplash.com/photo-1544816155-12df9643f363?w=600&auto=format&fit=crop&q=80',
            verification_pin='2290',
            created_at=now - timedelta(days=5),
            completed_at=now - timedelta(days=5, hours=-3)
        )
        db.session.add(d7)
        db.session.flush()

        cd7 = ClothesDetail(
            donation_id=d7.id,
            clothes_type='winterwear',
            condition='reusable',
            target_age_group='elderly',
            clean_washed=True
        )
        db.session.add(cd7)

        assign7 = DonationAssignment(
            donation_id=d7.id,
            organization_id=org3.id, # Mathru Chhaya
            status='completed',
            scheduled_pickup_time=now - timedelta(days=5, hours=2),
            actual_pickup_time=now - timedelta(days=5, hours=1),
            volunteer_name='Anand Kulkarni',
            volunteer_phone='9449887766',
            notes='All blankets distributed to senior residents before winter nights.'
        )
        db.session.add(assign7)

        # Add sample feedback/complaint for Admin to view and manage
        rep1 = ReportFeedback(
            reporter_id=donor1.id,
            reported_user_id=org_user2.id,
            donation_id=d5.id,
            report_type='feedback',
            subject='Fast and respectful volunteer team',
            message='The volunteer Ramesh arrived promptly with proper sanitization boxes. Excellent communication!',
            status='resolved',
            admin_response='Thank you for acknowledging Annapurna Network volunteers!',
            created_at=now - timedelta(days=1)
        )
        db.session.add(rep1)

        rep2 = ReportFeedback(
            reporter_id=org_user1.id,
            reported_user_id=None,
            donation_id=None,
            report_type='complaint',
            subject='Need larger capacity refrigerated storage vehicle',
            message='Requesting admin coordination to connect us with refrigerated van logistics for hot summer days.',
            status='pending',
            created_at=now - timedelta(hours=4)
        )
        db.session.add(rep2)

        db.session.commit()
        print("[SUCCESS] Database successfully initialized and seeded with rich test data!")

if __name__ == '__main__':
    seed_database()
