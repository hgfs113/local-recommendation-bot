# local-recomendation-bot

## Постановка задачи

Разрабатываем телеграм-бот, который будет рекомендовать варианты досуга в зависимости от местонахождения пользователя. Будет реализована возможность настроить рекомендации под себя.

## Возможности

Персонализированная рекомендательная система досуговых мероприятий, ресторанов, культурных объектов и т.д города-героя Москва.

## Запуск

Убедитесь, что установлены все зависимости
```python3 -m pip install -r requiremets.txt```

Бот запускается командой
```python3 geoguesser_bot.py```

## Тестирование

При тестировании используется модуль `pytest`. Тесты запускаются командой:
```pytest core/test_ut.py```

## Выгонка документации

```sphinx-build doc _build```

## Локализация

Созданиеs:
```pybabel extract --input-dirs=. --output-file=messages.pot```
```mkdir -p locale/en/LC_MESSAGES```
```mv locale/en/LC_MESSAGES/locale.po locale/en/LC_MESSAGES/messages.mo```
Чтобы сделать `*.mo` генерат: ```pybabel compile -d locale --locale en```

**UI**

Окно 1 (старт).
- Отправить геолокацию
- Указать адрес

На кнопку "Отправить геолокацию" желательно научится вводить, принимать и обрабатывать геолокацию, которую предоставляет телеграмм. На кнопку "Указать адрес" желательно уметь парсить адрес, введённый в ручную.

Окно 2 (выбор).
- Показать ближайшие рестораны
- Показать ближайшие парки
- Показать ближайшие театры
- Показать ближайшие музеи
- Показать всё
- Назад

На кнопки "Показать ..." переходим в окно рекомендаций. На кнопку "Назад" переходим в окно 1.

Окно рекомендаций.
- Карточка 1
    Нравится / Не нравится
- Карточка 2
    Нравится / Не нравится
...
- Карточка N
    Нравится / Не нравится
- Далее
- Назад

На кнопку "Далее" показывается ещё N карточек. На кнопку "Назад" переходим в окно 2.

**UX**

Рекомендательная система должна иметь кратковременную и долговременную память. Кротковременная память: рестораны подбираются по предпочтениям в текущей сессии (прим. если в текущей сессии нравятся рестораны с итальянской кухней, то рекомендуем их 80/20, но в долговременной истории релаксируем рекомендации до 50% разнообразных кухонь и 50% итальянских). Пример долговременной памяти: запомнаем стоимость ресторанов и рекомендуем в основном из его сегмента. Другой пример: если пользователь кликает в основном на парки, то в кнопке "показать всё" будет больше парков.

**Backend**

Рекомендации разбиваются на несколько условно параллельных вертикалей, каждая из которых составляет список релевантных объектов (пример - "рестораны", "театры", "парки"). Основная логика набора рекомандаций общая, но должна быть определённая степень свободы внутри каждой вертикали. Пример: для ресторанов смотрим на время работы, у театров - на время спектаклей.

В UI должен быть выбор - рекоммендуй мне что-то конкретное (прим. только рестораны), или рекоммендуй мне всё подряд. Во втором случае замешиваем ответы с каждой вертикали. Например, отправляем пачку из 1 рекомендации с каждой вертикали, замешанную по порядку, или учитываем интересы пользователя и строим квотированную пачку (прим. 10% парки, 30% театры, 60% рестораны, размер пачки можно поднять до 20).

**Про неперсональные рекоммендации**

Холодную ленту можно набирать замешиванием 3 рекомендации с каждой вертикали (через одну), внутри каждой вертикали можно брать топ по рейтингу + поддержать разнообразие ценовой категории для ресторанов (р, рр, ррр). Информация есть в Я.Картах, для которой есть API.

**Поход в API Я.Карт**

По крону запускается таска, которая ходит в Я.Карты и собирает полный список заведений города. Далее приписывается версия (прим. текущее дата и время), кладётся на жёсткий диск (в облако или локально) и в оперативную память машинки. Финальный шаг процедуры - обновление актуальной версии, после чего рекоммендер ходит уже в него.
