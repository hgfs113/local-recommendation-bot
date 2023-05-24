from .utils import get_nearest, ItemType, Item, RecommendItem
from .recommender import CandidatesHolder, FoodRecommender


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
    pass

def test_candidates_holder():
    pass

def test_item_rating():
    pass
