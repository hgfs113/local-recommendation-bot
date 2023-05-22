from .utils import get_nearest, Item, RecommendItem
from .recommender import FoodRecommender


# Тест на случай, когда все места уже были рекомендованы
def test_get_nearest_all_duplicate():
    places = [
        Item('hash1', 'hash1', *(1, 1)),
        Item('hash2', 'hash2', *(2, 2)),
        Item('hash3', 'hash3', *(3, 3))
    ]
    USER_INFO = {
        'recommend_history': set(place.get_hash() for place in places)
    }
    coords = (0, 0)
    N = 2
    result = get_nearest(USER_INFO, places, coords, N)
    assert result == []


def test_Recommender_stream_blender():
    # Тестирование метода stream_blender
    # Создаем тестовые данные
    USER_INFO = {'lon': 30.315868,
                 'lat': 59.939095,
                 'recommend_history': set()}
    recommended_items = [RecommendItem(Item('hash1', 'hash1', 1, 1), dist=0.1),
                         RecommendItem(Item('hash2', 'hash2', 2, 1), dist=0.2),
                         RecommendItem(Item('hash3', 'hash3', 1, 2), dist=0.3),
                         RecommendItem(Item('hash4', 'hash4', 2, 2), dist=0.4),
                         RecommendItem(Item('hash5', 'hash5', 2, 3), dist=0.5)]

    # Тестируется произвольный дочерний класс абстрактного Recommender
    recommender = FoodRecommender()

    # Тестируем случай, когда blender_limit больше или равен
    # длине recommended_items
    stream_items = recommender.stream_blender(
            USER_INFO,
            recommended_items,
            blender_limit=6
        )
    assert len(stream_items) == 5
    assert stream_items[-1].dist <= 0.5
