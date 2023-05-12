from telebot import types
import telebot

from typing import Final
from core import utils, recommender


TOKEN: Final = '6109688099:AAGJZuj0kVPEdjTZgaO27O5ZF-ey2WfFMis'
BOT_USERNAME: Final = '@local_recommendation_bot'
USER_DICT = dict()


bot = telebot.TeleBot(token=TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("👋 Поздороваться")
    markup.add(btn1)
    bot.send_message(message.from_user.id,
                     "👋 Привет! Я твой бот c географическими рекомендациями!",
                     reply_markup=markup)


@bot.message_handler(commands=['add_geo'])
def add_geo(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text="Отправить местоположение",
                                request_location=True)
    btn2 = types.KeyboardButton(text="Указать адрес")
    btn3 = types.KeyboardButton('Вернуться назад')
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.from_user.id,
                     "Нажми на кнопку и передай мне свое местоположение",
                     reply_markup=markup)


@bot.message_handler(content_types=["location"])
def handle_location(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if message.location is not None:
        btn1 = types.KeyboardButton(text="Да")
        btn2 = types.KeyboardButton(text="Нет")
        markup.add(btn1, btn2)

        lon, lat = message.location.longitude, message.location.latitude
        USER_DICT['lon'] = lon
        USER_DICT['lat'] = lat

        flag, mess = utils.get_address_from_coords((lon, lat))

        if flag:
            bot.send_message(message.from_user.id,
                             "Твой адрес:" + mess + "?",
                             reply_markup=markup)
        else:
            bot.send_message(message.from_user.id,
                             mess,
                             reply_markup=markup)

    else:
        bot.send_message(message.from_user.id,
                         'Не могу определить твою локацию :(',
                         reply_markup=markup)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if1 = '👋 Поздороваться'
    if2 = 'Вернуться назад'
    if (message.text == if1) | (message.text == if2):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Как пользоваться ботом?')
        btn2 = types.KeyboardButton('СТАРТ')
        btn3 = types.KeyboardButton('Наш репозиторий')
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.from_user.id,
                         '❓ Что вас интересует?',
                         reply_markup=markup)

    elif message.text == 'Как пользоваться ботом?':
        mess = r"""Воспользуйтесь командой /add\_geo,
        чтобы добавить ваше местонахождение"""
        bot.send_message(message.from_user.id,
                         mess,
                         parse_mode='MarkdownV2')
        
    elif message.text == 'СТАРТ':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton(text="Отправить местоположение",
                                    request_location=True)
        btn2 = types.KeyboardButton(text="Указать адрес")
        btn3 = types.KeyboardButton('Вернуться назад')
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.from_user.id,
                     "Нажми на кнопку и передай мне свое местоположение",
                     reply_markup=markup)

    elif message.text == 'Отправить местоположение':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Рестораны')
        btn2 = types.KeyboardButton('Парки')
        btn3 = types.KeyboardButton('Театры')
        btn4 = types.KeyboardButton('Музеи')
        btn5 = types.KeyboardButton('Всё')
        markup.add(btn1, btn2, btn3, btn4, btn5)
        bot.send_message(message.from_user.id,
                         'Выбери, какие рекомендации ты хочешь получить',
                         reply_markup=markup,
                         parse_mode='Markdown')
        
    elif message.text.startswith('Введите адрес в формате'):
        print('Введите адрес в формате... TODO')

    elif message.text == 'Наш репозиторий':
        mess = 'Детали нашего проекта вы можете посмотреть по '
        link = '[ссылке](https://github.com/hgfs113/local-recommendation-bot)'
        bot.send_message(message.from_user.id,
                         mess + link,
                         parse_mode='Markdown')

    elif message.text == "Указать адрес":
        mess = """Введите адрес в формате x.x, x.x (для координат)
        или в формате Город, Улица, Номер дома (через запятую)"""
        bot.send_message(message.from_user.id,
                         mess,
                         parse_mode='Markdown')

    elif message.text in ['Рестораны', 'Парки', 'Театры', 'Музеи', 'Всё']:
        USER_DICT[message.from_user.id] = message.text
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Посмотреть варианты')
        btn2 = types.KeyboardButton('Вернуться назад')
        markup.add(btn1, btn2)
        bot.send_message(message.from_user.id,
                         "Вы выбрали " + message.text.lower(),
                         reply_markup=markup,
                         parse_mode='Markdown')

    elif message.text == "Посмотреть варианты":
        if 'lon' not in USER_DICT or 'lat' not in USER_DICT:
            bot.send_message(message.from_user.id,
                             'Я не знаю, где ты находишься',
                             parse_mode='Markdown')
        else:
            nearest_places = recommender.recommend(USER_DICT)
            for i, place in enumerate(nearest_places):
                p, d = place
                d = utils.dist_to_str(d)
                bot.send_message(message.from_user.id,
                                 f'#{i+1}: {p.get_name()},\
                                 адрес: {p.get_address()}\
                                 расстояние от Вас: {d}',
                                 parse_mode='Markdown')
            bot.send_message(message.from_user.id,
                             'Ещё варианты',
                             parse_mode='Markdown')
            
    elif message.text == "Ещё варианты":
        print('Ещё варианты... TODO')

    else:
        try:
            address = message.text.split(',')
            address = list(map(lambda x: x.strip(), address))
            if len(address) == 2:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                btn1 = types.KeyboardButton(text="Да")
                btn2 = types.KeyboardButton(text="Нет")
                markup.add(btn1, btn2)

                flag, mess = utils.get_address_from_coords(address)
                print('else:', flag, mess)

                if flag:
                    bot.send_message(message.from_user.id,
                                     "Твой адрес:" + mess + "?",
                                     reply_markup=markup)
                else:
                    bot.send_message(message.from_user.id,
                                     mess,
                                     reply_markup=markup)
        except Exception:
            bot.send_message(message.from_user.id,
                             'Я не понимаю твою команду :(',
                             parse_mode='Markdown')


bot.polling(none_stop=True, interval=0)
