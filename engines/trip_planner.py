import os
import random
import traceback
import math
import requests
from datetime import datetime, timedelta

try:
    import folium  # type: ignore
except ImportError:
    folium = None

try:
    from html2image import Html2Image
except ImportError:
    Html2Image = None

# استيراد قاعدة بيانات الأماكن الحقيقية لجمهورية مصر العربية من مشروعك
try:
    from data.egypt_places import REAL_PLACES_DB
except ImportError:
    REAL_PLACES_DB = {}


class TripPlanner:
    CITY_TRANSLATIONS = {
        "cairo": "القاهرة", "القاهرة": "القاهرة",
        "alex": "الإسكندرية", "alexandria": "الإسكندرية", "الإسكندرية": "الإسكندرية",
        "giza": "الجيزة", "الجيزة": "الجيزة",
        "luxor": "الأقصر", "الأقصر": "الأقصر",
        "aswan": "أسوان", "أسوان": "أسوان",
        "mansoura": "المنصورة", "المنصورة": "المنصورة",
        "tanta": "طنطا", "طنطا": "طنطا",
        "dahab": "دهب", "دهب": "دهب",
        "hurghada": "الغردقة", "الغردقة": "الغردقة",
        "sharm": "شرم الشيخ", "sharm el sheikh": "شرم الشيخ", "شرم الشيخ": "شرم الشيخ"
    }

    CITY_COORDINATES_REGISTRY = {
        "القاهرة": (30.0444, 31.2357), "الإسكندرية": (31.2001, 29.9187), "الجيزة": (30.0131, 31.2089),
        "الأقصر": (25.6872, 32.6396), "أسوان": (24.0889, 32.8998), "المنصورة": (31.0409, 31.3785),
        "طنطا": (30.7865, 30.9998), "دهب": (28.5003, 34.5170), "شرم الشيخ": (27.9158, 34.3299),
        "الغردقة": (27.2579, 33.8116)
    }

    PRIORITY_LANDMARKS_DB = {
        "القاهرة": [
            {"name": "خان الخليلي", "type": "tourism", "lat": 30.0476, "lon": 31.2625, "importance": 10,
             "price_tier": "budget", "vibe_tags": ["historic", "cultural", "social"]},
            {"name": "حديقة الأزهر", "type": "park", "lat": 30.0444, "lon": 31.2658, "importance": 10,
             "price_tier": "budget", "vibe_tags": ["scenic", "romantic", "family", "relaxed"]},
            {"name": "ممشى أهل مصر", "type": "tourism", "lat": 30.0091, "lon": 31.2289, "importance": 9,
             "price_tier": "mid", "vibe_tags": ["scenic", "family", "social"]},
            {"name": "سيتي ستارز", "type": "mall", "lat": 30.0731, "lon": 31.3458, "importance": 9,
             "price_tier": "luxury", "vibe_tags": ["upscale", "youth", "family", "social"]},
            {"name": "كايرو فيستيفال سيتي", "type": "mall", "lat": 30.0271, "lon": 31.4105, "importance": 8,
             "price_tier": "luxury", "vibe_tags": ["upscale", "family", "social"]},
            {"name": "حي الزمالك (كورنيش النيل)", "type": "tourism", "lat": 30.0626, "lon": 31.2197, "importance": 8,
             "price_tier": "mid", "vibe_tags": ["scenic", "romantic", "quiet"]},
            {"name": "مقهى الفيشاوي", "type": "cafe", "lat": 30.0478, "lon": 31.2627, "importance": 9,
             "price_tier": "budget", "vibe_tags": ["historic", "cultural", "social"]},
            {"name": "ميدان التحرير والمتحف المصري", "type": "tourism", "lat": 30.0478, "lon": 31.2336, "importance": 9,
             "price_tier": "budget", "vibe_tags": ["historic", "cultural"]},
            {"name": "مطعم أبو طارق", "type": "restaurant", "lat": 30.0500, "lon": 31.2400, "importance": 8,
             "price_tier": "budget", "vibe_tags": ["family", "youth"]},
        ],
        "المنصورة": [
            {"name": "جزيرة الورد", "type": "park", "lat": 31.0335, "lon": 31.3805, "importance": 10,
             "price_tier": "budget", "vibe_tags": ["family", "scenic", "relaxed", "romantic"]},
            {"name": "ممشى توريل", "type": "tourism", "lat": 31.0420, "lon": 31.3795, "importance": 9,
             "price_tier": "budget", "vibe_tags": ["scenic", "romantic", "family", "relaxed"]},
            {"name": "نادي الجزيرة", "type": "tourism", "lat": 31.0350, "lon": 31.3810, "importance": 7,
             "price_tier": "mid", "vibe_tags": ["family", "relaxed"]},
            {"name": "Sun Mall المنصورة", "type": "mall", "lat": 31.0289, "lon": 31.3819, "importance": 8,
             "price_tier": "mid", "vibe_tags": ["family", "youth", "social"]},
            {"name": "مول الجامعة", "type": "mall", "lat": 31.0455, "lon": 31.3697, "importance": 7,
             "price_tier": "budget", "vibe_tags": ["youth", "social"]},
            {"name": "جامعة المنصورة (كورنيش النيل)", "type": "tourism", "lat": 31.0457, "lon": 31.3699, "importance": 6,
             "price_tier": "budget", "vibe_tags": ["scenic", "youth"]},
            {"name": "مطعم كشري زيزو", "type": "restaurant", "lat": 31.0395, "lon": 31.3800, "importance": 7,
             "price_tier": "budget", "vibe_tags": ["family", "youth"]},
            {"name": "كافيه اندريا المنصورة", "type": "cafe", "lat": 31.0410, "lon": 31.3780, "importance": 6,
             "price_tier": "luxury", "vibe_tags": ["upscale", "romantic", "quiet"]},
            # 🆕 أماكن luxury/youth أُضيفت لتغطية mood=luxury الذي كان غير مدعوم
            # فعليًا قبل كده (الكود كان بيرجع نفس قائمة tourism/park بدون
            # تمييز "راقي" عن "شعبي"). دي أماكن حقيقية معروفة في المنصورة.
            {"name": "Porto Mansoura", "type": "mall", "lat": 31.0145, "lon": 31.3680, "importance": 8,
             "price_tier": "luxury", "vibe_tags": ["upscale", "youth", "social"]},
            {"name": "U Plaza Mansoura", "type": "mall", "lat": 31.0470, "lon": 31.3650, "importance": 6,
             "price_tier": "mid", "vibe_tags": ["youth", "social"]},
            {"name": "Starbucks المنصورة", "type": "cafe", "lat": 31.0400, "lon": 31.3790, "importance": 6,
             "price_tier": "luxury", "vibe_tags": ["upscale", "youth", "social"]},
            {"name": "كافيه كوستا المنصورة", "type": "cafe", "lat": 31.0415, "lon": 31.3770, "importance": 5,
             "price_tier": "mid", "vibe_tags": ["youth", "social"]},
        ],
        "الإسكندرية": [
            {"name": "قلعة قايتباي", "type": "tourism", "lat": 31.2138, "lon": 29.8855, "importance": 10,
             "price_tier": "budget", "vibe_tags": ["historic", "scenic", "romantic"]},
            {"name": "مكتبة الإسكندرية", "type": "tourism", "lat": 31.2089, "lon": 29.9092, "importance": 10,
             "price_tier": "mid", "vibe_tags": ["cultural", "historic", "quiet"]},
            {"name": "كورنيش الإسكندرية (المنشية)", "type": "tourism", "lat": 31.1975, "lon": 29.8925, "importance": 8,
             "price_tier": "budget", "vibe_tags": ["scenic", "romantic", "family"]},
            {"name": "حدائق المنتزه", "type": "park", "lat": 31.2864, "lon": 29.9928, "importance": 9,
             "price_tier": "budget", "vibe_tags": ["scenic", "family", "relaxed", "romantic"]},
            {"name": "سان ستيفانو مول", "type": "mall", "lat": 31.2447, "lon": 29.9692, "importance": 8,
             "price_tier": "luxury", "vibe_tags": ["upscale", "youth", "social"]},
            {"name": "سيتي سنتر الإسكندرية", "type": "mall", "lat": 31.1922, "lon": 29.9511, "importance": 7,
             "price_tier": "mid", "vibe_tags": ["family", "youth", "social"]},
            {"name": "المتحف اليوناني الروماني", "type": "museum", "lat": 31.1975, "lon": 29.9050, "importance": 7,
             "price_tier": "budget", "vibe_tags": ["cultural", "historic", "quiet"]},
            {"name": "كافيه تريانون", "type": "cafe", "lat": 31.1996, "lon": 29.8978, "importance": 8,
             "price_tier": "luxury", "vibe_tags": ["upscale", "romantic", "historic", "quiet"]},
            {"name": "مطعم سمك فاروس", "type": "restaurant", "lat": 31.2010, "lon": 29.8870, "importance": 7,
             "price_tier": "mid", "vibe_tags": ["family", "scenic"]},
        ],
        "الجيزة": [
            {"name": "أهرامات الجيزة وأبو الهول", "type": "tourism", "lat": 29.9792, "lon": 31.1342, "importance": 10,
             "price_tier": "mid", "vibe_tags": ["historic", "cultural", "scenic"]},
            {"name": "المتحف المصري الكبير (GEM)", "type": "museum", "lat": 29.9930, "lon": 31.1147, "importance": 10,
             "price_tier": "mid", "vibe_tags": ["cultural", "historic", "family"]},
            {"name": "حديقة الحيوان بالجيزة", "type": "zoo", "lat": 30.0287, "lon": 31.2123, "importance": 7,
             "price_tier": "budget", "vibe_tags": ["family", "kids", "relaxed"]},
            {"name": "كايرو مول", "type": "mall", "lat": 30.0083, "lon": 31.2080, "importance": 6,
             "price_tier": "mid", "vibe_tags": ["family", "youth", "social"]},
            {"name": "كورنيش النيل (المعادي/الجيزة)", "type": "tourism", "lat": 29.9627, "lon": 31.2298, "importance": 6,
             "price_tier": "budget", "vibe_tags": ["scenic", "romantic", "relaxed"]},
            {"name": "مطعم أبو شكرة (الهرم)", "type": "restaurant", "lat": 29.9870, "lon": 31.1480, "importance": 7,
             "price_tier": "mid", "vibe_tags": ["family", "historic"]},
            {"name": "كافيهات شارع الهرم", "type": "cafe", "lat": 29.9900, "lon": 31.1700, "importance": 5,
             "price_tier": "budget", "vibe_tags": ["youth", "social"]},
            {"name": "حديقة الأورمان", "type": "park", "lat": 30.0285, "lon": 31.2095, "importance": 6,
             "price_tier": "budget", "vibe_tags": ["family", "relaxed", "scenic"]},
        ],
        "الأقصر": [
            {"name": "معبد الكرنك", "type": "tourism", "lat": 25.7188, "lon": 32.6573, "importance": 10,
             "price_tier": "mid", "vibe_tags": ["historic", "cultural"]},
            {"name": "وادي الملوك", "type": "tourism", "lat": 25.7402, "lon": 32.6014, "importance": 10,
             "price_tier": "mid", "vibe_tags": ["historic", "cultural", "adventure"]},
            {"name": "معبد الأقصر", "type": "tourism", "lat": 25.6997, "lon": 32.6396, "importance": 9,
             "price_tier": "budget", "vibe_tags": ["historic", "cultural", "scenic"]},
            {"name": "كورنيش النيل بالأقصر", "type": "tourism", "lat": 25.6970, "lon": 32.6390, "importance": 7,
             "price_tier": "budget", "vibe_tags": ["scenic", "romantic", "relaxed"]},
            {"name": "معابد البر الغربي (الرامسيوم/حتشبسوت)", "type": "tourism", "lat": 25.7402, "lon": 32.6066, "importance": 9,
             "price_tier": "mid", "vibe_tags": ["historic", "cultural", "adventure"]},
            {"name": "متحف الأقصر", "type": "museum", "lat": 25.7011, "lon": 32.6428, "importance": 7,
             "price_tier": "budget", "vibe_tags": ["cultural", "historic", "quiet"]},
            {"name": "سوق الأقصر السياحي", "type": "tourism", "lat": 25.6960, "lon": 32.6420, "importance": 6,
             "price_tier": "budget", "vibe_tags": ["social", "youth"]},
            {"name": "مطعم سفنكس على النيل", "type": "restaurant", "lat": 25.6985, "lon": 32.6400, "importance": 6,
             "price_tier": "mid", "vibe_tags": ["scenic", "romantic", "family"]},
            {"name": "كافيه كورنيش الأقصر", "type": "cafe", "lat": 25.6975, "lon": 32.6395, "importance": 5,
             "price_tier": "budget", "vibe_tags": ["scenic", "relaxed"]},
        ],
        "أسوان": [
            {"name": "السد العالي", "type": "tourism", "lat": 23.9700, "lon": 32.8775, "importance": 9,
             "price_tier": "budget", "vibe_tags": ["historic", "cultural"]},
            {"name": "معبد فيلة", "type": "tourism", "lat": 24.0258, "lon": 32.8843, "importance": 10,
             "price_tier": "mid", "vibe_tags": ["historic", "cultural", "scenic", "adventure"]},
            {"name": "النوبة (القرية النوبية - الشلال)", "type": "tourism", "lat": 24.0950, "lon": 32.8800, "importance": 8,
             "price_tier": "mid", "vibe_tags": ["cultural", "family", "social"]},
            {"name": "كورنيش النيل بأسوان", "type": "tourism", "lat": 24.0889, "lon": 32.8998, "importance": 7,
             "price_tier": "budget", "vibe_tags": ["scenic", "romantic", "relaxed"]},
            {"name": "حديقة النباتات (جزيرة الكتاب)", "type": "park", "lat": 24.0875, "lon": 32.8838, "importance": 7,
             "price_tier": "budget", "vibe_tags": ["scenic", "relaxed", "romantic", "family"]},
            {"name": "سوق أسوان السياحي", "type": "tourism", "lat": 24.0900, "lon": 32.8990, "importance": 6,
             "price_tier": "budget", "vibe_tags": ["social", "youth"]},
            {"name": "مطعم 1902 أسوان", "type": "restaurant", "lat": 24.0870, "lon": 32.8920, "importance": 6,
             "price_tier": "mid", "vibe_tags": ["scenic", "romantic"]},
            {"name": "كافيه كورنيش أسوان", "type": "cafe", "lat": 24.0895, "lon": 32.8995, "importance": 5,
             "price_tier": "budget", "vibe_tags": ["scenic", "relaxed"]},
        ],
        "طنطا": [
            {"name": "مسجد السيد البدوي", "type": "tourism", "lat": 30.7865, "lon": 30.9998, "importance": 9,
             "price_tier": "budget", "vibe_tags": ["historic", "cultural"]},
            {"name": "حديقة طنطا العامة (الجزيرة)", "type": "park", "lat": 30.7900, "lon": 31.0010, "importance": 7,
             "price_tier": "budget", "vibe_tags": ["family", "relaxed", "scenic"]},
            {"name": "كورنيش بحر طنطا", "type": "tourism", "lat": 30.7920, "lon": 31.0050, "importance": 6,
             "price_tier": "budget", "vibe_tags": ["scenic", "romantic", "relaxed"]},
            {"name": "تنتا مول", "type": "mall", "lat": 30.7830, "lon": 30.9950, "importance": 6,
             "price_tier": "mid", "vibe_tags": ["family", "youth", "social"]},
            {"name": "مطعم الشابوري طنطا", "type": "restaurant", "lat": 30.7880, "lon": 30.9970, "importance": 5,
             "price_tier": "budget", "vibe_tags": ["family", "youth"]},
            {"name": "كافيهات شارع البحر طنطا", "type": "cafe", "lat": 30.7910, "lon": 31.0030, "importance": 5,
             "price_tier": "budget", "vibe_tags": ["youth", "social"]},
        ],
        "دهب": [
            {"name": "البلو هول (Blue Hole)", "type": "tourism", "lat": 28.5772, "lon": 34.5400, "importance": 10,
             "price_tier": "mid", "vibe_tags": ["adventure", "outdoor", "scenic"]},
            {"name": "لاجونة دهب (Lagoon)", "type": "beach", "lat": 28.5050, "lon": 34.5130, "importance": 9,
             "price_tier": "mid", "vibe_tags": ["family", "relaxed", "scenic", "outdoor"]},
            {"name": "كانيون دهب", "type": "tourism", "lat": 28.6230, "lon": 34.5580, "importance": 8,
             "price_tier": "mid", "vibe_tags": ["adventure", "outdoor"]},
            {"name": "سوق دهب وممشى البحر", "type": "tourism", "lat": 28.5003, "lon": 34.5170, "importance": 7,
             "price_tier": "budget", "vibe_tags": ["social", "youth", "scenic"]},
            {"name": "جزيرة الفرعون", "type": "tourism", "lat": 28.6650, "lon": 34.5860, "importance": 7,
             "price_tier": "mid", "vibe_tags": ["adventure", "scenic", "historic"]},
            {"name": "مطعم نخيل دهب", "type": "restaurant", "lat": 28.5010, "lon": 34.5160, "importance": 6,
             "price_tier": "mid", "vibe_tags": ["scenic", "romantic", "relaxed"]},
            {"name": "كافيهات ممشى دهب البحري", "type": "cafe", "lat": 28.5005, "lon": 34.5175, "importance": 6,
             "price_tier": "budget", "vibe_tags": ["scenic", "relaxed", "youth"]},
        ],
        "شرم الشيخ": [
            {"name": "نبق المحمية الطبيعية", "type": "park", "lat": 28.0167, "lon": 34.4167, "importance": 8,
             "price_tier": "mid", "vibe_tags": ["adventure", "outdoor", "scenic"]},
            {"name": "ناما باي (Naama Bay)", "type": "tourism", "lat": 27.9119, "lon": 34.3300, "importance": 10,
             "price_tier": "luxury", "vibe_tags": ["upscale", "youth", "social", "romantic"]},
            {"name": "سوهو سكوير", "type": "mall", "lat": 27.8460, "lon": 34.2960, "importance": 8,
             "price_tier": "luxury", "vibe_tags": ["upscale", "youth", "social", "family"]},
            {"name": "رأس محمد (المحمية الطبيعية)", "type": "park", "lat": 27.7333, "lon": 34.2500, "importance": 9,
             "price_tier": "mid", "vibe_tags": ["adventure", "outdoor", "scenic"]},
            {"name": "السوق القديم بشرم الشيخ", "type": "tourism", "lat": 27.8580, "lon": 34.2660, "importance": 7,
             "price_tier": "budget", "vibe_tags": ["social", "youth"]},
            {"name": "مطعم فاروز ناما باي", "type": "restaurant", "lat": 27.9120, "lon": 34.3305, "importance": 6,
             "price_tier": "luxury", "vibe_tags": ["upscale", "romantic", "scenic"]},
            {"name": "كافيهات ناما باي", "type": "cafe", "lat": 27.9115, "lon": 34.3295, "importance": 6,
             "price_tier": "luxury", "vibe_tags": ["upscale", "youth", "social"]},
        ],
        "الغردقة": [
            {"name": "مارينا الغردقة", "type": "tourism", "lat": 27.2461, "lon": 33.8347, "importance": 9,
             "price_tier": "mid", "vibe_tags": ["scenic", "social", "romantic"]},
            {"name": "السقالة (الغردقة القديمة)", "type": "tourism", "lat": 27.2370, "lon": 33.8230, "importance": 8,
             "price_tier": "budget", "vibe_tags": ["historic", "social", "youth"]},
            {"name": "جزيرة الجفتون", "type": "beach", "lat": 27.2167, "lon": 33.9500, "importance": 9,
             "price_tier": "mid", "vibe_tags": ["adventure", "outdoor", "family", "scenic"]},
            {"name": "سنزو مول الغردقة", "type": "mall", "lat": 27.2579, "lon": 33.8116, "importance": 7,
             "price_tier": "mid", "vibe_tags": ["family", "youth", "social"]},
            {"name": "مطعم فيشاوي الغردقة", "type": "restaurant", "lat": 27.2400, "lon": 33.8250, "importance": 6,
             "price_tier": "mid", "vibe_tags": ["family", "scenic"]},
            {"name": "كافيهات مارينا الغردقة", "type": "cafe", "lat": 27.2465, "lon": 33.8350, "importance": 6,
             "price_tier": "mid", "vibe_tags": ["scenic", "romantic", "social"]},
            {"name": "حديقة الغردقة العامة", "type": "park", "lat": 27.2550, "lon": 33.8200, "importance": 5,
             "price_tier": "budget", "vibe_tags": ["family", "relaxed"]},
        ],
    }

    CITY_SEASONAL_TEMPS = {
        "القاهرة":     [14, 16, 19, 24, 28, 31, 32, 32, 30, 27, 21, 16],
        "الإسكندرية":  [15, 15, 17, 20, 23, 26, 27, 28, 27, 24, 20, 16],
        "الجيزة":      [14, 16, 19, 24, 28, 31, 32, 32, 30, 27, 21, 16],
        "الأقصر":      [18, 20, 25, 31, 36, 39, 40, 40, 37, 32, 25, 19],
        "أسوان":       [20, 22, 27, 32, 37, 40, 41, 41, 38, 34, 27, 21],
        "المنصورة":    [14, 15, 18, 22, 26, 29, 30, 30, 28, 25, 20, 15],
        "طنطا":        [14, 15, 18, 22, 26, 29, 30, 30, 28, 25, 20, 15],
        "دهب":         [19, 20, 23, 27, 31, 34, 35, 35, 33, 29, 24, 20],
        "شرم الشيخ":   [20, 21, 24, 28, 32, 35, 36, 36, 34, 30, 25, 21],
        "الغردقة":     [19, 20, 23, 27, 31, 34, 35, 35, 33, 29, 24, 20],
    }

    MOOD_TRANSLATIONS = {
        "family": "عائلية", "youth": "شبابية", "romantic": "رومانسية", "adventure": "مغامرة",
        "tourism": "سياحية", "luxury": "راقية"
    }

    MOOD_CATEGORY_WEIGHTS = {
        "youth": [
            ("cafe", 0.40), ("restaurant", 0.20), ("park", 0.20), ("mall", 0.20)
        ],
        "family": [
            ("museum", 0.25), ("park", 0.25), ("restaurant", 0.25), ("mall", 0.25)
        ],
        "romantic": [
            ("tourism", 0.30), ("cafe", 0.30), ("park", 0.20), ("restaurant", 0.20)
        ],
        "adventure": [
            ("tourism", 0.35), ("park", 0.25), ("attraction", 0.20), ("restaurant", 0.20)
        ],
        "tourism": [
            ("tourism", 0.40), ("museum", 0.25), ("attraction", 0.20), ("restaurant", 0.15)
        ],
        "luxury": [
            ("mall", 0.30), ("cafe", 0.30), ("restaurant", 0.25), ("tourism", 0.15)
        ],
    }

    MOOD_PLACE_TYPES = {
        mood: [cat for cat, _ in weights] for mood, weights in MOOD_CATEGORY_WEIGHTS.items()
    }

    CATEGORY_COST_RANGES = {
        "beach": (40, 100), "cafe": (40, 90), "tourism": (0, 20),
        "museum": (20, 40), "mall": (20, 60), "park": (10, 30),
        "restaurant": (70, 140), "default": (30, 70)
    }

    DEFAULT_OPENING_HOURS_BY_TYPE = {
        "tourism": {"open": "08:00", "close": "17:00"},
        "museum": {"open": "09:00", "close": "16:00"},
        "mall": {"open": "10:00", "close": "23:00"},
        "cafe": {"open": "08:00", "close": "00:00"},
        "restaurant": {"open": "11:00", "close": "00:00"},
        "park": {"open": "07:00", "close": "20:00"},
        "zoo": {"open": "09:00", "close": "16:00"},
        "beach": {"open": "06:00", "close": "19:00"},
        "cinema": {"open": "11:00", "close": "01:00"},
        "attraction": {"open": "09:00", "close": "17:00"},
        "default": {"open": "09:00", "close": "21:00"},
    }

    VISIT_DURATION_MINUTES_BY_TYPE = {
        "tourism": 120,
        "museum": 90,
        "mall": 90,
        "cafe": 45,
        "restaurant": 60,
        "park": 60,
        "zoo": 90,
        "beach": 120,
        "cinema": 150,
        "attraction": 90,
        "default": 75,
    }

    VALID_INTERNAL_CATEGORIES = {
        "restaurant", "cafe", "park", "mall", "museum",
        "zoo", "beach", "cinema", "tourism", "attraction",
    }

    PLACE_NAME_BLACKLIST = [
        "memorial", "monument", "historic", "plaque", "juice",
        "atm", "bank", "parking", "bus stop", "bus station",
        "station", "government", "office", "موقع", "نصب",
        "تذكاري", "محطة أتوبيس", "موقف", "بنك", "صراف",
        "كشك", "مكتب حكومي", "وزارة", "مديرية",
    ]

    MIN_ACCEPTABLE_RATING = 4.2
    MIN_ACCEPTABLE_REVIEWS = 30
    MAX_ACCEPTABLE_DISTANCE_KM = 20.0
    MIN_PLACE_NAME_LENGTH = 4

    CATEGORY_BASE_POPULARITY = {
        "tourism": 8, "mall": 8, "cafe": 7, "restaurant": 7,
        "park": 5, "museum": 6, "attraction": 7, "beach": 7,
        "zoo": 6, "cinema": 6, "default": 4,
    }

    GEOAPIFY_TYPE_QUERY_MAP = {
        "tourism": "tourism.sights",
        "museum": "entertainment.museum",
        "cafe": "catering.cafe",
        "restaurant": "catering.restaurant",
        "mall": "commercial.shopping_mall",
        "park": "leisure.park",
        "attraction": "tourism.attraction",
        "beach": "beach",
        "zoo": "entertainment.zoo",
        "cinema": "entertainment.cinema",
    }

    GEOAPIFY_ENDPOINT = "https://api.geoapify.com/v2/places"

    ARABIC_TYPE_LABELS = {
        "tourism": "معلم سياحي", "cafe": "كافيه", "mall": "مركز تجاري",
        "restaurant": "مطعم", "park": "حديقة عامة", "museum": "متحف",
        "attraction": "معلم جذب", "beach": "شاطئ", "zoo": "حديقة حيوان",
        "cinema": "سينما", "default": "مكان"
    }

    def __init__(self, gemini_key: str = None, openweather_key: str = None, places_service=None,
                 geoapify_key: str = None):
        self.openweather_key = openweather_key or os.getenv("OPENWEATHER_API_KEY")
        self.geoapify_key = geoapify_key or os.getenv("GEOAPIFY_API_KEY")
        self.places_service = places_service

    def _safe_float(self, val, default=0.0):
        try:
            return float(val) if val is not None else default
        except Exception:
            return default

    def _haversine_distance(self, lat1, lon1, lat2, lon2):
        try:
            R = 6371.0
            r_lat1, r_lon1 = math.radians(self._safe_float(lat1)), math.radians(self._safe_float(lon1))
            r_lat2, r_lon2 = math.radians(self._safe_float(lat2)), math.radians(self._safe_float(lon2))
            dlat, dlon = r_lat2 - r_lat1, r_lon2 - r_lon1
            a = math.sin(dlat / 2) ** 2 + math.cos(r_lat1) * math.cos(r_lat2) * math.sin(dlon / 2) ** 2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return round(R * c, 2)
        except Exception:
            return 0.0

    def _parse_time_str(self, time_str):
        try:
            h, m = time_str.split(":")
            h, m = int(h), int(m)
            if h == 0 and m == 0:
                return 24 * 60
            return h * 60 + m
        except Exception:
            return None

    def _get_visit_duration_minutes(self, place_type):
        return self.VISIT_DURATION_MINUTES_BY_TYPE.get(
            place_type, self.VISIT_DURATION_MINUTES_BY_TYPE["default"]
        )

    def _get_opening_hours_for_place(self, place):
        raw_hours = place.get("opening_hours_raw")
        if raw_hours and isinstance(raw_hours, dict) and raw_hours.get("open") and raw_hours.get("close"):
            return {
                "open": raw_hours["open"],
                "close": raw_hours["close"],
                "is_estimated": False,
            }

        default_hours = self.DEFAULT_OPENING_HOURS_BY_TYPE.get(
            place.get("type"), self.DEFAULT_OPENING_HOURS_BY_TYPE["default"]
        )
        return {
            "open": default_hours["open"],
            "close": default_hours["close"],
            "is_estimated": True,
        }

    def _is_open_at(self, place, visit_time_minutes, visit_duration_minutes=150):
        hours = self._get_opening_hours_for_place(place)
        open_min = self._parse_time_str(hours["open"])
        close_min = self._parse_time_str(hours["close"])

        if open_min is None or close_min is None:
            return True, hours

        visit_end_minutes = visit_time_minutes + visit_duration_minutes

        if close_min <= open_min:
            close_min += 24 * 60

        is_open = (visit_time_minutes >= open_min) and (visit_end_minutes <= close_min)
        return is_open, hours

    def _is_valid_place_name(self, name):
        if not name:
            return False
        name_lower = name.lower()
        for bad_word in self.PLACE_NAME_BLACKLIST:
            if bad_word.lower() in name_lower:
                return False
        return True

    def _passes_quality_filters(self, place, center_lat, center_lon, require_reviews=True):
        if place.get("type") not in self.VALID_INTERNAL_CATEGORIES:
            return False, "type_not_in_whitelist"

        name = place.get("name") or ""
        if not self._is_valid_place_name(name):
            return False, "name_blacklisted"

        if len(name.strip()) < self.MIN_PLACE_NAME_LENGTH:
            return False, "name_too_short"

        rating = place.get("rating")
        if rating is not None and rating < self.MIN_ACCEPTABLE_RATING:
            return False, "rating_too_low"

        reviews_count = place.get("reviews_count")
        if require_reviews and reviews_count is not None and reviews_count < self.MIN_ACCEPTABLE_REVIEWS:
            return False, "not_enough_reviews"

        dist = self._haversine_distance(center_lat, center_lon, place.get("lat"), place.get("lon"))
        if dist > self.MAX_ACCEPTABLE_DISTANCE_KM:
            return False, "too_far_from_center"

        return True, "ok"

    def _filter_places_quality(self, places, center_lat, center_lon, require_reviews=True):
        accepted = []
        for p in places:
            ok, reason = self._passes_quality_filters(p, center_lat, center_lon, require_reviews=require_reviews)
            if ok:
                accepted.append(p)
            else:
                print(f"[Quality Filter] Rejected '{p.get('name')}' (type={p.get('type')}, "
                      f"source={p.get('source')}) -> reason: {reason}")
        return accepted

    def _calculate_ranking_score(self, place, center_lat, center_lon, mood_lower=None, max_review_baseline=2000):
        rating = place.get("rating")
        if rating is not None:
            rating_component = (rating / 5.0) * 100
        else:
            rating_component = 45.0

        reviews_count = place.get("reviews_count")
        if reviews_count is not None and reviews_count > 0:
            reviews_component = min(100.0, (reviews_count / max_review_baseline) * 100)
        else:
            reviews_component = 0.0

        importance = place.get("priority_importance")
        if importance is not None:
            popularity_component = (importance / 10.0) * 100
        else:
            base = self.CATEGORY_BASE_POPULARITY.get(place.get("type"), self.CATEGORY_BASE_POPULARITY["default"])
            popularity_component = (base / 10.0) * 100

        dist_km = self._haversine_distance(center_lat, center_lon, place.get("lat"), place.get("lon"))
        distance_component = max(0.0, 100.0 - (dist_km / self.MAX_ACCEPTABLE_DISTANCE_KM) * 100.0)

        mood_affinity_component = self._calculate_mood_affinity(place, mood_lower)

        score = (
            0.30 * rating_component +
            0.25 * reviews_component +
            0.15 * popularity_component +
            0.10 * distance_component +
            0.20 * mood_affinity_component
        )
        return round(score, 2)

    def _estimate_rating_from_importance(self, importance):
        """
        تقدير rating منطقي من priority_importance (1-10) بدل عشوائي بحت.
        الـ importance معلومة حقيقية مكتوبة يدويًا حسب شهرة المكان الفعلية،
        فربطها بـ rating تقديري أصدق بكثير من رقم عشوائي مالوش علاقة
        بجودة المكان. بنضيف jitter صغير (±0.05) فوق الـ mapping الأساسي
        عشان منعملش نفس الرقم بالضبط لكل مكان بنفس importance، لكن
        النطاق العام لسه محكوم بالـ importance الحقيقي - يعني مكان
        importance=10 هيفضل دايمًا أعلى من مكان importance=5 تقريبًا،
        مش بيتقلب عشوائيًا فوق وتحت بلا قاعدة.

        النطاق محصور 4.0-4.9 (وليس لحد 5.0) لأن مفيش مكان "كامل العلامة"
        فعليًا في الواقع، ودي تمييز مقصود عن أي rating حقيقي مستقبلي
        من مصدر موثوق (Google/Foursquare) واللي ممكن يوصل بالفعل لـ 5.0.
        """
        base = 4.0 + (self._safe_float(importance, 5.0) / 10.0) * 0.9
        jittered = base + random.uniform(-0.05, 0.05)
        return round(max(4.0, min(4.9, jittered)), 1)

    def _calculate_mood_affinity(self, place, mood_lower):
        """
        يقيس مدى توافق المكان بالذات (مش بس نوعه) مع الـ mood المطلوب،
        باستخدام tags price_tier وvibe_tags اللي بتوصف "شخصية" المكان.
        ده اللي بيفرّق بين Andrea (راقي/رومانسي) وكشري زيزو (شعبي/عائلي)
        رغم إن الاتنين ممكن يكونوا نفس النوع (cafe/restaurant) بالضبط.

        لو المكان مفيهوش price_tier/vibe_tags أصلاً (مثلاً جاي من
        Geoapify بدون بيانات إضافية)، بيرجع نقطة متوسطة محايدة (50) بدل
        ما يُعاقَب أو يُفضَّل ظلمًا بسبب نقص بيانات وصفية مش متاحة.
        """
        if not mood_lower:
            return 50.0

        mood_profile = self.MOOD_VIBE_PROFILES.get(mood_lower)
        if not mood_profile:
            return 50.0

        score = 50.0  # نقطة بداية محايدة

        place_vibes = set(place.get("vibe_tags") or [])
        wanted_vibes = set(mood_profile.get("vibes", []))
        if place_vibes and wanted_vibes:
            overlap = len(place_vibes & wanted_vibes)
            if overlap > 0:
                score += min(40.0, overlap * 20.0)
            elif place.get("vibe_tags"):
                # المكان له vibe معروف لكنه مش متوافق خالص مع الموود المطلوب
                score -= 15.0

        place_tier = place.get("price_tier")
        wanted_tiers = mood_profile.get("price_tiers")
        if place_tier and wanted_tiers:
            if place_tier in wanted_tiers:
                score += 10.0
            else:
                score -= 10.0

        return max(0.0, min(100.0, score))

    # 🎭 ملف تعريف كل mood: أي vibe tags وأي price tiers تتوافق معاه.
    # ده اللي بيخلي الموود يأثر على *ترتيب* الأماكن جوه نفس الكاتيجوري،
    # مش بس يحدد *أنواع* الأماكن (زي ما كان MOOD_CATEGORY_WEIGHTS بيعمل
    # قبل كده). مكان "luxury+romantic" هيترتب فوق مكان "budget+family"
    # في رحلة mood=romantic حتى لو الاتنين نوعهم cafe.
    MOOD_VIBE_PROFILES = {
        "youth": {"vibes": ["youth", "trendy", "social"], "price_tiers": ["budget", "mid"]},
        "family": {"vibes": ["family", "kids", "relaxed"], "price_tiers": ["budget", "mid"]},
        "romantic": {"vibes": ["romantic", "scenic", "quiet"], "price_tiers": ["mid", "luxury"]},
        "adventure": {"vibes": ["adventure", "outdoor", "active"], "price_tiers": ["budget", "mid"]},
        "tourism": {"vibes": ["historic", "cultural", "scenic"], "price_tiers": ["budget", "mid", "luxury"]},
        "luxury": {"vibes": ["luxury", "upscale", "romantic"], "price_tiers": ["luxury"]},
    }

    def _rank_places(self, places, center_lat, center_lon, mood_lower=None):
        for p in places:
            p["_ranking_score"] = self._calculate_ranking_score(p, center_lat, center_lon, mood_lower=mood_lower)
        return sorted(places, key=lambda x: x["_ranking_score"], reverse=True)

    def _encode_polyline(self, points):
        last_lat, last_lng = 0, 0
        result = []
        for lat, lng in points:
            lat, lng = int(lat * 1e5), int(lng * 1e5)
            d_lat, d_lng = lat - last_lat, lng - last_lng
            for val in [d_lat, d_lng]:
                val = ~(val << 1) if val < 0 else val << 1
                while val >= 0x20:
                    result.append(chr((0x20 | (val & 0x1f)) + 63))
                    val >>= 5
                result.append(chr(val + 63))
            last_lat, last_lng = lat, lng
        return "".join(result)

    def _fetch_realtime_weather(self, city_name, lat=None, lon=None):
        if self.openweather_key and lat is not None and lon is not None:
            try:
                url = "https://api.openweathermap.org/data/2.5/weather"
                params = {
                    "lat": lat,
                    "lon": lon,
                    "appid": self.openweather_key,
                    "units": "metric",
                    "lang": "ar",
                }
                response = requests.get(url, params=params, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    temp = round(self._safe_float(data.get("main", {}).get("temp"), 25))
                    humidity = int(data.get("main", {}).get("humidity", 50))
                    wind_speed = round(self._safe_float(data.get("wind", {}).get("speed"), 3.5) * 3.6, 1)
                    description = data.get("weather", [{}])[0].get("description", "أجواء معتدلة")
                    weather_score = self._compute_weather_score(temp, humidity, wind_speed)
                    return {
                        "temperature": temp,
                        "description": description,
                        "humidity": humidity,
                        "wind_speed": wind_speed,
                        "weather_score": weather_score,
                        "is_realtime_api": True,
                        "source": "OpenWeatherMap API",
                    }
            except Exception as e:
                print(f"[Weather Warning]: OpenWeather request failed -> {str(e)}")

        return self._estimate_seasonal_weather(city_name)

    def _compute_weather_score(self, temp, humidity, wind_speed):
        score = 100.0
        if temp < 10 or temp > 38:
            score -= 30
        elif temp < 15 or temp > 34:
            score -= 15
        if humidity > 75:
            score -= 10
        if wind_speed > 35:
            score -= 10
        return max(40, round(score))

    def _estimate_seasonal_weather(self, city_name):
        city_display = self.CITY_TRANSLATIONS.get(str(city_name).lower().strip(), city_name)
        month_idx = datetime.now().month - 1
        temps_table = self.CITY_SEASONAL_TEMPS.get(city_display, self.CITY_SEASONAL_TEMPS["القاهرة"])
        base_temp = temps_table[month_idx]
        estimated_temp = base_temp + random.randint(-2, 2)
        weather_score = self._compute_weather_score(estimated_temp, 50, 14)
        return {
            "temperature": estimated_temp,
            "description": "تقدير تقريبي حسب متوسطات الموسم",
            "humidity": 50,
            "wind_speed": 14,
            "weather_score": weather_score,
            "is_realtime_api": False,
            "source": "Seasonal Average Estimate (Fallback)",
        }

    def _fetch_osrm_polyline(self, places_list):
        if len(places_list) < 2:
            return None
        try:
            coords_str = ";".join([f"{p['lon']},{p['lat']}" for p in places_list])
            url = f"http://router.project-osrm.org/route/v1/driving/{coords_str}?overview=full&geometries=polyline"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("routes"):
                    return data["routes"][0]["geometry"], "OSRM API Router"
        except Exception:
            pass
        return None

    def _get_transport_details(self, dist_km):
        if dist_km == 0:
            return "📍 نقطة الانطلاق", 0
        elif dist_km < 0.6:
            return f"🚶 مشي {max(1, int(dist_km * 12))} دقيقة", max(1, int(dist_km * 12))
        else:
            return f"🚕 تاكسي/ميكروباص {max(2, int(dist_km * 4))} دقيقة", max(2, int(dist_km * 4))

    def _generate_explainable_reason(self, place_name, mood_lower, rank, p_type):
        if rank == 1:
            return f"Selected as the primary anchor point because it perfectly satisfies the '{mood_lower}' traveler profile guidelines and initializes the routing topology."

        type_explanations = {
            "tourism": "Selected as a major cultural and historical landmark to enrich the tourism experience while preserving execution sequence efficiency.",
            "cafe": "Chosen to provide a strategic and highly-rated leisure stop, ensuring category diversity and route relaxation.",
            "mall": "Integrated as a modern commercial activity hub to support multi-interest engagement without breaking the routing chain.",
            "restaurant": "Dynamically selected to offer an essential high-quality culinary experience that satisfies both proximity and budget constraints.",
            "park": "Chosen to introduce an open green recreational space, successfully balancing the itinerary's structural composition."
        }
        return type_explanations.get(p_type, "Selected strategically to enforce the category uniqueness constraint while minimizing sequential physical distance.")

    def _get_priority_landmarks(self, city_title, allowed_types=None):
        city_clean = city_title.strip()
        landmarks = self.PRIORITY_LANDMARKS_DB.get(city_clean, [])
        if not landmarks:
            for k, v in self.PRIORITY_LANDMARKS_DB.items():
                if city_clean.lower() in k.lower() or k.lower() in city_clean.lower():
                    landmarks = v
                    break

        results = []
        for item in landmarks:
            if allowed_types and item.get("type") not in allowed_types:
                continue
            # لو فيه rating حقيقي مكتوب يدويًا في الداتا (مستقبلًا، بعد ما
            # تتأكد منه من مصدر موثوق)، بيتاخد هو بالأولوية ويتعلّم كـ
            # "verified_manual". غير ذلك، نقدّر rating من الـ importance
            # (معلومة حقيقية موجودة) بدل ما نسيبه None أو نعمل عشوائي بحت.
            real_rating = item.get("rating")
            if real_rating is not None:
                rating_value = real_rating
                rating_source = "verified_manual"
            else:
                rating_value = self._estimate_rating_from_importance(item.get("importance", 5))
                rating_source = "estimated_from_importance"

            results.append({
                "osm_id": None,
                "osm_type": "node",
                "source": "priority_landmark",
                "name": item["name"],
                "type": item.get("type", "tourism"),
                "lat": self._safe_float(item.get("lat")),
                "lon": self._safe_float(item.get("lon")),
                "image_available": False,
                "image_source": "curated",
                "rating": rating_value,
                "rating_source": rating_source,
                "reviews_count": item.get("reviews_count"),
                "priority_importance": item.get("importance", 8),
                "price_tier": item.get("price_tier"),
                "vibe_tags": item.get("vibe_tags", []),
                "opening_hours_raw": item.get("opening_hours_raw"),
                "opening_hours_source": "curated_manual" if item.get("opening_hours_raw") else None,
            })
        return results

    def _get_places_from_local_db(self, city_title):
        city_clean = city_title.strip()
        db_places = REAL_PLACES_DB.get(city_clean, [])
        if not db_places:
            for k, v in REAL_PLACES_DB.items():
                if city_clean.lower() in k.lower() or k.lower() in city_clean.lower():
                    db_places = v
                    break

        results = []
        if db_places and isinstance(db_places, list):
            for item in db_places:
                if not isinstance(item, dict):
                    continue
                if not item.get("name") or item.get("lat") is None or item.get("lon") is None:
                    continue

                raw_rating = item.get("rating")
                raw_reviews = item.get("reviews_count")
                results.append({
                    "osm_id": item.get("osm_id"),
                    "osm_type": item.get("osm_type", "node"),
                    "source": "local_db",
                    "name": item.get("name"),
                    "type": item.get("type", "default"),
                    "lat": self._safe_float(item.get("lat")),
                    "lon": self._safe_float(item.get("lon")),
                    "image_available": item.get("image_available", False),
                    "image_source": item.get("image_source", "placeholder"),
                    "rating": self._safe_float(raw_rating) if raw_rating is not None else None,
                    "reviews_count": int(raw_reviews) if raw_reviews is not None else None,
                    "price_tier": item.get("price_tier"),
                    "vibe_tags": item.get("vibe_tags", []),
                    "opening_hours_raw": item.get("opening_hours_raw"),
                    "opening_hours_source": "local_db" if item.get("opening_hours_raw") else None,
                })
        return results

    def _fetch_geoapify_places(self, internal_type, center_lat, center_lon, radius_m=6000, limit=15):
        if not self.geoapify_key:
            print("[Geoapify DEBUG] No geoapify_key configured, skipping this source.")
            return []

        categories = self.GEOAPIFY_TYPE_QUERY_MAP.get(internal_type)
        if not categories:
            return []

        try:
            params = {
                "categories": categories,
                "filter": f"circle:{center_lon},{center_lat},{radius_m}",
                "bias": f"proximity:{center_lon},{center_lat}",
                "limit": limit,
                "apiKey": self.geoapify_key,
            }
            print(f"[Geoapify DEBUG] type='{internal_type}' -> requesting categories='{categories}' "
                  f"radius={radius_m}m around ({center_lat},{center_lon})")
            response = requests.get(self.GEOAPIFY_ENDPOINT, params=params, timeout=15)
            print(f"[Geoapify DEBUG] -> HTTP {response.status_code}")

            if response.status_code != 200:
                print(f"[Geoapify DEBUG] non-200 response body (first 300 chars): {response.text[:300]}")
                return []

            data = response.json()
            features = data.get("features", [])
            print(f"[Geoapify DEBUG] -> {len(features)} raw features returned")

            results = []
            skipped_no_name = 0
            for feat in features:
                props = feat.get("properties", {})
                name = props.get("name")
                if not name:
                    skipped_no_name += 1
                    continue
                coords = feat.get("geometry", {}).get("coordinates", [None, None])
                lon, lat = coords[0], coords[1]
                if lat is None or lon is None:
                    continue

                rating = self._estimate_geoapify_quality_score(props)
                parsed_hours = self._parse_geoapify_opening_hours(
                    props.get("opening_hours") or props.get("datasource", {}).get("raw", {}).get("opening_hours")
                )

                results.append({
                    "osm_id": props.get("place_id"),
                    "osm_type": "node",
                    "source": "geoapify",
                    "name": name,
                    "type": internal_type,
                    "category_raw": props.get("categories", []),
                    "lat": self._safe_float(lat),
                    "lon": self._safe_float(lon),
                    "image_available": False,
                    "image_source": "geoapify",
                    "rating": rating,
                    "rating_source": "estimated_from_metadata_richness",
                    "reviews_count": None,
                    "opening_hours_raw": parsed_hours,
                    "opening_hours_source": "osm" if parsed_hours else None,
                    "price_tier": None,
                    "vibe_tags": [],
                })

            print(f"[Geoapify DEBUG] -> {len(results)} usable named places "
                  f"({skipped_no_name} skipped for missing name)")
            return results
        except requests.exceptions.Timeout:
            print("[Geoapify WARNING] request TIMEOUT after 15s")
            return []
        except Exception as e:
            print(f"[Geoapify WARNING] UNEXPECTED ERROR ({type(e).__name__}): {str(e)[:200]}")
            return []

    def _parse_geoapify_opening_hours(self, raw_value):
        if not raw_value or not isinstance(raw_value, str):
            return None

        value = raw_value.strip()
        if value in ("24/7", "24 hours", "Open 24 hours"):
            return {"open": "00:00", "close": "00:00"}

        import re
        match = re.search(r'(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})', value)
        if not match:
            return None

        open_time, close_time = match.group(1), match.group(2)
        if "," in value or ";" in value:
            return None

        return {"open": open_time, "close": close_time}

    def _estimate_geoapify_quality_score(self, props):
        score = 4.0
        if props.get("wiki_and_media"):
            score += 0.4
        if props.get("website") or props.get("contact", {}).get("website"):
            score += 0.2
        if props.get("address_line2"):
            score += 0.1
        return round(min(score, 4.8), 1)

    def _generate_dynamic_fallback_places(self, city_title, mood_lower, center_lat, center_lon):
        city_clean = city_title.strip()
        category_weights = self.MOOD_CATEGORY_WEIGHTS.get(
            mood_lower, [("tourism", 0.4), ("restaurant", 0.3), ("cafe", 0.3)]
        )
        allowed_types = [cat for cat, _ in category_weights]

        target_total = 16
        per_type_targets = {
            cat: max(3, round(weight * target_total)) for cat, weight in category_weights
        }

        combined = []
        existing_names = set()

        priority_types_for_query = list(set(allowed_types) | {"tourism"})
        priority_raw = self._get_priority_landmarks(city_clean, allowed_types=priority_types_for_query)
        priority_valid = self._filter_places_quality(priority_raw, center_lat, center_lon, require_reviews=False)

        for p in priority_valid:
            if p["name"] not in existing_names:
                combined.append(p)
                existing_names.add(p["name"])
        if priority_valid:
            print(f"[Places INFO] Loaded {len(priority_valid)} curated priority landmarks for '{city_clean}'")

        local_results = self._get_places_from_local_db(city_clean)
        local_filtered_raw = [p for p in local_results if p["type"] in allowed_types] or local_results
        local_filtered = self._filter_places_quality(local_filtered_raw, center_lat, center_lon)
        for p in local_filtered:
            if p["name"] not in existing_names:
                combined.append(p)
                existing_names.add(p["name"])

        if not self.geoapify_key:
            print("[Places WARNING] No GEOAPIFY_API_KEY configured — cannot fetch real places online. "
                  "Set GEOAPIFY_API_KEY in your .env file (free tier at geoapify.com).")

        for cat, target_count in per_type_targets.items():
            already_have = sum(1 for p in combined if p["type"] == cat)
            if already_have >= target_count:
                continue

            geoapify_raw = self._fetch_geoapify_places(cat, center_lat, center_lon, limit=15)
            geoapify_valid = self._filter_places_quality(geoapify_raw, center_lat, center_lon)

            if len(geoapify_valid) < target_count:
                print(f"[Places INFO] Geoapify gave only {len(geoapify_valid)}/{target_count} "
                      f"valid '{cat}' places after quality filtering.")

            added = 0
            for p in geoapify_valid:
                if p["name"] not in existing_names and added < (target_count - already_have):
                    combined.append(p)
                    existing_names.add(p["name"])
                    added += 1

        if len(combined) >= 3:
            ranked = self._rank_places(combined, center_lat, center_lon, mood_lower=mood_lower)
            sources_used = sorted({p["source"] for p in ranked})
            types_used = sorted({p["type"] for p in ranked})
            print(f"[Places INFO] Final places combined from sources: {sources_used}, "
                  f"types: {types_used} -> {len(ranked)} valid places, ranked by quality score")
            for p in ranked[:6]:
                print(f"  -> [{p['_ranking_score']:.1f}] {p['name']} (type={p['type']}, source={p['source']})")
            return ranked

        print("[Places Warning]: All real data sources failed or returned no places passing "
              "quality filters (priority landmarks + local DB + Geoapify). "
              "Using estimated placeholder places — verify connectivity and GEOAPIFY_API_KEY.")
        results = []
        types_needed = allowed_types[:5] if allowed_types else ["tourism", "cafe", "mall", "restaurant", "park"]
        for idx, t in enumerate(types_needed):
            offset_lat = (idx + 1) * 0.0035 * (-1 if idx % 2 == 0 else 1)
            offset_lon = (idx + 1) * 0.0045 * (1 if idx % 2 == 0 else -1)
            results.append({
                "osm_id": None,
                "osm_type": "node",
                "source": "placeholder_estimate",
                "name": f"{self.ARABIC_TYPE_LABELS.get(t, 'مكان')} (تقديري - لم يتم تأكيده) - {city_title}",
                "type": t,
                "lat": round(center_lat + offset_lat, 4),
                "lon": round(center_lon + offset_lon, 4),
                "image_available": False,
                "image_source": "placeholder_fallback",
                "rating": None,
                "reviews_count": 0,
                "opening_hours_source": "estimated",
                "price_tier": None,
                "vibe_tags": [],
            })
        return results

    def _generate_interactive_html_map(self, center_lat, center_lon, places):
        if not folium:
            return
        try:
            m = folium.Map(location=[center_lat, center_lon], zoom_start=14, control_scale=True)
            points = []
            for idx, p in enumerate(places):
                points.append([p["lat"], p["lon"]])
                popup_html = f"""
                <div style='font-family: Arial, sans-serif; width: 180px; direction: ltr;'>
                    <h4 style='margin:0 0 5px 0; color:#2c3e50;'>#{p['visit_order']} {p['name'].split(' (')[0]}</h4>
                    <b style='color:#f39c12;'>⭐ {p['rating']}</b> ({p['reviews_count']} reviews)<br>
                    <b>💰 Cost:</b> {p['estimated_cost_egp']} EGP<br>
                    <b>⏰ Arrival:</b> {p['arrival_time']}<br>
                    <span style='font-size:11px; color:#7f8c8d;'>Type: {p['type']}</span>
                </div>
                """
                folium.Marker(
                    location=[p["lat"], p["lon"]],
                    popup=folium.Popup(popup_html, max_width=200),
                    tooltip=f"Stop {p['visit_order']}: {p['name']}",
                    icon=folium.Icon(color="blue" if idx > 0 else "green", icon="info-sign")
                ).add_to(m)

            if len(points) > 1:
                folium.PolyLine(locations=points, color="crimson", weight=4, opacity=0.8, tooltip="Optimized AI Route").add_to(m)
            m.save("trip_map.html")
        except Exception as e:
            print(f"[Map Generation Warning]: {str(e)}")

    def _generate_graphic_poster(self, city, mood_en, weather_temp, cost, dist, duration, score, confidence, places):
        if not Html2Image:
            print("[Poster Warning]: html2image library not installed. run 'pip install html2image'")
            return
        try:
            hti = Html2Image(output_path='.')
            stations_html = ""
            for p in places:
                is_first = "first-station" if p['visit_order'] == 1 else ""
                clean_name = p['name'].split(' (')[0]
                stations_html += f"""
                <div class="station-card {is_first}">
                    <div class="station-timeline"><div class="station-bullet"></div></div>
                    <div class="station-info">
                        <div class="station-time">{p['arrival_time']}</div>
                        <div class="station-name">{clean_name}</div>
                        <div class="station-meta">⭐ {p['rating']} • {p['type'].upper()}</div>
                    </div>
                </div>
                """

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap');
                    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Poppins', sans-serif; }}
                    body {{
                        background: radial-gradient(circle at top, #1e1b4b, #090514);
                        width: 650px; height: 950px; color: #ffffff; overflow: hidden; padding: 40px;
                        display: flex; flex-direction: column; justify-content: space-between;
                    }}
                    .header {{ border-bottom: 2px solid #06b6d4; padding-bottom: 20px; margin-bottom: 25px; }}
                    .brand {{ font-size: 14px; font-weight: 800; color: #06b6d4; text-transform: uppercase; letter-spacing: 3px; margin-bottom: 5px; }}
                    .title {{ font-size: 32px; font-weight: 800; background: linear-gradient(to right, #ffffff, #a5b4fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-transform: uppercase; }}
                    .grid-metrics {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 35px; }}
                    .metric-box {{ background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 15px 10px; text-align: center; backdrop-filter: blur(10px); }}
                    .metric-label {{ font-size: 11px; color: #64748b; font-weight: 600; margin-bottom: 5px; letter-spacing: 1px; }}
                    .metric-value {{ font-size: 16px; font-weight: 600; color: #f8fafc; }}
                    .section-title {{ font-size: 18px; font-weight: 600; color: #06b6d4; margin-bottom: 20px; letter-spacing: 1px; text-transform: uppercase; }}
                    .stations-container {{ position: relative; flex-grow: 1; padding-left: 20px; }}
                    .stations-container::before {{
                        content: ''; position: absolute; left: 29px; top: 15px; bottom: 40px; width: 4px;
                        background: linear-gradient(to bottom, #06b6d4, #d946ef); box-shadow: 0 0 10px rgba(6, 182, 212, 0.4); z-index: 1;
                    }}
                    .station-card {{ display: flex; align-items: flex-start; margin-bottom: 25px; position: relative; z-index: 2; }}
                    .station-timeline {{ width: 22px; margin-right: 25px; display: flex; justify-content: center; padding-top: 5px; }}
                    .station-bullet {{ width: 16px; height: 16px; border-radius: 50%; background: #090514; border: 3px solid #06b6d4; box-shadow: 0 0 8px #06b6d4; }}
                    .first-station .station-bullet {{ border-color: #d946ef; box-shadow: 0 0 12px #d946ef; }}
                    .station-info {{ flex-grow: 1; background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 14px; padding: 15px 20px; display: flex; align-items: center; justify-content: space-between; backdrop-filter: blur(8px); }}
                    .station-time {{ font-size: 16px; font-weight: 600; color: #d946ef; min-width: 60px; }}
                    .station-name {{ font-size: 18px; font-weight: 600; color: #ffffff; flex-grow: 1; padding-left: 15px; }}
                    .station-meta {{ font-size: 13px; color: #eab308; font-weight: 600; background: rgba(234, 179, 8, 0.1); padding: 4px 10px; border-radius: 20px; }}
                    .ai-banner {{ background: linear-gradient(135deg, rgba(6, 182, 212, 0.1), rgba(217, 70, 239, 0.1)); border: 1px solid rgba(6, 182, 212, 0.2); border-radius: 16px; padding: 20px; margin-top: 20px; display: flex; justify-content: space-between; align-items: center; }}
                    .score-title {{ font-size: 18px; font-weight: 600; color: #ffffff; margin-bottom: 4px; }}
                    .score-sub {{ font-size: 12px; color: #94a3b8; }}
                    .score-badge {{ font-size: 24px; font-weight: 800; color: #06b6d4; background: rgba(6, 182, 212, 0.15); padding: 10px 20px; border-radius: 12px; border: 1px solid rgba(6, 182, 212, 0.3); }}
                    .footer {{ margin-top: 25px; display: flex; justify-content: space-between; font-size: 11px; color: #475569; border-top: 1px solid rgba(255, 255, 255, 0.05); padding-top: 15px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <div class="brand">Smart Travel AI Engine</div>
                    <div class="title">Explore {city}</div>
                </div>
                <div class="grid-metrics">
                    <div class="metric-box"><div class="metric-label">WEATHER</div><div class="metric-value">⚡ {weather_temp}°C</div></div>
                    <div class="metric-box"><div class="metric-label">BUDGET</div><div class="metric-value">💰 {cost} EGP</div></div>
                    <div class="metric-box"><div class="metric-label">DISTANCE</div><div class="metric-value">📍 {dist} KM</div></div>
                    <div class="metric-box"><div class="metric-label">DURATION</div><div class="metric-value">⏱️ {duration.split(' ')[0]} H</div></div>
                </div>
                <div class="section-title">🗺️ Arrival Stations & Route Track</div>
                <div class="stations-container">{stations_html}</div>
                <div class="ai-banner">
                    <div>
                        <div class="score-title">AI Recommendation Confidence</div>
                        <div class="score-sub">Greedy Traveling Salesperson (TSP) Performance: {confidence}%</div>
                    </div>
                    <div class="score-badge">{score} / 100</div>
                </div>
                <div class="footer">
                    <div>Status: Production Verified • {mood_en.upper()} MODE</div>
                    <div>© Powered by Core AI Platform</div>
                </div>
            </body>
            </html>
            """
            hti.screenshot(html_str=html_content, save_as='trip_poster.png', size=(650, 950))
            print("[Poster Generation]: Ultra Premium HTML-Rendered Poster Saved Successfully!")
        except Exception as e:
            print(f"[Poster Generation Warning]: {str(e)}")

    def create_trip(self, city=None, budget=None, mood=None, lat=None, lon=None, user_history=None, **kwargs):
        try:
            if not city:
                city = "القاهرة"
            city_low = city.lower().strip()
            city_display = self.CITY_TRANSLATIONS.get(city_low, city.title() if city.isalpha() else city)
            mood_lower = str(mood).lower().strip() if mood else "youth"
            mood_ar = self.MOOD_TRANSLATIONS.get(mood_lower, mood_lower)

            user_budget = self._safe_float(budget, default=1000.0)

            if lat and lon:
                center_lat, center_lon = self._safe_float(lat), self._safe_float(lon)
            else:
                center_lat, center_lon = self.CITY_COORDINATES_REGISTRY.get(city_display, (30.0444, 31.2357))

            all_places = self._generate_dynamic_fallback_places(city_display, mood_lower, center_lat, center_lon)
            total_considered = len(all_places)

            optimized_places = []
            unvisited = list(all_places)
            curr_lat, curr_lon = center_lat, center_lon
            used_categories = set()

            TOURISM_REPEAT_CAP = 3
            tourism_count_in_trip = 0

            TOTAL_TRIP_STOPS = 7

            tourism_ratio = (
                sum(1 for p in all_places if p["type"] == "tourism") / len(all_places)
                if all_places else 0
            )
            trip_start_str = "09:00" if tourism_ratio > 0.5 else "10:00"
            TRIP_START_MINUTES = self._parse_time_str(trip_start_str)
            TRIP_DAY_END_MINUTES = self._parse_time_str("22:00")

            simulated_clock = TRIP_START_MINUTES

            for step in range(1, TOTAL_TRIP_STOPS + 1):
                if not unvisited:
                    break
                if simulated_clock >= TRIP_DAY_END_MINUTES:
                    print(f"[TSP INFO] Step {step}: reached realistic day-end cutoff "
                          f"(22:00) at simulated time {simulated_clock // 60:02d}:"
                          f"{simulated_clock % 60:02d} -> stopping trip here with "
                          f"{len(optimized_places)} stops")
                    break
                candidates = [
                    x for x in unvisited
                    if x["type"] not in used_categories
                    or (x["type"] == "tourism" and tourism_count_in_trip < TOURISM_REPEAT_CAP)
                ]
                if not candidates:
                    print(f"[TSP INFO] Step {step}: no diverse-type candidates left "
                          f"(tourism cap={TOURISM_REPEAT_CAP} reached or no alternatives) "
                          f"-> falling back to all unvisited real places")
                    candidates = unvisited

                if step == 1:
                    non_cafes = [x for x in candidates if x["type"] != "cafe"]
                    if non_cafes:
                        candidates = non_cafes

                open_candidates = []
                for p in candidates:
                    p_visit_duration = self._get_visit_duration_minutes(p["type"])
                    is_open, hours_info = self._is_open_at(p, simulated_clock, p_visit_duration)
                    if is_open:
                        open_candidates.append(p)

                if not open_candidates:
                    any_open_in_unvisited = []
                    for p in unvisited:
                        p_visit_duration = self._get_visit_duration_minutes(p["type"])
                        is_open, _ = self._is_open_at(p, simulated_clock, p_visit_duration)
                        if is_open:
                            any_open_in_unvisited.append(p)
                    if any_open_in_unvisited:
                        print(f"[Opening Hours] Step {step}: preferred-type candidates all closed, "
                              f"but found {len(any_open_in_unvisited)} open alternative(s) elsewhere "
                              f"-> using those instead of a closed preferred-type place")
                        open_candidates = any_open_in_unvisited

                if open_candidates:
                    if len(open_candidates) < len(candidates):
                        closed_names = [p["name"] for p in candidates if p not in open_candidates]
                        print(f"[Opening Hours] Step {step}: excluded {len(closed_names)} "
                              f"place(s) closed at this time -> {closed_names}")
                    candidates = open_candidates
                else:
                    if optimized_places:
                        print(f"[TSP INFO] Step {step}: no open candidates remain anywhere "
                              f"(estimated hours) at {simulated_clock // 60:02d}:"
                              f"{simulated_clock % 60:02d} -> stopping trip with "
                              f"{len(optimized_places)} stops instead of adding a closed place")
                        break
                    else:
                        print(f"[Opening Hours] Step {step}: all candidates appear closed at "
                              f"{simulated_clock // 60:02d}:{simulated_clock % 60:02d} (estimated hours), "
                              f"but trip is empty so far -> proceeding without this filter to avoid an empty trip")

                max_candidate_dist = max(
                    (self._haversine_distance(curr_lat, curr_lon, p["lat"], p["lon"]) for p in candidates),
                    default=1.0
                ) or 1.0

                def _combined_cost(p):
                    quality_score = p.get("_ranking_score", 50.0)
                    step_dist = self._haversine_distance(curr_lat, curr_lon, p["lat"], p["lon"])
                    proximity_score = 100.0 - (step_dist / max_candidate_dist) * 100.0

                    hours = self._get_opening_hours_for_place(p)
                    close_min = self._parse_time_str(hours["close"]) or (24 * 60)
                    if close_min <= self._parse_time_str(hours["open"] or "00:00"):
                        close_min += 24 * 60
                    minutes_until_close = max(0, close_min - simulated_clock)
                    urgency_score = max(0.0, 100.0 - (minutes_until_close / (8 * 60)) * 100.0)

                    combined = (0.60 * quality_score) + (0.25 * proximity_score) + (0.15 * urgency_score)
                    return -combined

                best_place = min(candidates, key=_combined_cost)

                travel_dist = self._haversine_distance(curr_lat, curr_lon, best_place["lat"], best_place["lon"])
                _, travel_minutes_est = self._get_transport_details(travel_dist)
                projected_arrival = simulated_clock + travel_minutes_est
                projected_departure = projected_arrival + self._get_visit_duration_minutes(best_place["type"])

                best_hours = self._get_opening_hours_for_place(best_place)
                best_close_min = self._parse_time_str(best_hours["close"]) or (24 * 60)
                if best_close_min <= (self._parse_time_str(best_hours["open"]) or 0):
                    best_close_min += 24 * 60

                if projected_departure > best_close_min:
                    remaining_candidates = [c for c in candidates if c is not best_place]
                    if remaining_candidates:
                        print(f"[Opening Hours] Step {step}: best candidate '{best_place['name']}' "
                              f"would close before visit ends ({projected_departure // 60:02d}:"
                              f"{projected_departure % 60:02d} > {best_hours['close']}) -> "
                              f"trying next-best candidate instead")
                        best_place = min(remaining_candidates, key=_combined_cost)
                        travel_dist = self._haversine_distance(curr_lat, curr_lon, best_place["lat"], best_place["lon"])
                        _, travel_minutes_est = self._get_transport_details(travel_dist)
                        projected_arrival = simulated_clock + travel_minutes_est
                        projected_departure = projected_arrival + self._get_visit_duration_minutes(best_place["type"])
                    elif optimized_places:
                        print(f"[TSP INFO] Step {step}: only remaining candidate "
                              f"'{best_place['name']}' would close before visit ends "
                              f"({projected_departure // 60:02d}:{projected_departure % 60:02d} > "
                              f"{best_hours['close']}) and no alternative exists -> "
                              f"stopping trip with {len(optimized_places)} stops")
                        break

                if projected_departure > TRIP_DAY_END_MINUTES and optimized_places:
                    print(f"[TSP INFO] Step {step}: adding '{best_place['name']}' would end "
                          f"at {projected_departure // 60:02d}:{projected_departure % 60:02d}, "
                          f"past the realistic day-end cutoff (22:00) -> stopping trip with "
                          f"{len(optimized_places)} stops")
                    break

                optimized_places.append(best_place)
                used_categories.add(best_place["type"])
                if best_place["type"] == "tourism":
                    tourism_count_in_trip += 1

                simulated_clock = projected_departure

                curr_lat, curr_lon = best_place["lat"], best_place["lon"]
                unvisited.remove(best_place)

            loop_guard = 0
            while loop_guard < 10:
                total_current_est = 0
                for p in optimized_places:
                    c_range = self.CATEGORY_COST_RANGES.get(p["type"], self.CATEGORY_COST_RANGES["default"])
                    total_current_est += c_range[0] if user_budget < 400 else random.randint(c_range[0], c_range[1])

                if total_current_est <= user_budget or len(optimized_places) <= 1:
                    break
                optimized_places.pop()
                loop_guard += 1

            weather_data = self._fetch_realtime_weather(city, center_lat, center_lon)
            final_places_cards = []
            total_distance = 0.0
            total_transit_minutes = 0
            current_timeline = datetime.strptime(trip_start_str, "%H:%M")
            accumulated_final_cost = 0

            for i, p in enumerate(optimized_places):
                p_type = p["type"]
                dist_from_prev = self._haversine_distance(
                    center_lat if i == 0 else optimized_places[i - 1]["lat"],
                    center_lon if i == 0 else optimized_places[i - 1]["lon"],
                    p["lat"], p["lon"]
                )
                total_distance += dist_from_prev

                transport_label, transit_mins = self._get_transport_details(dist_from_prev)
                total_transit_minutes += transit_mins
                if i > 0:
                    current_timeline += timedelta(minutes=transit_mins)

                arrival_time_str = current_timeline.strftime("%H:%M")
                arrival_minutes_of_day = current_timeline.hour * 60 + current_timeline.minute
                visit_duration_mins = self._get_visit_duration_minutes(p_type)
                current_timeline += timedelta(minutes=visit_duration_mins)
                departure_time_str = current_timeline.strftime("%H:%M")

                place_is_open, hours_info = self._is_open_at(p, arrival_minutes_of_day, visit_duration_mins)
                if not place_is_open:
                    print(f"[Opening Hours WARNING] Final check: '{p['name']}' arrival at "
                          f"{arrival_time_str} may fall outside estimated hours "
                          f"({hours_info['open']}-{hours_info['close']})")

                cost_range = self.CATEGORY_COST_RANGES.get(p_type, self.CATEGORY_COST_RANGES["default"])
                p_cost = cost_range[0] if user_budget < 400 else random.randint(cost_range[0], cost_range[1])
                accumulated_final_cost += p_cost

                distance_score = max(5.0, round(30.0 - (dist_from_prev * 3), 1))
                rating_value = p.get("rating") if p.get("rating") is not None else 4.2
                rating_score = round((rating_value / 5.0) * 25, 1)
                dynamic_score = round(distance_score + rating_score + (float(weather_data["weather_score"]) * 0.2) + 20.0, 1)

                osm_id = p["osm_id"]
                osm_type = p["osm_type"]
                embed_map_url = f"https://www.openstreetmap.org/export/embed.html?bbox={p['lon']-0.01}%2C{p['lat']-0.01}%2C{p['lon']+0.01}%2C{p['lat']+0.01}&layer=mapnik&marker={p['lat']}%2C{p['lon']}"
                google_maps_url = f"https://www.google.com/maps/search/?api=1&query={p['lat']},{p['lon']}"
                maps_url = f"https://www.openstreetmap.org/{osm_type}/{osm_id}" if osm_id else google_maps_url

                opening_hours_source = p.get("opening_hours_source") or ("osm" if not hours_info["is_estimated"] else "estimated")

                final_places_cards.append({
                    "visit_order": i + 1,
                    "osm_id": osm_id,
                    "osm_type": osm_type,
                    "source": p.get("source", "unknown"),
                    "name": p["name"],
                    "type": p_type,
                    "image_available": p["image_available"],
                    "image_source": p["image_source"],
                    "maps_url": maps_url,
                    "google_maps_url": google_maps_url,
                    "embed_map_url": embed_map_url,
                    "lat": p["lat"],
                    "lon": p["lon"],
                    "rating": p.get("rating"),
                    "rating_source": p.get("rating_source", "unavailable"),
                    "reviews_count": p.get("reviews_count"),
                    "price_tier": p.get("price_tier"),
                    "vibe_tags": p.get("vibe_tags", []),
                    "distance_from_previous_km": dist_from_prev,
                    "travel_time": f"{transit_mins} min",
                    "transport_mode": transport_label,
                    "arrival_time": arrival_time_str,
                    "departure_time": departure_time_str,
                    "opening_hours": f"{hours_info['open']} - {hours_info['close']}",
                    "opening_hours_is_estimated": hours_info["is_estimated"],
                    "opening_hours_source": opening_hours_source,
                    "likely_open_at_arrival": place_is_open,
                    "estimated_cost_egp": p_cost,
                    "dynamic_score": dynamic_score,
                    "quality_ranking_score": p.get("_ranking_score"),
                    "is_priority_landmark": p.get("source") == "priority_landmark",
                    "why_selected_here": self._generate_explainable_reason(p["name"], mood_lower, i + 1, p_type)
                })

            route_coords = [(p["lat"], p["lon"]) for p in optimized_places]
            osrm_res = self._fetch_osrm_polyline(optimized_places)
            route_geometry, route_source = osrm_res if osrm_res else (self._encode_polyline(route_coords), "Local Encoded Polyline Generator (Fallback)")

            score_breakdown = {
                "distance_efficiency": max(60, int(100 - (total_distance * 2))),
                "budget_efficiency": 100 if accumulated_final_cost <= user_budget else 50,
                "preference_match": 95,
                "weather_suitability": int(weather_data.get("weather_score", 90))
            }

            overall_route_score = round(
                (0.30 * score_breakdown["distance_efficiency"]) +
                (0.25 * score_breakdown["budget_efficiency"]) +
                (0.25 * score_breakdown["preference_match"]) +
                (0.20 * score_breakdown["weather_suitability"]), 1
            )

            confidence_breakdown = {
                "data_completeness": 98 if all(x["osm_id"] for x in final_places_cards) else 85,
                "source_reliability": 100,
                "constraint_satisfaction": 100 if accumulated_final_cost <= user_budget else 60
            }
            confidence_score = round(
                (0.40 * overall_route_score) +
                (0.30 * confidence_breakdown["source_reliability"]) +
                (0.30 * confidence_breakdown["data_completeness"]), 1
            )

            total_stay_mins = sum(self._get_visit_duration_minutes(p["type"]) for p in optimized_places)
            grand_total_mins = total_stay_mins + total_transit_minutes
            duration_str = f"{grand_total_mins // 60} hours {grand_total_mins % 60} minutes"

            self._generate_interactive_html_map(center_lat, center_lon, final_places_cards)
            self._generate_graphic_poster(
                city=city_display, mood_en=mood_lower, weather_temp=weather_data["temperature"],
                cost=accumulated_final_cost, dist=round(total_distance, 2), duration=duration_str,
                score=overall_route_score, confidence=confidence_score, places=final_places_cards
            )

            return {
                "trip_name": f"خطتك لرحلة {mood_ar} في {city_display}",
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "ai_engine_architecture": {
                    "recommendation_type": "Hybrid AI Layer",
                    "optimization_engine": "Constrained Greedy Traveling Salesperson (TSP)",
                    "personalization_strategy": "Cold Start Profile Matching",
                    "weather_aware": True,
                    "budget_aware": True
                },
                "system_constraints": {
                    "max_category_repeat": 1,
                    "budget_limit_enforced": True,
                    "weather_filter_enabled": True,
                    "minimum_rating_threshold": 4.0
                },
                "budget_constraint_satisfied": accumulated_final_cost <= user_budget,
                "overall_route_score": overall_route_score,
                "overall_route_score_breakdown": score_breakdown,
                "recommendation_confidence": confidence_score,
                "confidence_formula": "(0.40 * Route_Score) + (0.30 * Source_Reliability) + (0.30 * Data_Completeness)",
                "confidence_breakdown": confidence_breakdown,
                "total_distance_km": round(total_distance, 2),
                "total_duration": duration_str,
                "estimated_total_cost_egp": accumulated_final_cost,
                "user_input_budget_egp": user_budget,
                "weather": weather_data,
                "route_polyline_source": route_source,
                "route_polyline": route_geometry,
                "places": final_places_cards,
                "optimization_summary": {
                    "algorithm": "Constrained Greedy Traveling Salesperson (TSP) Engine",
                    "budget_policy": "Dynamic Trim & Exchange Loop Execution",
                    "diversity_policy": "Strict Uniqueness (MAX_CATEGORY_REPEAT = 1)",
                    "places_considered": total_considered,
                    "places_selected": len(final_places_cards),
                    "places_data_sources": list({p.get("source", "unknown") for p in final_places_cards})
                }
            }
        except Exception as e:
            traceback.print_exc()
            return {"error": f"An unexpected error occurred: {str(e)}"}
