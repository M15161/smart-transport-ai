from services.places_service import PlacesService
import json


class RecommendationEngine:

    def __init__(self):

        self.profile_file = "data/user_profile.json"

        self.places_service = PlacesService()

    def load_profile(self):

        with open(
            self.profile_file,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    def recommend(self):

        profile = self.load_profile()

        city = (
            profile["cities"][-1]
            if profile["cities"]
            else "Cairo"
        )

        mood = (
            profile["preferred_mood"]
            if profile["preferred_mood"]
            else "عادية"
        )

        avg_budget = 0

        if profile["budget_history"]:

            avg_budget = (
                sum(profile["budget_history"])
                / len(profile["budget_history"])
            )

        places = self.places_service.get_places(
            city=city,
            limit=10
        )

        return {

            "recommended_city": city,

            "recommended_budget": avg_budget,

            "recommended_mood": mood,

            "places": places
        }