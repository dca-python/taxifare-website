import os
import requests
import pydeck as pdk
import streamlit as st

PREDICTION_URL = 'https://taxifare.lewagon.ai/predict'

# Get Mapbox Access Token from secrets or environment variable
MAPBOXGL_ACCESS_TOKEN = st.secrets.get('MAPBOXGL_ACCESS_TOKEN', os.environ.get("MAPBOXGL_ACCESS_TOKEN"))

def get_coordinates(location):
    """Returns the (lng, lat) tuple for a given location string."""
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{location}.json"
    params = {
        'access_token': MAPBOXGL_ACCESS_TOKEN,
        'limit': 1
    }
    response = requests.get(url, params=params, timeout=5)
    data = response.json()
    if data['features']:
        coordinates = data['features'][0]['geometry']['coordinates']
        return coordinates
    return None

# UI Layout
st.markdown('# New York Taxifare')

col1, col2 = st.columns(2)
pickup_input = col1.text_input('Pickup Location', 'Central Park')
dropoff_input = col2.text_input('Dropoff Location', 'Empire State Building')

# Prepare location strings
pickup = "new york " + pickup_input.lower() if "new york" not in pickup_input.lower() else pickup_input.lower()
dropoff = "new york " + dropoff_input.lower() if "new york" not in pickup_input.lower() else pickup_input.lower()

if pickup:
    pickup_coordinates = get_coordinates(pickup)
    pickup_longitude = pickup_coordinates[0]
    pickup_latitude = pickup_coordinates[1]

if dropoff:
    dropoff_coordinates = get_coordinates(dropoff)
    dropoff_longitude = dropoff_coordinates[0]
    dropoff_latitude = dropoff_coordinates[1]

# Map Configuration
view_state = pdk.ViewState(
    longitude=pickup_longitude,
    latitude=pickup_latitude,
    zoom=11
)

data = [
    {"position": [pickup_longitude, pickup_latitude], "name": "Pickup"},
    {"position": [dropoff_longitude, dropoff_latitude], "name": "Dropoff"},
]

point_layer = pdk.Layer(
    'ScatterplotLayer',
    data=data,
    get_position='position',
    get_radius=100,
    get_fill_color=[55, 0, 0],
    pickable=True
)

st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v11',
        initial_view_state=view_state,
        layers=[point_layer],  # line_layer
        tooltip={"text": "{name}"}
))

# Further User Input
col3, col4 = st.columns(2)
pickup_date = col3.date_input('Pickup Date')
pickup_time = col4.time_input('Pickup Time')
pickup_datetime = f"{pickup_date} {pickup_time}"

passenger_count = st.slider('Number of Passengers', 1, 8, 1)
params = {
        'pickup_datetime': pickup_datetime,
        'pickup_longitude': pickup_longitude,
        'pickup_latitude': pickup_latitude,
        'dropoff_longitude': dropoff_longitude,
        'dropoff_latitude': dropoff_latitude,
        'passenger_count': passenger_count
}

# Button Styling
st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: dark-grey;
        color: white;
        height: 4em;
        width: 8em;
        font-size: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Fare Calculation
col5, col6 = st.columns(2)
if col5.button('Calculate Fare') and all(params.values()):
    response = requests.get(url=PREDICTION_URL, params=params, timeout=5)
    prediction_json = response.json()
    prediction = round(prediction_json["fare"], 2)
    prediction_string = format(prediction, '.2f')
    col6.metric("Your Fare", f"$ {prediction_string}")
else:
    col6.metric("Your Fare", "$ 0.00")
