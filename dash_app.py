import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import random
from datetime import datetime
from collections import deque
import time

# =================================================================================
# --- UI REDESIGN CONFIGURATION: BRIGHT, AIRY, AND VIBRANT ---
# =================================================================================

# Color Palette: Bright, Clean, and Professional
ACCENT_PRIMARY = "#3A86FF"  # Bright Sky Blue (Main action/level data)
ACCENT_SECONDARY = "#FF6B6B"  # Vibrant Coral (Anomaly/Warning)
TEXT_DARK = "#333A40"  # Near-black for high contrast text
TEXT_MUTED = "#95A5A6"  # Soft Gray for secondary text
BG_LIGHT = "#F4F7F9"  # Lightest Blue-Gray Background
CARD_BG = "#FFFFFF"  # Pure White for floating cards
SUCCESS_COLOR = "#2ECC71"  # Emerald Green (Positive trend)
DANGER_COLOR = ACCENT_SECONDARY  # Use Coral for danger
WARNING_COLOR = "#FDCB6E"  # Soft Yellow/Orange (Low Alert)

# Enhanced Modern Shadow Configuration for depth
SOFT_SHADOW_SM = "0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.03)"
SOFT_SHADOW_MD = "0 6px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04)"
SOFT_SHADOW_LG = "0 15px 30px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.04)"

GRID_STYLE = {
    "background": BG_LIGHT,
    "minHeight": "100vh",
    "padding": "20px",
    "color": TEXT_DARK,
    "fontFamily": "Inter, sans-serif"
}

MAX_HISTORY_POINTS = 20

# --- NEW METRIC WEIGHTS ---
WEIGHT_LEVEL_DISPARITY = 0.4  # Weight for MTDI in P-Conflict
WEIGHT_RESILIENCE = 0.4  # Weight for HCRS in P-Conflict
# -------------------------

# =================================================================================
# --- DWLR SENSORS DATA (Distributed based on Foreign Border Criteria & Mainland Only) ---
# =================================================================================

# Status simulation options (weighted towards NORMAL)
STATUS_OPTIONS = ['NORMAL', 'NORMAL', 'NORMAL', 'NORMAL', 'LOW_ALERT', 'ANOMALY']

# --- Geospatial Data: Bounding Boxes for Indian States/UTs (Excluding Islands) ---
# Format: (Latitude Min, Latitude Max, Longitude Min, Longitude Max)
INDIAN_REGIONS = {
    # 5 Landlocked States (No Foreign Border/Coast) - HIGH DENSITY TARGET
    "Haryana": (27.5, 30.7, 74.5, 77.7),
    "Madhya Pradesh": (21.0, 26.9, 74.0, 82.8),
    "Chhattisgarh": (17.5, 23.5, 80.0, 84.0),
    "Jharkhand": (22.0, 25.5, 83.5, 88.0),
    "Telangana": (15.7, 19.5, 77.0, 81.8),

    # 27 Border/Coastal States/UTs - LOW DENSITY TARGET
    "Jammu and Kashmir (UT)": (32.5, 36.0, 73.5, 76.5),
    "Ladakh (UT)": (32.0, 36.5, 75.0, 80.0),
    "Himachal Pradesh": (30.0, 33.5, 75.5, 79.0),
    "Punjab": (29.5, 32.5, 73.5, 77.5),
    "Uttarakhand": (29.0, 31.5, 77.5, 81.0),
    "Delhi (NCT)": (28.3, 28.8, 76.8, 77.3),
    "Uttar Pradesh": (23.5, 31.0, 77.0, 84.8),
    "Chandigarh (UT)": (30.7, 30.8, 76.7, 76.8),
    "Rajasthan": (23.0, 30.0, 69.5, 78.5),
    "Gujarat": (20.0, 24.5, 68.0, 74.5),
    "Maharashtra": (15.5, 22.0, 72.5, 80.8),
    "Goa": (14.9, 15.9, 73.7, 74.5),
    "Daman, Diu, Dadra & Nagar Haveli (UT)": (20.0, 20.7, 72.8, 73.5),
    "Bihar": (24.0, 27.5, 83.5, 88.5),
    "West Bengal": (21.5, 27.5, 86.0, 89.5),
    "Odisha": (17.5, 22.5, 81.5, 87.5),
    "Andhra Pradesh": (12.5, 19.5, 77.0, 84.5),
    "Karnataka": (11.5, 18.5, 74.0, 78.5),
    "Kerala": (8.0, 12.8, 74.8, 77.5),
    "Tamil Nadu": (8.0, 13.5, 76.5, 80.5),
    "Puducherry (UT)": (11.8, 12.0, 79.8, 80.0),
    "Sikkim": (27.0, 28.0, 88.0, 88.8),
    "Arunachal Pradesh": (26.5, 29.5, 91.5, 97.0),
    "Assam": (24.5, 27.8, 89.8, 96.0),
    "Meghalaya": (25.0, 26.0, 90.0, 92.5),
    "Nagaland": (25.0, 27.0, 93.5, 95.5),
    "Manipur": (23.8, 25.7, 93.0, 95.0),
    "Mizoram": (21.5, 24.5, 92.2, 93.5),
    "Tripura": (22.5, 24.5, 91.0, 92.5),
}
MOCK_STATES = list(INDIAN_REGIONS.keys())  # 32 regions total (5 landlocked + 27 border/coastal)

# --- Categorization for Distribution Logic ---
LANDLOCKED_STATES = ["Haryana", "Madhya Pradesh", "Chhattisgarh", "Jharkhand", "Telangana"]
COASTAL_BORDER_REGIONS = [state for state in MOCK_STATES if state not in LANDLOCKED_STATES]

