import pandas as pd
import random

# All Indian states and UTs with their approximate center coordinates
indian_states = {
    'ANDHRA PRADESH': (15.9129, 79.7400),
    'ARUNACHAL PRADESH': (28.2180, 94.7278),
    'ASSAM': (26.2006, 92.9376),
    'BIHAR': (25.0961, 85.3131),
    'CHHATTISGARH': (21.2787, 81.8661),
    'GOA': (15.2993, 74.1240),
    'GUJARAT': (23.0225, 72.5714),
    'HARYANA': (29.0588, 76.0856),
    'HIMACHAL PRADESH': (31.1048, 77.1734),
    'JHARKHAND': (23.6102, 85.2799),
    'KARNATAKA': (15.3173, 75.7139),
    'KERALA': (10.8505, 76.2711),
    'MADHYA PRADESH': (22.9734, 78.6569),
    'MAHARASHTRA': (19.7515, 75.7139),
    'MANIPUR': (24.6637, 93.9063),
    'MEGHALAYA': (25.4670, 91.3662),
    'MIZORAM': (23.1645, 92.9376),
    'NAGALAND': (26.1584, 94.5624),
    'ODISHA': (20.9517, 85.0985),
    'PUNJAB': (31.1471, 75.3412),
    'RAJASTHAN': (27.0238, 74.2179),
    'SIKKIM': (27.5330, 88.5122),
    'TAMIL NADU': (11.1271, 78.6569),
    'TELANGANA': (18.1124, 79.0193),
    'TRIPURA': (23.9408, 91.9882),
    'UTTAR PRADESH': (26.8467, 80.9462),
    'UTTARAKHAND': (30.0668, 79.0193),
    'WEST BENGAL': (22.9868, 87.8550),
    'ANDAMAN AND NICOBAR ISLANDS': (11.7401, 92.6586),
    'CHANDIGARH': (30.7333, 76.7794),
    'DADRA AND NAGAR HAVELI AND DAMAN AND DIU': (20.1809, 73.0169),
    'DELHI': (28.7041, 77.1025),
    'JAMMU AND KASHMIR': (34.0837, 74.7973),
    'LADAKH': (34.1526, 77.5770),
    'LAKSHADWEEP': (10.5667, 72.6417),
    'PUDUCHERRY': (11.9416, 79.8083)
}

