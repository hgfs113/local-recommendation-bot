from telebot import types
import telebot


bot = telebot.TeleBot('6109688099:AAGJZuj0kVPEdjTZgaO27O5ZF-ey2WfFMis')


@bot.message_handler(commands=['start'])
def start(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("👋 Поздороваться")
    markup.add(btn1)
    bot.send_message(message.from_user.id,
                     "👋 Привет! Я твой бот c географическими рекомендациями!",
                     reply_markup=markup)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):

    if message.text == '👋 Поздороваться':
        # создание новых кнопок
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Как пользоваться ботом?')
        btn2 = types.KeyboardButton('Выбрать тип рекомендаций')
        btn3 = types.KeyboardButton('Наш репозиторий')
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.from_user.id,
                         '❓ Что вас интересует?',
                         reply_markup=markup)  # ответ бота

    elif message.text == 'Как пользоваться ботом?':
        bot.send_message(message.from_user.id,
                         'Воспользуйтесь командой /add_geo, чтобы добавить ваше местонахождение.')

    elif message.text == 'Выбрать тип рекомендаций':
        bot.send_message(message.from_user.id,
                         'Здесь будет возможность выбрать тип рекомендации',
                         parse_mode='Markdown')

    elif message.text == 'Наш репозиторий':
        str1 = 'Детали нашего проекта вы можете посмотреть по '
        str2 = '[ссылке](https://github.com/hgfs113/local-recommendation-bot)'
        bot.send_message(message.from_user.id,
                         str1 + str2,
                         parse_mode='Markdown')


bot.polling(none_stop=True, interval=0)  # обязательная для работы бота часть