# Original Real Station Data (kept for consistency)
RAW_STATION_DATA = [
    {"Agency_Name": "Andhra Pradesh GW", "State_Name": "Andhra Pradesh", "District_Name": "KURNOOL",
     "Tahsil_Name": "KURNOOL", "Station_Name": "KURNOOL -AWS", "Latitude": 15.75064, "Longitude": 78.0668,
     "Station_Type": "SURFACE", "Station_Status": "INSTALLED"},
    {"Agency_Name": "Tamil Nadu GW", "State_Name": "Tamil Nadu", "District_Name": "CHENNAI",
     "Tahsil_Name": "CHENNAI", "Station_Name": "CHENNAI -CITY", "Latitude": 13.0827, "Longitude": 80.2707,
     "Station_Type": "GROUND", "Station_Status": "INSTALLED"},
    {"Agency_Name": "Maharashtra GW", "State_Name": "Maharashtra", "District_Name": "PUNE",
     "Tahsil_Name": "PUNE", "Station_Name": "PUNE -WEST", "Latitude": 18.5204, "Longitude": 73.8567,
     "Station_Type": "GROUND", "Station_Status": "INSTALLED"},
]
NUM_REAL_STATIONS = len(RAW_STATION_DATA)  # 3 real stations

# --- Distribution Logic based on User Request ---
TOTAL_TARGET_DOTS = 1000  # Max limit
TARGET_LANDLOCKED = 100
TARGET_COASTAL_BORDER = 20
TOTAL_MOCK_DOTS = TARGET_LANDLOCKED + TARGET_COASTAL_BORDER  # 120 total mock dots

# Ensure the total is under 1000
TOTAL_DOTS = NUM_REAL_STATIONS + TOTAL_MOCK_DOTS  # 3 + 120 = 123
NUM_RANDOM_STATIONS = TOTAL_DOTS - NUM_REAL_STATIONS  # 120 random stations to generate

# Allocation
ALLOCATION = {}

# 1. Landlocked States (100 dots / 5 states = 20 dots per state)
points_per_landlocked = TARGET_LANDLOCKED // len(LANDLOCKED_STATES)  # 100 / 5 = 20
landlocked_remainder = TARGET_LANDLOCKED % len(LANDLOCKED_STATES)  # 0

for state in LANDLOCKED_STATES:
    ALLOCATION[state] = points_per_landlocked  # 20 per state

# 2. Coastal/Border Regions (20 dots / 27 regions = 0.74 dots per region, rounded down to 0, 20 remainders)
points_per_coastal_border_base = TARGET_COASTAL_BORDER // len(COASTAL_BORDER_REGIONS)  # 20 / 27 = 0
coastal_border_remainder = TARGET_COASTAL_BORDER % len(COASTAL_BORDER_REGIONS)  # 20

# Distribute the 20 remainder points to the first 20 Coastal/Border regions (1 dot each)
for idx, state in enumerate(COASTAL_BORDER_REGIONS):
    ALLOCATION[state] = points_per_coastal_border_base + (1 if idx < coastal_border_remainder else 0)


# Sanity Check (Total random points): sum(ALLOCATION.values()) must be 120
# print(f"Total Allocated Dots: {sum(ALLOCATION.values())}") # Should be 120

# --- Function to generate random mock stations within a state's bounding box ---
def generate_random_station(i, state_name):
    """Generates a mock station entry, forcing the location to be within the state/UT bounding box."""

    region_key = state_name if state_name in INDIAN_REGIONS else random.choice(MOCK_STATES)
    lat_min, lat_max, lon_min, lon_max = INDIAN_REGIONS[region_key]

    lat = round(random.uniform(lat_min, lat_max), 5)
    lon = round(random.uniform(lon_min, lon_max), 5)

    station_name = f"MOCK-{state_name.split()[0].upper()}-{i}"

    return {
        "Agency_Name": "Mock Network", "State_Name": region_key,
        "District_Name": f"Mock District {i % 10}",
        "Tahsil_Name": "Mock Tahsil", "Station_Name": station_name,
        "Latitude": lat, "Longitude": lon,
        "Station_Type": random.choice(["GROUND", "SURFACE"]),
        "Station_Status": "INSTALLED"
    }


# --- Generate Stations based on Allocation ---
RANDOM_STATIONS = []
station_counter = 0

for state, num_points in ALLOCATION.items():
    for i in range(num_points):
        RANDOM_STATIONS.append(generate_random_station(station_counter, state))
        station_counter += 1

# Combine real and random data sources
ALL_RAW_STATIONS = RAW_STATION_DATA + RANDOM_STATIONS  # Total 123 stations

# Transform and enrich data for the dashboard (rest of the data preparation logic is unchanged)
MOCK_DWLR_SENSORS = []
STATION_IDS = []

for i, item in enumerate(ALL_RAW_STATIONS):
    # Create a clean, unique ID
    station_id = f"{item['Station_Name'].replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '').upper()}_{i}"

    # Simulate data needed for the live dashboard logic
    # Ensure the State name is clean for the mock data
    state_name = item['State_Name'].replace(' (UT)', '').replace(' (NCT)', '')
    simulated_status = random.choice(STATUS_OPTIONS) if 'MOCK-' in item['Station_Name'] else STATUS_OPTIONS[
        i % len(STATUS_OPTIONS)]
    # Simulate water level around the 100m mark for consistent charting
    simulated_level = round(100.0 + random.uniform(-5.0, 5.0), 2)

    MOCK_DWLR_SENSORS.append({
        'id': station_id,
        'lat': item['Latitude'],
        'lon': item['Longitude'],
        'status': simulated_status,
        'level': simulated_level,
        'type': item['Station_Type'],
        'Station_Name_Full': item['Station_Name'],
        'District': item['District_Name'],
        'Tahsil': item['Tahsil_Name'],
        'State': item['State_Name']  # Include Full State/UT name for better hover text
    })
    STATION_IDS.append(station_id)

