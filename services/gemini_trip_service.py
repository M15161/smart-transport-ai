# import json
# import google.generativeai as genai


# class GeminiTripService:

#     def __init__(self, api_key):

#         genai.configure(api_key=api_key)

#         self.model = genai.GenerativeModel(
#             "gemini-2.5-flash"
#         )

#     def generate_trip(
#         self,
#         city,
#         budget,
#         mood,
#         places
#     ):

# #         prompt = f"""
# # أنت خبير سياحي.

# # أنشئ رحلة يوم كامل.

# # المدينة:
# # {city}

# # الميزانية:
# # {budget}

# # نوع الرحلة:
# # {mood}

# # الأماكن المتاحة:
# # {places}

# # أعد النتيجة JSON فقط.

# # مثال:

# # {{
# #     "trip_name": "",
# #     "estimated_cost": 0,
# #     "schedule": [
# #         {{
# #             "time": "10:00",
# #             "activity": ""
# #         }}
# #     ]
# # }}
# # """

#         prompt = f"""
# أنت خبير سياحي محترف في مصر.

# أنشئ رحلة مناسبة للمستخدم.

# المدينة:
# {city}

# الميزانية:
# {budget}

# نوع الرحلة:
# {mood}

# الأماكن المتاحة:
# {places}

# القواعد:

# - استخدم فقط الأماكن الموجودة.
# - لا تتجاوز الميزانية.
# - أضف توقيت لكل نشاط.
# - أضف تكلفة تقديرية.
# - أضف وسيلة انتقال بين الأماكن.

# أعد JSON فقط.

# {{
#   "trip_name": "",
#   "estimated_cost": 0,
#   "schedule": [
#     {{
#       "time": "",
#       "place": "",
#       "activity": "",
#       "transport": "",
#       "cost": 0
#     }}
#   ]
# }}
# """
#     def generate_description(
#         self,
#         city,
#         mood,
#         budget,
#         places
#     ):

#         prompt = f"""
# أنت مرشد سياحي محترف.

# اكتب وصفاً جذاباً لرحلة داخل {city}.

# نوع الرحلة:
# {mood}

# الميزانية:
# {budget}

# الأماكن:
# {places}

# اكتب فقرة عربية قصيرة من 4 إلى 6 أسطر.
# """

#         response = self.model.generate_content(prompt)

#         return response.text.strip()


#         # response = self.model.generate_content(
#         #     prompt
#         # )
      

#         # text = response.text

#         # text = text.replace(
#         #     "```json",
#         #     ""
#         # ).replace(
#         #     "```",
#         #     ""
#         # )

#         # try:
#         #     return json.loads(text)

#         # except Exception:

#         #     return {
#         #         "raw_response": text
#         #     }

import json
import google.generativeai as genai


class GeminiTripService:

    def __init__(self, api_key):

        genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel(
            "gemini-2.5-flash"
        )

    def generate_trip(
        self,
        city,
        budget,
        mood,
        places
    ):

        prompt = f"""
أنت خبير سياحي محترف في مصر.

أنشئ رحلة مناسبة للمستخدم.

المدينة:
{city}

الميزانية:
{budget}

نوع الرحلة:
{mood}

الأماكن المتاحة:
{places}

القواعد:

- استخدم فقط الأماكن الموجودة.
- لا تتجاوز الميزانية.
- أضف توقيت لكل نشاط.
- أضف تكلفة تقديرية.
- أضف وسيلة انتقال بين الأماكن.

أعد JSON فقط.

{{
  "trip_name": "",
  "estimated_cost": 0,
  "schedule": [
    {{
      "time": "",
      "place": "",
      "activity": "",
      "transport": "",
      "cost": 0
    }}
  ]
}}
"""

        response = self.model.generate_content(prompt)

        text = response.text.strip()

        text = text.replace(
            "```json",
            ""
        ).replace(
            "```",
            ""
        )

        try:
            return json.loads(text)

        except Exception:

            return {
                "raw_response": text
            }

    def generate_description(
        self,
        city,
        mood,
        budget,
        total_cost,
        places
    ):

#         prompt = f"""
# أنت مرشد سياحي محترف.

# اكتب وصفاً جذاباً لرحلة داخل {city}.

# نوع الرحلة:
# {mood}

# الميزانية:
# {budget}

# التكلفة الفعلية للرحلة:
# {total_cost} جنيه

# الأماكن:
# {places}



# اكتب فقرة عربية قصيرة من 4 إلى 6 أسطر.
# """
        place_names = [
            p.get("name", "")
            for p in places
        ]

        prompt = f"""
        أنت مرشد سياحي محترف.

        اكتب وصفاً جذاباً لرحلة داخل {city}.

        نوع الرحلة:
        {mood}

        الميزانية:
        {budget} جنيه
    
        التكلفة الفعلية:
        {total_cost} جنيه
        الأماكن المختارة:
        {', '.join(place_names)}

        القواعد:
        - اذكر أسماء الأماكن الموجودة فقط.
        - اجعل الوصف حماسياً ومناسباً لنوع الرحلة.
        - لا تضف أماكن غير موجودة.
        - اجعل الوصف من 4 إلى 6 أسطر.

        اكتب الوصف فقط بدون JSON.
        """
        response = self.model.generate_content(
            prompt
        )

        return response.text.strip()
    def generate_tips(
        self,
        city,
        mood
    ):

        prompt = f"""
        أنت مرشد سياحي محترف.
    أعطني 3 نصائح قصيرة لرحلة {mood}
    في {city}.

    أعد النتيجة كسطور فقط.
    """

        response = self.model.generate_content(
            prompt
        )

        return response.text