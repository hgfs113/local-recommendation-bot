from utils import get_nearest, PlaceEntry


# Тест на случай, когда все места уже были рекомендованы
def test_get_nearest_all_duplicate():
    places = [
        PlaceEntry('hash1', 'hash1', *(1, 1)),
        PlaceEntry('hash2', 'hash2', *(2, 2)),
        PlaceEntry('hash3', 'hash3', *(3, 3))
    ]
    USER_DICT = {
        'recommend_history': set(place.get_hash() for place in places)
    }
    coords = (0, 0)
    N = 2
    result = get_nearest(USER_DICT, places, coords, N)
    assert result == []
