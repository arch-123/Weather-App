urls = {
    "api_key": "API_KEY",
    "location": {
        "base_url": "http://api.openweathermap.org/geo/1.0/direct?q={}&limit={}&appid={}",
        "limit" : "5",
        "city_name": "Mumbai"
    },
    "current_weather": {
        "base_url": "https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}"
    },
    "forecast": {
        "base_url": "https://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}&appid={}"
    },
    "aqi":{
        "base_url": "http://api.openweathermap.org/data/2.5/air_pollution?lat={}&lon={}&appid={}"
    }
}

air_quality = {
    1: "Good",
    2: "Fair",
    3: "Moderate",
    4: "Poor",
    5: "Very Poor"
}