from telebot import TeleBot, types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from core import recommender, utils
from collections import defaultdict


TOKEN = '6109688099:AAGJZuj0kVPEdjTZgaO27O5ZF-ey2WfFMis'
BOT_USERNAME = '@local_recommendation_bot'
RECNAME_FOOD = 'Рестораны 🍳'
RECNAME_SHOP = 'Магазины 🛒'
RECNAME_PARK = 'Парки 🌲'
RECNAME_THEATER = 'Театры 🎭'
RECNAME_MUSEUM = 'Музеи 🖼️'
RECNAME_ALL = 'Всё 🎈'
RECNAME_TO_ITEM_TYPE = {
    RECNAME_FOOD: utils.ItemType.FOOD,
    RECNAME_SHOP: utils.ItemType.SHOP
}

USER_INFO_AGGREGATOR = defaultdict(dict)
REC_HIST = defaultdict(dict)
CANDIDATES_HOLDER = recommender.CandidatesHolder()

food_recomender = recommender.FoodRecommender(
    recommender.ItemType.FOOD,
    CANDIDATES_HOLDER)
shop_recomender = recommender.ShopRecommender(
    recommender.ItemType.SHOP,
    CANDIDATES_HOLDER)
bot = TeleBot(token=TOKEN)


def gen_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("👍", callback_data="cb_yes"),
               InlineKeyboardButton("👎", callback_data="cb_no"))
    return markup


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.message.id in REC_HIST[call.from_user.id]:
        place_id = REC_HIST[call.from_user.id][call.message.id]
        CANDIDATES_HOLDER.add_rating(
                item_id=place_id,
                rating_good=(call.data == "cb_yes")
        )
        bot.answer_callback_query(call.id, "Answer recorded")
        del REC_HIST[call.from_user.id][call.message.id]
    else:
        bot.answer_callback_query(call.id, "You have already vote")


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton('👋 Поздороваться')
    markup.add(btn)
    bot.send_message(message.from_user.id,
                     '👋 Привет! Я твой бот c географическими рекомендациями!',
                     reply_markup=markup)


@bot.message_handler(commands=['add_geo'])
def add_geo(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text='Отправить местоположение 🌎',
                                request_location=True)
    btn2 = types.KeyboardButton(text='Указать адрес 🗺️')
    btn3 = types.KeyboardButton('Вернуться назад 🛬')
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.from_user.id,
                     'Нажми на кнопку и передай мне свое местоположение',
                     reply_markup=markup)


