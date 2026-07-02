# import requests


# class PlacesService:

#     OVERPASS_URL = "https://overpass-api.de/api/interpreter"

#     def get_places(
#         self,
#         city,
#         place_type="restaurant",
#         limit=10
#     ):

#         query = f"""
#         [out:json];
#         area["name"="{city}"]->.searchArea;

#         (
#           node["amenity"="{place_type}"](area.searchArea);
#         );

#         out center {limit};
#         """

#         response = requests.get(
#             self.OVERPASS_URL,
#             params={"data": query},
#             timeout=30
#         )

#         print("Status:", response.status_code)
#         print("Response:")      
#         print(response.text[:500])

#         data = response.json()

#         places = []

#         for item in data.get("elements", []):

#             places.append({
#                 "name": item.get(
#                     "tags",
#                     {}
#                 ).get(
#                     "name",
#                     "Unknown"
#                 ),
#                 "lat": item.get("lat"),
#                 "lon": item.get("lon")
#             })

#         return places

# services/places_service.py

# import osmnx as ox
# import pandas as pd


# class PlacesService:

#     def get_places(
#         self,
#         city,
#         place_type=None,
#         limit=20
#     ):

#         try:

#             gdf = ox.features_from_place(
#                 f"{city}, Egypt",
#                 tags={"amenity": True}
#             )

#             if "name" not in gdf.columns:
#                 return []

#             results = []

#             for _, row in gdf.iterrows():

#                 name = row.get("name")

#                 amenity = row.get("amenity")

#                 if pd.isna(name):
#                     continue

#                 if place_type and amenity != place_type:
#                     continue

#                 results.append({
#                     "name": str(name),
#                     "type": str(amenity)
#                 })

#                 if len(results) >= limit:
#                     break

#             return results

#         except Exception as e:

#             return {
#                 "error": str(e)
#             }

# import osmnx as ox
# import pandas as pd


# class PlacesService:


#     PLACE_FILTERS = {

#     "restaurant": {
#         "amenity": "restaurant"
#     },

#     "cafe": {
#         "amenity": "cafe"
#     },

#     "park": {
#         "leisure": "park"
#     },

#     "mall": {
#         "shop": "mall"
#     },

#     "tourism": {
#         "tourism": True
#     }
# }

#     def get_places(
#         self,
#         city,
#         place_type=None,
#         limit=20
#     ):

#         try:

#             tags = PLACE_FILTERS.get(
#              place_type,
#             {"tourism": True}
#             )

#             gdf = ox.features_from_place(
#               f"{city}, Egypt",
#              tags=tags
#             )

#             results = []

#             for _, row in gdf.iterrows():

#                 name = row.get("name")

#                 if pd.isna(name):
#                     continue

#                 amenity = row.get(
#                     "amenity",
#                     "unknown"
#                 )

#                 if (
#                     place_type
#                     and amenity != place_type
#                 ):
#                     continue

#                 try:

#                     lat = row.geometry.centroid.y

#                     lon = row.geometry.centroid.x

#                 except:

#                     lat = None

#                     lon = None

#                 maps_url = None

#                 if lat and lon:

#                     maps_url = (
#                         f"https://www.google.com/maps?q="
#                         f"{lat},{lon}"
#                     )

#                 website = row.get(
#                     "website",
#                     None
#                 )

#                 facebook = (
#                     row.get("facebook")
#                     or row.get("contact:facebook")
#                 )

#                 instagram = (
#                     row.get("instagram")
#                     or row.get("contact:instagram")
#                 )

#                 results.append({

#                     "name": str(name),

#                     "type": str(amenity),

#                     "lat": lat,

#                     "lon": lon,

#                     "maps_url": maps_url,

#                     "website": website,

#                     "facebook": facebook,

#                     "instagram": instagram
#                 })

#                 if len(results) >= limit:
#                     break

#             return results

#         except Exception as e:

#             return {
#                 "error": str(e)
#             }
# import osmnx as ox
# import pandas as pd
# from utils.city_normalizer import CityNormalizer
# from math import radians, sin, cos, sqrt, atan2



# class PlacesService:
#     def __init__(self):
#         self.city_normalizer = CityNormalizer()

#     PLACE_FILTERS = {

#         "restaurant": {
#             "amenity": "restaurant"
#         },

#         "cafe": {
#             "amenity": "cafe"
#         },

#         "park": {
#             "leisure": "park"
#         },

