import pandas as pd
import random

# Read existing data
df_existing = pd.read_csv('sample_institutions.csv')

# Additional cities for each state to expand coverage
additional_cities = {
    'ANDHRA PRADESH': ['Tirupati', 'Kakinada', 'Rajahmundry', 'Anantapur', 'Chittoor'],
    'ARUNACHAL PRADESH': ['Ziro', 'Along', 'Seppa', 'Roing', 'Tezu'],
    'ASSAM': ['Tezpur', 'Bongaigaon', 'Tinsukia', 'Goalpara', 'Karimganj'],
    'BIHAR': ['Purnia', 'Katihar', 'Begusarai', 'Saharsa', 'Arrah'],
    'CHHATTISGARH': ['Jagdalpur', 'Ambikapur', 'Rajnandgaon', 'Dhamtari', 'Mahasamund'],
    'GOA': ['Bicholim', 'Curchorem', 'Sanguem', 'Quepem', 'Pernem'],
    'GUJARAT': ['Gandhinagar', 'Anand', 'Bharuch', 'Jamnagar', 'Junagadh'],
    'HARYANA': ['Hisar', 'Rohtak', 'Sonipat', 'Yamunanagar', 'Sirsa'],
    'HIMACHAL PRADESH': ['Bilaspur', 'Hamirpur', 'Una', 'Chamba', 'Kangra'],
    'JHARKHAND': ['Hazaribagh', 'Giridih', 'Dumka', 'Chaibasa', 'Gumla'],
    'KARNATAKA': ['Gulbarga', 'Bijapur', 'Shimoga', 'Tumkur', 'Davangere'],
    'KERALA': ['Palakkad', 'Malappuram', 'Kannur', 'Kasaragod', 'Pathanamthitta'],
    'MADHYA PRADESH': ['Sagar', 'Rewa', 'Satna', 'Khandwa', 'Dewas'],
    'MAHARASHTRA': ['Kolhapur', 'Sangli', 'Solapur', 'Ahmednagar', 'Latur'],
    'MANIPUR': ['Ukhrul', 'Senapati', 'Tamenglong', 'Chandel', 'Jiribam'],
    'MEGHALAYA': ['Williamnagar', 'Resubelpara', 'Ampati', 'Khliehriat', 'Mawkyrwat'],
    'MIZORAM': ['Mamit', 'Lawngtlai', 'Siaha', 'Hnahthial', 'Saitual'],
    'NAGALAND': ['Zunheboto', 'Phek', 'Longleng', 'Kiphire', 'Noklak'],
    'ODISHA': ['Puri', 'Balasore', 'Jeypore', 'Baripada', 'Dhenkanal'],
    'PUNJAB': ['Moga', 'Firozpur', 'Kapurthala', 'Hoshiarpur', 'Sangrur'],
    'RAJASTHAN': ['Bikaner', 'Alwar', 'Bharatpur', 'Sikar', 'Pali'],
    'SIKKIM': ['Jorethang', 'Singtam', 'Ravangla', 'Yuksom', 'Pelling'],
    'TAMIL NADU': ['Vellore', 'Erode', 'Tirunelveli', 'Thoothukudi', 'Dindigul'],
    'TELANGANA': ['Mahbubnagar', 'Adilabad', 'Medak', 'Nalgonda', 'Rangareddy'],
    'TRIPURA': ['Sabroom', 'Khowai', 'Teliamura', 'Amarpur', 'Sonamura'],
    'UTTAR PRADESH': ['Meerut', 'Bareilly', 'Aligarh', 'Moradabad', 'Saharanpur'],
    'UTTARAKHAND': ['Pithoragarh', 'Almora', 'Nainital', 'Chamoli', 'Bageshwar'],
    'WEST BENGAL': ['Malda', 'Cooch Behar', 'Jalpaiguri', 'Purulia', 'Bankura']
}

# Generate additional data
new_data = []
institute_id = len(df_existing) + 1

for state, cities in additional_cities.items():
    for city in cities:
        # Add 2-4 institutions per city
        num_institutes = random.randint(2, 4)
        
        for i in range(num_institutes):
            category = random.choice(['PRIVATE (P)', 'GOVERNMENT (G)'])
            
            # Get approximate coordinates for the state
            state_coords = {
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
                'WEST BENGAL': (22.9868, 87.8550)
            }
            
            if state in state_coords:
                lat, lon = state_coords[state]
                # Add variation for city location
                lat_variation = random.uniform(-1.0, 1.0)
                lon_variation = random.uniform(-1.0, 1.0)
                
                new_data.append({
                    'district': city.upper(),
                    'state': state,
                    'category_type': category,
                    'name': f'ITI {city} {institute_id}',
                    'city': city,
                    'geo_location_coordinates': f'{lat + lat_variation:.4f},{lon + lon_variation:.4f}'
                })
                
                institute_id += 1

# Combine with existing data
df_new = pd.DataFrame(new_data)
df_combined = pd.concat([df_existing, df_new], ignore_index=True)

# Save expanded dataset
df_combined.to_csv('sample_institutions.csv', index=False)
print(f"Added {len(new_data)} new institutions")
print(f"Total institutions: {len(df_combined)}")
print(f"States covered: {len(df_combined['state'].unique())}")