# --- DROPDOWN FIX: Refactor for clear labels and dramatically reduced size ---
# --- FIX: Reducing to 100 entries for stability ---
# Since total stations is 123, we can safely sample up to 100.
DROPDOWN_SAMPLE_SIZE = min(100, len(MOCK_DWLR_SENSORS))
SAMPLED_STATIONS = MOCK_DWLR_SENSORS[:DROPDOWN_SAMPLE_SIZE]

DROPDOWN_OPTIONS = [
    {
        # Ensure label is a single, clean string
        'label': f"{s['Station_Name_Full']} ({s['State']})",
        'value': s['id']
    }
    for s in SAMPLED_STATIONS
]


# ----------------------------------------------------------------


# =================================================================================
# --- DATA FETCHING AND PROCESSING (Functionality is preserved) ---
# =================================================================================

def get_station_by_id(station_id):
    """Retrieves the full sensor data for the selected ID."""
    for sensor in MOCK_DWLR_SENSORS:
        if sensor['id'] == station_id:
            return sensor
    # Fallback if the selected station isn't found in the mock list (shouldn't happen with the fix)
    return MOCK_DWLR_SENSORS[0] if MOCK_DWLR_SENSORS else None


def generate_live_data(last_level, selected_station_id, override_rainfall_str):
    """
    MOCK data generation for the dashboard, linked to the properties of the
    selected real station.
    """
    selected_station = get_station_by_id(selected_station_id)
    if not selected_station:
        # Fallback to a default station if the selected one is not found
        selected_station = MOCK_DWLR_SENSORS[0]

    # Initial level or last level from history
    if not selected_station:
        selected_station = MOCK_DWLR_SENSORS[0]

    last_level = selected_station.get('level', 100.0)

    # --- MOCK DATA SIMULATION ---
    # Slight variation on the initial level
    water_level = round(last_level + random.uniform(-0.1, 0.1), 2)
    water_level = max(95.0, min(105.0, water_level))

    rainfall_factor = 0.0
    try:
        override_rainfall = float(override_rainfall_str) if override_rainfall_str is not None else 0.0
        # Rainfall impact: 10mm of simulated rain increases level by 0.5m
        rainfall_factor = override_rainfall * 0.05
    except (ValueError, TypeError):
        override_rainfall = 0.0
        pass

    # Basic daily change simulation
    level_change_base = random.uniform(-0.5, 0.75)
    next_day_level = round(water_level + level_change_base + rainfall_factor, 2)
    next_day_level = max(95.0, min(105.0, next_day_level))  # Keep within bounds

    rainfall = round(random.uniform(0, 5) + override_rainfall, 2)
    avg_temp = round(random.uniform(20, 35), 1)
    pet = round(random.uniform(3, 7), 2)

    # Simplified MTDI/HCRS calculation for mock data
    mtdi = round(abs(water_level - 100) * 0.1 + random.uniform(0.05, 0.2), 4)  # Index of Disparity (higher is worse)
    hcrs = round((105.0 - water_level) / 0.1, 0)  # Resilience Score (lower is worse, based on max 105)
    hcrs = max(0, min(100, hcrs))

    risk_proba = random.uniform(0.1, 0.75)
    is_anomaly = "FALSE"
    anomaly_score = round(random.uniform(0.01, 0.1), 4)
    if water_level < 97.0 or selected_station['status'] == 'ANOMALY':  # Link to initial status
        risk_proba = random.uniform(0.75, 0.95)
        is_anomaly = "TRUE"
        anomaly_score = round(random.uniform(0.5, 0.9), 4)

    # --- NEW: P-Conflict Score Calculation ---
    # Simulate a population density factor (higher for lower Lat/Lon range - denser areas)
    lat = selected_station['lat']
    lon = selected_station['lon']
    # Higher density factor for southern and eastern areas (mock simulation)
    density_base = 0.05
    if lat < 20 and lon > 78: density_base = 0.3

    pop_density_factor = density_base + random.uniform(0.0, 0.1)

    # Formula: MTDI (Disparity) * Weight + (100-HCRS) (Vulnerability) * Weight + PopDensityFactor
    p_conflict_score = (mtdi * WEIGHT_LEVEL_DISPARITY) + \
                       ((100 - hcrs) / 100 * WEIGHT_RESILIENCE) + \
                       pop_density_factor
    p_conflict_score = round(min(1.0, p_conflict_score), 4)  # Cap at 1.0

    # Simulate Sensor Trust Index (STI)
    # STI is penalized by high Anomaly Score and a random data gap factor
    data_gap_factor = random.uniform(0.0, 0.1)  # Mock factor for data gaps/jitter
    sti = round(100.0 - (anomaly_score * 500) - (data_gap_factor * 10), 0)
    sti = max(0, min(100, sti))
    # --- END NEW: P-Conflict Score Calculation ---

    # Update the level in the MOCK_DWLR_SENSORS list for consistency
    selected_station['level'] = water_level

    # --- END MOCK DATA SIMULATION ---

    return {
        "Real_Time_Input": {
            "water_level": water_level, "rainfall_mm": rainfall, "avg_temp_c": avg_temp,
            "pet_mm": pet,
            "station_type": selected_station['type'],
            "district": selected_station['District'],
            "elevation": 150 + random.randint(-10, 10),
            "lat": selected_station['lat'], "lon": selected_station['lon']
        },
        "Water_Level_Prediction": {"Next_Day_Level": next_day_level},
        "Drought_Risk_Index": {"Probability_Critical_Drop": risk_proba},
        "Estimated_Recharge": {"30_Day_Net_Change": round(random.uniform(-3.0, 3.0), 2)},
        "Simulated_Extraction": {"Rate": round(random.uniform(5.0, 15.0), 2)},
        "Anomaly_Check": {"Is_Anomaly": is_anomaly, "Score": anomaly_score},
        "MTDI": mtdi,
        "HCRS": hcrs,
        "PConflict": p_conflict_score,  # <-- ADDED
        "STI": sti  # <-- ADDED
    }


