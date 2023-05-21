import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
import utils


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

    def stream_blender(self, USER_DICT, recommended_items, blender_limit=5):
        """
        Возвращает финальную пачку рекомендаций с вертикали.

        Получает карточки recommended_items, перемешивает их
        согласно определённым правилам и возвращает финальные
        N карточек рекомендаций
        """
        idxs = np.arange(len(recommended_items))
        random_idxs = np.random.choice(
                idxs,
                size=min(len(recommended_items), blender_limit),
                replace=False
            )

        stream_items = []
        for idx in random_idxs:
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
            if utils.validate_point((lon, lat)):
                item = utils.Item(row.Name_en,
                                  row.Address_en,
                                  lon,
                                  lat)
                candidates.append(item)
        return candidates

    def get_recommended_items(self, USER_DICT, places, coords, limit):
        """Возвращает limit ближайших ресторанов."""
        items_with_dist = utils.get_nearest(USER_DICT, places, coords, limit)
        recommended_items = []

        for (item, dist) in items_with_dist:
            recommended_item = utils.RecommendItem(item.name,
                                                   item.address,
                                                   item.lon,
                                                   item.lat,
                                                   dist)
            recommended_items.append(recommended_item)

        return recommended_items
