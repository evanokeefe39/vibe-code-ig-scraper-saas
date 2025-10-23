from geopy.geocoders import Nominatim

def geocode_location(address):
    geolocator = Nominatim(user_agent="vibe-scraper")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    return None, None