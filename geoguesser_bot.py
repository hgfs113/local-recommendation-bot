from telebot import TeleBot, types
from core import recommender, state_diagram


TOKEN = '6109688099:AAGJZuj0kVPEdjTZgaO27O5ZF-ey2WfFMis'
BOT_USERNAME = '@local_recommendation_bot'
CANDIDATES_HOLDER = recommender.CandidatesHolder()
EMBEDDINGS_HOLDER = recommender.EmbeddingsHolder()
HISTORY_PATH = 'storage/history'
FEEDBACK_EVENT_PROCESSOR = recommender.FeedbackEventProcessor(HISTORY_PATH)

food_recomender = recommender.Recommender(
    recommender.ItemType.FOOD,
    CANDIDATES_HOLDER,
    EMBEDDINGS_HOLDER,
    FEEDBACK_EVENT_PROCESSOR)
shop_recomender = recommender.Recommender(
    recommender.ItemType.SHOP,
    CANDIDATES_HOLDER,
    EMBEDDINGS_HOLDER,
    FEEDBACK_EVENT_PROCESSOR)

bot = TeleBot(token=TOKEN)
check_state = state_diagram.StateDiagram(bot, food_recomender, shop_recomender)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data.startswith("react"):
        # reccomendation reaction
        if call.message.id in state_diagram.REC_HIST[call.from_user.id]:
            user_id = call.from_user.id
            mess_id = call.message.id
            item_id = state_diagram.REC_HIST[user_id][mess_id]
            rating_good = 1 * (call.data == "react_yes")
            CANDIDATES_HOLDER.add_rating(
                    item_id=item_id,
                    rating_good=(call.data == "react_yes")
            )
            FEEDBACK_EVENT_PROCESSOR.write_user_item_rating(
                    user_id=user_id,
                    item_id=item_id,
                    rating_good=rating_good
            )
            bot.answer_callback_query(call.id, "Оценка записана")
            del state_diagram.REC_HIST[call.from_user.id][call.message.id]
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


@bot.message_handler(commands=['add_geo', 'back', 'clear_history'])
def add_geo(message):
    check_state.bot_answer(message)


@bot.message_handler(content_types=['location'])
def handle_location(message):
    check_state.read_address(message, True)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    check_state.bot_answer(message)


def main():
    food_path = 'PlacesDatabase/food_places'
    shop_path = 'PlacesDatabase/shop_places'
    CANDIDATES_HOLDER.update(
        food_path=food_path,
        shop_path=shop_path)
    EMBEDDINGS_HOLDER.update(
        food_path=food_path,
        shop_path=shop_path)
    bot.polling(none_stop=True, interval=0)
