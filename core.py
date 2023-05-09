import requests
from math import radians, cos, sin, asin, sqrt

def get_address_from_coords(coords):
    lon, lat = coords[0], coords[1]
    PARAMS = {
        "apikey": "4e6e6cda-7f5c-417b-a6d0-90a5b6445055",
        "format": "json",
        "lang": "ru_RU",
        "kind": "house",
        "geocode": "%s, %s" % (lon, lat),
    }

    try:
        r = requests.get(url="https://geocode-maps.yandex.ru/1.x/",
                         params=PARAMS)
        json_data = r.json()
        mess = json_data["response"]["GeoObjectCollection"][
            "featureMember"][0]["GeoObject"]["metaDataProperty"][
            "GeocoderMetaData"
        ]["AddressDetails"]["Country"]["AddressLine"]
        return True, mess
    except Exception:
        mess = """Не могу определить адрес по этой локации/координатам"""
        return False, mess
    
def validate_point(p):
    lat, lon = p
    return (-90 <= lat <= 90) and (-180 <= lon <= 180)

def distance_haversine(p1, p2):
    lat1, lon1 = p1
    lat2, lon2 = p2
    if not validate_point(p1) or not validate_point(p2):
        return None

    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    d = R * c
    return d