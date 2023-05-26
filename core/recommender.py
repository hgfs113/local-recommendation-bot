import os
import pickle
import numpy as np
import pandas as pd
from .utils import ItemType, Item, ItemId, RecommendItem
from .utils import validate_point, get_nearest
from .utils import stream_blender_diego


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
        item_id_to_candidate = {}
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
                item_id_to_candidate[item.item_id] = item
        return item_id_to_candidate

    def add_rating(self, *, item_id=None, rating_good=True):
        for item_type, candidates in self.type_to_candidates.items():
            if item_id in candidates:
                candidate = self.type_to_candidates[item_type][item_id]
                candidate.add_rating(
                    1 * rating_good
                )
                return


class EmbeddingsHolder:

    """
    Хранилище эмбеддингов всех кандидатов.

    В класс можно передать уже созданный словарь type_to_embeddings,
    либо оставить поле пустым, после чего будет автоматически создан
    словарь type_to_embeddings для всех доступных на текущий момент
    видов рекомендаций.

    Метод update обновит информацию о всех доступных в базе данных эмбеддингах,
    то есть перезапишет их для дальнейшего использования роекомендером.
    """

    def __init__(self, type_to_embeddings=None):
        if type_to_embeddings is not None:
            self.type_to_embeddings = type_to_embeddings
        else:
            self.type_to_embeddings = {
                ItemType.FOOD: dict(),
                ItemType.SHOP: dict()
            }

    def get_embeddings_by_type(self, item_type):
        return self.type_to_embeddings[item_type]

    def update(self, food_path, shop_path):
        self.type_to_embeddings[ItemType.FOOD] =\
            self.read_embeddings_by_type(ItemType.FOOD, food_path)
        self.type_to_embeddings[ItemType.SHOP] =\
            self.read_embeddings_by_type(ItemType.FOOD, shop_path)

    def read_embeddings_by_type(self, item_type, path):
        with open(path + '.pb', 'rb') as f:
            embeddings = pickle.load(f)
        df = pd.read_csv(path + '.csv')
        item_id_to_embedding = {}
        for i, row in enumerate(df.itertuples()):
            item = Item(
                item_type,
                row.name,
                row.address,
                row.lon,
                row.lat)
            embedding = embeddings[i] / np.linalg.norm(embeddings[i])
            item_id_to_embedding[item.item_id] = embedding
        return item_id_to_embedding


class FeedbackEventProcessor():

    """
    В этом классе происходит взаимодействие пользователей с рекомендациями.

    Содержит метод write_user_item_rating(), который пишет
    оценку пользователя в файл history_path.

    Содержит метод read_user_history, который возвращает словарь item_to_rating
    с историей оценок пользователя, или None, если истории нет.
    """

    def __init__(self, history_path):
        """Сохраняет путь до папки с историями пользователей."""
        self.history_path = history_path
        if not os.path.exists(self.history_path):
            os.makedirs(self.history_path)

    def write_user_item_rating(self, user_id, item_id, rating_good):
        """
        Записывает оценку пользователя элементу рекомендаций.

        Запись происходит в формате `type,id,rating`,
        где type и id - есть поля ItemId, а rating - плюс или минус единица
        в зависимости от оценки пользователя.
        """
        user_history_path = os.path.join(self.history_path, "history_" + str(user_id))
        mode = 'a' if os.path.exists(user_history_path) else 'w'
        rating = 1.0 if rating_good else -1.0
        with open(user_history_path, mode) as f:
            f.write(f'{item_id.type},{item_id.id},{rating}\n')

    def read_user_history(self, user_id, limit=None):
        """
        Читаем историю оценок пользователя.

        Возвращает словарь item_id_to_rating, который содержит последние
        limit оценок пользователя. Если limit не задан, то возвращает
        всю историю без ограничений.
        """
        user_history_path = self.history_path + '_' + str(user_id)
        if not os.path.exists(user_history_path):
            return None

        item_id_to_rating = {}
        with open(user_history_path, 'r') as f:
            history = f.read()

        events = history.split('\n')
        if limit is not None:
            events = events[len(events) - limit:]

        for row in events:
            s = row.split(',')
            try:
                type, id, rating = int(s[0]), int(s[1]), float(s[2])
                item_id = ItemId(type, id)
                item_id_to_rating[item_id] = rating
            except Exception:
                continue
        return item_id_to_rating

    def clear_user_history(self, user_id):
        """Удаление пользовательской истории."""
        user_history_path = self.history_path + '_' + str(user_id)
        if os.path.exists(user_history_path):
            os.remove(user_history_path)


