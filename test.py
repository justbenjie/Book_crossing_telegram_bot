from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

geolocator = Nominatim(user_agent="staronki_bot", timeout=15)


for i, j in zip(range(-50, 50), range(-50, 50)):
    location = geolocator.reverse((i, j), exactly_one=True)
    try:
        print(location.raw["address"])
    except AttributeError:
        print("none")
