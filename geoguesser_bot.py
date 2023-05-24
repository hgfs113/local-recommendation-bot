from telebot import TeleBot, types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from core import recommender, utils, state_diagram
from collections import defaultdict
import gettext


TOKEN = '6109688099:AAGJZuj0kVPEdjTZgaO27O5ZF-ey2WfFMis'
BOT_USERNAME = '@local_recommendation_bot'
CANDIDATES_HOLDER = recommender.CandidatesHolder()

food_recomender = recommender.FoodRecommender(
    recommender.ItemType.FOOD,
    CANDIDATES_HOLDER)
shop_recomender = recommender.ShopRecommender(
    recommender.ItemType.SHOP,
    CANDIDATES_HOLDER)

bot = TeleBot(token=TOKEN)
check_state = state_diagram.StateDiagram(bot, food_recomender, shop_recomender)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data.startswith("react"):
        # reccomendation reaction
        if call.message.id in REC_HIST[call.from_user.id]:
            place_id = REC_HIST[call.from_user.id][call.message.id]
            CANDIDATES_HOLDER.add_rating(
                    item_id=place_id,
                    rating_good=(call.data == "react_yes")
            )
            bot.answer_callback_query(call.id, "Оценка записана")
            del REC_HIST[call.from_user.id][call.message.id]
        else:
            bot.answer_callback_query(call.id, "Вы уже оставили оценку")


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton('👋 Поздороваться')
    markup.add(btn)
    bot.send_message(message.from_user.id,
                     '👋 Привет! Я твой бот c географическими рекомендациями!',
                     reply_markup=markup)


@bot.message_handler(commands=['add_geo', 'back'])
def add_geo(message):
    check_state.bot_answer(message)


@bot.message_handler(content_types=['location'])
def handle_location(message):
    check_state.read_address(message, True)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    check_state.bot_answer(message)


if __name__ == "__main__":
    CANDIDATES_HOLDER.update(
        food_path='PlacesDatabase/food_places.csv',
        shop_path='PlacesDatabase/shopping_v1.csv')
    bot.polling(none_stop=True, interval=0)