#         "mall": {
#             "shop": "mall"
#         },

#         "tourism": {
#             "tourism": True
#         }
#     }
#     ALLOWED_TOURISM = [
#     "museum",
#     "attraction",
#     "artwork",
#     "gallery"
#     ]

#     def calculate_distance(
#         self,
#         lat1,
#         lon1,
#         lat2,
#         lon2
#     ):
#         R = 6371

#         dlat = radians(lat2 - lat1)
#         dlon = radians(lon2 - lon1)

#         a = (
#             sin(dlat / 2) ** 2
#             + cos(radians(lat1))
#             * cos(radians(lat2))
#             * sin(dlon / 2) ** 2
#         )

#         c = 2 * atan2(
#             sqrt(a),
#             sqrt(1 - a)
#         )

#         return R * c



#     def get_places(
#         self,
#         city,
#         place_type=None,
#         limit=20,
#         user_lat=None,
#         user_lon=None,
#         max_distance=10
#     ):

#         try:

#             tags = self.PLACE_FILTERS.get(
#                 place_type,
#                 {"tourism": True}
#             )
            
#             city = self.city_normalizer.normalize(city)

#             gdf = ox.features_from_place(
#                 f"{city}, Egypt",
#                 tags=tags
#             )

#             results = []

#             for _, row in gdf.iterrows():

#                 name = row.get("name")

#                 if pd.isna(name):
#                     continue

#                 try:

#                     lat = float(
#                         row.geometry.centroid.y
#                     )

#                     lon = float(
#                         row.geometry.centroid.x
#                     )

#                 except Exception:

#                     lat = None
#                     lon = None

#                 maps_url = None

#                 if lat is not None and lon is not None:

#                     maps_url = (
#                         f"https://www.google.com/maps?q="
#                         f"{lat},{lon}"
#                     )

#                 website = row.get("website")

#                 facebook = (
#                     row.get("facebook")
#                     or row.get("contact:facebook")
#                 )

#                 instagram = (
#                     row.get("instagram")
#                     or row.get("contact:instagram")
#                 )
#                 address = row.get("addr:street")

#                 phone = (
#                     row.get("phone")
#                      or row.get("contact:phone")
#                     )

#                 # place_category = (
#                 #     row.get("amenity")
#                 #     or row.get("tourism")
#                 #     or row.get("shop")
#                 #     or row.get("leisure")
#                 #     or "unknown"
#                 # )
#                 place_category = None

#                 for field in [
#                     "amenity",
#                     "tourism",
#                      "shop",
#                     "leisure"
#                 ]:

#                     value = row.get(field)

#                     if value is not None and not pd.isna(value):
#                         place_category = value
#                         break

#                 if place_category is None:
#                   place_category = place_type



#                 distance = None

#                 if (
#                     user_lat
#                     and user_lon
#                     and lat
#                     and lon
#                 ):

#                         distance = self.calculate_distance(
#                             user_lat,
#                             user_lon,
#                             lat,
#                             lon
#                         )

#                         if distance > max_distance:
#                             continue

#                 results.append({

#                     "name": str(name),

#                    "type": str(place_category),

#                     "address":
#                         None if pd.isna(address)
#                         else address,

#                     "phone":
#                         None if pd.isna(phone)
#                         else phone,

#                     "lat": lat,

#                     "lon": lon,
#                     "distance_km": distance,

#                     "maps_url": maps_url,

#                     "website":
#                         None if pd.isna(website)
#                         else website,

#                     "facebook":
#                         None if pd.isna(facebook)
#                         else facebook,

#                     "instagram":
#                         None if pd.isna(instagram)
#                         else instagram
#                 })

#                 tourism_type = row.get("tourism")

#                 if place_type == "tourism":
                    
#                     if tourism_type not in ALLOWED_TOURISM:
#                         continue


#                 if len(results) >= limit:
#                     break

#             return results

#         except Exception as e:

#             return {
#                 "error": str(e)
#             }

# import osmnx as ox
# import pandas as pd
# from math import radians, sin, cos, sqrt, atan2
# from utils.city_normalizer import CityNormalizer


# class PlacesService:

#     PLACE_FILTERS = {
#         "restaurant": {"amenity": "restaurant"},
#         "cafe": {"amenity": "cafe"},
#         "park": {"leisure": "park"},
#         "mall": {"shop": "mall"},
#         "tourism": {"tourism": True}
#     }

