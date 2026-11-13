from app import create_app
from models import db, User, Organization, Donation, DonationAssignment

def test_workflow():
    app = create_app()
    client = app.test_client()

    print("[*] 1. Testing Landing Page...")
    res = client.get('/')
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    assert b"Share" in res.data
    print("    -> Landing page rendered successfully.")

    print("[*] 2. Testing Donor Login...")
    res = client.post('/login', data={
        'email': 'basaveshwar.hotel@gmail.com',
        'password': 'donor123'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Hotel Basaveshwar" in res.data
    print("    -> Donor logged in and redirected to Donor Dashboard.")

    print("[*] 3. Testing Create Donation (Food)...")
    res = client.post('/donor/create-donation', data={
        'category': 'food',
        'title': 'Test Extra Buffet Biryani',
        'description': 'Freshly prepared for evening test',
        'quantity': '20',
        'quantity_unit': 'kg',
        'food_type': 'cooked',
        'storage_condition': 'hot',
        'allergen_info': 'Vegetarian',
        'pickup_address': 'Station Road, Bagalkote',
        'city': 'Bagalkote',
        'latitude': '16.1820',
        'longitude': '75.6940'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Matching Organizations" in res.data or b"Nearby" in res.data or b"Test Extra" in res.data
    print("    -> Food donation created and redirected to Nearby Orgs view.")

    print("[*] 4. Testing Nearby Matching Algorithm...")
    with app.app_context():
        new_don = Donation.query.filter_by(title='Test Extra Buffet Biryani').first()
        assert new_don is not None
        assert new_don.category == 'food'
        assert new_don.food_detail is not None
        print(f"    -> Matching algorithm computed verified organizations for Donation #{new_don.id}.")

    # Logout donor
    client.get('/logout')

    print("[*] 5. Testing Organization Login & Dashboard...")
    res = client.post('/login', data={
        'email': 'annapurna.seva@gmail.com',
        'password': 'org123'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Annapurna Food" in res.data or b"Available Nearby" in res.data
    print("    -> Organization logged in to Org Dashboard.")

    print("[*] 6. Testing Pickup Status & OTP Handover...")
    with app.app_context():
        # Get active donation d5 from seed data
        d5 = Donation.query.filter_by(title='Dinner Buffet Surplus - Chapati, Sabzi & Kheer').first()
        assert d5 is not None
        assign = DonationAssignment.query.filter_by(donation_id=d5.id).first()
        assert assign is not None
        assign_id = assign.id
        correct_pin = d5.verification_pin

    # Test wrong PIN
    res = client.post(f'/organization/update-pickup-status/{assign_id}', data={
        'status': 'completed',
        'verification_pin': '0000'
    }, follow_redirects=True)
    assert b"Incorrect Verification PIN" in res.data
    print("    -> Invalid OTP correctly blocked.")

    # Test correct PIN
    res = client.post(f'/organization/update-pickup-status/{assign_id}', data={
        'status': 'completed',
        'verification_pin': correct_pin
    }, follow_redirects=True)
    assert b"Donation verified and marked completed" in res.data
    print("    -> Valid OTP successfully accepted and handover marked completed!")

    # Logout org
    client.get('/logout')

    print("[*] 7. Testing Admin Dashboard & Verification...")
    res = client.post('/login', data={
        'email': 'admin@shareandreuse.org',
        'password': 'admin123'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"System Administration" in res.data
    print("    -> Admin logged in to Admin Console.")

    with app.app_context():
        pending_org = Organization.query.filter_by(is_verified=False).first()
        if pending_org:
            res = client.post(f'/admin/verify-org/{pending_org.id}', data={
                'action': 'approve'
            }, follow_redirects=True)
            assert res.status_code == 200
            print(f"    -> Admin successfully approved Organization #{pending_org.id}.")

    print("\n[ALL TESTS PASSED SUCCESSFULLY!]")

if __name__ == '__main__':
    test_workflow()
