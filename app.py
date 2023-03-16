from flask import Flask, render_template, request
import requests, json
from config import urls, air_quality
from datetime import datetime
import pandas as pd

app = Flask(__name__)

def get_lat_lon(city_name):
    location_url = urls["location"]["base_url"].format(city_name, urls["location"]["limit"], urls["api_key"])
    response = requests.get(location_url)
    lat, lon = 0, 0
    if response.status_code == 200:
        x = response.json()
        lat = x[0]['lat']
        lon = x[0]['lon']
    return lat, lon


def kelvin_to_celcius(temp):
    return str(round(temp - 273.15)) + " ℃";


def clean_current_weather_api_response(x):
    data = {}
    data['Weather'] = x['weather'][0]['description'].capitalize()
    data['Temperature'] = kelvin_to_celcius(x['main']['temp'])
    data['Temperature(feels like)'] = kelvin_to_celcius(x['main']['feels_like'])
    data['Min Temperature'] = kelvin_to_celcius(x['main']['temp_min'])
    data['Max Temperature'] = kelvin_to_celcius(x['main']['temp_max'])
    data['Humidity'] = str(x['main']['humidity']) + " %"
    data['Visibility'] = str(round(x['visibility']/1000, 1)) + " kms"
    data['Pressure'] = str(x['main']['pressure']) + " hPa"
    data['Wind Speed'] = str(round(x['wind']['speed']*3.6, 1)) + " km/hr"
    return data


def get_current_weather(lat, lon):
    url = urls["current_weather"]["base_url"].format(str(lat), str(lon), urls["api_key"])
    response = requests.get(url)
    if response.status_code == 200:
        x = response.json()
        # print(x)
    data = clean_current_weather_api_response(x)
    return data


def hour_format_converter_24_to_12(df):
    def check_hour(x):
        if x>12: return str(x-12) + " PM"
        if x==12: return str(x) + " PM"
        if x==0: return "12 AM"
        return str(x) + " AM"
    return df.astype(int).apply(lambda x: check_hour(x))


def clean_future_weather_api_response(res):
    for i in range(len(res['list'])):
        res['list'][i]['weather'] = res['list'][i]['weather'][0]
    df = pd.json_normalize(res['list'])
    df['dt'] = df['dt'].apply(lambda i: datetime.utcfromtimestamp(i).strftime("%d %b-%H"))
    df[['Date', 'Hour']] = df['dt'].str.split("-", expand = True)
    df['Hour'] = hour_format_converter_24_to_12(df['Hour'])
    df = df[[
        'Date', 'Hour', 'weather.description', 'main.temp', 'main.feels_like', 'main.temp_min', 
        'main.temp_max', 'main.humidity', 'visibility', 'main.pressure', 'wind.speed'
    ]]
    df = df.rename(columns = {
        'weather.description': "Weather",
        'main.temp': "Temperature", 
        'main.feels_like': "Temperature(feels like)", 
        'main.temp_min': "Min Temperature", 
        'main.temp_max': "Max Temperature", 
        'main.humidity': "Humidity",
        'visibility': "Visibility",
        'main.pressure': "Pressure", 
        'wind.speed': "Wind Speed"
    })
    df['Weather'] = df['Weather'].astype(str).str.capitalize()
    df['Temperature'] = df['Temperature'].apply(lambda x: kelvin_to_celcius(x))
    df['Temperature(feels like)'] = df['Temperature(feels like)'].apply(lambda x: kelvin_to_celcius(x))
    df['Min Temperature'] = df['Min Temperature'].apply(lambda x: kelvin_to_celcius(x))
    df['Max Temperature'] = df['Max Temperature'].apply(lambda x: kelvin_to_celcius(x))
    df['Humidity'] = df['Humidity'].astype(str) + " %"
    df['Visibility'] = (df['Visibility']/1000).astype(str) + " kms"
    df['Pressure'] = df['Pressure'].round(1).astype(str) + " hPa"
    df['Wind Speed'] = (df['Wind Speed']*3.6).round(1).astype(str) + " km/hr"
    return df


def get_future_weather(lat, lon):
    url = urls["forecast"]["base_url"].format(str(lat), str(lon), urls["api_key"])
    response = requests.get(url)
    if response.status_code == 200:
        x = response.json()
        # print(x)
    data = clean_future_weather_api_response(x)
    return data


def clean_aqi_api_response(x):
    aqi_index = x['list'][0]['main']['aqi']
    return air_quality[aqi_index]


def get_aqi(lat, lon):
    url = urls["aqi"]["base_url"].format(str(lat), str(lon), urls["api_key"])
    response = requests.get(url)
    if response.status_code == 200:
        x = response.json()
        # print(x)
    data = clean_aqi_api_response(x)
    return data


@app.route("/handlesubmit", methods=['POST'])
def handleSubmit():
    city_name = request.form['city']
    try:
        lat, lon = get_lat_lon(city_name)
    except:
        return render_template(
            "index.html", error = True, 
            error_mssg="City '{}' does not exists!".format(city_name)
        )
    try:
        current_weather = get_current_weather(lat, lon)
        future_weather = get_future_weather(lat, lon)
        aqi = get_aqi(lat, lon)
    except:
        return render_template(
            "index.html", error = True, 
            error_mssg="Cannot fetch weather data for '{}'!".format(city_name)
        )
    
    return render_template(
        "weather.html", 
        city=city_name, 
        current_weather=current_weather, 
        future_weather = future_weather,
        aqi = aqi,
        error = False
    )


@app.route("/")
def welcome_page():
    return render_template("index.html")

if __name__=="__main__":
    app.run(debug = True)