#     ALLOWED_TOURISM = [
#         "museum",
#         "attraction",
#         "gallery",
#         "artwork"
#     ]

#     def __init__(self):
#         self.city_normalizer = CityNormalizer()

#     def calculate_distance(
#         self,
#         lat1,
#         lon1,
#         lat2,
#         lon2
#     ):
#         R = 6371

#         dlat = radians(lat2 - lat1)
#         dlon = radians(lon2 - lon1)

#         a = (
#             sin(dlat / 2) ** 2
#             + cos(radians(lat1))
#             * cos(radians(lat2))
#             * sin(dlon / 2) ** 2
#         )

#         c = 2 * atan2(
#             sqrt(a),
#             sqrt(1 - a)
#         )

#         return R * c

#     def get_places(
#         self,
#         city,
#         place_type=None,
#         limit=20,
#         user_lat=None,
#         user_lon=None,
#         max_distance=10
#     ):

#         try:

#             city = self.city_normalizer.normalize(city)

#             tags = self.PLACE_FILTERS.get(
#                 place_type,
#                 {"tourism": True}
#             )

#             gdf = ox.features_from_place(
#                 f"{city}, Egypt",
#                 tags=tags
#             )

#             results = []

#             for _, row in gdf.iterrows():

#                 name = row.get("name")

#                 if pd.isna(name):
#                     continue

#                 tourism_type = row.get("tourism")

#                 if place_type == "tourism":
#                     if tourism_type not in self.ALLOWED_TOURISM:
#                         continue

#                 try:
#                     lat = float(row.geometry.centroid.y)
#                     lon = float(row.geometry.centroid.x)

#                 except Exception:
#                     continue

#                 distance = None

#                 if (
#                     user_lat is not None
#                     and user_lon is not None
#                 ):

#                     distance = self.calculate_distance(
#                         user_lat,
#                         user_lon,
#                         lat,
#                         lon
#                     )

#                     if distance > max_distance:
#                         continue

#                 place_category = None

#                 for field in [
#                     "amenity",
#                     "tourism",
#                     "shop",
#                     "leisure"
#                 ]:

#                     value = row.get(field)

#                     if value is not None and not pd.isna(value):
#                         place_category = value
#                         break

#                 if place_category is None:
#                     place_category = place_type

#                 # rating = row.get("stars")

#                 # if pd.isna(rating):
#                 #     rating = 4.0   
#                 #  
#                 rating = None
#                 reviews_count = None

#                 image_url = None

#                 if place_category == "cafe":
#                     image_url = (
#                         "https://images.unsplash.com/photo-1509042239860-f550ce710b93"
#                     )

#                 elif place_category == "restaurant":
#                     image_url = (
#                         "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4"
#                     )

#                 elif place_category == "park":
#                     image_url = (
#                         "https://images.unsplash.com/photo-1506744038136-46273834b3fb"
#                     )

#                 elif place_category in [
#                     "museum",
#                     "attraction",
#                     "gallery",
#                     "tourism"
#                 ]:
#                     image_url = (
#                         "https://images.unsplash.com/photo-1518998053901-5348d3961a04"
#                     )

#                 elif place_category == "mall":
#                     image_url = (
#                         "https://images.unsplash.com/photo-1483985988355-763728e1935b"
#                     )
#                     DEFAULT_IMAGES = {
#                         "cafe": "https://images.unsplash.com/photo-1509042239860-f550ce710b93",
#                         "restaurant": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4",
#                         "park": "https://images.unsplash.com/photo-1506744038136-46273834b3fb",
#                         "museum": "https://images.unsplash.com/photo-1518998053901-5348d3961a04",
#                         "attraction": "https://images.unsplash.com/photo-1524492412937-b28074a5d7da",
#                         "mall": "https://images.unsplash.com/photo-1481437156560-3205f6a55735"
#                     }

#                 results.append({

#                     "name": str(name),

#                     "type": str(place_category),

#                     "rating": rating,

#                     "reviews_count": reviews_count,

#                     "image": DEFAULT_IMAGES.get(
#                         place_category,
#                         "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee"
#                     ),

#                     "address":
#                         None if pd.isna(row.get("addr:street"))
#                         else row.get("addr:street"),

#                     "phone":
#                         None if pd.isna(
#                             row.get("phone")
#                             or row.get("contact:phone")
#                         )
#                         else (
#                             row.get("phone")
#                             or row.get("contact:phone")
#                         ),

#                     "lat": lat,
#                     "lon": lon,

