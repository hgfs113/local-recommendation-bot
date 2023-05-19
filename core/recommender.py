from core import utils


def recommend(USER_DICT):
    places = utils.get_places('PlacesDatabase/food_places.csv')
    lon, lat = USER_DICT['lon'], USER_DICT['lat']
    nearest_places = utils.get_nearest(places, (lon, lat), 5)

    if 'recommend_history' not in USER_DICT:
        USER_DICT['recommend_history'] = set()
    for place in nearest_places:
        USER_DICT['recommend_history'].add(place)
    print(USER_DICT['recommend_history'])

    return nearest_places