import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
import json

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
        height: 150px;
    }
    .spacer {
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="title">Indian Institutes for Skill Development and Entrepreneurship</h1>', unsafe_allow_html=True)

# Load sample data
with st.spinner('Loading comprehensive data...'):
    try:
        df_institutions = pd.read_csv('sample_institutions.csv')
        st.success('Comprehensive data loaded successfully!')
    except FileNotFoundError:
        st.error('Sample data file not found. Please run comprehensive_data.py first.')
        st.stop()

if len(df_institutions) > 0:
    if 'geo_location_coordinates' in df_institutions.columns:
        df_institutions[['Latitude', 'Longitude']] = df_institutions['geo_location_coordinates'].str.split(',', expand=True).apply(lambda x: pd.to_numeric(x, errors='coerce'))
        df_institutions_1 = df_institutions.copy()
        df_institutions_1['district'] = df_institutions_1['district'].str.strip().str.upper()
        df_institutions_1['state'] = df_institutions_1['state'].str.strip().str.upper()
    
    df_institutions_summary = df_institutions[['district', 'state', 'category_type']]
    df_institutions_summary['district'] = df_institutions_summary['district'].str.strip().str.upper()
    df_institutions_summary['state'] = df_institutions_summary['state'].str.strip().str.upper()
    private_iti_count = df_institutions_summary[df_institutions_summary['category_type'].str.upper() == 'PRIVATE (P)'].shape[0]
    government_iti_count = df_institutions_summary[df_institutions_summary['category_type'].str.upper() == 'GOVERNMENT (G)'].shape[0]

    # Group by state and count institutions
    df_institutions = df_institutions_summary.groupby(['district', 'state', 'category_type']).size().reset_index(name='count')
    df_institutions.columns = ['district_name', 'state', 'category_type', 'count']
    
    # Create state-wise summary
    state_summary = df_institutions.groupby('state')['count'].sum().reset_index()
    state_summary.columns = ['state', 'total_count']

    state_names = df_institutions['state'].unique().tolist()
    state_names = sorted(state_names)
    selected_state = st.selectbox('Select a state', ["Select a state"] + state_names)

    st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    
    with col1:
        if selected_state != 'Select a state':
            filtered_data = df_institutions_1[df_institutions_1['state'] == selected_state]
            
            total_private_iti_count = df_institutions[(df_institutions['state'] == selected_state) & (df_institutions['category_type'].str.upper() == 'PRIVATE (P)')]['count'].sum()
            total_government_iti_count = df_institutions[(df_institutions['state'] == selected_state) & (df_institutions['category_type'].str.upper() == 'GOVERNMENT (G)')]['count'].sum()

            with st.spinner(f'Generating {selected_state} map...'):
                # Get state institutions and calculate boundaries
                state_institutions = df_institutions_1[df_institutions_1['state'] == selected_state]
                
                if not state_institutions.empty:
                    # Calculate state boundaries
                    min_lat = state_institutions['Latitude'].min() - 0.5
                    max_lat = state_institutions['Latitude'].max() + 0.5
                    min_lon = state_institutions['Longitude'].min() - 0.5
                    max_lon = state_institutions['Longitude'].max() + 0.5
                    
                    # Center of the state
                    center_lat = state_institutions['Latitude'].mean()
                    center_lon = state_institutions['Longitude'].mean()
                    map_center = [center_lat, center_lon]
                    
                    # Create map focused on the state
                    m = folium.Map(location=map_center, zoom_start=7)
                    
                    # Fit map to state boundaries
                    m.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])
                    
                    # Create district-wise data for selected state
                    district_data = df_institutions[df_institutions['state'] == selected_state].groupby('district_name')['count'].sum().reset_index()
                    
                    # Add circles for each district with size based on count
                    for _, row in district_data.iterrows():
                        district_institutions = df_institutions_1[
                            (df_institutions_1['state'] == selected_state) & 
                            (df_institutions_1['district'] == row['district_name'])
                        ]
                        if not district_institutions.empty:
                            district_lat = district_institutions['Latitude'].mean()
                            district_lon = district_institutions['Longitude'].mean()
                            
                            # Color based on count (green scale)
                            if row['count'] <= 2:
                                color = '#90EE90'  # Light green
                            elif row['count'] <= 4:
                                color = '#32CD32'  # Lime green
                            elif row['count'] <= 6:
                                color = '#228B22'  # Forest green
                            else:
                                color = '#006400'  # Dark green
                            
                            folium.CircleMarker(
                                location=[district_lat, district_lon],
                                radius=row['count'] * 4 + 8,  # Larger size for state view
                                popup=f"<b>{row['district_name']}</b><br>Institutions: {row['count']}",
                                color='black',
                                weight=2,
                                fillColor=color,
                                fillOpacity=0.8,
                                tooltip=f"{row['district_name']}: {row['count']} institutions"
                            ).add_to(m)
                    
                    # Add state-specific legend
                    legend_html = f'''
                    <div style="position: fixed; 
                                bottom: 50px; left: 50px; width: 180px; height: 140px; 
                                background-color: white; border:2px solid grey; z-index:9999; 
                                font-size:14px; padding: 10px">
                    <p><b>{selected_state}</b></p>
                    <p><b>District Institutions</b></p>
                    <p><i class="fa fa-circle" style="color:#90EE90"></i> 1-2</p>
                    <p><i class="fa fa-circle" style="color:#32CD32"></i> 3-4</p>
                    <p><i class="fa fa-circle" style="color:#228B22"></i> 5-6</p>
                    <p><i class="fa fa-circle" style="color:#006400"></i> 7+</p>
                    </div>
                    '''
                    m.get_root().html.add_child(folium.Element(legend_html))
                    
                else:
                    # Fallback if no data
                    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)
                    st.warning(f"No institution data found for {selected_state}")

                folium_static(m, width=500, height=500)
        else:
            with st.spinner('Loading India map with state-wise data...'):
                # Create India map with state-wise color coding
                map_center = [20.5937, 78.9629]
                m = folium.Map(location=map_center, zoom_start=5)
                
                # Add circles for each state with color based on institution count
                for _, row in state_summary.iterrows():
                    state_institutions = df_institutions_1[df_institutions_1['state'] == row['state']]
                    if not state_institutions.empty:
                        state_lat = state_institutions['Latitude'].mean()
                        state_lon = state_institutions['Longitude'].mean()
                        
                        # Color grading based on total count
                        if row['total_count'] <= 3:
                            color = '#FFE4E1'  # Very light
                        elif row['total_count'] <= 5:
                            color = '#FFA07A'  # Light salmon
                        elif row['total_count'] <= 7:
                            color = '#FF6347'  # Tomato
                        elif row['total_count'] <= 9:
                            color = '#FF4500'  # Orange red
                        else:
                            color = '#DC143C'  # Crimson
                        
                        folium.CircleMarker(
                            location=[state_lat, state_lon],
                            radius=row['total_count'] * 2 + 8,  # Size based on count
                            popup=f"<b>{row['state']}</b><br>Total Institutions: {row['total_count']}",
                            color='black',
                            weight=2,
                            fillColor=color,
                            fillOpacity=0.8,
                            tooltip=f"{row['state']}: {row['total_count']} institutions"
                        ).add_to(m)
                
                # Add legend
                legend_html = '''
                <div style="position: fixed; 
                            bottom: 50px; left: 50px; width: 150px; height: 120px; 
                            background-color: white; border:2px solid grey; z-index:9999; 
                            font-size:14px; padding: 10px">
                <p><b>Institutions Count</b></p>
                <p><i class="fa fa-circle" style="color:#FFE4E1"></i> 1-3</p>
                <p><i class="fa fa-circle" style="color:#FFA07A"></i> 4-5</p>
                <p><i class="fa fa-circle" style="color:#FF6347"></i> 6-7</p>
                <p><i class="fa fa-circle" style="color:#FF4500"></i> 8-9</p>
                <p><i class="fa fa-circle" style="color:#DC143C"></i> 10+</p>
                </div>
                '''
                m.get_root().html.add_child(folium.Element(legend_html))
                
                folium_static(m, width=500, height=500)

    with col2:
        if selected_state != 'Select a state':
            total_count = total_private_iti_count + total_government_iti_count
            card = f"""
            <div class="box">
                <h4>Total ITIs Count</h4>
                <p style="font-size: 24px;">{total_count}</p>
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
            total_count = private_iti_count + government_iti_count
            card = f"""
            <div class="box">
                <h5>Total ITIs Count</h5>
                <p style="font-size: 24px;">{total_count}</p>
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