#                     "distance_km": distance,

#                     "maps_url":
#                         f"https://www.google.com/maps?q={lat},{lon}",

#                     "website":
#                         None if pd.isna(row.get("website"))
#                         else row.get("website"),

#                     "facebook":
#                         None if pd.isna(
#                             row.get("facebook")
#                             or row.get("contact:facebook")
#                         )
#                         else (
#                             row.get("facebook")
#                             or row.get("contact:facebook")
#                         ),

#                     "instagram":
#                         None if pd.isna(
#                             row.get("instagram")
#                             or row.get("contact:instagram")
#                         )
#                         else (
#                             row.get("instagram")
#                             or row.get("contact:instagram")
#                         )

#                 })

#                 if len(results) >= limit:
#                     break

#             return results

#         except Exception as e:
#             return {
#                 "error": str(e)
#             }
        

# class GooglePlacesService:
#     pass       

# import osmnx as ox
# import pandas as pd
# from math import radians, sin, cos, sqrt, atan2
# from utils.city_normalizer import CityNormalizer


# class PlacesService:

#     # فلاتر البحث الأساسية في OpenStreetMap
#     PLACE_FILTERS = {
#         "restaurant": {"amenity": "restaurant"},
#         "cafe": {"amenity": "cafe"},
#         "park": {"leisure": "park"},
#         "mall": {"shop": "mall"},
#         "tourism": {"tourism": True}
#     }

#     # الأماكن السياحية المسموح بها فقط لتجنب الفوضى (مثل الفنادق أو اللوحات الإرشادية)
#     ALLOWED_TOURISM = [
#         "museum",
#         "attraction",
#         "gallery",
#         "artwork"
#     ]

#     # الصور الافتراضية لكل نوع (تم نقلها هنا لمنع الـ NameError ولتنظيف الكود)
#     DEFAULT_IMAGES = {
#         "cafe": "https://images.unsplash.com/photo-1509042239860-f550ce710b93",
#         "restaurant": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4",
#         "park": "https://images.unsplash.com/photo-1506744038136-46273834b3fb",
#         "museum": "https://images.unsplash.com/photo-1518998053901-5348d3961a04",
#         "attraction": "https://images.unsplash.com/photo-1524492412937-b28074a5d7da",
#         "mall": "https://images.unsplash.com/photo-1481437156560-3205f6a55735",
#         "default": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee"
#     }

#     def __init__(self):
#         self.city_normalizer = CityNormalizer()

#     def calculate_distance(self, lat1, lon1, lat2, lon2):
#         R = 6371  # نصف قطر الأرض بالكيلومترات
#         dlat = radians(lat2 - lat1)
#         dlon = radians(lon2 - lon1)

#         a = (sin(dlat / 2) ** 2
#              + cos(radians(lat1))
#              * cos(radians(lat2))
#              * sin(dlon / 2) ** 2)

#         c = 2 * atan2(sqrt(a), sqrt(1 - a))
#         return R * c

#     def get_places(self, city, place_type=None, limit=20, user_lat=None, user_lon=None, max_distance=10):
#         try:
#             # توحيد اسم المدينة
#             city = self.city_normalizer.normalize(city)

#             # جلب الفلتر المناسب
#             tags = self.PLACE_FILTERS.get(place_type, {"tourism": True})

#             # جلب البيانات من OSMnx
#             # gdf = ox.features_from_place(f"{city}, Egypt", tags=tags)
#             try:
#                 gdf = ox.features_from_place(
#                     f"{city}, Egypt",
#                     tags=tags
#                 )
#             except Exception:
#                 print(f"OSM FAILED: {city} - {place_type}")
#                 return []
            
#             # إذا كانت البيانات فارغة، ارجع مصفوفة فارغة مباشرة دون الدخول في أخطاء
#             if gdf.empty:
#                 return []

#             results = []

#             for _, row in gdf.iterrows():
#                 name = row.get("name")
#                 if pd.isna(name) or not str(name).strip():
#                     continue

#                 tourism_type = row.get("tourism")

#                 # تصفية الأماكن السياحية غير المرغوبة
#                 if place_type == "tourism" and tourism_type not in self.ALLOWED_TOURISM:
#                     continue

#                 # استخراج الإحداثيات بأمان اعتماداً على الـ Centroid
#                 try:
#                     lat = float(row.geometry.centroid.y)
#                     lon = float(row.geometry.centroid.x)
#                 except Exception:
#                     continue

