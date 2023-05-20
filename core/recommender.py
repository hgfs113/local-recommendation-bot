from core import utils


def before_recommend(USER_DICT):
    if 'recommend_history' not in USER_DICT:
        USER_DICT['recommend_history'] = set()


def recommend(USER_DICT):
    places = utils.get_places('PlacesDatabase/food_places.csv')
    lon, lat = USER_DICT['lon'], USER_DICT['lat']
    nearest_places = utils.get_nearest(USER_DICT, places, (lon, lat), 5)

    for place in nearest_places:
        place_hash = place[0].get_hash()
        USER_DICT['recommend_history'].add(place_hash)

    return nearest_places
