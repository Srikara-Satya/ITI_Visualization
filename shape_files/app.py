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

current_directory = os.getcwd()
district_shapefile_path = r"/mount/src/nsdc/shape_file/DISTRICT_BOUNDARY.shp"
state_shapefile_path = r"/mount/src/nsdc/shape_file/STATE_BOUNDARY.shp"

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

# excel_file = st.file_uploader("Upload Excel File", type=['xlsx'])
with st.spinner('Fetching ITI data...'):
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
# st.success('Data fetched successfully!')

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
                if filtered_gdf.crs != 'epsg:4326':
                    filtered_gdf = filtered_gdf.to_crs(epsg=4326)

                combined_geometry = filtered_gdf['geometry'].unary_union
                centroid = combined_geometry.centroid
                map_center = [centroid.y, centroid.x]
                bounds = combined_geometry.bounds

                bbox = [
                    [bounds[1], bounds[0]],  # Lower left corner (lat, lon)
                    [bounds[3], bounds[2]]   # Upper right corner (lat, lon)
                ]

                def calculate_zoom_level(bbox, map_dimensions):
                    map_width, map_height = map_dimensions
                    lat_range = abs(bbox[0][0] - bbox[1][0])
                    lon_range = abs(bbox[0][1] - bbox[1][1])
                    world_map_width = 360
                    pixels_per_degree = map_width / world_map_width
                    degrees_displayed_x = map_width / pixels_per_degree
                    degrees_displayed_y = map_height / pixels_per_degree
                    scale_x = lon_range / degrees_displayed_x
                    scale_y = lat_range / degrees_displayed_y
                    zoom_level_x = math.floor(-math.log(scale_x, 2))
                    zoom_level_y = math.floor(-math.log(scale_y, 2))
                    return min(zoom_level_x, zoom_level_y)

                map_dimensions = (800, 600)
                zoom_start = calculate_zoom_level(bbox, map_dimensions)
                m = folium.Map(location=map_center, zoom_start=zoom_start, min_zoom=zoom_start, max_zoom=18)
                m.fit_bounds(bbox)
                folium.Choropleth(
                    geo_data=filtered_gdf,
                    data=filtered_gdf,
                    columns=['District', 'count'],
                    key_on='feature.properties.District',
                    fill_color='YlGn',
                    fill_opacity=0.7,
                    line_opacity=0.2,
                ).add_to(m)
                folium.GeoJson(state_gdf, style_function=lambda feature: {'fillColor': 'transparent', 'color': 'black', 'weight': 1, 'dashArray': '5, 5'}).add_to(m)
                st.markdown('<div class="map-container">', unsafe_allow_html=True)
                
                try:
                    if not df_institutions_1.empty:
                        df_institutions_2 = df_institutions_1[df_institutions_1['state'] == selected_state]
                        for idx, row in df_institutions_2.iterrows():
                            if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
                                icon_image = r"/mount/src/nsdc/shape_file/location_icon.png"
                                icon = CustomIcon(icon_image, icon_size=(20, 20))
                                popup_html =  f"""
                                <div style="font-size: 14px; line-height: 1.6; width: 150px;">
                                <span style="color: orange; font-weight: bold;">Name:</span> {row['name']}<br>
                                <span style="color: orange; font-weight: bold;">City:</span> {row['city']}<br>
                                <span style="color: orange; font-weight: bold;">State:</span> {row['state']}</div>"""
                                marker = folium.Marker(location=[row['Latitude'], row['Longitude']], icon=icon, popup= popup_html)
                                marker.add_to(m)
                except NameError:
                    pass

                folium_static(m, width=500, height=500)
                st.markdown('</div>', unsafe_allow_html=True)

        else:
            state_district_sum = df_institutions.groupby('state')['count'].sum().reset_index()
            total_district_count = state_district_sum['count'].sum()
            state_gdf = state_gdf.merge(state_district_sum, left_on='STATE', right_on='state')

            with st.spinner('Loading map...'):
                map_center = [28.65612869068646, 77.13936765193347]
                m = folium.Map(location=map_center, zoom_start=4, min_zoom=4, max_zoom=18)
                folium.Choropleth(
                    geo_data=state_gdf,
                    data=state_gdf,
                    columns=['STATE', 'count'],
                    key_on='feature.properties.STATE',
                    fill_color='YlGn',
                    fill_opacity=0.7,
                    line_opacity=0.2
                ).add_to(m)
                folium.GeoJson(state_gdf, style_function=lambda feature: {'fillColor': 'transparent', 'color': 'black', 'weight': 1, 'dashArray': '5, 5'}).add_to(m)

                try:
                    if not df_institutions_1.empty:
                        for idx, row in df_institutions_1.iterrows():
                            if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
                                icon_image = r"/mount/src/nsdc/shape_file/location_icon.png"
                                icon = CustomIcon(
                                    icon_image,
                                    icon_size=(20, 20)
                                )
                                popup_html =  f"""
                                <div style="font-size: 14px; line-height: 1.6; width: 150px;">
                                <span style="color: orange; font-weight: bold;">Name:</span> {row['name']}<br>
                                <span style="color: orange; font-weight: bold;">City:</span> {row['city']}<br>
                                <span style="color: orange; font-weight: bold;">State:</span> {row['state']}</div>"""
                                marker = folium.Marker(location=[row['Latitude'], row['Longitude']], icon=icon, popup= popup_html)
                                marker.add_to(m)
                except NameError:
                    pass

                st.markdown('<div class="map-container">', unsafe_allow_html=True)
                folium_static(m, width=500, height=500)
                st.markdown('</div>', unsafe_allow_html=True)

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
