import random


class SmartTripEngine:

    PRICE_MAP = {
        "cafe": 120,
        "restaurant": 250,
        "park": 30,
        "tourism": 80,
        "mall": 100
    }

    def generate_schedule(
        # self,
        # cafes,
        # restaurants,
        # parks,
        # tourism,
        # malls,
        # mood
            self,
        cafes,
        restaurants,
        parks,
        tourism,
        malls,
        mood,
        budget=None
    ):
        if not isinstance(cafes, list):
            cafes = []

        if not isinstance(restaurants, list):
            restaurants = []

        if not isinstance(parks, list):
            parks = []

        if not isinstance(tourism, list):
            tourism = []

        if not isinstance(malls, list):
            malls = []

        places = []

        if mood in ["شبابية", "مغامرة"]:

            places.extend(cafes[:2])
            places.extend(tourism[:2])

        elif mood == "عائلية":

            places.extend(parks[:2])
            places.extend(restaurants[:2])
            places.extend(malls[:1])

        elif mood == "اقتصادية":

            places.extend(parks[:3])
            places.extend(tourism[:2])

        else:

            places.extend(cafes[:2])
            places.extend(tourism[:2])

        schedule = []

        total_cost = 0

        hour = 10

        for place in places:

            cost = self.PRICE_MAP.get(
                place["type"],
                100
            )

            total_cost += cost

            ACTIVITIES = {
                "cafe": {
                    "activity": "الاستمتاع بالمشروبات والتقاط الصور",
                    "duration": "2 hours"
                },
                "park": {
                    "activity": "التنزه والاسترخاء",
                    "duration": "2 hours"
                },
                "restaurant": {
                    "activity": "تناول وجبة",
                    "duration": "1 hour"
                },
                "mall": {
                    "activity": "التسوق والترفيه",
                    "duration": "2 hours"
                },
                "tourism": {
                    "activity": "زيارة معلم سياحي",
                    "duration": "2 hours"
                }
            }

            schedule.append({

                "time": f"{hour}:00",

                "name": place["name"],

                "type": place["type"],

                "activity": activity,
                
                "duration": duration,
                
                "transport": transport,

                "address": place.get("address"),

                "lat": place.get("lat"),

                "lon": place.get("lon"),

                "maps_url": place.get("maps_url"),

                "website": place.get("website"),

                "facebook": place.get("facebook"),

                "instagram": place.get("instagram"),

                "estimated_cost": cost
               
            })

            hour += 2
            while budget and total_cost > budget and schedule:

                place_type = place.get("type")

                activity = ACTIVITIES.get(
                    place_type,
                    {}
                ).get(
                    "activity",
                    "زيارة المكان"
                )

                duration = ACTIVITIES.get(
                    place_type,
                    {}
                ).get(
                    "duration",
                    "1 hour"
                )

                if len(schedule) == 0:
                    transport = "Start Point"
                # elif len(schedule) < 1:
                #     transport = "Walk"

                # elif len(schedule) < 5:
                #     transport = "Uber"

                else:
                    transport = "Taxi"
                    
                removed = schedule.pop()

                total_cost -= removed["estimated_cost"]

        return {

            "trip_name": f"رحلة {mood}",

            "estimated_cost": total_cost,

            "places": schedule
        }