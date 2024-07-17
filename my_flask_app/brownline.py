import requests
import json
import folium
import time
import os
import math
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, filename='train_tracker.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

def haversine(lon1, lat1, lon2, lat2):
    R = 6371  # Radius of the earth in km
    dlon = math.radians(lon2 - lon1)
    dlat = math.radians(lat2 - lat1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

def get_closest_stop(current_location, stops):
    closest_stop = None
    min_distance = float('inf')
    
    for stop in stops:
        distance = haversine(current_location[1], current_location[0], stop['lon'], stop['lat'])
        if distance < min_distance:
            min_distance = distance
            closest_stop = stop
    
    return closest_stop

def get_brown_line_chicago_kimball(api_key):
    base_url = "http://lapi.transitchicago.com/api/1.0/ttarrivals.aspx"
    params = {
        'key': api_key,
        'mapid': '40380',
        'rt': 'Brn',
        'outputType': 'JSON'
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        if 'eta' in data['ctatt']:
            filtered_data = [eta for eta in data['ctatt']['eta'] if eta['destNm'] == 'Kimball']
            return {'ctatt': {'tmst': data['ctatt']['tmst'], 'eta': filtered_data}}
        else:
            logging.error(f"No 'eta' key in response. Data received: {data}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data: {e}")
        return None

def save_historical_data(data, filename):
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            json.dump([], f)
    
    with open(filename, 'r') as f:
        history = json.load(f)
    
    history.append(data)
    
    with open(filename, 'w') as f:
        json.dump(history, f, indent=4)
    
    logging.info(f"Data saved to {filename}")

def plot_on_map(data, map_filename, current_location=None):
    m = folium.Map(location=[41.8781, -87.6298], zoom_start=12)
    for eta in data['ctatt']['eta']:
        lat = float(eta['lat'])
        lon = float(eta['lon'])
        popup = f"Train {eta['rn']} to {eta['destNm']} arriving at {eta['arrT']}"
        folium.Marker(
            location=[lat, lon],
            popup=popup,
            icon=folium.Icon(color='blue', icon='train')
        ).add_to(m)
    
    folium.Marker(
        location=[41.8963, -87.6280],
        popup="Chicago Station",
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)
    
    if current_location:
        folium.Marker(
            location=current_location,
            popup="Your Location",
            icon=folium.Icon(color='green', icon='home')
        ).add_to(m)
        
        stops = [
            {'staNm': 'Clark/Lake', 'lat': 41.88573, 'lon': -87.6309},
            {'staNm': 'Chicago', 'lat': 41.8963, 'lon': -87.6280},
            {'staNm': 'Merchandise Mart', 'lat': 41.8884, 'lon': -87.6337},
        ]
        closest_stop = get_closest_stop(current_location, stops)
        if closest_stop:
            folium.Marker(
                location=[closest_stop['lat'], closest_stop['lon']],
                popup=f"Closest Stop: {closest_stop['staNm']}",
                icon=folium.Icon(color='purple', icon='info-sign')
            ).add_to(m)

    m.save(map_filename)
    logging.info(f"Map saved to {map_filename}")

def main():
    api_key = 'ed28b0ed593f449bafb1327463e2425b'
    history_filename = 'historical_data.json'
    map_filename = 'brown_line_chicago_kimball_map.html'
    current_location = (41.8903, -87.63548)  # Example current location

    while True:
        data = get_brown_line_chicago_kimball(api_key)
        if data:
            save_historical_data(data, history_filename)
            plot_on_map(data, map_filename, current_location)
        time.sleep(60)

if __name__ == '__main__':
    main()
