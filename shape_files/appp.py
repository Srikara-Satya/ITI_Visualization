import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import folium_static

# Paths to your shapefiles
district_shapefile_path = r"C:\Users\srika\Downloads\nsdc\shape_file\DISTRICT_BOUNDARY.shp"
state_shapefile_path = r"C:\Users\srika\Downloads\nsdc\shape_file\STATE_BOUNDARY.shp"

# Function to load GeoDataFrames and handle exceptions
def load_geodata(file_path, file_type):
    try:
        with st.spinner(f'Loading {file_type} boundaries...'):
            gdf = gpd.read_file(file_path)
        if gdf is not None:
            st.success(f'{file_type} boundaries loaded successfully!')
            return gdf
        else:
            st.error(f"{file_type} GeoDataFrame is None after loading.")
            return None
    except Exception as e:
        st.error(f"Failed to load {file_type} shapefile: {e}")
        return None

# Load GeoDataFrames
district_gdf = load_geodata(district_shapefile_path, "district")
state_gdf = load_geodata(state_shapefile_path, "state")

# Check if GeoDataFrames loaded successfully
if district_gdf is None or state_gdf is None:
    st.error("Could not load one or both GeoDataFrames. Please check the shapefile paths and their validity.")
    st.stop()  # Stop execution if there's an issue with loading

# Display the columns for debugging
st.write("District GeoDataFrame Columns:", district_gdf.columns.tolist())
st.write("State GeoDataFrame Columns:", state_gdf.columns.tolist())

# Data cleaning for district and state names (if required)
if 'district_name' in district_gdf.columns:
    district_gdf['district_name'] = district_gdf['district_name'].str.title().str.strip()
else:
    st.warning("Column 'district_name' not found in district GeoDataFrame.")

if 'state_name' in state_gdf.columns:
    state_gdf['state_name'] = state_gdf['state_name'].str.title().str.strip()
else:
    st.warning("Column 'state_name' not found in state GeoDataFrame.")

# Initialize selected_state
selected_state = None

# User inputs for filtering
if 'state_name' in state_gdf.columns:
    selected_state = st.sidebar.selectbox('Select a state:', state_gdf['state_name'].unique())
    filtered_districts = district_gdf[district_gdf['state_name'] == selected_state]
else:
    st.error("Cannot filter districts as 'state_name' column is missing in the state GeoDataFrame.")
    st.stop()

# Check if selected_state is defined before proceeding
if selected_state:
    # Folium map creation
    st.title(f'District Map of {selected_state}')
    
    # Check if filtered_districts is empty
    if filtered_districts.empty:
        st.warning("No districts found for the selected state.")
    else:
        map_center = [filtered_districts.geometry.centroid.y.mean(), filtered_districts.geometry.centroid.x.mean()]
        m = folium.Map(location=map_center, zoom_start=7)

        # Add district boundaries to the map
        for _, row in filtered_districts.iterrows():
            district_name = row['district_name']
            geometry = row['geometry']
            
            folium.GeoJson(
                geometry,
                name=district_name,
                tooltip=folium.GeoJsonTooltip(fields=['district_name'], aliases=['District:'])
            ).add_to(m)

        # Display the map using Streamlit
        folium_static(m)
else:
    st.error("No state selected. Please select a state to view the district map.")
