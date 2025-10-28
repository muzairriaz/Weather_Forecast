from flask import Flask, render_template, request
import requests

app = Flask(__name__)

API_KEY = "YOUR-API-KEY"  # Replace with your real key

@app.route("/", methods=["GET", "POST"])
def home():
    weather_data = None
    error = None

    if request.method == "POST":
        input_city = request.form.get("city")

        try:
            # Step 1: Get location details
            url = "http://dataservice.accuweather.com/locations/v1/cities/search"
            params = {"apikey": API_KEY, "q": input_city}
            response = requests.get(url, params=params)
            data = response.json()

            if not data:
                error = "City not found. Try again."
            else:
                location_key = data[0]["Key"]

                location_info = {
                    "city": data[0]["EnglishName"],
                    "continent": data[0]["Region"]["EnglishName"],
                    "country": data[0]["Country"]["EnglishName"],
                    "country_id": data[0]["AdministrativeArea"]["CountryID"],
                    "latitude": data[0]["GeoPosition"]["Latitude"],
                    "longitude": data[0]["GeoPosition"]["Longitude"]
                }

                # Step 2: Get 5-day forecast
                forecast_url = f"http://dataservice.accuweather.com/forecasts/v1/daily/5day/{location_key}"
                forecast_params = {"apikey": API_KEY, "metric": "true"}
                forecast_response = requests.get(forecast_url, params=forecast_params)
                forecast_data = forecast_response.json()

                daily = forecast_data["DailyForecasts"]

                weather_data = {
                    "location": location_info,
                    "today": {
                        "date": daily[0]["Date"].split("T")[0],
                        "min": daily[0]["Temperature"]["Minimum"]["Value"],
                        "max": daily[0]["Temperature"]["Maximum"]["Value"],
                        "weather": daily[0]["Day"]["IconPhrase"]
                    },
                    "tomorrow": {
                        "date": daily[1]["Date"].split("T")[0],
                        "min": daily[1]["Temperature"]["Minimum"]["Value"],
                        "max": daily[1]["Temperature"]["Maximum"]["Value"],
                        "weather": daily[1]["Day"]["IconPhrase"]
                    }
                }
        except Exception as e:
            error = f"Error fetching data: {str(e)}"

    return render_template("index.html", weather_data=weather_data, error=error)

if __name__ == "__main__":
    app.run(debug=True)