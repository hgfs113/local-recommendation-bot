from core import utils


def recommend(USER_DICT):
    places = utils.get_places('PlacesDatabase/food_places.csv')
    lon, lat = USER_DICT['lon'], USER_DICT['lat']
    nearest_places = utils.get_nearest(places, (lon, lat), 5)
    return nearest_places