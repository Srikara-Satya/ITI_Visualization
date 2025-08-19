import pandas as pd

# Create sample data for testing
sample_data = {
    'district': ['MUMBAI', 'PUNE', 'DELHI', 'BANGALORE'],
    'state': ['MAHARASHTRA', 'MAHARASHTRA', 'DELHI', 'KARNATAKA'],
    'category_type': ['PRIVATE (P)', 'GOVERNMENT (G)', 'PRIVATE (P)', 'GOVERNMENT (G)'],
    'name': ['ITI Mumbai', 'ITI Pune', 'ITI Delhi', 'ITI Bangalore'],
    'city': ['Mumbai', 'Pune', 'Delhi', 'Bangalore'],
    'geo_location_coordinates': ['19.0760,72.8777', '18.5204,73.8567', '28.7041,77.1025', '12.9716,77.5946']
}

df = pd.DataFrame(sample_data)
df.to_csv('sample_institutions.csv', index=False)
print("Sample data created: sample_institutions.csv")