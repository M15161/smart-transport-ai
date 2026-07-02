import json
from difflib import get_close_matches


class CityNormalizer:

    def __init__(self):

        with open(
            "data/egypt_locations.json",
            "r",
            encoding="utf-8"
        ) as f:

            self.data = json.load(f)

        self.lookup = {}

        for official_city, aliases in self.data.items():

            self.lookup[
                official_city.lower()
            ] = official_city

            for alias in aliases:

                self.lookup[
                    alias.lower()
                ] = official_city

    def normalize(self, city):

        city = city.strip().lower()

        if city in self.lookup:

            return self.lookup[city]

        matches = get_close_matches(
            city,
            self.lookup.keys(),
            n=1,
            cutoff=0.6
        )

        if matches:

            return self.lookup[
                matches[0]
            ]

        return city