class Recommender():

    """Основной класс рекомендера с единой для всех вертикалей логикой."""

    def __init__(self, item_type, candidates_holder,
                 embeddings_holder=None, feedback_event_processor=None):
        """
        Содержит тип рекоммендера и хранителя кандидатов.

        Также содержит хранителя эмбеддингов и обработчик оценок, которые
        не являются обязательными.

        Кандидаты в рекомендере берутся из candidates_holder по item_type.
        После вызова метода update() в candidates_holder все кандидаты
        будут обновлены в рекомендере автоматически.

        Эмбеддинги в рекомендере берутся из embeddings_holder по item_type.
        После вызова метода update() в embeddings_holder все эмбеддинги
        будут обновлены в рекомендере автоматически.

        Обработчик оценок используется для считывания оценок пользователя
        из истории непосредственно внутри recommend.
        """
        self.item_type = item_type
        self.candidates_holder = candidates_holder
        self.embeddings_holder = embeddings_holder
        self.feedback_event_processor = feedback_event_processor

    def before_recommend(self, USER_INFO, user_history_limit=None):
        """
        Подготовка к вызову рекомендера.

        Метод для подготовки данных перед вызовом рекомендера
        для его корректной работы:

        Создаёт множество recommend_history, если история пользователя
        отсутсвует. Записывает в item_id_to_rating последние user_history_limit
        оценок пользователя. Если user_history_limit не задано, то запишет
        всю историю пользователя.
        """
        if 'recommend_history' not in USER_INFO:
            USER_INFO['recommend_history'] = set()
        user_id = USER_INFO['user_id']
        read_user_history = self.feedback_event_processor.read_user_history
        item_id_to_rating = read_user_history(user_id, user_history_limit)
        USER_INFO['item_id_to_rating'] = item_id_to_rating

    def get_light_recommender_items(self, USER_INFO, candidates,
                                    coords, limit):
        """
        Лёгкий рекомендер.

        Возвращает список из limit рекомендательных карточек,
        отранжированных по расстоянию, которые затем будут переданы
        в тяжёлый рекомендер.
        """
        items_with_dist = get_nearest(USER_INFO, candidates, coords, limit)
        recommended_items = []

        for (item, dist) in items_with_dist:
            recommended_item = RecommendItem(item, dist)
            recommended_items.append(recommended_item)

        return recommended_items

    def get_heavy_recommender_items(self, USER_INFO, light_recommender_items,
                                    embeddings, limit):
        """
        Тяжёлый рекомендер.

        Возвращает список из limit рекомендательных карточек,
        отранжированных по косиносному расстоянию пользовательских
        и айтемных эмбеддингов Диего. Результат тяжёлого рекомендера
        будет обработан в stream_blender.
        """
        item_id_to_rating = USER_INFO['item_id_to_rating']
        if item_id_to_rating is None:
            heavy_recommender_items = light_recommender_items
            np.random.shuffle(heavy_recommender_items)
            return heavy_recommender_items[:limit]

        user_embedding = None
        for item_id, rating in item_id_to_rating.items():
            if item_id not in embeddings:
                print('WARNING: item was not found in embeddings holder')
                continue
            user_item_embedding = rating * embeddings[item_id]
            if user_embedding is None:
                user_embedding = user_item_embedding
            else:
                user_embedding += user_item_embedding

        if user_embedding is None:
            print('WARNING: user embedding is None after feedback processing')
            heavy_recommender_items = light_recommender_items
            np.random.shuffle(heavy_recommender_items)
            return heavy_recommender_items[:limit]

        user_embedding /= np.linalg.norm(user_embedding)
        item_to_score = {}
        for item in light_recommender_items:
            item_id = item.item_id
            if item_id in embeddings:
                embedding = embeddings[item_id]
                item_to_score[item] = np.dot(user_embedding, embedding)
            else:
                item_to_score[item] = -1

        items_score_sorted = sorted(item_to_score.items(), key=lambda x: -x[1])
        items_sorted = [k for k, v in items_score_sorted]
        heavy_recommender_items = items_sorted[:limit]

        return heavy_recommender_items

    def stream_blender(self, USER_INFO, recommended_items,
                       blender_limit=5, mode='Diego', temperature=1):
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

    def recommend(self, USER_INFO, user_history_limit=None,
                  light_recommender_limit=200, heavy_recommender_limit=20,
                  blender_limit=5):
        """
        Основная функция рекомендера.

        Рекомендер возвращает список из limit карточек рекомендаций,
        которые затем будут обработаны в большом блендере
        """
        self.before_recommend(USER_INFO, user_history_limit)

        lon, lat = USER_INFO['lon'], USER_INFO['lat']
        item_type = self.item_type
        candidates = self.candidates_holder.get_candidates_by_type(item_type)
        light_recommended_items = self.get_light_recommender_items(
            USER_INFO,
            candidates,
            (lon, lat),
            light_recommender_limit)

        embeddings = self.embeddings_holder.get_embeddings_by_type(item_type)
        recommended_items = self.get_heavy_recommender_items(
            USER_INFO,
            light_recommended_items,
            embeddings,
            heavy_recommender_limit)

        for recommended_item in recommended_items:
            item_id = recommended_item.item_id
            USER_INFO['recommend_history'].add(item_id)

        stream_items = self.stream_blender(
            USER_INFO,
            recommended_items,
            blender_limit)

        return stream_items
