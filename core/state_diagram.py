from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from core import utils
from collections import defaultdict
import gettext


_ = gettext.translation(
    domain="messages",
    localedir="locale",
    languages=["en"],
).gettext


BC_HOW = 'Как пользоваться ботом? 🤓'
BC_START = 'СТАРТ 🚀'
BC_CLEAR = 'Очистить историю 🤐'
BC_REPO = 'Наш репозиторий 👻'


RECNAME_FOOD = _('Рестораны 🍳')
RECNAME_SHOP = _('Магазины 🛒')
RECNAME_PARK = _('Парки 🌲')
RECNAME_THEATER = _('Театры 🎭')
RECNAME_MUSEUM = _('Музеи 🖼️')
# RECNAME_ALL = _('Всё 🎈')
RECNAME_TO_ITEM_TYPE = {
    RECNAME_FOOD: utils.ItemType.FOOD,
    RECNAME_SHOP: utils.ItemType.SHOP
}


USER_INFO_AGGREGATOR = defaultdict(dict)
REC_HIST = defaultdict(dict)


class StateDiagram:
    def __init__(self, bot, feedback_event_processor,
                 food_recomender, shop_recomender):
        self.feedback_event_processor = feedback_event_processor
        self.bot = bot
        self.food_recomender = food_recomender
        self.shop_recomender = shop_recomender
        self.state = None
        self.markup = None
        self.bc = [
            BC_HOW,
            BC_START,
            BC_CLEAR,
            BC_REPO
        ]
        self.recom_types = [RECNAME_FOOD,
                            RECNAME_SHOP,
                            RECNAME_PARK,
                            RECNAME_THEATER,
                            RECNAME_MUSEUM]
        self.init_markups()

    def init_markups(self):
        self.base_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        self.base_markup.add(*(types.KeyboardButton(cmd) for cmd in self.bc))

        self.check_rec_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_var = types.KeyboardButton('Посмотреть варианты 🤔')
        btn_back = types.KeyboardButton('Вернуться назад 🛬')
        self.check_rec_markup.add(btn_var, btn_back)

        self.rec_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        self.rec_markup.add(*(
            types.KeyboardButton(rec_type) for rec_type in self.recom_types
        ))
        self.rec_markup.add(btn_back)

        self.loc_mark = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_address = types.KeyboardButton(text='Указать адрес 🗺️')
        btn_dest = types.KeyboardButton(text='Отправить местоположение 🌎',
                                        request_location=True)
        self.loc_mark.add(btn_address, btn_dest, btn_back)

        self.start_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn = types.KeyboardButton('👋 Поздороваться')
        self.start_markup.add(btn)

        self.reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton(text='Да ✔️')
        btn2 = types.KeyboardButton(text='Нет ❌')
        self.reply_markup.add(btn1, btn2)

    def bot_answer(self, message):
        if message.text == '👋 Поздороваться':
            self.start_interface(message)

        elif message.text == BC_HOW:
            self.usual_message(message, "how_use")

        elif message.text == BC_REPO:
            self.usual_message(message, "link")

        elif message.text == BC_CLEAR:
            self.clear_history(message)

        elif message.text in [BC_START, '/add_geo']:
            self.initialize_user(message)

        elif message.text in ['Вернуться назад 🛬', '/back']:
            self.backward_go(message)

        elif message.text in ['Отправить местоположение 🌎',
                              'Указать адрес 🗺️', 'Да ✔️']:
            self.main(message)

        elif message.text == 'Нет ❌':
            self.initialize_user(message)

        elif message.text.startswith('Введите адрес в формате'):
            print('Введите адрес в формате... TODO')

        elif message.text in self.recom_types:
            self.select_recommendation(message)

        elif message.text == 'Посмотреть варианты 🤔':
            self.show_recommendation(message)

        else:
            self.read_address(message)

    def backward_go(self, message):
        USER_INFO = USER_INFO_AGGREGATOR[message.from_user.id]
        if "state" not in USER_INFO:
            USER_INFO["state"] = "START_INTERFACE"
            mess = "Это стартовый интерфейс"
            self.bot.send_message(message.from_user.id,
                                  mess,
                                  reply_markup=self.base_markup)
        elif USER_INFO["state"] == "START_INTERFACE":
            mess = "Это стартовый интерфейс"
            self.bot.send_message(message.from_user.id,
                                  mess,
                                  reply_markup=self.base_markup)
        elif USER_INFO["state"] in ["INITIALIZE_USER", "RECOMMENDATION"]:
            USER_INFO["state"] = "START_INTERFACE"
            self.bot.send_message(message.from_user.id,
                                  '❓ Что вас интересует?',
                                  reply_markup=self.base_markup)
        elif USER_INFO["state"] == "MAIN":
            USER_INFO["state"] = "INITIALIZE_USER"
            mess = 'Нажми на кнопку и передай мне свое местоположение'
            self.bot.send_message(message.from_user.id,
                                  mess,
                                  reply_markup=self.loc_mark)
        elif USER_INFO["state"] == "SHOW_RECOMMENDATION":
            USER_INFO["state"] = "RECOMMENDATION"
            mess = 'Выбери, какие рекомендации ты хочешь получить'
            self.bot.send_message(message.from_user.id,
                                  mess,
                                  reply_markup=self.rec_markup,
                                  parse_mode='Markdown')

    def start_interface(self, message):
        USER_INFO = USER_INFO_AGGREGATOR[message.from_user.id]
        USER_INFO["state"] = "START_INTERFACE"
        self.bot.send_message(message.from_user.id,
                              '❓ Что вас интересует?',
                              reply_markup=self.base_markup)

    def clear_history(self, message):
        USER_INFO = USER_INFO_AGGREGATOR[message.from_user.id]
        if "state" in USER_INFO:
            if "user_id" in USER_INFO:
                self.feedback_event_processor.clear_user_history(
                    USER_INFO["user_id"])
            else:
                print('WARNING: user id not in USER_INFO')
        else:
            print('WARNING: state not in USER_INFO')
        self.bot.send_message(message.from_user.id,
                              'Ваша история удалена 😈',
                              parse_mode='Markdown')

    def usual_message(self, message, what_message):
        if what_message == "how_use":
            how_to_msg = r'Воспользуйтесь командой /add\_geo, ' \
                r'чтобы добавить ваше местонахождение\. ' \
                r'Воспользуйтесь командой /back, ' \
                r'чтобы вернуться на команду назад\. ' \
                r'Воспользуйтесь командой /clear_history, ' \
                r'чтобы очистить историю\.'
            self.bot.send_message(message.from_user.id,
                                  how_to_msg,
                                  parse_mode='MarkdownV2')
        elif what_message == "link":
            mess = 'Детали нашего проекта вы можете посмотреть по '
            m = '[ссылке]'
            link = '(https://github.com/hgfs113/local-recommendation-bot)'
            self.bot.send_message(message.from_user.id,
                                  mess + m + link,
                                  parse_mode='Markdown')

    def initialize_user(self, message):
        USER_INFO = USER_INFO_AGGREGATOR[message.from_user.id]
        GOOD_VARIANTS = ["START_INTERFACE", "MAIN",
                         "INITIALIZE_USER"]
        if "state" not in USER_INFO:
            USER_INFO["state"] = "START_INTERFACE"
            mess = "Вы не можете воспользоваться этой командой, \
            пока не нажмете 'старт'"
            self.bot.send_message(message.from_user.id,
                                  mess,
                                  reply_markup=self.base_markup)
        elif USER_INFO["state"] in GOOD_VARIANTS:
            mess = 'Нажми на кнопку и передай мне свое местоположение'
            USER_INFO["state"] = "INITIALIZE_USER"
            self.bot.send_message(message.from_user.id,
                                  mess,
                                  reply_markup=self.loc_mark)
        else:
            mess = "Вы не можете воспользоваться этой командой, \
            пока не завершите текущий процесс."
            self.bot.send_message(message.from_user.id,
                                  mess,
                                  reply_markup=self.select_markup(message))

    def select_markup(self, message):
        USER_INFO = USER_INFO_AGGREGATOR[message.from_user.id]
        if "state" not in USER_INFO:
            return self.start_markup
        elif USER_INFO["state"] == "START_INTERFACE":
            return self.base_markup
        elif USER_INFO["state"] == "INITIALIZE_USER":
            return self.loc_mark

    def main(self, message):
        USER_INFO = USER_INFO_AGGREGATOR[message.from_user.id]
        if "state" not in USER_INFO:
            mess = "Странное поведение"
            self.bot.send_message(message.from_user.id,
                                  mess,
                                  reply_markup=self.select_markup(message))
        elif USER_INFO["state"] == "INITIALIZE_USER":
            if message.text in ["Да ✔️", 'Отправить местоположение 🌎']:
                USER_INFO["state"] = "RECOMMENDATION"
                mess = 'Выбери, какие рекомендации ты хочешь получить'
                self.bot.send_message(message.from_user.id,
                                      mess,
                                      reply_markup=self.rec_markup,
                                      parse_mode='Markdown')
            elif message.text == 'Указать адрес 🗺️':
                USER_INFO["state"] = "INITIALIZE_USER"
                mess = 'Введите адрес в формате x.x, x.x (для координат)'
                ' или в формате Город, Улица, Номер дома (через запятую)'
                self.bot.send_message(message.from_user.id,
                                      mess,
                                      parse_mode='Markdown')
        else:
            mess = "Вы не можете воспользоваться этой командой, \
            пока не завершите текущий процесс."
            self.bot.send_message(message.from_user.id,
                                  mess,
                                  reply_markup=self.select_markup(message))

    def read_address(self, message, flag_mess=False):
        USER_INFO = USER_INFO_AGGREGATOR[message.from_user.id]
        if "state" not in USER_INFO:
            mess = "Странное поведение"
            self.bot.send_message(message.from_user.id,
                                  mess,
                                  reply_markup=self.select_markup(message))
        elif USER_INFO["state"] in ["RECOMMENDATION", "INITIALIZE_USER"]:
            if flag_mess:
                if message.location is not None:
                    lon = message.location.longitude
                    lat = message.location.latitude
                    USER_INFO['lon'] = lon
                    USER_INFO['lat'] = lat

                    flag, mess = utils.get_address_from_coords((lon, lat))

                    if flag:
                        self.bot.send_message(message.from_user.id,
                                              'Твой адрес:' + mess + '?',
                                              reply_markup=self.reply_markup)
                    else:
                        self.bot.send_message(
                            message.from_user.id,
                            mess,
                            reply_markup=self.loc_mark)
                else:
                    self.bot.send_message(message.from_user.id,
                                          'Не могу определить твою локацию 😿',
                                          reply_markup=self.loc_mark)
            else:
                try:
                    address = message.text.split(',')
                    address = list(map(lambda x: x.strip(), address))
                    if len(address) == 2:

                        flag, mess = utils.get_address_from_coords(address)
                        print('else:', flag, mess)

                        if flag:
                            self.bot.send_message(
                                message.from_user.id,
                                'Твой адрес:' + mess + '?',
                                reply_markup=self.reply_markup)
                        else:
                            self.bot.send_message(message.from_user.id,
                                                  mess,
                                                  reply_markup=self.loc_mark)
                except Exception:
                    self.bot.send_message(message.from_user.id,
                                          'Я не понимаю твою команду :(',
                                          parse_mode='Markdown')
        else:
            mess = "Странное поведение"
            self.bot.send_message(message.from_user.id,
                                  mess,
                                  reply_markup=self.select_markup(message))

    def select_recommendation(self, message):
        USER_INFO = USER_INFO_AGGREGATOR[message.from_user.id]
        if "state" not in USER_INFO:
            mess = "Странное поведение"
            self.bot.send_message(message.from_user.id,
                                  mess,
                                  reply_markup=self.select_markup(message))
        elif USER_INFO["state"] == "RECOMMENDATION":
            if message.text not in RECNAME_TO_ITEM_TYPE:
                self.bot.send_message(message.from_user.id,
                                      'Этот тип рекомендаций ещё недоступен',
                                      reply_markup=self.rec_markup,
                                      parse_mode='Markdown')
            else:
                USER_INFO["state"] = "SHOW_RECOMMENDATION"
                self.bot.send_message(message.from_user.id,
                                      'Вы выбрали ' + message.text.lower(),
                                      reply_markup=self.check_rec_markup,
                                      parse_mode='Markdown')
                m_text = message.text
                USER_INFO['recommender_type'] = RECNAME_TO_ITEM_TYPE[m_text]
        else:
            mess = "Вы не можете воспользоваться этой командой, \
            пока не завершите текущий процесс"
            self.bot.send_message(message.from_user.id,
                                  mess,
                                  reply_markup=self.select_markup(message))

    def show_recommendation(self, message):
        USER_INFO = USER_INFO_AGGREGATOR[message.from_user.id]
        USER_INFO['user_id'] = message.from_user.id
        if 'lon' not in USER_INFO or 'lat' not in USER_INFO:
            self.bot.send_message(message.from_user.id,
                                  'Я не знаю, где ты находишься',
                                  parse_mode='Markdown',
                                  reply_markup=self.location_markup)
        else:
            if 'recommender_type' not in USER_INFO:
                self.bot.send_message(message.from_user.id,
                                      'Вы не выбрали тип рекомендаций',
                                      parse_mode='Markdown',
                                      reply_markup=self.rec_markup)
            elif USER_INFO['recommender_type'] == utils.ItemType.FOOD:
                recommender = self.food_recomender
            elif USER_INFO['recommender_type'] == utils.ItemType.SHOP:
                recommender = self.shop_recomender
            else:
                self.bot.send_message(message.from_user.id,
                                      'Этот тип рекомендаций ещё не доступен',
                                      parse_mode='Markdown')

            if recommender is not None:
                recommended_items = recommender.recommend(
                    USER_INFO,
                    user_history_limit=20,
                    light_recommender_limit=400,
                    heavy_recommender_limit=15,
                    blender_limit=5)
                self.write_recommendations(recommended_items, message)

    def gen_markup(self):
        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(InlineKeyboardButton("👍", callback_data="react_yes"),
                   InlineKeyboardButton("👎", callback_data="react_no"))
        return markup

    def write_recommendations(self, recommended_items, message):
        for i, place in enumerate(recommended_items):
            d = utils.dist_to_str(place.dist)
            msg_sent = self.bot.send_message(
                    message.from_user.id,
                    f'#{i+1}: **{place.name}**\n'
                    f'- адрес: {place.address}\n'
                    f'- расстояние от Вас: {d}\n'
                    f'- рейтинг: {place.get_rating() or "Не указан"}',
                    parse_mode='Markdown', reply_markup=self.gen_markup()
                )
            REC_HIST[message.from_user.id][msg_sent.message_id] = place.item_id

        self.bot.send_message(message.from_user.id,
                              'Ещё варианты? 😎',
                              parse_mode='Markdown')
