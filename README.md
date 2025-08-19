# ITI Visualization - Industrial Training Institutes in India

A comprehensive Streamlit web application for visualizing Industrial Training Institutes (ITIs) across India with interactive choropleth maps and statistical insights. This project includes a dataset with district, state, category type, ITI name, city, and geo-coordinates, enabling interactive maps, state-wise comparisons, and category-based insights into ITI distribution.

## 🌟 Features

- **Interactive Maps**: State and district-level visualization with color-coded choropleth maps
- **Data Filtering**: Select specific states to view detailed district-wise information
- **Multiple Data Sources**: Support for database, CSV upload, and sample data
- **Real-time Statistics**: View counts of private vs government institutions
- **Responsive Design**: Clean, professional interface with statistical cards

## 🗺️ Map Features

- **Color Grading**: Green for highest ITI counts, red for lowest (RdYlGn color scheme)
- **State Focus**: Click a state to see only that state's districts
- **Light Boundaries**: Subtle district and state boundaries for better readability
- **Tooltips**: Hover over regions to see institution counts

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Srikara-Satya/ITI_Visualization.git
   cd ITI_Visualization
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   ```bash
   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Open in browser**
   Navigate to `http://localhost:8501`

## 📊 Data Sources

The application supports three data sources (in priority order):

### 1. File Upload
- Upload CSV or Excel files directly through the web interface
- Required columns: `district`, `state`, `category_type`, `name`, `city`, `geo_location_coordinates`

### 2. PostgreSQL Database
- Configure database credentials in `.streamlit/secrets.toml`
- Automatically queries `training_institutes` table

### 3. Sample Data
- Falls back to `sample_institutions.csv` with 184+ institutions across all Indian states

## ⚙️ Configuration

### Database Setup (Optional)

Create `.streamlit/secrets.toml`:
```toml
[database.postgres]
dbname = "your_database_name"
user = "your_username"
password = "your_password"
host = "localhost"
port = "5432"
```

### Data Format

Your data should include these columns:
- `district`: District name
- `state`: State name
- `category_type`: "PRIVATE (P)" or "GOVERNMENT (G)"
- `name`: Institution name
- `city`: City name
- `geo_location_coordinates`: "latitude,longitude" format

## 📁 Project Structure

```
ITI_Visualization/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── sample_institutions.csv         # Sample data file
├── comprehensive_data.py           # Script to generate sample data
├── .streamlit/
│   └── secrets.toml               # Database configuration
└── shape_files/
    ├── district/
    │   └── DISTRICT_BOUNDARY.shp  # District shapefiles
    └── state/
        └── STATE_BOUNDARY.shp     # State shapefiles
```

## 🛠️ Dependencies

- **streamlit**: Web application framework
- **geopandas**: Geospatial data processing
- **pandas**: Data manipulation
- **folium**: Interactive maps
- **streamlit-folium**: Streamlit-Folium integration
- **psycopg2-binary**: PostgreSQL adapter

## 🌐 Sharing Your App

### Local Network
```bash
streamlit run app.py --server.address 0.0.0.0
```
Share: `http://YOUR_IP:8501`

### VS Code Port Forwarding
1. Run the app in VS Code terminal
2. Click "Make Public" when port notification appears
3. Share the generated URL

### Streamlit Community Cloud
1. Push code to GitHub
2. Deploy at [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository

## 📈 Usage

1. **View All States**: Default view shows India map with state-wise ITI counts
2. **Select State**: Use dropdown to focus on specific state districts
3. **Upload Data**: Use file uploader to visualize your own ITI data
4. **Analyze Statistics**: View private vs government institution counts in sidebar

## 🎨 Color Scheme

- **Green**: Highest number of institutions
- **Yellow**: Medium number of institutions
- **Red**: Lowest number of institutions
- **Light Gray**: Boundaries and borders

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check existing issues in the repository
2. Create a new issue with detailed description
3. Include error messages and steps to reproduce

## 🔄 Updates

- **v1.0**: Initial release with basic mapping functionality
- **v1.1**: Added file upload support and improved UI
- **v1.2**: Enhanced color schemes and state-focused views
