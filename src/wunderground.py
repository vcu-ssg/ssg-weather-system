from flask import Flask, Response
import requests
import json

app = Flask(__name__)

# API for wunderground
# https://docs.google.com/document/d/1eKCnKXI9xnoMGRRzOL1xPCBihNV2rOet08qpE_gArAY/edit?tab=t.0
#
# Current conditions:
# https://docs.google.com/document/d/1KGb8bTVYRsNgljnNH67AMhckY8AQT2FVwZ9urj8SWBs/edit?tab=t.0
#
# Forecasts:
# https://docs.google.com/document/d/1_Zte7-SdOjnzBttb1-Y9e0Wgl0_3tah9dSwXUyEA3-c/edit?tab=t.0


#  https://api.weather.com/v2/pws/observations/current?stationId=KVARICHM156&format=json&units=e&apiKey=a861c99323614407a1c9932361b4073f
#
# units={e,m} english or metric


LOCATIONS = [
    'KVARICHM156'
]

API_KEY = "a861c99323614407a1c9932361b4073f"
WEATHER_API_URL = "http://api.weather.com/v2/pws/observations/current"
UNITS = "e"
FORMAT = 'json'
PREFIX = "wunderground"

@app.route('/metrics')
def metrics():
    metrics = []
    for location in LOCATIONS:
        # Fetch weather data for each location
        params={
            'stationId': location,
            'format': FORMAT,
            'units': UNITS,
            'apiKey': API_KEY
        }
        response = requests.get( WEATHER_API_URL, params=params )
        if response.status_code == 200:
            try:
                data = response.json()
                print("Response JSON:", data)
                metrics = metrics + convert_to_prometheus( data )

            except requests.JSONDecodeError:
                print("Error decoding JSON. Response text:", response.text)
        else:
            print(f"HTTP Error {response.status_code}: {response.text}")


    # Join all metrics into a response
    return Response("\n".join( metrics ), mimetype="text/plain")


def convert_to_prometheus(data):
    prometheus_metrics = []
    
    # Extract observations
    observations = data.get("observations", [])
    if not observations:
        return "# No data available"
    
    for obs in observations:
        # Extract the timestamp in epoch format
        epoch_timestamp = obs.get("epoch", 0) * 1000
        
        # Extract common labels
        labels = {
            "stationID": obs.get("stationID"),
            "neighborhood": obs.get("neighborhood"),
            "country": obs.get("country"),
            "softwareType": obs.get("softwareType"),
        }
        
        # Format labels for Prometheus
        label_str = ",".join([f'{key}="{value}"' for key, value in labels.items() if value is not None])
        
        # Add common fields with timestamp
        prometheus_metrics.append(f'{PREFIX}_lon{{{label_str}}} {obs.get("lon", 0)} {epoch_timestamp}')
        prometheus_metrics.append(f'{PREFIX}_lat{{{label_str}}} {obs.get("lat", 0)} {epoch_timestamp}')
        prometheus_metrics.append(f'{PREFIX}_uv{{{label_str}}} {obs.get("uv", 0)} {epoch_timestamp}')
        prometheus_metrics.append(f'{PREFIX}_windir{{{label_str}}} {obs.get("windir", 0)} {epoch_timestamp}')
        prometheus_metrics.append(f'{PREFIX}_humidity{{{label_str}}} {obs.get("humidity", 0)} {epoch_timestamp}')
        prometheus_metrics.append(f'{PREFIX}_solar_radiation{{{label_str}}} {obs.get("solarRadiation", 0)} {epoch_timestamp}')
        
        # Add imperial fields with "imperial" in the metric name and timestamp
        imperial = obs.get("imperial", {})
        for key, value in imperial.items():
            if value is not None:
                prometheus_metrics.append(f'{PREFIX}_imperial_{key}{{{label_str}}} {value} {epoch_timestamp}')
  
    # Combine metrics into Prometheus format
    return prometheus_metrics


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9123)