@bot.message_handler(content_types=['location'])
def handle_location(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if message.location is not None:
        btn1 = types.KeyboardButton(text='Да ✔️')
        btn2 = types.KeyboardButton(text='Нет ❌')
        markup.add(btn1, btn2)

        USER_INFO = USER_INFO_AGGREGATOR[message.from_user.id]
        lon, lat = message.location.longitude, message.location.latitude
        USER_INFO['lon'] = lon
        USER_INFO['lat'] = lat

        flag, mess = utils.get_address_from_coords((lon, lat))

        if flag:
            bot.send_message(message.from_user.id,
                             'Твой адрес:' + mess + '?',
                             reply_markup=markup)
        else:
            bot.send_message(message.from_user.id,
                             mess,
                             reply_markup=markup)

    else:
        bot.send_message(message.from_user.id,
                         'Не могу определить твою локацию 😿',
                         reply_markup=markup)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    start_actions = ['👋 Поздороваться', 'Вернуться назад 🛬']

    base_commands = [
            'Как пользоваться ботом? 🤓',
            'СТАРТ 🚀',
            'Наш репозиторий 👻'
        ]
    base_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    base_markup.add(*(types.KeyboardButton(cmd) for cmd in base_commands))

    recommendation_types = [RECNAME_FOOD, RECNAME_SHOP,
                            RECNAME_PARK, RECNAME_THEATER,
                            RECNAME_MUSEUM, RECNAME_ALL]
    rec_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    rec_markup.add(*(
            types.KeyboardButton(rec_type) for rec_type in recommendation_types
        )
    )

    check_rec_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_var = types.KeyboardButton('Посмотреть варианты 🤔')
    btn_back = types.KeyboardButton('Вернуться назад 🛬')
    check_rec_markup.add(btn_var, btn_back)

    location_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_address = types.KeyboardButton(text='Указать адрес 🗺️')
    btn_dest = types.KeyboardButton(text='Отправить местоположение 🌎',
                                    request_location=True)
    location_markup.add(btn_address, btn_dest, btn_back)

    if message.text in start_actions:
        bot.send_message(message.from_user.id,
                         '❓ Что вас интересует?',
                         reply_markup=base_markup)

    elif message.text == 'Как пользоваться ботом? 🤓':
        how_to_msg = r'Воспользуйтесь командой /add\_geo, ' \
            r'чтобы добавить ваше местонахождение'
        bot.send_message(message.from_user.id,
                         how_to_msg,
                         parse_mode='MarkdownV2')

    elif message.text == 'СТАРТ 🚀':
        bot.send_message(message.from_user.id,
                         'Нажми на кнопку и передай мне свое местоположение',
                         reply_markup=location_markup)

    # FIXME replace 'Да' by another logic
    elif message.text in ['Отправить местоположение 🌎', 'Да ✔️']:
        bot.send_message(message.from_user.id,
                         'Выбери, какие рекомендации ты хочешь получить',
                         reply_markup=rec_markup,
                         parse_mode='Markdown')

    elif message.text.startswith('Введите адрес в формате'):
        print('Введите адрес в формате... TODO')

    elif message.text == 'Наш репозиторий 👻':
        mess = 'Детали нашего проекта вы можете посмотреть по '
        link = '[ссылке](https://github.com/hgfs113/local-recommendation-bot)'
        bot.send_message(message.from_user.id,
                         mess + link,
                         parse_mode='Markdown')

    elif message.text == 'Указать адрес 🗺️':
        mess = 'Введите адрес в формате x.x, x.x (для координат)'
        ' или в формате Город, Улица, Номер дома (через запятую)'
        bot.send_message(message.from_user.id,
                         mess,
                         parse_mode='Markdown')

    elif message.text in recommendation_types:
        if message.text not in RECNAME_TO_ITEM_TYPE:
            bot.send_message(message.from_user.id,
                             'Этот тип рекомендаций ещё недоступен',
                             reply_markup=check_rec_markup,
                             parse_mode='Markdown')
        else:
            bot.send_message(message.from_user.id,
                             'Вы выбрали ' + message.text.lower(),
                             reply_markup=check_rec_markup,
                             parse_mode='Markdown')
            USER_INFO = USER_INFO_AGGREGATOR[message.from_user.id]
            USER_INFO['recommender_type'] = RECNAME_TO_ITEM_TYPE[message.text]

    elif message.text == 'Посмотреть варианты 🤔':
        USER_INFO = USER_INFO_AGGREGATOR[message.from_user.id]
        if 'lon' not in USER_INFO or 'lat' not in USER_INFO:
            bot.send_message(message.from_user.id,
                             'Я не знаю, где ты находишься',
                             parse_mode='Markdown')
        else:
            if USER_INFO['recommender_type'] == utils.ItemType.FOOD:
                recommender = food_recomender
            elif USER_INFO['recommender_type'] == utils.ItemType.SHOP:
                recommender = shop_recomender
            else:
                bot.send_message(message.from_user.id,
                                 'Вы не выбрали тип рекомендаций',
                                 parse_mode='Markdown')
            if recommender is not None:
                recommended_items = recommender.recommend(
                    USER_INFO,
                    recommend_limit=20,
                    blender_limit=5)
                write_recommendations(recommended_items, message)

    else:
        try:
            address = message.text.split(',')
            address = list(map(lambda x: x.strip(), address))
            if len(address) == 2:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                btn1 = types.KeyboardButton(text='Да')
                btn2 = types.KeyboardButton(text='Нет')
                markup.add(btn1, btn2)

                flag, mess = utils.get_address_from_coords(address)
                print('else:', flag, mess)

                if flag:
                    bot.send_message(message.from_user.id,
                                     'Твой адрес:' + mess + '?',
                                     reply_markup=markup)
                else:
                    bot.send_message(message.from_user.id,
                                     mess,
                                     reply_markup=markup)
        except Exception:
            bot.send_message(message.from_user.id,
                             'Я не понимаю твою команду :(',
                             parse_mode='Markdown')


def write_recommendations(recommended_items, message):
    for i, place in enumerate(recommended_items):
        d = utils.dist_to_str(place.dist)
        msg_sent = bot.send_message(
                message.from_user.id,
                f'#{i+1}: **{place.name}**\n'
                f'- адрес: {place.address}\n'
                f'- расстояние от Вас: {d}\n'
                f'- рейтинг: {place.get_rating() or "Не указан"}',
                parse_mode='Markdown', reply_markup=gen_markup()
            )
        REC_HIST[message.from_user.id][msg_sent.message_id] = place.item_id

    bot.send_message(message.from_user.id,
                     'Ещё варианты? 😎',
                     parse_mode='Markdown')


if __name__ == "__main__":
    CANDIDATES_HOLDER.update(
        food_path='PlacesDatabase/food_places.csv',
        shop_path='PlacesDatabase/shopping_v1.csv')
    bot.polling(none_stop=True, interval=0)