# Major cities for each state
state_cities = {
    'ANDHRA PRADESH': ['Visakhapatnam', 'Vijayawada', 'Guntur', 'Nellore', 'Kurnool'],
    'ARUNACHAL PRADESH': ['Itanagar', 'Naharlagun', 'Pasighat', 'Tezpur', 'Bomdila'],
    'ASSAM': ['Guwahati', 'Silchar', 'Dibrugarh', 'Jorhat', 'Nagaon'],
    'BIHAR': ['Patna', 'Gaya', 'Bhagalpur', 'Muzaffarpur', 'Darbhanga'],
    'CHHATTISGARH': ['Raipur', 'Bhilai', 'Korba', 'Bilaspur', 'Durg'],
    'GOA': ['Panaji', 'Margao', 'Vasco da Gama', 'Mapusa', 'Ponda'],
    'GUJARAT': ['Ahmedabad', 'Surat', 'Vadodara', 'Rajkot', 'Bhavnagar'],
    'HARYANA': ['Gurugram', 'Faridabad', 'Panipat', 'Ambala', 'Karnal'],
    'HIMACHAL PRADESH': ['Shimla', 'Dharamshala', 'Solan', 'Mandi', 'Kullu'],
    'JHARKHAND': ['Ranchi', 'Jamshedpur', 'Dhanbad', 'Bokaro', 'Deoghar'],
    'KARNATAKA': ['Bangalore', 'Mysore', 'Hubli', 'Mangalore', 'Belgaum'],
    'KERALA': ['Kochi', 'Thiruvananthapuram', 'Kozhikode', 'Thrissur', 'Kollam'],
    'MADHYA PRADESH': ['Bhopal', 'Indore', 'Gwalior', 'Jabalpur', 'Ujjain'],
    'MAHARASHTRA': ['Mumbai', 'Pune', 'Nagpur', 'Nashik', 'Aurangabad'],
    'MANIPUR': ['Imphal', 'Thoubal', 'Bishnupur', 'Churachandpur', 'Kakching'],
    'MEGHALAYA': ['Shillong', 'Tura', 'Jowai', 'Nongpoh', 'Baghmara'],
    'MIZORAM': ['Aizawl', 'Lunglei', 'Saiha', 'Champhai', 'Kolasib'],
    'NAGALAND': ['Kohima', 'Dimapur', 'Mokokchung', 'Tuensang', 'Wokha'],
    'ODISHA': ['Bhubaneswar', 'Cuttack', 'Rourkela', 'Berhampur', 'Sambalpur'],
    'PUNJAB': ['Ludhiana', 'Amritsar', 'Jalandhar', 'Patiala', 'Bathinda'],
    'RAJASTHAN': ['Jaipur', 'Jodhpur', 'Udaipur', 'Kota', 'Ajmer'],
    'SIKKIM': ['Gangtok', 'Namchi', 'Gyalshing', 'Mangan', 'Rangpo'],
    'TAMIL NADU': ['Chennai', 'Coimbatore', 'Madurai', 'Tiruchirappalli', 'Salem'],
    'TELANGANA': ['Hyderabad', 'Warangal', 'Nizamabad', 'Khammam', 'Karimnagar'],
    'TRIPURA': ['Agartala', 'Dharmanagar', 'Udaipur', 'Kailashahar', 'Belonia'],
    'UTTAR PRADESH': ['Lucknow', 'Kanpur', 'Ghaziabad', 'Agra', 'Varanasi'],
    'UTTARAKHAND': ['Dehradun', 'Haridwar', 'Roorkee', 'Haldwani', 'Rudrapur'],
    'WEST BENGAL': ['Kolkata', 'Howrah', 'Durgapur', 'Asansol', 'Siliguri'],
    'ANDAMAN AND NICOBAR ISLANDS': ['Port Blair', 'Diglipur', 'Mayabunder', 'Rangat', 'Car Nicobar'],
    'CHANDIGARH': ['Chandigarh'],
    'DADRA AND NAGAR HAVELI AND DAMAN AND DIU': ['Daman', 'Diu', 'Silvassa'],
    'DELHI': ['New Delhi', 'Delhi', 'Gurgaon', 'Faridabad', 'Noida'],
    'JAMMU AND KASHMIR': ['Srinagar', 'Jammu', 'Anantnag', 'Baramulla', 'Udhampur'],
    'LADAKH': ['Leh', 'Kargil', 'Nubra', 'Zanskar', 'Drass'],
    'LAKSHADWEEP': ['Kavaratti', 'Agatti', 'Minicoy', 'Amini', 'Andrott'],
    'PUDUCHERRY': ['Puducherry', 'Karaikal', 'Mahe', 'Yanam']
}

# Generate comprehensive data
data = []
institute_id = 1

for state, (lat, lon) in indian_states.items():
    cities = state_cities[state]
    # Generate 3-8 institutions per state
    num_institutes = random.randint(3, 8)
    
    for i in range(num_institutes):
        city = random.choice(cities)
        category = random.choice(['PRIVATE (P)', 'GOVERNMENT (G)'])
        
        # Add some random variation to coordinates (within ~50km radius)
        lat_variation = random.uniform(-0.5, 0.5)
        lon_variation = random.uniform(-0.5, 0.5)
        
        institute_lat = lat + lat_variation
        institute_lon = lon + lon_variation
        
        # Generate district name (simplified)
        district = city.upper()
        
        data.append({
            'district': district,
            'state': state,
            'category_type': category,
            'name': f'ITI {city} {institute_id}',
            'city': city,
            'geo_location_coordinates': f'{institute_lat:.4f},{institute_lon:.4f}'
        })
        
        institute_id += 1

# Create DataFrame and save
df = pd.DataFrame(data)
df.to_csv('sample_institutions.csv', index=False)
print(f"Comprehensive data created with {len(df)} institutions across {len(indian_states)} states/UTs")
print(f"Private institutions: {len(df[df['category_type'] == 'PRIVATE (P)'])}")
print(f"Government institutions: {len(df[df['category_type'] == 'GOVERNMENT (G)'])}")