import geopandas as gpd
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium, folium_static
import math
import os
from folium import CustomIcon
import psycopg2

st.markdown("""
    <style>
    .title {
        color: black;
        text-align: center;
    }
    .box {
        border: 2px solid #000;
        padding: 20px;
        border-radius: 10px;
        width: 100%;
        box-sizing: border-box;
        text-align: center;
        margin-bottom: 20px;
        height: 150px;  /* Fixed height for all boxes */
    }
    .container {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
    }
    .map-container {
        height: 0px;
    }
    .box-container {
        height: 0px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .spacer {
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="title">Indian Institutes for Skill Development and Entrepreneurship</h1>', unsafe_allow_html=True)

# Option to upload new data
uploaded_file = st.file_uploader("Upload new ITI data (CSV/Excel)", type=['csv', 'xlsx'], help="Upload a file with columns: district, state, category_type, name, city, geo_location_coordinates")

current_directory = os.getcwd()
district_shapefile_path = r"C:\project\shape_files\district\DISTRICT_BOUNDARY.shp"
state_shapefile_path = r"C:\project\shape_files\state\STATE_BOUNDARY.shp"

if 'district_gdf' not in st.session_state:
    with st.spinner('Loading district boundaries...'):
        st.session_state['district_gdf'] = gpd.read_file(district_shapefile_path)
if 'state_gdf' not in st.session_state:
    with st.spinner('Loading state boundaries...'):
        st.session_state['state_gdf'] = gpd.read_file(state_shapefile_path)

district_gdf = st.session_state['district_gdf']
state_gdf = st.session_state['state_gdf']

district_gdf['District'] = district_gdf['District'].str.replace('>', 'A')
district_gdf['District'] = district_gdf['District'].str.replace('|', 'I')
district_gdf['STATE'] = district_gdf['STATE'].str.replace('>', 'A')
district_gdf['STATE'] = district_gdf['STATE'].str.replace('|', 'I')
district_gdf['STATE'] = district_gdf['STATE'].str.replace('ANDAMAN & NICOBAR', 'ANDAMAN AND NICOBAR ISLANDS')
state_gdf['STATE'] = state_gdf['STATE'].str.replace('>', 'A')
state_gdf['STATE'] = state_gdf['STATE'].str.replace('|', 'I')
state_gdf['STATE'] = state_gdf['STATE'].str.replace('ANDAMAN & NICOBAR', 'ANDAMAN AND NICOBAR ISLANDS')

# Load data from uploaded file, database, or sample data
if uploaded_file is not None:
    with st.spinner('Loading uploaded data...'):
        if uploaded_file.name.endswith('.csv'):
            df_institutions = pd.read_csv(uploaded_file)
        else:
            df_institutions = pd.read_excel(uploaded_file)
        st.success('Uploaded data loaded successfully!')
else:
    # Try database first, then fallback to sample data
    with st.spinner('Fetching ITI data...'):
        try:
            conn = psycopg2.connect(
                database=st.secrets.database.postgres.dbname,
                user=st.secrets.database.postgres.user,
                password=st.secrets.database.postgres.password,
                host=st.secrets.database.postgres.host,
                port=st.secrets.database.postgres.port
            )
            cursor = conn.cursor()
            query = "SELECT * FROM training_institutes"
            cursor.execute(query)
            rows = cursor.fetchall()
            df_institutions = pd.DataFrame(rows, columns=[desc[0] for desc in cursor.description])
            cursor.close()
            conn.close()
            st.success('Database data loaded successfully!')
        except Exception as e:
            st.warning(f'Database connection failed, using sample data')
            try:
                df_institutions = pd.read_csv('sample_institutions.csv')
                st.info('Using sample data')
            except FileNotFoundError:
                st.error('No data source available')
                st.stop()
# if excel_file:
if len(df_institutions) > 0:
    # df_institutions = pd.read_excel(excel_file, sheet_name=0)
    if 'geo_location_coordinates' in df_institutions.columns:
        # df_institutions[['Latitude', 'Longitude']] = df_institutions['geo_location_coordinates'].str.split(',', expand=True).astype(float)
        df_institutions[['Latitude', 'Longitude']] = df_institutions['geo_location_coordinates'].str.split(',', expand=True).apply(lambda x: pd.to_numeric(x, errors='coerce'))
        df_institutions_1 = df_institutions.copy()
        df_institutions_1['district'] = df_institutions_1['district'].str.strip().str.upper()
        df_institutions_1['state'] = df_institutions_1['state'].str.strip().str.upper()
    df_institutions = df_institutions[['district', 'state', 'category_type']]
    df_institutions['district'] = df_institutions['district'].str.strip().str.upper()
    df_institutions['state'] = df_institutions['state'].str.strip().str.upper()
    private_iti_count = df_institutions[df_institutions['category_type'].str.upper() == 'PRIVATE (P)'].shape[0]
    government_iti_count = df_institutions[df_institutions['category_type'].str.upper() == 'GOVERNMENT (G)'].shape[0]

    df_institutions = df_institutions.groupby(['district', 'state', 'category_type']).size().reset_index(name='count')
    df_institutions.columns = ['district_name', 'state', 'category_type', 'count']

    district_gdf = district_gdf.merge(df_institutions.groupby(['district_name', 'state'])['count'].sum().reset_index(), left_on=['District', 'STATE'], right_on=['district_name', 'state'], how='left')
    district_gdf['count'] = district_gdf['count'].fillna(0)

    state_names = df_institutions['state'].unique().tolist()
    state_names = sorted(state_names)
    selected_state = st.selectbox('Select a state', ["Select a state"] + state_names)

    st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)  # Add spacer to ensure gap

    col1, col2 = st.columns([3, 1])
    
    with col1:
        if selected_state != 'Select a state':
            filtered_gdf = district_gdf[district_gdf['STATE'] == selected_state]
            
            total_private_iti_count = df_institutions[(df_institutions['state'] == selected_state) & (df_institutions['category_type'].str.upper() == 'PRIVATE (P)')]['count'].sum()
            total_government_iti_count = df_institutions[(df_institutions['state'] == selected_state) & (df_institutions['category_type'].str.upper() == 'GOVERNMENT (G)')]['count'].sum()

            with st.spinner(f'Generating {selected_state} map...'):
                if not filtered_gdf.empty:
                    if filtered_gdf.crs != 'epsg:4326':
                        filtered_gdf = filtered_gdf.to_crs(epsg=4326)

                    # Calculate bounds for the selected state only
                    bounds = filtered_gdf.total_bounds
                    bbox = [
                        [bounds[1], bounds[0]],  # Lower left corner (lat, lon)
                        [bounds[3], bounds[2]]   # Upper right corner (lat, lon)
                    ]
                    
                    # Calculate center of the state
                    center_lat = (bounds[1] + bounds[3]) / 2
                    center_lon = (bounds[0] + bounds[2]) / 2
                    map_center = [center_lat, center_lon]
                    
                    # Create map focused ONLY on the selected state
                    m = folium.Map(
                        location=map_center, 
                        zoom_start=8,
                        min_zoom=6,
                        max_zoom=12
                    )
                    
                    # Fit bounds tightly to the state
                    m.fit_bounds(bbox, padding=(20, 20))
                    
                    # Add choropleth layer for districts in selected state only
                    folium.Choropleth(
                        geo_data=filtered_gdf,
                        data=filtered_gdf,
                        columns=['District', 'count'],
                        key_on='feature.properties.District',
                        fill_color='RdYlGn',
                        fill_opacity=0.8,
                        line_opacity=0.3,
                        legend_name=f'ITI Count in {selected_state}',
                        highlight=True
                    ).add_to(m)
                    
                    # Add district boundaries with light styling
                    folium.GeoJson(
                        filtered_gdf,
                        style_function=lambda feature: {
                            'fillColor': 'transparent',
                            'color': 'lightgray',
                            'weight': 1,
                            'opacity': 0.5
                        },
                        tooltip=folium.features.GeoJsonTooltip(
                            fields=['District', 'count'],
                            aliases=['District:', 'ITI Count:'],
                            localize=True,
                            sticky=True,
                            labels=True,
                            style="""
                                background-color: white;
                                border: 2px solid black;
                                border-radius: 3px;
                                box-shadow: 3px;
                            """
                        )
                    ).add_to(m)
                    
                    # Add state boundary outline
                    state_boundary = state_gdf[state_gdf['STATE'] == selected_state]
                    if not state_boundary.empty:
                        folium.GeoJson(
                            state_boundary,
                            style_function=lambda feature: {
                                'fillColor': 'transparent',
                                'color': 'gray',
                                'weight': 2,
                                'opacity': 0.7
                            }
                        ).add_to(m)

                else:
                    # Fallback if no districts found for the state
                    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)
                    st.warning(f"No district data found for {selected_state}")

                folium_static(m, width=500, height=500)

        else:
            state_district_sum = df_institutions.groupby('state')['count'].sum().reset_index()
            total_district_count = state_district_sum['count'].sum()
            
            # Merge state data with state boundaries
            state_gdf_merged = state_gdf.merge(state_district_sum, left_on='STATE', right_on='state', how='left')
            state_gdf_merged['count'] = state_gdf_merged['count'].fillna(0)
            
            with st.spinner('Loading India map...'):
                if state_gdf_merged.crs != 'epsg:4326':
                    state_gdf_merged = state_gdf_merged.to_crs(epsg=4326)
                
                map_center = [20.5937, 78.9629]
                m = folium.Map(location=map_center, zoom_start=5)
                
                # Add choropleth layer for states (green for highest, red for lowest)
                folium.Choropleth(
                    geo_data=state_gdf_merged,
                    data=state_gdf_merged,
                    columns=['STATE', 'count'],
                    key_on='feature.properties.STATE',
                    fill_color='RdYlGn',
                    fill_opacity=0.7,
                    line_opacity=0.2,
                    legend_name='ITI Count by State'
                ).add_to(m)
                
                # Add state boundaries with tooltips
                folium.GeoJson(
                    state_gdf_merged,
                    style_function=lambda feature: {
                        'fillColor': 'transparent',
                        'color': 'lightgray',
                        'weight': 1,
                        'opacity': 0.6
                    },
                    tooltip=folium.features.GeoJsonTooltip(
                        fields=['STATE', 'count'],
                        aliases=['State:', 'ITI Count:'],
                        localize=True
                    )
                ).add_to(m)
                
                folium_static(m, width=500, height=500)

    with col2:
        st.markdown('<div class="box-container">', unsafe_allow_html=True)
        if selected_state != 'Select a state':
            card = f"""
            <div class="box">
                <h4>Total ITIs Count</h4>
                <p style="font-size: 24px;">{total_private_iti_count + total_government_iti_count}</p>
            </div>
            """
            card1 = f"""
            <div class="box">
                <h5>Private ITIs Count</h5>
                <p style="font-size: 24px;">{total_private_iti_count}</p>
            </div>
            """
            card2 = f"""
            <div class="box">
                <h5>Government ITIs Count</h5>
                <p style="font-size: 24px;">{total_government_iti_count}</p>
            </div>
            """
            st.markdown(card, unsafe_allow_html=True)
            st.markdown(card1, unsafe_allow_html=True)
            st.markdown(card2, unsafe_allow_html=True)
        else:
            empty = 'Nothing to show yet'
            card = f"""
            <div class="box">
                <h5>Total ITIs Count</h5>
                <p style="font-size: 24px;">{total_district_count}</p>
            </div>
            """
            card1 = f"""
            <div class="box">
                <h5>Private ITIs Count</h5>
                <p style="font-size: 24px;">{private_iti_count}</p>
            </div>
            """
            card2 = f"""
            <div class="box">
                <h5>Government ITIs Count</h5>
                <p style="font-size: 24px;">{government_iti_count}</p>
            </div>
            """
            st.markdown(card, unsafe_allow_html=True)
            st.markdown(card1, unsafe_allow_html=True)
            st.markdown(card2, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
