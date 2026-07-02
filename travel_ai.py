import os
from services.nlu_service import NLUService
from engines.route_engine import RouteEngine
from engines.trip_planner import TripPlanner
from services.profile_service import ProfileService
from engines.recommendation_engine import RecommendationEngine
from utils.city_normalizer import CityNormalizer

class TravelAI:
    def __init__(self, api_key):
        self.nlu = NLUService(api_key)
        
        # 🎯 هنا تم ربط وتمرير الـ api_key لمحرك الطرق لتشغيل موديل جيمناي جواه
        self.route_engine = RouteEngine(api_key=api_key)
        
        self.profile_service = ProfileService()
        self.recommendation_engine = RecommendationEngine()
        # self.trip_planner = TripPlanner(api_key=os.getenv("GOOGLE_API_KEY"))
        self.trip_planner = TripPlanner(gemini_key=os.getenv("GOOGLE_API_KEY"))
        self.city_normalizer = CityNormalizer()

    def process(self, user_text):
        # 1. تحليل النص وفهم الـ Intent والـ Entities (source, destination)
        parsed = self.nlu.parse(user_text)
        self.profile_service.update(parsed)

        city = parsed.get("city")
        if city:
            city = self.city_normalizer.normalize(city)

        intent = parsed.get("intent")

        # 2. توجيه الـ Intent إلى الـ Engine المناسب
        if intent == "trip_planner":
            return self.trip_planner.create_trip(
                city=city,
                budget=parsed.get("budget", 500),
                mood=parsed.get("mood", "عادية")
            )

        if intent == "recommendation":
            return self.recommendation_engine.recommend()

        # فحص إنتنت المواصلات والطرق
        if intent in ["route_generation", "travel", "route"]:
            source = parsed.get("source")
            destination = parsed.get("destination")

            if source:
                source = self.city_normalizer.normalize(source)

            if destination:
                destination = self.city_normalizer.normalize(destination)

            # استدعاء محرك الطرق الذكي والمطور
            return self.route_engine.generate_routes(source, destination)

        return parsed