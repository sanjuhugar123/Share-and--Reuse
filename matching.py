import math
from datetime import datetime
from models import Organization, User

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees) using Haversine formula.
    Returns distance in kilometers.
    """
    if None in (lat1, lon1, lat2, lon2):
        return 9999.0
        
    try:
        lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])
    except (ValueError, TypeError):
        return 9999.0

    # Earth radius in kilometers
    R = 6371.0
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    
    distance = R * c
    return round(distance, 2)


def estimate_transit_time_minutes(distance_km):
    """
    Simple practical estimation for urban/semi-urban pickup transit time.
    Assuming average city speed ~ 25 km/h + 10 min dispatch handling.
    """
    speed_kmh = 25.0
    transit_mins = (distance_km / speed_kmh) * 60.0 + 10.0
    return int(round(transit_mins))


def find_matching_organizations(donation, max_radius_km=50.0):
    """
    Find and rank verified organizations suitable for a specific donation.
    Applies location proximity, category eligibility, urgency weighting, and recycling routing.
    """
    # Only active & verified organizations
    orgs = Organization.query.join(User).filter(
        Organization.is_verified == True,
        User.is_active == True
    ).all()
    
    matches = []
    donor_lat = donation.latitude
    donor_lon = donation.longitude
    is_food = donation.category == 'food'
    is_clothes = donation.category == 'clothes'
    
    now = datetime.utcnow()
    hours_remaining = None
    is_urgent_food = False
    
    if is_food and donation.food_detail:
        if donation.food_detail.expiry_deadline:
            diff = (donation.food_detail.expiry_deadline - now).total_seconds() / 3600.0
            hours_remaining = max(0.0, diff)
            if hours_remaining <= 4.0:
                is_urgent_food = True
                donation.food_detail.is_urgent = True

    cloth_condition = None
    if is_clothes and donation.clothes_detail:
        cloth_condition = donation.clothes_detail.condition

    for org in orgs:
        # Check basic category capability
        if is_food and not org.accepts_food:
            continue
        if is_clothes and not org.accepts_clothes and not (cloth_condition == 'damaged_recycling' and org.accepts_damaged_clothes):
            continue
            
        # Specific Clothes routing:
        # Reusable clothes -> NGOs, orphanages, old age homes
        # Damaged/Scrap clothes -> Recyclers & upcyclers
        suitability_reason = []
        is_high_compatibility = False
        
        if is_clothes:
            if cloth_condition == 'damaged_recycling':
                if org.org_type == 'recycler' or org.accepts_damaged_clothes:
                    suitability_reason.append("Specialized in textile recycling & upcycling")
                    is_high_compatibility = True
                else:
                    # Skip regular orphanages/old-age homes for torn/damaged clothes
                    continue
            else: # Reusable
                if org.org_type in ['orphanage', 'old_age_home', 'ngo', 'food_bank']:
                    suitability_reason.append("Directly distributes wearable clothes to beneficiaries")
                    is_high_compatibility = True
                elif org.org_type == 'recycler':
                    # Recyclers are lower priority for perfectly good reusable clothes
                    suitability_reason.append("Can accept for secondary redistribution")
        
        # Calculate distance
        org_lat = org.user.latitude
        org_lon = org.user.longitude
        distance_km = haversine_distance(donor_lat, donor_lon, org_lat, org_lon)
        
        # Max radius filter
        if distance_km > max_radius_km:
            continue
            
        transit_time = estimate_transit_time_minutes(distance_km)
        
        # Scoring algorithm
        # Proximity score (0 to 100): closer is higher
        proximity_score = max(0.0, 100.0 - (distance_km * 2.0))
        
    
        # Urgency adjustment
        match_score = proximity_score

        if is_food:
            if donation.food_detail:
                food_type = donation.food_detail.food_type or 'general'
            else:
                food_type = 'general'

            suitability_reason.append(
                f"Accepts {food_type.capitalize()} food"
            )

            if is_urgent_food:
                suitability_reason.append(
                    "Prioritized for urgent dispatch (< 4 hours shelf life)"
                )

                if distance_km <= 10.0:
                    match_score += 35.0
                elif distance_km <= 20.0:
                    match_score += 15.0
                else:
                    match_score -= 20.0
            else:
                match_score += 10.0

        
                
        if is_clothes and is_high_compatibility:
            match_score += 25.0
            
        # Organization capacity factor
        if org.capacity_note:
            suitability_reason.append(f"Capacity: {org.capacity_note}")
            
        match_score = round(max(5.0, min(99.0, match_score)), 1)
        
        matches.append({
            'organization': org,
            'user': org.user,
            'distance_km': distance_km,
            'transit_time_mins': transit_time,
            'match_score': match_score,
            'reasons': suitability_reason,
            'is_urgent': is_urgent_food
        })
        
    # Sort by match_score descending, then distance ascending
    matches.sort(key=lambda x: (-x['match_score'], x['distance_km']))
    return matches