# =================================================================================
# --- DASHBOARD COMPONENTS (REDESIGNED) ---
# =================================================================================

def get_color_and_icon(delta_value, base_color_name, custom_metric=None):
    """Maps color name to hex value and determines the icon."""
    color_map = {'success': SUCCESS_COLOR, 'danger': DANGER_COLOR, 'warning': WARNING_COLOR, 'primary': ACCENT_PRIMARY}

    # Custom color logic for MTDI/HCRS/PConflict/STI
    if custom_metric == 'MTDI':
        # Delta value here is the index itself (higher is worse)
        color = DANGER_COLOR if delta_value > 0.5 else (WARNING_COLOR if delta_value > 0.3 else SUCCESS_COLOR)
        return color, '⚡'
    elif custom_metric == 'HCRS':
        # Delta value here is the score itself (lower is worse)
        color = DANGER_COLOR if delta_value < 50 else (WARNING_COLOR if delta_value < 75 else SUCCESS_COLOR)
        return color, '💡'
    elif custom_metric == 'PConflict':  # <--- NEW LOGIC
        # Score is 0 to 1 (higher is worse)
        color = DANGER_COLOR if delta_value > 0.6 else (WARNING_COLOR if delta_value > 0.3 else SUCCESS_COLOR)
        return color, '🔥'
    elif custom_metric == 'STI':  # <--- NEW LOGIC
        # Score is 0 to 100 (lower is worse)
        color = DANGER_COLOR if delta_value < 80 else (WARNING_COLOR if delta_value < 90 else SUCCESS_COLOR)
        return color, '🛡️'

    # Standard delta logic
    if delta_value is None:
        return color_map.get(base_color_name, TEXT_MUTED), '—'

    color = color_map.get(base_color_name, TEXT_MUTED)
    icon = '▲' if delta_value > 0 else ('▼' if delta_value < 0 else '—')
    return color, icon


def create_metric_card(title, value, unit="", delta_value=None, delta_color_name="primary", icon_emoji="📊",
                       custom_metric=None):
    # Pass the raw numeric delta value to get_color_and_icon
    delta_hex_color, icon = get_color_and_icon(delta_value, delta_color_name, custom_metric)

    # Format the main value (this is what gets displayed)
    display_value = f"{value}"

    delta_text = html.Div()
    if delta_value is not None:
        delta_sign = '+' if delta_value > 0 else ''

        # Logic for the bottom line of the card
        if custom_metric == 'STI':
            status_text = "Integrity Compromised" if delta_value < 80 else (
                "Review Data Source" if delta_value < 90 else "Data Trusted")
            delta_text = html.Span(
                [
                    html.Span(icon, className="me-1"),
                    status_text
                ],
                style={'color': delta_hex_color, 'fontSize': '0.9rem', 'fontWeight': '600'}
            )
        elif custom_metric == 'PConflict':
            status_text = "High Conflict Risk" if delta_value > 0.6 else (
                "Moderate Tension" if delta_value > 0.3 else "Low Tension")
            delta_text = html.Span(
                [
                    html.Span(icon, className="me-1"),
                    status_text
                ],
                style={'color': delta_hex_color, 'fontSize': '0.9rem', 'fontWeight': '600'}
            )
        elif custom_metric == 'MTDI':
            status_text = "Critical Disparity" if delta_value > 0.5 else (
                "Watch Trend" if delta_value > 0.3 else "Stable Trend")
            delta_text = html.Span(
                [
                    html.Span(icon, className="me-1"),
                    status_text
                ],
                style={'color': delta_hex_color, 'fontSize': '0.9rem', 'fontWeight': '600'}
            )
        elif custom_metric == 'HCRS':
            status_text = "High Risk" if delta_value < 50 else ("Moderate Risk" if delta_value < 75 else "Low Risk")
            delta_text = html.Span(
                [
                    html.Span(icon, className="me-1"),
                    status_text
                ],
                style={'color': delta_hex_color, 'fontSize': '0.9rem', 'fontWeight': '600'}
            )
        else:
            # Standard delta display (for prediction and recharge)
            delta_text = html.Span(
                [
                    html.Span(icon, className="me-1"),
                    f"{delta_sign}{delta_value:.2f} {unit} (24hr)"
                ],
                style={'color': delta_hex_color, 'fontSize': '0.9rem', 'fontWeight': '600'}
            )

    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.Div([
                        html.Span(icon_emoji, style={'fontSize': '1.5rem', 'color': delta_hex_color}),
                        html.P(title, className="mb-0 ms-2",
                               style={"fontSize": "1.0rem", "color": TEXT_MUTED, "fontWeight": 500}),
                    ], className="d-flex align-items-center mb-2"),

                    html.Div([
                        html.Span(
                            display_value,
                            style={"color": TEXT_DARK, "fontWeight": "900", "fontSize": "2.5rem"}
                        ),
                        html.Span(
                            f" {unit}",
                            style={"color": TEXT_MUTED, "fontWeight": "500", "fontSize": "1.1rem", "marginLeft": "5px"}
                        )
                    ], className="d-flex align-items-baseline mb-2"),

                    # Delta/Status area
                    delta_text,
                ],
                style={"padding": "20px"}
            )
        ],
        className="border-0 hover-lift",
        style={
            "borderRadius": "18px",
            "backgroundColor": CARD_BG,
            "boxShadow": SOFT_SHADOW_MD,
            "transition": "all 0.3s ease",
            "borderLeft": f"5px solid {delta_hex_color}"
        },
    )


# =================================================================================
# --- APPLICATION LAYOUT (REDESIGNED) ---
# =================================================================================

