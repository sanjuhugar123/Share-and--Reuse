# Share & Reuse 🌿

> **Intelligent Surplus Food & Reusable/Recycled Clothes Redistribution Platform**  
> *5th Semester Computer Science / Engineering Academic Project*  
> Location Focus: Bagalkote & Surroundings, Karnataka

---

## 📌 Project Overview
**Share & Reuse** is a full-stack web platform bridging individuals, banquet halls, restaurants, and colleges having surplus food and reusable/damaged textiles with verified charitable organizations (NGOs, orphanages, old-age homes, food redistribution networks) and industrial textile upcycling/recycling centers.

Unlike ordinary donation portals, this system features **intelligent location-based matching** using the **Haversine great-circle distance algorithm** combined with an **Urgent Food Shelf-Life Alert System** and **Dual-Stream Textile Segregation (Wearable vs. Industrial Recycling)**.

---

## 🌟 Key Innovations & Technical Highlights

1. **Urgent Food Matching Algorithm**:
   - Collects food preparation time, pickup deadline, storage conditions (*hot, ambient, refrigerated, frozen*), and allergen notes.
   - Automatically computes shelf-life remaining: if $\le 4\text{ hours}$, triggers urgent dispatch alerts to nearby food redistribution networks and orphanages.
2. **Dual-Stream Clothing Routing**:
   - **Reusable Condition**: Routed to NGOs, orphanages, and old age homes for direct beneficiary wear.
   - **Damaged / Fabric Scrap**: Automatically routed to Textile Recyclers & Upcyclers to divert scrap from municipal landfills.
3. **Location-Based Proximity Engine**:
   - Uses the **Haversine formula** to calculate true distance in kilometers between donor and verified recipients.
   - Visualizes live interactive maps with Leaflet & OpenStreetMap.
4. **Secure OTP Handover**:
   - Generates a 4-digit PIN for the donor. The organization volunteer enters this PIN at the time of physical handover to confirm receipt.
5. **Impact Analytics & Appreciation Certificates**:
   - Real-time Chart.js visualizations for admin oversight.
   - Printable Certificate of Social Impact for donors upon completion.

---

## 👥 User Roles & Demo Credentials

| Role | Name | Email | Password | Features |
| :--- | :--- | :--- | :--- | :--- |
| **Donor (Hotel)** | Hotel Basaveshwar Grand | `basaveshwar.hotel@gmail.com` | `donor123` | Post surplus buffet food, track pickup, view OTP PIN |
| **Donor (Function Hall)** | Royal Palace Hall | `royalpalace.events@gmail.com` | `donor123` | Post banquet meals & linen scrap for recycling |
| **Donor (College)** | BVVS Campus Central Mess | `bvvs.hostel@bvvs.edu` | `donor123` | Post packaged grains, rice, grocery surplus |
| **Donor (Person)** | Rajesh K. Sharma | `rajesh.sharma@gmail.com` | `donor123` | Donate reusable kids winterwear |
| **Organization (Orphanage)** | Sneha Deepa Children Home | `snehadheepa.orphanage@gmail.com` | `org123` | Accept meals & reusable kids clothing |
| **Organization (Food Bank)** | Annapurna Food Network | `annapurna.seva@gmail.com` | `org123` | Urgent cooked meal rescue with transport vans |
| **Organization (Recycler)** | GreenWeave Textile Recycling | `greenweave.recycling@gmail.com` | `org123` | Receive damaged fabric & textile cuts |
| **Admin** | System Administrator | `admin@shareandreuse.org` | `admin123` | Verify NGOs, manage users, view Chart.js impact stats |

*(Note: The login page also provides 1-click buttons to auto-fill any of these accounts!)*

---

## 🛠️ Technology Stack

- **Backend**: Python 3.13, Flask 3.1, Flask-SQLAlchemy, Werkzeug
- **Database**: SQLite (default, zero configuration) or MySQL 8.0 (scripts provided)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons
- **Mapping & Geolocation**: Leaflet.js, OpenStreetMap
- **Data Analytics**: Chart.js

---

## 🚀 Quick Start Guide

### 1. Activate Environment & Install Dependencies
Open PowerShell inside the project directory:
```powershell
# Navigate to project folder
cd C:\Users\SANJU\.gemini\antigravity\scratch\share_and_reuse

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install requirements (already installed in venv)
pip install -r requirements.txt
```

### 2. Run Database Seeding (Pre-loaded with Bagalkote Data)
```powershell
python seed_data.py
```

### 3. Run the Flask Web Application
```powershell
python app.py
```
Open your web browser and visit:  
👉 **`http://localhost:5000`**

### 4. Run Automated Test Suite
```powershell
python test_app.py
```

---

## 🗄️ Switching to MySQL (Optional)
The project works out of the box with SQLite. If you want to use MySQL Workbench or phpMyAdmin for college lab demonstration:

1. Import schema:
   - Run `database/schema.sql` in MySQL Workbench or `mysql -u root -p < database/schema.sql`.
   - Optionally import `database/seed_data.sql`.
2. Open `config.py` and set:
   ```python
   USE_MYSQL = True
   MYSQL_USER = 'root'
   MYSQL_PASSWORD = 'your_mysql_password'
   MYSQL_DB = 'share_and_reuse'
   ```
3. Restart `python app.py`.

---

## 📂 Project Directory Structure

```
share_and_reuse/
├── app.py                   # Main Flask application & route controllers
├── config.py                # Database configuration (SQLite / MySQL)
├── models.py                # Database models (User, Org, Donation, Food, Clothes, etc.)
├── matching.py              # Haversine distance & Urgent-food recommendation engine
├── seed_data.py             # Realistic test data seeder (Bagalkote hotels, NGOs, recyclers)
├── test_app.py              # Automated test suite
├── requirements.txt         # Python package dependencies
├── README.md                # Documentation & quick start guide
├── database/
│   ├── schema.sql           # Pure MySQL 8.0 DDL schema script
│   └── seed_data.sql        # MySQL sample insert queries
├── static/
│   ├── css/style.css        # Custom styles, badges, animations, print rules
│   ├── js/main.js           # Expiry countdown timers, form toggles, location helpers
│   └── uploads/             # User-uploaded donation photos
└── templates/
    ├── base.html            # Responsive layout with role-based navigation & footer
    ├── index.html           # Landing page with impact counters & live listings
    ├── login.html           # Login screen with 1-click test credential fill
    ├── register.html        # Registration screen for Donors & Organizations
    ├── donor_dashboard.html # Donor dashboard with stats & active listings
    ├── create_donation.html # Donation form with dynamic food/clothes fields & map pin
    ├── nearby_orgs.html     # Proximity map & ranked nearby matching organizations
    ├── donation_detail.html # Item details, live status tracker & OTP display
    ├── org_dashboard.html   # Organization dashboard with urgent food banner & filters
    ├── accepted_pickups.html# Dispatch management & OTP handover verification
    ├── donation_history.html# Complete history & impact records
    ├── certificate.html     # Printable certificate of appreciation
    ├── admin_dashboard.html # Admin analytics, Chart.js graphs & verification queue
    └── report_issue.html    # Complaint & feedback submission form
```
