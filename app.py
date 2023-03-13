from flask import Flask, render_template, request
import requests, json
from config import urls

app = Flask(__name__)




def get_lat_lon(city_name):
    location_url = (
        urls["location"]["base_url"] 
        + "q=" + city_name 
        + "&limit=" + urls["location"]["limit"] 
        + "&appid=" + urls["api_key"]
    )
    response = requests.get(location_url)
    lat, lon = 0, 0
    if response.status_code == 200:
        x = response.json()
        lat = x[0]['lat']
        lon = x[0]['lon']
    return lat, lon


def clean_api_response(x):
    data = {}
    data['Weather'] = x['weather'][0]['main']
    data['Temperature'] = kelvin_to_celcius(x['main']['temp'])
    data['Temperature(feels like)'] = kelvin_to_celcius(x['main']['feels_like'])
    data['Min Temperature'] = kelvin_to_celcius(x['main']['temp_min'])
    data['Max Temperature'] = kelvin_to_celcius(x['main']['temp_max'])
    data['Humidity'] = str(x['main']['humidity']) + " %"
    data['Visibility'] = str(x['visibility']) + " meter"
    data['Pressure'] = str(x['main']['pressure']) + " hPa"
    data['Wind Speed'] = str(x['wind']['speed']) + " meter/sec"
    return data


@app.route("/handlesubmit", methods=['POST'])
def get_current_weather():
    city_name = request.form['city']
    lat, lon = get_lat_lon(city_name)
    current_weather_url = (
        urls["current_weather"]["base_url"]
        + "lat=" + str(lat)
        +"&lon=" + str(lon)
        + "&appid=" + urls["api_key"]
    )
    response = requests.get(current_weather_url)
    if response.status_code == 200:
        x = response.json()
        print(x)
    data = clean_api_response(x)
    return render_template("weather.html", weather=data, city=city_name)

def kelvin_to_celcius(temp):
    return str(round(temp - 273.15)) + " ℃";


@app.route("/")
def welcome_page():
    return render_template("index.html")

if __name__=="__main__":
    app.run(debug = True)
