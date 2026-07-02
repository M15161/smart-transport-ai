import requests


class WeatherService:

    def get_weather(self, city):

        try:
            url = (
                f"https://wttr.in/{city}?format=j1"
            )

            response = requests.get(
                url,
                timeout=10
            )

            data = response.json()

            current = data["current_condition"][0]

            return {
                "temperature": current["temp_C"],
                "description": current["weatherDesc"][0]["value"],
                "humidity": current["humidity"],
                "wind_speed": current["windspeedKmph"]
            }

        except Exception:

            return {
                "temperature": None,
                "description": "غير متاح",
                "humidity": None,
                "wind_speed": None
            }
# import requests
# from datetime import datetime


# class WeatherService:

#     API_KEY = "YOUR_OPENWEATHER_API_KEY"

#     def get_weather(self, city):

#         try:

#             url = (
#                 "https://api.openweathermap.org/data/2.5/weather"
#                 f"?q={city}"
#                 f"&appid={self.API_KEY}"
#                 "&units=metric"
#                 "&lang=ar"
#             )

#             response = requests.get(
#                 url,
#                 timeout=10
#             )

#             data = response.json()

#             if response.status_code != 200:

#                 return self.default_weather()

#             temp = data["main"]["temp"]

#             feels_like = data["main"]["feels_like"]

#             humidity = data["main"]["humidity"]

#             pressure = data["main"]["pressure"]

#             wind_speed = data["wind"]["speed"]

#             clouds = data["clouds"]["all"]

#             visibility = data.get(
#                 "visibility",
#                 0
#             ) / 1000

#             description = data["weather"][0]["description"]

#             sunrise = datetime.fromtimestamp(
#                 data["sys"]["sunrise"]
#             ).strftime("%H:%M")

#             sunset = datetime.fromtimestamp(
#                 data["sys"]["sunset"]
#             ).strftime("%H:%M")

#             score = 100

#             recommendations = []

#             warnings = []

#             if temp > 40:

#                 score -= 40

#                 warnings.append(
#                     "درجة الحرارة مرتفعة جداً"
#                 )

#             elif temp > 35:

#                 score -= 25

#                 warnings.append(
#                     "الطقس حار"
#                 )

#             elif temp < 10:

#                 score -= 25

#                 warnings.append(
#                     "الجو بارد"
#                 )

#             if humidity > 80:

#                 score -= 10

#                 warnings.append(
#                     "الرطوبة مرتفعة"
#                 )

#             if wind_speed > 12:

#                 score -= 15

#                 warnings.append(
#                     "رياح قوية"
#                 )

#             if visibility < 3:

#                 score -= 20

#                 warnings.append(
#                     "الرؤية ضعيفة"
#                 )

#             if score >= 85:

#                 trip_status = "ممتاز"

#                 comfort = "Excellent"

#             elif score >= 70:

#                 trip_status = "جيد"

#                 comfort = "Good"

#             elif score >= 50:

#                 trip_status = "متوسط"

#                 comfort = "Moderate"

#             else:

#                 trip_status = "غير مناسب"

#                 comfort = "Poor"

#             if temp >= 35:

#                 clothing = (
#                     "ملابس صيفية خفيفة"
#                 )

#                 best_time = "17:00"

#             elif temp >= 25:

#                 clothing = (
#                     "ملابس خفيفة"
#                 )

#                 best_time = "16:00"

#             elif temp >= 15:

#                 clothing = (
#                     "ملابس عادية"
#                 )

#                 best_time = "10:00"

#             else:

#                 clothing = (
#                     "جاكيت أو ملابس شتوية"
#                 )

#                 best_time = "11:00"

#             recommendations.extend([
#                 "احمل زجاجة مياه",
#                 "استخدم Google Maps",
#                 "اشحن هاتفك قبل الخروج"
#             ])

#             if temp > 30:

#                 recommendations.append(
#                     "استخدم واقي شمس"
#                 )

#             if humidity > 70:

#                 recommendations.append(
#                     "اختر أماكن مكيفة"
#                 )

#             return {

#                 "temperature":
#                     round(temp),

#                 "feels_like":
#                     round(feels_like),

#                 "description":
#                     description,

#                 "humidity":
#                     humidity,

#                 "pressure":
#                     pressure,

#                 "wind_speed":
#                     wind_speed,

#                 "clouds":
#                     clouds,

#                 "visibility_km":
#                     round(visibility, 1),

#                 "sunrise":
#                     sunrise,

#                 "sunset":
#                     sunset,

#                 "weather_score":
#                     score,

#                 "trip_status":
#                     trip_status,

#                 "comfort_level":
#                     comfort,

#                 "best_time_to_start":
#                     best_time,

#                 "clothing_advice":
#                     clothing,

#                 "recommendations":
#                     recommendations,

#                 "warnings":
#                     warnings
#             }

#         except Exception as e:

#             print(
#                 "Weather Error:",
#                 e
#             )

#             return self.default_weather()

#     def default_weather(self):

#         return {

#             "temperature": None,

#             "feels_like": None,

#             "description": "غير متاح",

#             "humidity": None,

#             "pressure": None,

#             "wind_speed": None,

#             "clouds": None,

#             "visibility_km": None,

#             "sunrise": None,

#             "sunset": None,

#             "weather_score": 50,

#             "trip_status": "Unknown",

#             "comfort_level": "Unknown",

#             "best_time_to_start": "10:00",

#             "clothing_advice": "ملابس عادية",

#             "recommendations": [],

#             "warnings": []
#         }