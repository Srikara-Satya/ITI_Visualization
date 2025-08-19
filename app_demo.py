import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static

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

# Using sample CSV data
with st.spinner('Loading sample data...'):
    try:
        df_institutions = pd.read_csv('sample_institutions.csv')
        st.success('Sample data loaded successfully!')
    except FileNotFoundError:
        st.error('Sample data file not found. Please run sample_data.py first.')
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

    state_names = df_institutions_summary['state'].unique().tolist()
    state_names = sorted(state_names)
    selected_state = st.selectbox('Select a state', ["Select a state"] + state_names)

    st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    
    with col1:
        if selected_state != 'Select a state':
            filtered_data = df_institutions_1[df_institutions_1['state'] == selected_state]
            
            total_private_iti_count = df_institutions_summary[(df_institutions_summary['state'] == selected_state) & (df_institutions_summary['category_type'].str.upper() == 'PRIVATE (P)')].shape[0]
            total_government_iti_count = df_institutions_summary[(df_institutions_summary['state'] == selected_state) & (df_institutions_summary['category_type'].str.upper() == 'GOVERNMENT (G)')].shape[0]

            with st.spinner(f'Generating {selected_state} map...'):
                # Create a simple map centered on India
                map_center = [20.5937, 78.9629]  # India center
                m = folium.Map(location=map_center, zoom_start=5)
                
                # Add markers for institutions
                for idx, row in filtered_data.iterrows():
                    if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
                        popup_html = f"""
                        <div style="font-size: 14px; line-height: 1.6; width: 150px;">
                        <span style="color: orange; font-weight: bold;">Name:</span> {row['name']}<br>
                        <span style="color: orange; font-weight: bold;">City:</span> {row['city']}<br>
                        <span style="color: orange; font-weight: bold;">State:</span> {row['state']}</div>"""
                        folium.Marker(
                            location=[row['Latitude'], row['Longitude']], 
                            popup=popup_html,
                            tooltip=row['name']
                        ).add_to(m)

                folium_static(m, width=500, height=500)
        else:
            # Show overall India map
            map_center = [20.5937, 78.9629]
            m = folium.Map(location=map_center, zoom_start=5)
            
            for idx, row in df_institutions_1.iterrows():
                if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
                    popup_html = f"""
                    <div style="font-size: 14px; line-height: 1.6; width: 150px;">
                    <span style="color: orange; font-weight: bold;">Name:</span> {row['name']}<br>
                    <span style="color: orange; font-weight: bold;">City:</span> {row['city']}<br>
                    <span style="color: orange; font-weight: bold;">State:</span> {row['state']}</div>"""
                    folium.Marker(
                        location=[row['Latitude'], row['Longitude']], 
                        popup=popup_html,
                        tooltip=row['name']
                    ).add_to(m)
            
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