<img src="https://github.com/ICQ-BOTS/vaska_bot/blob/main/vaska.png" width="100" height="100">

# Васька

[Васька](https://icq.im/vaska_bot)

Старт:
1. Установка всех зависимостей 
```bash
pip3 install -r requirements.txt
```

2. Запуск space tarantool.
```bash
tarantoolctl start vaska.lua
```
> Файл из папки scheme нужно перекинуть в /etc/tarantool/instances.available


3. Загрузка данных в БД
Загрузка происходит командами боту в личные сообщения: 
* /addPhrases \*Фразы\*
* /addAnswer \*Фразы\*
Смотреть функции:
* add_phrases
* add_answer
* sticker


4. Вставляем свои данные в vaska_bot.py
Вводим токен бота и токен [wolframalpha](https://products.wolframalpha.com/api/)


5. Запуск бота!
```bash
python3 vaska_bot.py
```