# Use the lighter, more modern Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Custom CSS for the "better than Figma" look
custom_css = f"""
.hover-lift:hover {{
    transform: translateY(-5px);
    box-shadow: {SOFT_SHADOW_LG};
}}
.card-title-redesign {{
    font-size: 1.5rem;
    font-weight: 700;
    color: {ACCENT_PRIMARY};
    margin-bottom: 1.5rem;
    border-bottom: 2px solid {BG_LIGHT};
    padding-bottom: 10px;
}}
/* Standard Dash/Plotly classes */
.dash-dropdown .Select-control {{
    border-radius: 8px !important;
    border-color: {BG_LIGHT} !important;
    box-shadow: {SOFT_SHADOW_SM};
    height: 50px !important; /* Set the height of the header box to 50px as requested */
}}
/* Dropdown specific fix for label width */
.dash-dropdown .Select-value-label {{
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
.input-redesign {{
    border-radius: 8px !important;
    border: 1px solid {BG_LIGHT} !important;
    padding: 10px !important;
    font-size: 1.1rem !important;
    box-shadow: {SOFT_SHADOW_SM};
}}
.input-redesign:focus {{
    border-color: {ACCENT_PRIMARY} !important;
    box-shadow: 0 0 0 0.25rem {ACCENT_PRIMARY}30 !important;
}}

/* Fix for header text wrapping issue */
.header-titles h1 {{
    white-space: normal;
    word-break: break-word;
    line-height: 1.2;
    /* Ensure color is high contrast for loading */
    color: {TEXT_DARK} !important;
}}

@media (min-width: 992px) {{ /* Bootstrap lg breakpoint and up */
    .header-titles h1 {{
        white-space: nowrap;
    }}
}}
"""

app.index_string = f"""
<!DOCTYPE html>
<html>
    <head>
        {{%metas%}}
        <title>{{%title%}}</title>
        {{%favicon%}}
        {{%css%}}
        <style>{custom_css}</style>
    </head>
    <body>
        {{%app_entry%}}
        <footer>
            {{%config%}}
            {{%scripts%}}
            {{%renderer%}}
        </footer>
    </body>
</html>
"""

app.layout = html.Div(style=GRID_STYLE, children=[
    # 1. Real-Time Interval
    dcc.Interval(
        id='interval-component',
        interval=1 * 1000,
        n_intervals=0
    ),

    dcc.Store(
        id='water-level-history',
        data={'time': [], 'current_level': [], 'predicted_level': []}
    ),

    dbc.Container([
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Div([
                                        html.H1(
                                            "Aqua-Sight | DWLR CONSOLE",
                                            className="mb-1",

                                            style={"color": ACCENT_PRIMARY, "fontWeight": "900", "letterSpacing": "1px",
                                                   "fontSize": "2.8rem"}
                                        ),
                                        html.P(
                                            "Real-Time Subsurface Water Dynamics and Predictive Forecasting",
                                            style={"fontSize": "1.2rem", "color": TEXT_MUTED}
                                        )
                                    ], className="header-titles"),
                                    align="center",
                                    width={"size": 12, "md": 8}
                                ),

                                # Station Selector (Right Side)
                                dbc.Col(
                                    dcc.Dropdown(
                                        id='station-selector',
                                        # DROPDOWN FIX: Use the prepared options list (now reduced to 100 for stability)
                                        options=DROPDOWN_OPTIONS,
                                        value=MOCK_DWLR_SENSORS[0]['id'],  # Use the ID of the first sampled station
                                        clearable=False,
                                        className="dash-dropdown",
                                        style={"minWidth": "500px"}
                                    ),
                                    className="d-flex align-items-center justify-content-md-end mt-3 mt-md-0",
                                    align="center",
                                    width={"size": 8, "md": 8}
                                )
                            ],
                            className="g-0 align-items-center"
                        )
                    ),
                    className="border-0 hover-lift",
                    style={
                        "borderRadius": "20px",
                        "boxShadow": SOFT_SHADOW_LG
                    }
                ),
                width=12
            ),
            className="mb-4"
        ),

        # Status and Real-Time Metrics Row
        dbc.Row([
            dbc.Col(
                html.Div(id='status-message', className="p-3 mb-4",
                         style={"borderRadius": "10px", "fontWeight": "700"}),
                width=12
            ),
            dbc.Row(id='real-time-metrics-row', className="mb-5 g-4"),  # g-4 for consistent spacing
        ]),

        # --- Primary Forecast and Simulation Section ---
        html.H4("Forecasting & Risk Assessment", className="card-title-redesign"),
        dbc.Row([
            # Left Column: Prediction Metrics
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H5("Primary Forecast Vector", style={'color': TEXT_DARK, 'fontWeight': 600}),
                        dbc.Row(id='prediction-metrics-row', className="mt-3 g-3"),
                    ]),
                    className="border-0 hover-lift",
                    style={"backgroundColor": CARD_BG, "borderRadius": "18px", "boxShadow": SOFT_SHADOW_MD}
                ),
                lg=8, className="mb-4 mb-lg-0"
            ),
            # Right Column: "What If" Simulation Control
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H5("🧪 'What If' Simulation", className="card-title", style={'color': ACCENT_PRIMARY}),
                        html.P("Simulated 24hr Rainfall (mm):", className="mb-2",
                               style={'color': TEXT_DARK, 'fontWeight': 500}),
                        dcc.Input(
                            id='what-if-rainfall-input',
                            type='number',
                            value=0.0,
                            placeholder="Enter rainfall in mm",
                            min=0.0,
                            className="input-redesign",
                            style={'width': '100%'}
                        ),
                        html.Small("The 24hr forecast level instantly adapts to this input.",
                                   className="text-muted mt-2 d-block")
                    ]),
                    className="border-0 hover-lift",
                    style={
                        "backgroundColor": CARD_BG,
                        "borderRadius": "18px",
                        "border": f"3px solid {WARNING_COLOR}",  # Highlight this section
                        "boxShadow": SOFT_SHADOW_MD
                    }
                ),
                lg=4
            )
        ], className="mb-5 g-4"),

        # Core Analytics: Chart and Complex Metrics
        html.H4("Core Analytical Dashboard", className="card-title-redesign"),
        dbc.Row([
            # Live Chart
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H5("Water Level Trajectory (Last 20 Readings)",
                                style={'color': TEXT_DARK, 'fontWeight': 600}),
                        dcc.Graph(id='water-level-chart', config={'displayModeBar': False}, style={'height': '350px'})
                    ]),
                    className="border-0 hover-lift",
                    style={"backgroundColor": CARD_BG, "borderRadius": "18px", "boxShadow": SOFT_SHADOW_MD}
                ),
                lg=8, className="mb-4 mb-lg-0"
            ),
            # Unique Metrics (MTDI, HCRS, P-Conflict, STI)
            dbc.Col(
                # Updated layout to fit the four unique metric cards
                dbc.Row([
                    dbc.Col(html.Div(id='hcrs-card'), md=6, className="mb-4"),
                    dbc.Col(html.Div(id='mtdi-card'), md=6, className="mb-4"),
                    dbc.Col(html.Div(id='pconflict-card'), md=6, className="mb-md-0"),  # NEW CARD 1
                    dbc.Col(html.Div(id='sti-card'), md=6, className="mb-md-0"),  # NEW CARD 2
                ], className="g-4"),
                lg=4
            )
        ], className="mb-5 g-4"),

        # Geospatial Monitoring Array (Map)
        html.H4("Geospatial Network Monitor (Mainland Distribution)", className="card-title-redesign"),
        dbc.Row([
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        # IMPORTANT: displayModeBar=True (default) or not explicitly set allows zoom/pan controls
                        dcc.Graph(id='dwlr-map', style={'height': '65vh'})
                    ]),
                    className="border-0 hover-lift",
                    style={"backgroundColor": CARD_BG, "borderRadius": "18px", "boxShadow": SOFT_SHADOW_LG}
                ),
                width=12
            )
        ], className="mb-5"),

        # Detailed Report Section
        html.H4("System Integrity Report", className="card-title-redesign"),
        dbc.Row([
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.Div(id='detailed-report', style={'color': TEXT_DARK})
                    ]),
                    className="border-0 hover-lift",
                    style={"backgroundColor": CARD_BG, "borderRadius": "18px", "boxShadow": SOFT_SHADOW_MD}
                ),
                width=12
            )
        ])
    ], fluid=True)
])


