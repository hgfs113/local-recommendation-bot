import requests
import numpy as np
from scipy.spatial import distance_matrix
from math import radians, cos, sin, asin, sqrt


class Item:
    """
    Контейнер кандидата для рекомендации.

    Это может быть ресторан, парк или театр.
    Содержит название, адрес и координаты средний
    накопленный рейтинг.
    Умеет считать хэш.
    """

    def __init__(self, name, address, lon, lat):
        self.name = name
        self.address = address
        self.lon = lon
        self.lat = lat

        self.avg_rating = None
        self.counts = 0

    def get_hash(self):
        return hash(self.name + self.address)

    def get_coords(self):
        return (self.lon, self.lat)

    def get_rating(self):
        if self.counts > 5:
            return self.avg_rating
        return None

    def add_rating(self, rating):
        self.avg_rating = (
                self.counts * self.avg_rating + rating
            ) / (self.counts + 1)
        self.counts += 1

    def __repr__(self):
        return f'{self.name}, {self.address}. Coords: ({self.lon}, {self.lat})'


class RecommendItem(Item):
    """
    Элемент рекомендации.

    Наследуется от Item, содержит user-item информацию,
    такую как расстояние и пр.
    """

    def __init__(self, name, address, lon, lat, dist):
        self.dist = dist
        super().__init__(name, address, lon, lat)


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


def stream_blender_diego(USER_DICT, recommended_items,
                         blender_limit, temperature):
    user_coords = np.array([[USER_DICT['lon'], USER_DICT['lat']]])
    item_coords = []
    for item in recommended_items:
        item_coords.append([item.lon, item.lat])
    item_coords = np.array(item_coords)

    idx_set = set()
    free_idx_set = set(range(item_coords.shape[0]))

    d0 = distance_matrix(user_coords, item_coords)
    d0_copy = d0.copy()
    for _ in range(temperature):
        nearest_idx = d0_copy.argmin()
        d0_copy[:, nearest_idx] = -1
    nearest_idx = d0_copy.argmin()
    idx_set.add(nearest_idx)

    while len(idx_set) < blender_limit:
        idx = np.array(list(idx_set))
        free_idx = np.array(list(free_idx_set))
        d = distance_matrix(item_coords[idx], item_coords[free_idx])
        d_copy = d.copy()
        for _ in range(temperature):
            i, j = np.unravel_index(d_copy.argmax(), d_copy.shape)
            d_copy[i, j] = -1
        i, j = np.unravel_index(d_copy.argmax(), d_copy.shape)
        d[i, j] = -1
        idx_set.add(i)
        idx_set.add(j)
        if i in free_idx_set:
            free_idx_set.remove(i)
        if j in free_idx_set:
            free_idx_set.remove(j)

    stream_items = []
    for idx in idx_set:
        stream_items.append(recommended_items[idx])

    return stream_items
