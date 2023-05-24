import os
import pickle
import pandas as pd
from abc import ABC, abstractmethod
from .utils import ItemType, Item, RecommendItem
from .utils import validate_point, get_nearest, stream_blender_diego


class CandidatesHolder:

    """
    Хранилище кандидатов для рекомендации.

    В класс можно передать уже созданный словарь type_to_candidates,
    либо оставить поле пустым, после чего будет автоматически создан
    словарь type_to_candidates для всех доступных на текущий момент
    видов рекомендаций.

    Метод update обновит информацию о всех доступных в базе данных кандидатах,
    то есть перезапишет их для дальнейшего использования роекомендером.
    """

    def __init__(self, type_to_candidates=None):
        if type_to_candidates is not None:
            self.type_to_candidates = type_to_candidates
        else:
            self.type_to_candidates = {
                ItemType.FOOD: dict(),
                ItemType.SHOP: dict()
            }

    def get_candidates_by_type(self, item_type):
        return self.type_to_candidates[item_type]

    def update(self, food_path, shop_path):
        self.type_to_candidates[ItemType.FOOD] =\
            self.read_candidates_by_type(ItemType.FOOD, food_path)
        self.type_to_candidates[ItemType.SHOP] =\
            self.read_candidates_by_type(ItemType.FOOD, shop_path)

    def read_candidates_by_type(self, item_type, path):
        with open(path + '.pb', 'rb') as f:
            embeddings = pickle.load(f)
        df = pd.read_csv(path + '.csv')
        candidates = {}
        for i, row in enumerate(df.itertuples()):
            lon, lat = row.lon, row.lat
            if validate_point((lon, lat)):
                item = Item(
                    item_type,
                    row.name,
                    row.address,
                    lon,
                    lat,
                    embeddings[i])
                candidates[item.item_id] = item
        return candidates

    def add_rating(self, *, item_id=None, rating_good=True):
        for item_type, candidates in self.type_to_candidates.items():
            if item_id in candidates:
                candidate = self.type_to_candidates[item_type][item_id]
                candidate.add_rating(
                    1 * rating_good
                )
                return


class FeedbackEventProcessor():

    """
    В этом классе происходит взаимодействие пользователей с рекомендациями.

    Содержит метод write_user_item_rating(), который пишет
    оценку пользователя в файл history_path.
    """

    def __init__(self, history_path):
        self.history_path = history_path

    def write_user_item_rating(self, user_id, item_id, rating_good):
        mode = 'a' if os.path.exists(self.history_path) else 'w'
        rating = 1.0 if rating_good else -1.0
        with open(self.history_path, mode) as f:
            f.write(f'{user_id},{item_id},{rating}\n')


class Recommender(ABC):

    """
    Абстрактный класс рекомендера с единой для всех вертикалей логикой.

    В наследнике требуется переопределить некоторые абстрактные функции,
    играющие ключевую роль в рекомендациях.
    """

    def __init__(self, item_type, candidates_holder):
        """
        Содержит тип рекоммендера и хранителя кандидатов.

        Кандидаты в рекомендере берутся из candidates_holder по item_type.
        После вызова метода update() в candidates_holder все кандидаты
        будут обновлены в рекомендере автоматически.
        """
        self.item_type = item_type
        self.candidates_holder = candidates_holder

    @abstractmethod
    def get_light_recommender_items(self, USER_INFO, candidates,
                                    coords, limit):
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

    def stream_blender(self, USER_INFO, recommended_items,
                       blender_limit=5, mode='Diego', temperature=5):
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
        item_type = self.item_type
        candidates = self.candidates_holder.get_candidates_by_type(item_type)
        recommended_items = self.get_light_recommender_items(
            USER_INFO,
            candidates,
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


class FoodRecommender(Recommender):

    """Рекомендер ресторанов."""

    def get_light_recommender_items(self, USER_INFO, candidates,
                                    coords, limit):
        """Возвращает limit ближайших ресторанов."""
        items_with_dist = get_nearest(USER_INFO, candidates, coords, limit)
        recommended_items = []

        for (item, dist) in items_with_dist:
            recommended_item = RecommendItem(item, dist)
            recommended_items.append(recommended_item)

        return recommended_items


class ShopRecommender(Recommender):

    """Рекомендер магазинов."""

    def get_light_recommender_items(self, USER_INFO, candidates,
                                    coords, limit):
        """
        Возвращает limit ближайших ресторанов.

        Пока логика light recommender такая же, как и у FoodRecommender.
        Но это временно.
        """
        items_with_dist = get_nearest(USER_INFO, candidates, coords, limit)
        recommended_items = []

        for (item, dist) in items_with_dist:
            recommended_item = RecommendItem(item, dist)
            recommended_items.append(recommended_item)

        return recommended_items
