-- =====================================================================
-- SHARE & REUSE - MySQL Sample Seed Data Script
-- Location: Bagalkote & Surroundings, Karnataka
-- Passwords:
--   admin@shareandreuse.org       -> admin123
--   basaveshwar.hotel@gmail.com   -> donor123
--   royalpalace.events@gmail.com  -> donor123
--   bvvs.hostel@bvvs.edu          -> donor123
--   rajesh.sharma@gmail.com       -> donor123
--   snehadheepa.orphanage@gmail.com -> org123
--   annapurna.seva@gmail.com      -> org123
--   mathruchhaya.elderly@gmail.com -> org123
--   greenweave.recycling@gmail.com -> org123
-- =====================================================================

USE share_and_reuse;

-- 1. Insert Users
INSERT INTO users (id, email, password_hash, full_name, phone, role, donor_type, address, city, latitude, longitude, is_active)
VALUES 
(1, 'admin@shareandreuse.org', 'scrypt:32768:8:1$7f6a70a831d3ba75$e80b271d184eb430d88b48bb13b3558f6236b5ec6324021262d1645e99818ce0bb60cf1c305c21dfba14cff8cbf2cf847bc06d5c64372e93540e1b6f654b73b2', 'System Administrator', '9876543210', 'admin', NULL, 'Administrative Hub, DC Office Road', 'Bagalkote', 16.185300, 75.696800, 1),
(2, 'basaveshwar.hotel@gmail.com', 'scrypt:32768:8:1$7f6a70a831d3ba75$e80b271d184eb430d88b48bb13b3558f6236b5ec6324021262d1645e99818ce0bb60cf1c305c21dfba14cff8cbf2cf847bc06d5c64372e93540e1b6f654b73b2', 'Hotel Basaveshwar Grand', '9448123456', 'donor', 'hotel', 'Near Bus Stand, Station Road', 'Bagalkote', 16.182000, 75.694000, 1),
(3, 'royalpalace.events@gmail.com', 'scrypt:32768:8:1$7f6a70a831d3ba75$e80b271d184eb430d88b48bb13b3558f6236b5ec6324021262d1645e99818ce0bb60cf1c305c21dfba14cff8cbf2cf847bc06d5c64372e93540e1b6f654b73b2', 'Royal Palace Function Hall', '9880123987', 'donor', 'function_hall', 'Vidyagiri 4th Cross', 'Bagalkote', 16.175000, 75.688000, 1),
(4, 'bvvs.hostel@bvvs.edu', 'scrypt:32768:8:1$7f6a70a831d3ba75$e80b271d184eb430d88b48bb13b3558f6236b5ec6324021262d1645e99818ce0bb60cf1c305c21dfba14cff8cbf2cf847bc06d5c64372e93540e1b6f654b73b2', 'BVVS Campus Central Mess', '9900554433', 'donor', 'college', 'BVV Sangha Campus, Vidyagiri', 'Bagalkote', 16.172000, 75.685000, 1),
(5, 'rajesh.sharma@gmail.com', 'scrypt:32768:8:1$7f6a70a831d3ba75$e80b271d184eb430d88b48bb13b3558f6236b5ec6324021262d1645e99818ce0bb60cf1c305c21dfba14cff8cbf2cf847bc06d5c64372e93540e1b6f654b73b2', 'Rajesh K. Sharma', '9741238901', 'donor', 'person', 'House #42, Sector 8, Navanagar', 'Bagalkote', 16.168000, 75.660000, 1),
(6, 'snehadheepa.orphanage@gmail.com', 'scrypt:32768:8:1$7f6a70a831d3ba75$e80b271d184eb430d88b48bb13b3558f6236b5ec6324021262d1645e99818ce0bb60cf1c305c21dfba14cff8cbf2cf847bc06d5c64372e93540e1b6f654b73b2', 'Sneha Deepa Children Home', '9844001122', 'organization', NULL, 'Plot 15, Sector 12, Navanagar', 'Bagalkote', 16.164000, 75.658000, 1),
(7, 'annapurna.seva@gmail.com', 'scrypt:32768:8:1$7f6a70a831d3ba75$e80b271d184eb430d88b48bb13b3558f6236b5ec6324021262d1645e99818ce0bb60cf1c305c21dfba14cff8cbf2cf847bc06d5c64372e93540e1b6f654b73b2', 'Annapurna Food Redistribution Network', '9740118833', 'organization', NULL, 'APMC Yard Road, Ward 5', 'Bagalkote', 16.189000, 75.701000, 1),
(8, 'mathruchhaya.elderly@gmail.com', 'scrypt:32768:8:1$7f6a70a831d3ba75$e80b271d184eb430d88b48bb13b3558f6236b5ec6324021262d1645e99818ce0bb60cf1c305c21dfba14cff8cbf2cf847bc06d5c64372e93540e1b6f654b73b2', 'Mathru Chhaya Vrudhashrama', '9449887766', 'organization', NULL, 'Near Kalidas Nagar, Vidyagiri', 'Bagalkote', 16.177000, 75.690000, 1),
(9, 'greenweave.recycling@gmail.com', 'scrypt:32768:8:1$7f6a70a831d3ba75$e80b271d184eb430d88b48bb13b3558f6236b5ec6324021262d1645e99818ce0bb60cf1c305c21dfba14cff8cbf2cf847bc06d5c64372e93540e1b6f654b73b2', 'GreenWeave Upcycling & Textile Recycling', '9988223344', 'organization', NULL, 'Plot 88, KIADB Industrial Area', 'Bagalkote', 16.195000, 75.715000, 1)
ON DUPLICATE KEY UPDATE full_name=VALUES(full_name);

