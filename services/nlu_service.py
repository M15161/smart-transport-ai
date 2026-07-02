import json
import google.generativeai as genai


class NLUService:

    def __init__(self, api_key):

        genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel(
            "gemini-2.5-flash"
        )

    def parse(self, user_text):

        prompt = f"""
Extract the user request.

Return ONLY JSON.

Schema:

{{
  "intent":"",
  "city":"",
  "source":"",
  "destination":"",
  "budget":null,
  "days":null,
  "mood":"",
  "preference":""
}}

Possible intents:

- route_generation
- trip_planner
- recommendation
- preference_update
- chat

User:

{user_text}
"""

        response = self.model.generate_content(
            prompt
        )

        text = response.text

        text = text.replace("```json", "")
        text = text.replace("```", "")

        return json.loads(text)
# from google import genai
# import json


# class NLUService:

#     def __init__(self, api_key):

#         self.client = genai.Client(
#             api_key=api_key
#         )

#     def parse(self, user_text):

#         prompt = f"""
# Extract the user request.

# Return ONLY JSON.

# {{
#   "intent":"",
#   "city":"",
#   "source":"",
#   "destination":"",
#   "budget":null,
#   "days":null,
#   "mood":"",
#   "preference":""
# }}


# Possible intents:

# - route_generation
# - trip_planner
# - recommendation
# - preference_update
# - chat

# IMPORTANT:
# Use ONLY one of these values exactly.
# Never invent new intents.

# User:
# {user_text}
# """

#         response = self.client.models.generate_content(
#             model="gemini-2.5-flash",
#             contents=prompt
#         )

#         text = response.text.strip()

#         text = text.replace("```json", "")
#         text = text.replace("```", "")

#         return json.loads(text)