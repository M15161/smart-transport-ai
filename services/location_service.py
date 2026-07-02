import requests


class LocationService:

    def get_city_from_coordinates(
        self,
        lat,
        lon
    ):

        url = (
            "https://nominatim.openstreetmap.org/reverse"
        )

        params = {

            "lat": lat,

            "lon": lon,

            "format": "json"
        }

        headers = {

            "User-Agent": "TravelAI"
        }

        response = requests.get(
            url,
            params=params,
            headers=headers
        )

        data = response.json()

        address = data.get(
            "address",
            {}
        )

        return (
            address.get("city")
            or address.get("town")
            or address.get("state")
        )