#                 # حساب المسافة والتصفية بناءً عليها
#                 distance = None
#                 if user_lat is not None and user_lon is not None:
#                     distance = self.calculate_distance(user_lat, user_lon, lat, lon)
#                     if distance > max_distance:
#                         continue

#                 # تحديد التصنيف الفعلي للمكان
#                 place_category = None
#                 for field in ["amenity", "tourism", "shop", "leisure"]:
#                     value = row.get(field)
#                     if value is not None and not pd.isna(value):
#                         place_category = str(value)
#                         break

#                 if place_category is None:
#                     place_category = place_type

#                 # إعداد روابط هواتف وتواصل اجتماعي نظيفة
#                 phone = row.get("phone") or row.get("contact:phone")
#                 phone = None if pd.isna(phone) else str(phone)

#                 facebook = row.get("facebook") or row.get("contact:facebook")
#                 facebook = None if pd.isna(facebook) else str(facebook)

#                 instagram = row.get("instagram") or row.get("contact:instagram")
#                 instagram = None if pd.isna(instagram) else str(instagram)

#                 website = row.get("website")
#                 website = None if pd.isna(website) else str(website)

#                 address = row.get("addr:street")
#                 address = None if pd.isna(address) else str(address)

#                 # إضافة المكان إلى النتائج
#                 results.append({
#                     "name": str(name),
#                     "type": str(place_category),
#                     "rating": 4.0,         # OSM لا يحتوي على تقييمات حقيقية في الغالب
#                     "reviews_count": None,
#                     "image": self.DEFAULT_IMAGES.get(place_category, self.DEFAULT_IMAGES["default"]),
#                     "address": address,
#                     "phone": phone,
#                     "lat": lat,
#                     "lon": lon,
#                     "distance_km": round(distance, 2) if distance is not None else None,
#                     "maps_url": f"https://www.google.com/maps?q={lat},{lon}",
#                     "website": website,
#                     "facebook": facebook,
#                     "instagram": instagram
#                 })

#             # تحسين: ترتيب الأماكن حسب الأقرب للمستخدم أولاً قبل تطبيق الـ limit
#             if user_lat is not None and user_lon is not None:
#                 results.sort(key=lambda x: x["distance_km"] if x["distance_km"] is not None else 999999)

#             return results[:limit]

#         # except Exception as e:
#         #     return {"error": str(e)}
#         except Exception as e:
#             import traceback
#             traceback.print_exc()

#             return {
#                 "error": str(e)
#     }


# class GooglePlacesService:
#     pass

import osmnx as ox
import pandas as pd
from math import radians, sin, cos, sqrt, atan2
from utils.city_normalizer import CityNormalizer


