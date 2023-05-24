from .utils import get_nearest, ItemType, Item, RecommendItem
from .recommender import CandidatesHolder, FoodRecommender
import io


# Тест на случай, когда все места уже были рекомендованы
def test_get_nearest_all_duplicate():
    item1 = Item(ItemType.FOOD, 'hash1', 'hash1', *(1, 1))
    item2 = Item(ItemType.FOOD, 'hash2', 'hash2', *(2, 2))
    item3 = Item(ItemType.FOOD, 'hash3', 'hash3', *(3, 3))
    candidates = {
        item1.item_id: item1,
        item2.item_id: item2,
        item3.item_id: item3
    }
    USER_INFO = {
        'recommend_history': set(item_id for item_id in candidates)
    }
    coords = (0, 0)
    N = 2
    result = get_nearest(USER_INFO, candidates, coords, N)
    assert result == []


def test_Recommender_stream_blender():
    # Тестирование метода stream_blender
    # Создаем тестовые данные
    USER_INFO = {'lon': 30.315868,
                 'lat': 59.939095,
                 'recommend_history': set()}

    item1 = Item(ItemType.FOOD, 'hash1', 'hash1', 1, 1)
    item2 = Item(ItemType.FOOD, 'hash2', 'hash2', 2, 1)
    item3 = Item(ItemType.FOOD, 'hash3', 'hash3', 1, 2)
    item4 = Item(ItemType.FOOD, 'hash4', 'hash4', 2, 2)
    item5 = Item(ItemType.FOOD, 'hash5', 'hash5', 2, 3)

    candidates = {
        item1.item_id: item1,
        item2.item_id: item2,
        item3.item_id: item3,
        item4.item_id: item4,
        item5.item_id: item5,
    }
    type_to_candidates = {
        ItemType.FOOD: candidates
    }
    candidates_holder = CandidatesHolder(type_to_candidates)

    recommended_items = [
        RecommendItem(item1, dist=0.1),
        RecommendItem(item2, dist=0.2),
        RecommendItem(item3, dist=0.3),
        RecommendItem(item4, dist=0.4),
        RecommendItem(item5, dist=0.5)
    ]

    # Тестируется произвольный дочерний класс абстрактного Recommender
    recommender = FoodRecommender(ItemType.FOOD, candidates_holder)

    # Тестируем случай, когда blender_limit больше или равен
    # длине recommended_items
    stream_items = recommender.stream_blender(
            USER_INFO,
            recommended_items,
            blender_limit=6
        )
    assert len(stream_items) == 5
    assert stream_items[-1].dist <= 0.5


def test_item():
    ratings = [1, 0, 1, 1, 1, 0, 1, 1]
    item1 = Item(ItemType.FOOD, 'hash1', 'hash1', *(1, 1))
    for r in ratings:
        item1.add_rating(r)
    assert item1.get_rating() == sum(ratings) / len(ratings)

    output = io.StringIO()
    print(item1, file=output)
    contents = output.getvalue()
    output.close()

    assert contents == 'hash1, hash1. Coords: (1, 1)\n'


def test_candidates_holder():
    ratings = [1, 0, 1, 1, 1, 0, 1, 1]
    CANDIDATES_HOLDER = CandidatesHolder()

    CANDIDATES_HOLDER.update(
        food_path='PlacesDatabase/food_places.csv',
        shop_path='PlacesDatabase/shopping_v1.csv')

    assert len(CANDIDATES_HOLDER.get_candidates_by_type(ItemType.FOOD)) \
           == 20563
    assert len(CANDIDATES_HOLDER.get_candidates_by_type(ItemType.SHOP)) \
           == 59206

    item_id = list(CANDIDATES_HOLDER.get_candidates_by_type(
        ItemType.FOOD).keys())[0]

    for r in ratings:
        CANDIDATES_HOLDER.add_rating(item_id=item_id,
                                     rating_good=bool(r))

    assert CANDIDATES_HOLDER.get_candidates_by_type(ItemType.FOOD)[
               item_id].get_rating() == sum(ratings) / len(ratings)


def test_item_rating():
    ratings = [1] * 10
    USER_INFO = {'lon': 30.315868,
                 'lat': 59.939095,
                 'recommend_history': set()}

    CANDIDATES_HOLDER = CandidatesHolder()

    food_recomender = FoodRecommender(
        ItemType.FOOD,
        CANDIDATES_HOLDER)

    CANDIDATES_HOLDER.update(
        food_path='PlacesDatabase/food_places.csv',
        shop_path='PlacesDatabase/shopping_v1.csv')

    recommended1 = food_recomender.get_light_recommender_items(USER_INFO,
                CANDIDATES_HOLDER.get_candidates_by_type(ItemType.FOOD),
                (USER_INFO['lon'], USER_INFO['lat']), 5)

    item_id = list(CANDIDATES_HOLDER.get_candidates_by_type(
        ItemType.FOOD).keys())[0]

    for r in ratings:
        CANDIDATES_HOLDER.add_rating(item_id=item_id, rating_good=bool(r))

    recommended2 = food_recomender.get_light_recommender_items(USER_INFO,
                CANDIDATES_HOLDER.get_candidates_by_type(ItemType.FOOD),
                (USER_INFO['lon'], USER_INFO['lat']), 5)
    for r1, r2 in zip(recommended1, recommended2):
        assert r1.item_id == r2.item_id
