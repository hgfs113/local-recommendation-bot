import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

def get_address_from_coords(coords):
    PARAMS = {
        "apikey": "4e6e6cda-7f5c-417b-a6d0-90a5b6445055",
        "format": "json",
        "lang": "ru_RU",
        "kind": "house",
        "geocode": coords
    }

    try:
        r = requests.get(url="https://geocode-maps.yandex.ru/1.x/", params=PARAMS)
        json_data = r.json()
        address_str = json_data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["metaDataProperty"][
            "GeocoderMetaData"]["AddressDetails"]["Country"]["AddressLine"]
        return address_str

    except Exception as e:
        return "Не могу определить адрес по этой локации/координатам.\n\nОтправь мне локацию или координаты (долгота, широта):"


def start(update, context):
    print('Start!')
    update.message.reply_text('Привет! Это тестовый бот для определения твоего адреса. Отправь мне локацию или координаты (долгота, широта):')

def text(update, context):
    print('Text!')
    coords = update.message.text
    address_str = get_address_from_coords(coords)
    update.message.reply_text(address_str)

def location(update, context):
    print('Location!')
    message = update.message
    current_position = (message.location.longitude, message.location.latitude)
    coords = f"{current_position[0]},{current_position[1]}"
    address_str = get_address_from_coords(coords)
    update.message.reply_text(address_str)

def main():
    print('Main!')
    updater = Updater("5921166856:AAE0n2fsSAdjDdde2o8EmYUfKNKw4Nrom9E")#, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text, text))
    dispatcher.add_handler(MessageHandler(Filters.location, location))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()