import json


class ProfileService:

    def __init__(self):

        self.profile_file = "data/user_profile.json"

    def load(self):

        with open(
            self.profile_file,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    def save(self, profile):

        with open(
            self.profile_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                profile,
                f,
                ensure_ascii=False,
                indent=4
            )

    def update(self, parsed):

        profile = self.load()

        if parsed.get("city"):

            profile["cities"].append(
                parsed["city"]
            )

        if parsed.get("budget"):

            profile["budget_history"].append(
                parsed["budget"]
            )

        if parsed.get("mood"):

            profile["preferred_mood"] = (
                parsed["mood"]
            )

        profile["trip_count"] += 1

        self.save(profile)