import requests
import pandas as pd
from math import radians, cos, sin, asin, sqrt


class Item:
    """
    Элемент рекомендации.

    Это может быть ресторан, парк или театр.
    Содержит название, адрес и координаты.
    Умеет считать хэш.
    """

    def __init__(self, name, address, lon, lat):
        self.name = name
        self.address = address
        self.lon = lon
        self.lat = lat

    def get_hash(self):
        return hash(self.name + self.address)

    def get_coords(self):
        return (self.lon, self.lat)

    def __repr__(self):
        return f'{self.name}, {self.address}. Coords: ({self.lon}, {self.lat})'


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

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    d = R * c
    return d


def get_food_places(path):
    df_food = pd.read_csv(path)
    places = []
    for row in df_food.itertuples():
        lon, lat = row.Longitude_WGS84_en, row.Latitude_WGS84_en
        if validate_point((lon, lat)):
            item = Item(
                row.Name_en, row.Address_en,
                lon, lat
            )
            places.append(item)
    return places


def get_nearest(USER_DICT, places, coords, N):
    recommend_history = USER_DICT['recommend_history']
    place2dist = {}

    lon, lat = coords
    for place in places:
        place_hash = place.get_hash()
        if place_hash in recommend_history:
            continue
        p_lon, p_lat = place.get_coords()
        dist = distance_haversine((lon, lat), (p_lon, p_lat))
        place2dist[place] = dist

    return sorted(place2dist.items(), key=lambda item: item[1])[: N]


def dist_to_str(dist):
    km = int(dist)
    m = int((dist - km) * 1000)
    if km == 0:
        return f'{m} метров'
    elif m == 0:
        return f'{km} км'
    return f'{km} км {m} м'
