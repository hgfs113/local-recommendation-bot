from telebot import types
import telebot

from typing import Final
import requests


TOKEN: Final = '6109688099:AAGJZuj0kVPEdjTZgaO27O5ZF-ey2WfFMis'
BOT_USERNAME: Final = '@local_recommendation_bot'


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
    btn2 = types.KeyboardButton('Вернуться назад')
    markup.add(btn1, btn2)
    bot.send_message(message.from_user.id,
                     "Нажми на кнопку и передай мне свое местоположение",
                     reply_markup=markup)


@bot.message_handler(content_types=["location"])
def handle_location(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if message.location is not None:
        PARAMS = {
            "apikey": "4e6e6cda-7f5c-417b-a6d0-90a5b6445055",
            "format": "json",
            "lang": "ru_RU",
            "kind": "house",
            "geocode": "%s, %s" % (message.location.longitude,
                                   message.location.latitude),
        }

        try:
            r = requests.get(url="https://geocode-maps.yandex.ru/1.x/",
                             params=PARAMS)
            json_data = r.json()
            address_str = json_data["response"]["GeoObjectCollection"][
                "featureMember"][0]["GeoObject"]["metaDataProperty"][
                "GeocoderMetaData"
            ]["AddressDetails"]["Country"]["AddressLine"]
            bot.send_message(message.from_user.id,
                             address_str,
                             reply_markup=markup)

        except Exception:
            mess = """Не могу определить адрес по этой локации/координатам.\n\
            Отправь мне локацию или координаты (долгота, широта):"""
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
        btn2 = types.KeyboardButton('Выбрать тип рекомендаций')
        btn3 = types.KeyboardButton('Наш репозиторий')
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.from_user.id,
                         '❓ Что вас интересует?',
                         reply_markup=markup)

    elif message.text == 'Как пользоваться ботом?':
        mess = """Воспользуйтесь командой /add_geo,
        чтобы добавить ваше местонахождение"""
        bot.send_message(message.from_user.id,
                         mess,
                         parse_mode='MarkdownV2')

    elif message.text == 'Выбрать тип рекомендаций':
        bot.send_message(message.from_user.id,
                         'Здесь будет возможность выбрать тип рекомендации.',
                         parse_mode='Markdown')

    elif message.text == 'Наш репозиторий':
        mess = 'Детали нашего проекта вы можете посмотреть по '
        link = '[ссылке](https://github.com/hgfs113/local-recommendation-bot)'
        bot.send_message(message.from_user.id,
                         mess + link,
                         parse_mode='Markdown')

    else:
        bot.send_message(message.from_user.id, 'Я не понимаю твою команду :(',
                         parse_mode='Markdown')


bot.polling(none_stop=True, interval=0)
