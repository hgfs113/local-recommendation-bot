import numpy as np
from abc import ABC, abstractmethod
from core import utils


class Recommender(ABC):
    @abstractmethod
    def get_candidates(self):
        pass


    @abstractmethod
    def get_recommended_places(self, USER_DICT, places, coords, limit):
        pass


    def before_recommend(self, USER_DICT):
        """
            Метод для подготовки данных перед вызовом рекомендера
            для его корректной работы
        """
        if 'recommend_history' not in USER_DICT:
            USER_DICT['recommend_history'] = set()


    def stream_blender(self, USER_DICT, recommended_items, blender_limit=5):
        """
            Получает карточки recommended_items, перемешивает их
            согласно определённым правилам и возвращает финальные
            N карточек рекомендаций
        """
        idxs = np.arange(len(recommended_items))
        random_idxs = np.random.choice(idxs, size=blender_limit, replace=False)

        stream_items = []
        for idx in random_idxs:
            stream_items.append(recommended_items[idx])

        stream_items = sorted(stream_items, key = lambda item: item[1])
        return stream_items


    def recommend(self, USER_DICT, recommend_limit=20, blender_limit=5):
        """
            Рекомендер возвращает список из limit карточек рекомендаций,
            которые затем будут обработаны в большом блендере
        """
        self.before_recommend(USER_DICT)

        candidates = self.get_candidates()
        lon, lat = USER_DICT['lon'], USER_DICT['lat']
        recommended_items = self.get_recommended_places(USER_DICT,
                                                        candidates,
                                                        (lon, lat),
                                                        recommend_limit)

        for (item, dist) in recommended_items:
            item_hash = item.get_hash()
            USER_DICT['recommend_history'].add(item_hash)

        stream_items = self.stream_blender(USER_DICT, recommended_items, blender_limit)
        return stream_items


class FoodRecommender(Recommender):
    def get_candidates(self):
        return utils.get_food_places('PlacesDatabase/food_places.csv')


    def get_recommended_places(self, USER_DICT, places, coords, limit):
        return utils.get_nearest(USER_DICT, places, coords, limit)