class PlacesService:

    # فلاتر البحث الأساسية في OpenStreetMap
    PLACE_FILTERS = {
        "restaurant": {"amenity": "restaurant"},
        "cafe": {"amenity": "cafe"},
        "park": {"leisure": "park"},
        "mall": {"shop": "mall"},
        "tourism": {"tourism": True}
    }

    # الأماكن السياحية المسموح بها فقط لتجنب الفوضى (مثل الفنادق أو اللوحات الإرشادية)
    ALLOWED_TOURISM = [
        "museum",
        "attraction",
        "gallery",
        "artwork"
    ]

    # الصور الافتراضية لكل نوع (تم نقلها هنا لمنع الـ NameError ولتنظيف الكود)
    DEFAULT_IMAGES = {
        "cafe": "https://images.unsplash.com/photo-1509042239860-f550ce710b93",
        "restaurant": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4",
        "park": "https://images.unsplash.com/photo-1506744038136-46273834b3fb",
        "museum": "https://images.unsplash.com/photo-1518998053901-5348d3961a04",
        "attraction": "https://images.unsplash.com/photo-1524492412937-b28074a5d7da",
        "mall": "https://images.unsplash.com/photo-1481437156560-3205f6a55735",
        "default": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee"
    }

    def __init__(self):
        self.city_normalizer = CityNormalizer()

        # 💡 الحل السحري: إجبار OSMnx على جلب حقول التواصل الاجتماعي والاتصال من الخريطة
        social_tags = [
            "phone", "contact:phone", 
            "website", "contact:website",
            "facebook", "contact:facebook", 
            "instagram", "contact:instagram",
            "contact:twitter", "contact:youtube",
            "addr:street"
        ]
        
        # دمج التاجز الجديدة مع التاجز الافتراضية للمكتبة حتى لا تفقد البيانات الأساسية
        ox.settings.useful_tags_node = list(set(ox.settings.useful_tags_node + social_tags))
        ox.settings.useful_tags_way = list(set(ox.settings.useful_tags_way + social_tags))

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        R = 6371  # نصف قطر الأرض بالكيلومترات
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)

        a = (sin(dlat / 2) ** 2
             + cos(radians(lat1))
             * cos(radians(lat2))
             * sin(dlon / 2) ** 2)

        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c

    def get_places(self, city, place_type=None, limit=20, user_lat=None, user_lon=None, max_distance=10):
        try:
            # توحيد اسم المدينة
            city = self.city_normalizer.normalize(city)

            # جلب الفلتر المناسب
            tags = self.PLACE_FILTERS.get(place_type, {"tourism": True})

            # جلب البيانات من OSMnx بداخل try-except لحمايتها
            try:
                gdf = ox.features_from_place(
                    f"{city}, Egypt",
                    tags=tags
                )
            except Exception:
                print(f"OSM FAILED: {city} - {place_type}")
                return []
            
            # إذا كانت البيانات فارغة، ارجع مصفوفة فارغة مباشرة دون الدخول في أخطاء
            if gdf.empty:
                return []

            results = []

            for _, row in gdf.iterrows():
                name = row.get("name")
                if pd.isna(name) or not str(name).strip():
                    continue

                tourism_type = row.get("tourism")

                # تصفية الأماكن السياحية غير المرغوبة
                if place_type == "tourism" and tourism_type not in self.ALLOWED_TOURISM:
                    continue

                # استخراج الإحداثيات بأمان اعتماداً على الـ Centroid
                try:
                    lat = float(row.geometry.centroid.y)
                    lon = float(row.geometry.centroid.x)
                except Exception:
                    continue

                # حساب المسافة والتصفية بناءً عليها
                distance = None
                if user_lat is not None and user_lon is not None:
                    distance = self.calculate_distance(user_lat, user_lon, lat, lon)
                    if distance > max_distance:
                        continue

                # تحديد التصنيف الفعلي للمكان
                place_category = None
                for field in ["amenity", "tourism", "shop", "leisure"]:
                    value = row.get(field)
                    if value is not None and not pd.isna(value):
                        place_category = str(value)
                        break

                if place_category is None:
                    place_category = place_type

                # 💡 فحص واستخراج بيانات الاتصال والتواصل الاجتماعي بأمان وحمايتها من قيم NaN
                phone = row.get("phone") if "phone" in row and not pd.isna(row.get("phone")) else row.get("contact:phone")
                phone = None if pd.isna(phone) else str(phone)

                facebook = row.get("facebook") if "facebook" in row and not pd.isna(row.get("facebook")) else row.get("contact:facebook")
                facebook = None if pd.isna(facebook) else str(facebook)

                instagram = row.get("instagram") if "instagram" in row and not pd.isna(row.get("instagram")) else row.get("contact:instagram")
                instagram = None if pd.isna(instagram) else str(instagram)

                website = row.get("website") if "website" in row and not pd.isna(row.get("website")) else row.get("contact:website")
                website = None if pd.isna(website) else str(website)

                address = row.get("addr:street") if "addr:street" in row else None
                address = None if pd.isna(address) else str(address)

                # إضافة المكان إلى النتائج
                results.append({
                    "name": str(name),
                    "type": str(place_category),
                    "rating": 4.0,  # OSM لا يحتوي على تقييمات حقيقية في الغالب
                    "reviews_count": None,
                    "image": self.DEFAULT_IMAGES.get(place_category, self.DEFAULT_IMAGES["default"]),
                    "address": address,
                    "phone": phone,
                    "lat": lat,
                    "lon": lon,
                    "distance_km": round(distance, 2) if distance is not None else None,
                    "maps_url": f"https://www.google.com/maps/search/?api=1&query={lat},{lon}",
                    "website": website,
                    "facebook": facebook,
                    "instagram": instagram
                })

            # تحسين: ترتيب الأماكن حسب الأقرب للمستخدم أولاً قبل تطبيق الـ limit
            if user_lat is not None and user_lon is not None:
                results.sort(key=lambda x: x["distance_km"] if x["distance_km"] is not None else 999999)

            return results[:limit]

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"error": str(e)}


class GooglePlacesService:
    pass