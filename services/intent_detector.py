import re


class IntentDetector:

    def detect(self, text: str):

        text = text.lower()

        if any(word in text for word in [
            "من",
            "الى",
            "إلى",
            "اروح",
            "اذهب"
        ]):
            return "route_generation"

        if any(word in text for word in [
            "خروجة",
            "رحلة",
            "فسحة"
        ]):
            return "trip_planner"

        if any(word in text for word in [
            "اقترح",
            "رشح"
        ]):
            return "recommendation"

        return "chat"