-- 2. Insert Organizations
INSERT INTO organizations (id, user_id, org_name, org_type, registration_no, description, accepts_food, accepts_clothes, accepts_damaged_clothes, capacity_note, is_verified, verified_at)
VALUES 
(1, 6, 'Sneha Deepa Children Home', 'orphanage', 'TR-BGK-2018-094', 'Dedicated shelter supporting 65 orphaned and vulnerable children with nutrition, education, and healthcare.', 1, 1, 0, '65 children dining capacity', 1, NOW()),
(2, 7, 'Annapurna Food Redistribution Network', 'food_bank', 'NGO-BGK-2020-512', 'Mobile food rescue team equipped with insulated food transport vans. Serving slums and daily wage workers.', 1, 0, 0, 'Can collect and redistribute up to 350 kg food daily', 1, NOW()),
(3, 8, 'Mathru Chhaya Old Age Home', 'old_age_home', 'TR-BGK-2015-112', 'Provides peaceful, caring residential sanctuary for 48 senior citizens.', 1, 1, 0, '48 senior residents', 1, NOW()),
(4, 9, 'GreenWeave Upcycling & Textile Recycling', 'recycler', 'MSME-KA-02-0045182', 'Eco-friendly textile recycling unit transforming torn/scrap fabrics into industrial mats and upcycled bags.', 0, 1, 1, '500 kg weekly processing capacity', 1, NOW())
ON DUPLICATE KEY UPDATE org_name=VALUES(org_name);

-- 3. Insert Donations
INSERT INTO donations (id, donor_id, title, category, description, quantity, quantity_unit, status, pickup_address, city, latitude, longitude, image_url, verification_pin)
VALUES 
(1, 2, 'Surplus Veg Pulao, Dal & Paneer Curry', 'food', 'Freshly cooked hot meals from lunch banquet. Kept in clean food-grade hot cases.', 18.00, 'kg', 'available', 'Hotel Basaveshwar Grand, Station Road', 'Bagalkote', 16.182000, 75.694000, 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=600&auto=format&fit=crop&q=80', '8492'),
(2, 4, 'Unopened Packaged Rice, Wheat Flour & Biscuits', 'food', 'Surplus dry grocery items and biscuit cartons stored safely before college vacation break.', 35.00, 'kg', 'available', 'BVVS Central Mess Store, Vidyagiri', 'Bagalkote', 16.172000, 75.685000, 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=600&auto=format&fit=crop&q=80', '4321'),
(3, 5, 'Clean Children Sweaters, Jackets & T-Shirts', 'clothes', 'Gentle used winter sweaters, hoodies, and t-shirts for ages 5-14. Sanitized and folded.', 28.00, 'pieces', 'available', 'House #42, Sector 8, Navanagar', 'Bagalkote', 16.168000, 75.660000, 'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=600&auto=format&fit=crop&q=80', '7723'),
(4, 3, 'Torn Stage Drapes, Fabric Cuts & Stage Linen Scrap', 'clothes', 'Surplus damaged stage backdrop fabrics, torn drapes, not suitable for wear. Ideal for recycling.', 45.00, 'kg', 'available', 'Royal Palace Function Hall, Vidyagiri 4th Cross', 'Bagalkote', 16.175000, 75.688000, 'https://images.unsplash.com/photo-1558769132-cb1aea458c5e?w=600&auto=format&fit=crop&q=80', '9012')
ON DUPLICATE KEY UPDATE title=VALUES(title);

-- 4. Insert Food Details
INSERT INTO food_details (donation_id, food_type, preparation_time, expiry_deadline, storage_condition, allergen_info, is_urgent)
VALUES 
(1, 'cooked', DATE_SUB(NOW(), INTERVAL 2 HOUR), DATE_ADD(NOW(), INTERVAL 3 HOUR), 'hot', 'Contains dairy (paneer). Vegetarian only.', 1),
(2, 'packaged', DATE_SUB(NOW(), INTERVAL 2 DAY), DATE_ADD(NOW(), INTERVAL 15 DAY), 'ambient', 'Gluten (Wheat)', 0)
ON DUPLICATE KEY UPDATE food_type=VALUES(food_type);

-- 5. Insert Clothes Details
INSERT INTO clothes_details (donation_id, clothes_type, `condition`, target_age_group, clean_washed)
VALUES 
(3, 'kids', 'reusable', 'children', 1),
(4, 'mixed', 'damaged_recycling', 'all', 1)
ON DUPLICATE KEY UPDATE clothes_type=VALUES(clothes_type);
