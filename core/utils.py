import requests
import numpy as np
from enum import Enum
from scipy.spatial import distance_matrix
from math import radians, cos, sin, asin, sqrt


class ItemType(Enum):

    """
    Перечисление типов рекомендации.

    Является частью ключа, который определяет элемент рекомендации.
    """

    FOOD = 1
    SHOP = 2


class ItemId:

    """
    Уникальная пара (type, id).

    Однозначно определяет элемент рекомендации
    и является ключом к словарю кандидатов.
    """

    def __init__(self, type, id):
        self.type = type
        self.id = id

    def __hash__(self):
        return self.type * 4243 + self.id * 239017

    def __eq__(self, other):
        return (self.type == other.type) and (self.id == other.id)

    def __repr__(self):
        return str(hash(self))

    def __str__(self):
        return str(hash(self))


class Item:

    """
    Контейнер кандидата для рекомендации.

    Это может быть ресторан, парк или театр.
    Содержит название, адрес и координаты средний
    накопленный рейтинг.
    """

    def __init__(self, item_type, name, address, lon, lat, embedding=None):
        self.type = item_type
        self.name = name
        self.address = address
        self.lon = lon
        self.lat = lat
        self.embedding = embedding

        self.item_id = ItemId(self.type.value, hash(name + address))
        self.avg_rating = None
        self.counts = 0

    def get_coords(self):
        return (self.lon, self.lat)

    def get_rating(self):
        if self.counts > 5:
            return self.avg_rating
        return None

    def add_rating(self, rating):
        if self.avg_rating is None:
            self.avg_rating = 0
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

    def __init__(self, item, dist):
        self.dist = dist
        super().__init__(
            item.type,
            item.name,
            item.address,
            item.lon,
            item.lat,
            item.embedding)


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


def get_nearest(USER_INFO, candidates, coords, N):
    recommend_history = USER_INFO['recommend_history']
    place2dist = {}

    lon, lat = coords
    for item_id in candidates:
        if item_id in recommend_history:
            continue
        item = candidates[item_id]
        p_lon, p_lat = item.get_coords()
        dist = distance_haversine((lon, lat), (p_lon, p_lat))
        place2dist[item] = dist

    return sorted(place2dist.items(), key=lambda item: item[1])[: N]


def dist_to_str(dist):
    km = int(dist)
    m = int((dist - km) * 1000)
    if km == 0:
        return f'{m} метров'
    elif m == 0:
        return f'{km} км'
    return f'{km} км {m} м'


def stream_blender_diego(USER_INFO, recommended_items,
                         blender_limit, temperature,
                         max_iter=10000):
    user_coords = np.array([[USER_INFO['lon'], USER_INFO['lat']]])
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

    d = distance_matrix(item_coords, item_coords)
    cur_iter = 0
    while len(idx_set) < blender_limit:
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
        cur_iter += 1
        if cur_iter > max_iter:
            print('WARNING: stream blender got into an endless loop')
            break

    stream_items = []
    for idx in idx_set:
        stream_items.append(recommended_items[idx])

    return stream_items
