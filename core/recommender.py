import pandas as pd
from abc import ABC, abstractmethod
from .utils import ItemType, Item, RecommendItem
from .utils import validate_point, get_nearest, stream_blender_diego


class Recommender(ABC):

    """
    Абстрактный класс рекомендера с единой для всех вертикалей логикой.

    В наследнике требуется переопределить некоторые абстрактные функции,
    играющие ключевую роль в рекомендациях.
    """

    @abstractmethod
    def get_light_recommender_items(self, USER_INFO, items, coords, limit):
        """
        Лёгкий рекомендер.

        Возвращает список из limit рекомендательных карточек,
        которые затем будут обработаны в stream_blender.
        """
        pass

    def before_recommend(self, USER_INFO):
        """
        Подготовка к вызову рекомендера.

        Метод для подготовки данных перед вызовом рекомендера
        для его корректной работы.
        """
        if 'recommend_history' not in USER_INFO:
            USER_INFO['recommend_history'] = set()

    def stream_blender(self, USER_INFO, recommended_items, blender_limit=5,
                       mode='Diego', temperature=5):
        """
        Возвращает финальную пачку рекомендаций с вертикали.

        Получает карточки лёгкого рекомендера, перемешивает их
        согласно определённым правилам, которые задаются в mode,
        и возвращает финальные blender_limit карточек рекомендаций.

        По умолчанию выбран mode='Diego', который позволяет получать
        разнообразные по местоположению рекомендации. Параметр temperature
        задаёт степень разнообразия (чем больше temperature, тем его меньше)
        """
        if blender_limit > len(recommended_items):
            blender_limit = len(recommended_items)

        if mode == 'Diego':
            stream_items = stream_blender_diego(
                USER_INFO,
                recommended_items,
                blender_limit,
                temperature)
        else:
            print('ERROR: Unknown stream blender mode')
            return []

        stream_items = sorted(stream_items, key=lambda item: item.dist)
        return stream_items

    def recommend(self, USER_INFO, recommend_limit=20, blender_limit=5):
        """
        Основная функция рекомендера.

        Рекомендер возвращает список из limit карточек рекомендаций,
        которые затем будут обработаны в большом блендере
        """
        self.before_recommend(USER_INFO)

        lon, lat = USER_INFO['lon'], USER_INFO['lat']
        recommended_items = self.get_light_recommender_items(
            USER_INFO,
            self.candidates,
            (lon, lat),
            recommend_limit)

        for recommended_item in recommended_items:
            item_id = recommended_item.item_id
            USER_INFO['recommend_history'].add(item_id)

        stream_items = self.stream_blender(
            USER_INFO,
            recommended_items,
            blender_limit)
        return stream_items

    def add_rating(self, *, item_id=None, rating_good=True):
        for idx, cand in enumerate(self.candidates):
            if cand.item_id == item_id:
                self.candidates[idx].add_rating(1 * rating_good)
                print(self.candidates[idx].avg_rating)
                return


class FoodRecommender(Recommender):
    """Рекомендер ресторанов."""

    def __init__(self):
        """Сохраняет список всех ресторанов."""
        df_food = pd.read_csv('PlacesDatabase/food_places.csv')
        candidates = []
        for row in df_food.itertuples():
            lon, lat = row.Longitude_WGS84_en, row.Latitude_WGS84_en
            if validate_point((lon, lat)):
                item = Item(
                    ItemType.FOOD,
                    row.Name_en,
                    row.Address_en,
                    lon,
                    lat)
                candidates.append(item)
        self.candidates = candidates

    def get_light_recommender_items(self, USER_INFO, places, coords, limit):
        """Возвращает limit ближайших ресторанов."""
        items_with_dist = get_nearest(USER_INFO, places, coords, limit)
        recommended_items = []

        for (item, dist) in items_with_dist:
            recommended_item = RecommendItem(item, dist)
            recommended_items.append(recommended_item)

        return recommended_items