# =================================================================================
# --- DASH CALLBACKS (Functionality is preserved) ---
# =================================================================================

# 1. Callback to Fetch Data and Update Metrics/Store
@app.callback(
    [Output('status-message', 'children'),
     Output('real-time-metrics-row', 'children'),
     Output('prediction-metrics-row', 'children'),
     Output('detailed-report', 'children'),
     Output('water-level-history', 'data'),
     Output('mtdi-card', 'children'),
     Output('hcrs-card', 'children'),
     Output('pconflict-card', 'children'),  # <--- ADDED
     Output('sti-card', 'children')],  # <--- ADDED
    [Input('interval-component', 'n_intervals')],
    [State('station-selector', 'value'),
     State('water-level-history', 'data'),
     State('what-if-rainfall-input', 'value')]
)
def update_dashboard(n, selected_station_id, current_history, what_if_rainfall_input):
    """Fetches data (mock/live), applies 'What If' scenario, and updates all dashboard components."""

    current_time = datetime.now().strftime('%H:%M:%S')

    # Initial level or last level from history
    last_level = 100.0
    if current_history and current_history.get('current_level') and current_history['current_level']:
        last_level = current_history['current_level'][-1]

    # Initialize deques if not present or to ensure max length
    if not current_history:
        current_history = {'time': [], 'current_level': [], 'predicted_level': []}

    history_deques = {k: deque(current_history[k], maxlen=MAX_HISTORY_POINTS) for k in current_history}

    # --- DATA FETCHING STEP: CALL THE LIVE CONNECTOR ---
    results = generate_live_data(
        last_level=last_level,
        selected_station_id=selected_station_id,
        override_rainfall_str=what_if_rainfall_input  # Pass the numeric/string input directly
    )
    # ---------------------------------------------------

    # Get the station's full details for display
    current_station_details = get_station_by_id(selected_station_id)
    if not current_station_details:
        # Fallback to the first station if the selected one is not found (e.g. if a sampled one was removed)
        current_station_details = MOCK_DWLR_SENSORS[0]

    station_name_display = current_station_details['Station_Name_Full']

    # --- 1. Prepare Data & Update Historical Store ---
    input_data = results["Real_Time_Input"]
    water_level = input_data['water_level']
    next_day_level = results['Water_Level_Prediction']['Next_Day_Level']

    history_deques['time'].append(current_time)
    history_deques['current_level'].append(water_level)
    history_deques['predicted_level'].append(next_day_level)

    # Convert deques back to lists for dcc.Store
    new_history = {k: list(v) for k, v in history_deques.items()}

    # --- 2. Real-Time Inputs Row ---
    # Metric cards with new styling
    # NOTE: Passing None for delta_value here, as it's the current reading.
    real_time_children = [
        dbc.Col(create_metric_card("Water Level", f"{water_level:.2f}", unit="m", icon_emoji="💧", delta_value=None),
                lg=3, md=6),
        dbc.Col(create_metric_card("Rainfall", f"{input_data['rainfall_mm']:.2f}", unit="mm", icon_emoji="🌧️",
                                   delta_value=None), lg=3, md=6),
        dbc.Col(create_metric_card("Temperature", f"{input_data['avg_temp_c']:.1f}", unit="°C", icon_emoji="🌡️",
                                   delta_value=None), lg=3, md=6),
        dbc.Col(create_metric_card("Evapotranspiration", f"{input_data['pet_mm']:.2f}", unit="mm", icon_emoji="💨",
                                   delta_value=None), lg=3, md=6),
    ]

    # --- 3. Unique Metrics Cards ---

    # MTDI Card Logic (Index of Disparity, higher = worse)
    mtdi = results["MTDI"]
    mtdi_card = create_metric_card(
        "Trend Disparity Index (MTDI)",
        f"{mtdi:.4f}", unit="",
        delta_value=mtdi,  # Pass the raw numeric value
        custom_metric='MTDI'
    )

    # HCRS Card Logic (Resilience Score, lower = worse)
    hcrs = results["HCRS"]
    hcrs_card = create_metric_card(
        "Resilience Score (HCRS)",
        f"{hcrs:.0f}", unit="/ 100",
        delta_value=float(hcrs),  # Pass the raw numeric value
        custom_metric='HCRS'
    )

    # NEW: P-Conflict Card
    p_conflict = results["PConflict"]
    p_conflict_card = create_metric_card(
        "Predicted Conflict Score",
        f"{p_conflict:.4f}", unit="",
        delta_value=p_conflict,
        custom_metric='PConflict'  # <--- Pass the new metric type
    )

    # NEW: STI Card
    sti_score = results["STI"]
    sti_card = create_metric_card(
        "Sensor Trust Index (STI)",
        f"{sti_score:.0f}", unit="/ 100",
        delta_value=float(sti_score),
        custom_metric='STI'  # <--- Pass the new metric type
    )

    # --- 4. Prediction Metrics Row ---

    # Next Day Level Logic
    level_change = next_day_level - water_level
    prediction_delta_color = 'success' if level_change >= 0 else 'danger'

    # Drought Risk Logic
    risk_proba = results['Drought_Risk_Index']['Probability_Critical_Drop']
    risk_color = 'success'
    if risk_proba > 0.7:
        risk_color = 'danger'
    elif risk_proba > 0.4:
        risk_color = 'warning'

    # 30-Day Recharge Logic
    recharge_net_change = results['Estimated_Recharge']['30_Day_Net_Change']
    recharge_color = 'success' if recharge_net_change >= 0 else 'danger'

    prediction_children = [
        dbc.Col(create_metric_card(
            "24hr Level Forecast",
            f"{next_day_level:.2f}",
            unit="m",
            delta_value=level_change,  # Pass the raw numeric value
            delta_color_name=prediction_delta_color,
            icon_emoji="🔮"
        ), md=4),
        dbc.Col(create_metric_card(
            "Drought Risk Probability",
            f"{risk_proba * 100:.1f}%",
            unit="",
            delta_value=risk_proba,  # Pass the raw numeric value (for color/status logic)
            delta_color_name=risk_color,
            icon_emoji="⚠️"
        ), md=4),
        dbc.Col(create_metric_card(
            "30-Day Net Recharge",
            f"{recharge_net_change:.2f}",
            unit="m",
            delta_value=recharge_net_change,  # Pass the raw numeric value
            delta_color_name=recharge_color,
            icon_emoji="📈"
        ), md=4),
    ]

    # --- 5. Detailed Report ---
    anomaly_status = results['Anomaly_Check']['Is_Anomaly']
    anomaly_score = results['Anomaly_Check']['Score']
    anomaly_color = DANGER_COLOR if anomaly_status == 'TRUE' else SUCCESS_COLOR

    report_content = html.Div([
        html.Div([
            html.Span("Data Feed Time:", className="fw-bold me-2"),
            html.Span(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        ], className="mb-2"),
        html.Div([
            html.Span("Station:", className="fw-bold me-2"),
            html.Span(f"{station_name_display} ({current_station_details['State']})")
        ], className="mb-2"),
        html.Div([
            html.Span("Type/Elevation:", className="fw-bold me-2"),
            html.Span(f"{current_station_details['type']} / {input_data['elevation']}m")
        ], className="mb-2"),
        html.Div([
            html.Span("Anomaly Check:", className="fw-bold me-2"),
            html.Span(f"{anomaly_status} (Score: {anomaly_score:.4f})",
                      style={'fontWeight': 'bold', 'color': anomaly_color, 'padding': '4px 8px', 'borderRadius': '6px',
                             'backgroundColor': anomaly_color + '15'})
        ], className="mb-2"),
        html.Div([
            html.Span("Simulated Extraction Rate:", className="fw-bold me-2"),
            html.Span(f"{results['Simulated_Extraction']['Rate']:.2f} m³/day")
        ], className="mb-2"),
    ], style={'lineHeight': '1.6', 'fontSize': '0.95rem'})

    # Status Message (Colored Bar)
    if anomaly_status == 'TRUE':
        status_message_text = "⚠️ CRITICAL ALERT: Anomaly Detected. Immediate action required for "
        status_message_bg = DANGER_COLOR + '20'
        status_message_color = DANGER_COLOR
    else:
        status_message_text = "✅ System Operational: Data feed active and stable for "
        status_message_bg = SUCCESS_COLOR + '20'
        status_message_color = SUCCESS_COLOR

    status_message = html.P(
        [
            html.Span(status_message_text),
            html.Span(f"{station_name_display}.", style={'fontWeight': 'bold', 'textDecoration': 'underline'}),
            html.Span(f" Last updated: {current_time}"),
        ],
        style={
            'color': status_message_color,
            'backgroundColor': status_message_bg,
            'padding': '12px 15px',
            'borderRadius': '10px',
            'fontWeight': 500,
            'marginBottom': '0'
        }
    )

    return (
        status_message,
        real_time_children,
        prediction_children,
        report_content,
        new_history,
        html.Div(mtdi_card),
        html.Div(hcrs_card),
        html.Div(p_conflict_card),  # <--- ADDED
        html.Div(sti_card)  # <--- ADDED
    )


# 2. Callback to Update the Time-Series Chart
@app.callback(
    Output('water-level-chart', 'figure'),
    [Input('water-level-history', 'data')]
)
def update_graph_live(history_data):
    """Creates the Plotly figure from the dcc.Store data with refined styling."""

    fig = go.Figure()

    # Current Water Level Line (Vibrant Blue)
    fig.add_trace(go.Scatter(
        x=history_data['time'],
        y=history_data['current_level'],
        name='Current Level (m)',
        line=dict(color=ACCENT_PRIMARY, width=4, dash='solid'),
        mode='lines+markers',
        marker=dict(size=7, symbol='circle', color=CARD_BG, line=dict(width=2, color=ACCENT_PRIMARY))
    ))

    # Predicted Water Level Line (Soft Coral/Orange)
    fig.add_trace(go.Scatter(
        x=history_data['time'],
        y=history_data['predicted_level'],
        name='Predicted Next Day Level (Simulated)',
        line=dict(color=ACCENT_SECONDARY, width=2, dash='dash'),
        mode='lines',
        opacity=0.7
    ))

    all_levels = history_data['current_level'] + history_data['predicted_level']
    if all_levels:
        y_min = min(all_levels) - 0.5
        y_max = max(all_levels) + 0.5
    else:
        y_min, y_max = 95.0, 105.0

    fig.update_layout(
        title=None,  # Title moved to HTML header for better integration
        xaxis_title='Time of Reading',
        yaxis_title='Water Level (meters)',
        plot_bgcolor=CARD_BG,
        paper_bgcolor=CARD_BG,
        font=dict(color=TEXT_DARK, size=11),
        margin=dict(l=40, r=20, t=10, b=40),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.0,
            xanchor="left",
            x=0,
            bgcolor='rgba(255,255,255,0.7)',
            bordercolor=BG_LIGHT,
            borderwidth=1,
            font=dict(size=10)
        ),
        yaxis=dict(
            range=[y_min, y_max],
            fixedrange=True,
            gridcolor=BG_LIGHT,
            zerolinecolor=BG_LIGHT,
            showline=False
        ),
        xaxis=dict(
            showgrid=False,
            showline=True,
            linecolor=BG_LIGHT,
        ),
        hovermode="x unified"
    )

    return fig


