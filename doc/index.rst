.. local-recomendation-bot documentation master file, created by
   sphinx-quickstart on Sun May 21 01:59:09 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Документация проекта local-recomendation-bot
===================================================

local-recomendation-bot это бот для телеграмма, который рекомендует различные категории досуга на основании вашего местоположения и предыдущих выборов.

**Возможности**

- Получение геолокации встроенным способом через телеграмм или через текстовый адресс.
- Рекомендации по базе данных на основании расстояния
- Возможность ставить оценки рекомендациям, которые будут учитываться при дальнейших рекомендациях

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Содержание
==========

core.utils.Item
----------------------------------------------
.. autoclass:: core.utils.Item

core.utils.RecommendItem
----------------------------------------------
.. autoclass:: core.utils.RecommendItem

core.recommender.CandidatesHolder
----------------------------------------------
.. autoclass:: core.recommender.CandidatesHolder
   :members:

core.recommender.Recommender
----------------------------------------------
.. autoclass:: core.recommender.Recommender
   :members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
