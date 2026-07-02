import re


class EntityExtractor:

    def extract_budget(self, text):

        match = re.search(r"(\d+)\s*جنيه", text)

        if match:
            return int(match.group(1))

        return None

    def extract_days(self, text):

        match = re.search(r"(\d+)\s*(يوم|أيام)", text)

        if match:
            return int(match.group(1))

        return None

    def extract_route(self, text):

        pattern = r"من\s+(.*?)\s+(?:إلى|الى)\s+(.*)"

        match = re.search(
            pattern,
            text
        )

        if match:

            return {
                "source": match.group(1),
                "destination": match.group(2)
            }

        return {}

    def extract(self, text):

        result = {}

        result["budget"] = self.extract_budget(text)

        result["days"] = self.extract_days(text)

        route = self.extract_route(text)

        result.update(route)

        return result