# 3. Callback to Update the Map
@app.callback(
    Output('dwlr-map', 'figure'),
    [Input('station-selector', 'value')]
)
def update_dwlr_map(selected_station_id):
    """Generates the Plotly map figure showing all sensor locations with the targeted distribution."""

    df = pd.DataFrame(MOCK_DWLR_SENSORS)

    # Define color mapping for status using the new palette
    color_map = {
        'NORMAL': SUCCESS_COLOR,
        'LOW_ALERT': WARNING_COLOR,
        'ANOMALY': DANGER_COLOR
    }

    # Generate hover text
    df['hover_text'] = df.apply(lambda row:
                                f"<b>{row['Station_Name_Full']} ({row['State']})</b><br>"
                                f"District: {row['District']}<br>"
                                f"Type: {row['type']}<br>"
                                f"Level: {row['level']:.2f} m<br>"
                                f"Status: {row['status']}", axis=1)

    # Base map trace for all stations (Total 123 points)
    fig = px.scatter_mapbox(
        df,
        lat="lat",
        lon="lon",
        hover_data={"hover_text": True, "lat": False, "lon": False, "status": False},
        color="status",
        color_discrete_map=color_map,
        size=[10] * len(df),  # Consistent size, slightly larger for fewer dots
        zoom=3.8,  # Zoom level adjusted for all-India view
        center={"lat": 22.0, "lon": 78.0},  # Centered on India
        mapbox_style="carto-positron",  # Use token-free style for reliability
        title=None
    )

    fig.update_traces(
        # The hovertext is already formatted above in df['hover_text']
        hovertemplate='%{hovertext}<extra></extra>',
        marker=dict(
            opacity=0.8,
            size=10,  # Ensure size is set
        )
    )

    # Highlight the currently selected station with a vibrant pulse effect
    if selected_station_id:
        selected_data = df[df['id'] == selected_station_id]
        if not selected_data.empty:
            # Selected Station Trace (Primary Blue)
            fig.add_trace(go.Scattermapbox(
                lat=selected_data['lat'],
                lon=selected_data['lon'],
                mode='markers',
                marker=go.scattermapbox.Marker(
                    size=16,  # Slightly larger for visibility
                    color=ACCENT_PRIMARY,  # Primary blue fill
                    opacity=1.0,
                    symbol='circle'
                ),
                name='Selected Station',
                hoverinfo='text',
                hovertext=selected_data['hover_text']
            ))

            # Pulse Effect Trace (Larger and Fainter)
            fig.add_trace(go.Scattermapbox(
                lat=selected_data['lat'],
                lon=selected_data['lon'],
                mode='markers',
                marker=go.scattermapbox.Marker(
                    size=30,
                    color=ACCENT_PRIMARY,
                    opacity=0.2,  # Very transparent
                    symbol='circle'
                ),
                name='Pulse Effect',
                hoverinfo='none',
            ))

    fig.update_layout(
        plot_bgcolor=CARD_BG,
        paper_bgcolor=CARD_BG,
        font=dict(color=TEXT_DARK),
        margin=dict(l=0, r=0, t=0, b=0),
        clickmode='event+select',  # Enable click events
        hovermode='closest',
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99,
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor=BG_LIGHT,
            borderwidth=1
        ),
        mapbox=dict(
            style="carto-positron",  # Confirmed non-token style
            pitch=0,
            bearing=0,
            zoom=3.8,  # Initial zoom for India
            center={"lat": 22.0, "lon": 78.0}  # Center for India
        )
    )

    return fig


if __name__ == '__main__':
    # FIX: Corrected the obsolete method call from app.run_server to app.run
    app.run(debug=True)
