import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from .utils import validate_point, get_nearest, Item, RecommendItem


class Recommender(ABC):

    """
    Абстрактный класс рекомендера с единой для всех вертикалей логикой.

    В наследнике требуется переопределить некоторые абстрактные функции,
    играющие ключевую роль в рекомендациях.
    """

    @abstractmethod
    def get_candidates(self):
        """
        Возвращает список кандидатов.

        Кандидаты - все возможные айтемы,
        которые могут быть порекомендованы.
        """
        pass

    @abstractmethod
    def get_recommended_items(self, USER_DICT, items, coords, limit):
        """
        Лёгкий рекомендер.

        Возвращает список из limit рекомендательных карточек,
        которые затем будут обработаны в stream_blender.
        """
        pass

    def before_recommend(self, USER_DICT):
        """
        Подготовка к вызову рекомендера.

        Метод для подготовки данных перед вызовом рекомендера
        для его корректной работы.
        """
        if 'recommend_history' not in USER_DICT:
            USER_DICT['recommend_history'] = set()

    def stream_blender(self, USER_DICT, recommended_items,
                       blender_limit=5, temperature=5):
        """
        Возвращает финальную пачку рекомендаций с вертикали.

        Получает карточки recommended_items, перемешивает их
        согласно определённым правилам и возвращает финальные
        N карточек рекомендаций
        """
        if blender_limit > len(recommended_items):
            blender_limit = len(recommended_items)

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

        stream_items = sorted(stream_items, key=lambda item: item.dist)
        return stream_items

    def recommend(self, USER_DICT, recommend_limit=20, blender_limit=5):
        """
        Основная функция рекомендера.

        Рекомендер возвращает список из limit карточек рекомендаций,
        которые затем будут обработаны в большом блендере
        """
        self.before_recommend(USER_DICT)

        candidates = self.get_candidates()
        lon, lat = USER_DICT['lon'], USER_DICT['lat']
        recommended_items = self.get_recommended_items(USER_DICT,
                                                       candidates,
                                                       (lon, lat),
                                                       recommend_limit)

        for recommended_item in recommended_items:
            item_hash = recommended_item.get_hash()
            USER_DICT['recommend_history'].add(item_hash)

        stream_items = self.stream_blender(USER_DICT,
                                           recommended_items,
                                           blender_limit)
        return stream_items


class FoodRecommender(Recommender):
    """Рекомендер ресторанов."""

    def get_candidates(self):
        """Возвращает список всех ресторанов."""
        df_food = pd.read_csv('PlacesDatabase/food_places.csv')
        candidates = []
        for row in df_food.itertuples():
            lon, lat = row.Longitude_WGS84_en, row.Latitude_WGS84_en
            if validate_point((lon, lat)):
                item = Item(
                     row.Name_en,
                     row.Address_en,
                     lon,
                     lat)
                candidates.append(item)
        return candidates

    def get_recommended_items(self, USER_DICT, places, coords, limit):
        """Возвращает limit ближайших ресторанов."""
        items_with_dist = get_nearest(USER_DICT, places, coords, limit)
        recommended_items = []

        for (item, dist) in items_with_dist:
            recommended_item = RecommendItem(
                item.name,
                item.address,
                item.lon,
                item.lat,
                dist
            )
            recommended_items.append(recommended_item)

        return recommended_items
