# Телеграм-бот v.004
# Ссылка на бот: t.me/Tyurina_Elena_1MD15_bot

import random
import json
from gettext import find
from io import BytesIO

import telebot  # pyTelegramBotAPI 4.3.1
from telebot import types
import requests
import bs4
import BotGames # бот-игры
from menuBot import Menu
import DZ
# import googletrans
# from googletrans import Translator

bot = telebot.TeleBot('5144148734:AAEL1qxIJIXxsHP7lkCwtL9Pb4cLHE3a4RM')

# функция, обрабатывающая команды
@bot.message_handler(commands=["start"])
def start(message, res=False):
    txt_message = f"Привет, {message.from_user.first_name}! Я - текстовый бот для курса " \
                  f"программирования на языке Пайтон!"
    bot.send_message(message.chat.id, text=txt_message, reply_markup=Menu.getMenu("Главное меню").markup)

# Получение сообщений от юзера
@bot.message_handler(content_types=['text'])
def get_text_message(message):
    global game21

    chat_id = message.chat.id
    ms_text = message.text

    result = goto_menu(chat_id, ms_text) # попробуем использовать текст, как команду меню, и войти в меню
    if result == True:
        return # вошли в подменю, обработка не требуется

    if Menu.cur_menu != None and ms_text in Menu.cur_menu.buttons:

        if ms_text == ms_text == "Помощь":
            send_help(chat_id)

        elif ms_text == "Прислать собаку":
            bot.send_photo(chat_id, photo=get_dogURL(), caption="Вот тебе собачка!")

        elif ms_text == "Прислать анекдот":
            bot.send_message(chat_id, text=get_anekdot())

        elif ms_text == "Прислать фильм":
            send_film(chat_id)

        elif ms_text == "Угадай, кто?":
            get_ManOrNot(chat_id)

        elif ms_text == "Карту!":
            if game21 == None:
                goto_menu(chat_id, "Выход")
                return

            text_game = game21.get_cards(1)
            bot.send_media_group(chat_id, media=getMediaCards(game21)) # получить и отправить изображение карты
            bot.send_message(chat_id, text=text_game)

            if game21.status != None: #выход, если игра закончена
                goto_menu(chat_id, "Выход")
                return

        elif ms_text == "Стоп!":
            game21 = None
            goto_menu(chat_id, "Выход")
            return

        elif ms_text == "Камень":
            play_stone(bot, chat_id)

        elif ms_text == "Ножницы":
            play_scissors(bot, chat_id)

        elif ms_text == "Бумага":
            play_paper(bot, chat_id)

        elif ms_text == "Задание 1":
            DZ.dz1(bot, chat_id)

        elif ms_text == "Задание 2":
            DZ.dz2(bot, chat_id)

        elif ms_text == "Задание 3":
            DZ.dz3(bot, chat_id)

        elif ms_text == "Задание 4-5":
            DZ.dz45(bot, chat_id)

        elif ms_text == "Задание 6":
            DZ.dz6(bot, chat_id)

        elif ms_text == "Задание 7":
            DZ.dz7(bot, chat_id)

        elif ms_text == "Задание 8":
            DZ.dz8(bot, chat_id)

        elif ms_text == "Задание 9":
            DZ.dz9(bot, chat_id)

        elif ms_text == "Generate insult":
            bot.send_message(chat_id, text=gen_insult())

        elif ms_text == "Мудрость дня":
            bot.send_message(chat_id, text=get_wolf_quote() + "\U0001F43A")

    else:
        bot.send_message(chat_id, text="Извините, я не понимаю вашу команду: " + ms_text)
        goto_menu(chat_id, "Главное меню")

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call): # передать параметры
    pass

def goto_menu(chat_id, name_menu): # получение нужного элемента меню
    if name_menu == "Выход" and Menu.cur_menu != None and Menu.cur_menu.parent != None:
        target_menu = Menu.getMenu(Menu.cur_menu.parent.name)
    else:
        target_menu = Menu.getMenu(name_menu)

    if target_menu != None:
        bot.send_message(chat_id, text=target_menu.name, reply_markup=target_menu.markup)

        if target_menu.name == "Игра в 21":
            global game21
            game21 = BotGames.Game21() #новый экземпляр игры
            text_game = game21.get_cards(2) # просим 2 карты
            bot.send_media_group(chat_id, media=getMediaCards(game21))
            bot.send_message(chat_id, text=text_game)

        return True
    else:
        return False

def getMediaCards(game21):
    medias = []
    for url in game21.arr_cards_URL:
        medias.append(types.InputMediaPhoto(url))
    return medias

def send_help(chat_id):
    global bot
    bot.send_message(chat_id, text="Автор: Тюрина Елена")
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="Напишите автору",
                                      url="https://t.me/helenatyurina")
    markup.add(btn1)
    img = open('1МД15_Тюрина_Елена.jpg', 'rb')
    bot.send_photo(chat_id, img, reply_markup=markup)

def send_film(chat_id):
    film = get_randomFilm()
    info_str = f"<b>{film['Наименование']}</b>\n" \
               f"Год: {film['Год']}\n" \
               f"Страна: {film['Страна']}</b>\n" \
               f"Жанр: {film['Жанр']}\n" \
               f"Продолжительность: {film['Продолжительность']}"
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="Трейлер", url=film["Трейлер_url"])
    btn2 = types.InlineKeyboardButton(text="Смотреть онлайн", url=film["фильм_url"])
    markup.add(btn1, btn2)
    bot.send_photo(chat_id, photo=film['Обложка_url'], caption=info_str, parse_mode='HTML',
                   reply_markup=markup)

def get_anekdot():
    array_anekdots = []
    req_anek = requests.get('http://anekdotme.ru/random')
    if req_anek.status_code == 200:
        soup = bs4.BeautifulSoup(req_anek.text, "html.parser")
        result_find = soup.select('.anekdot_text')
        for result in result_find:
            array_anekdots.append(result.getText().strip())
    if len(array_anekdots) > 0:
        return array_anekdots[0]
    else:
        return ""

def get_dogURL():
    url = ""
    req = requests.get('https://random.dog/woof.json')
    if req.status_code == 200:
        r_json = req.json()
        url = r_json['url']
    return url

def get_ManOrNot(chat_id):
    global bot

    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="Проверить", url="https://vc.ru/dev/58543-thispersondoesnotexist-sayt-generator-realistichnyh-lic")
    markup.add(btn1)

    req = requests.get("https://thispersondoesnotexist.com/image", allow_redirects=True)
    if req.status_code == 200:
        img = BytesIO(req.content)
        bot.send_photo(chat_id, photo=img, reply_markup=markup, caption="Этот человек реален?")

def get_randomFilm():
    url = 'https://randomfilm.ru/'
    infoFilm = {}
    req_film = requests.get(url)
    soup = bs4.BeautifulSoup(req_film.text, "html.parser")
    result_find = soup.find ('div', align="center", style="width: 100%")
    infoFilm["Наименование"] = result_find.find("h2").getText()
    names = infoFilm["Наименование"].split(" / ")
    infoFilm["Наименование_rus"] = names[0].strip()
    if len(names) > 1:
        infoFilm["Наименование_eng"] = names[1].strip()

    images = []
    for img in result_find.findAll('img'):
        images.append(url + img.get('src'))
    infoFilm["Обложка_url"] = images[0]
    details = result_find.findAll('td')
    infoFilm["Год"] = details[0].contents[1].strip()
    infoFilm["Страна"] = details[1].contents[1].strip()
    infoFilm["Жанр"] = details[2].contents[1].strip()
    infoFilm["Продолжительность"] = details[3].contents[1].strip()
    infoFilm["Режиссёр"] = details[4].contents[1].strip()
    infoFilm["Актёры"] = details[5].contents[1].strip()
    infoFilm["Трейлер_url"] = url + details[6].contents[0]["href"]
    infoFilm["фильм_url"] = url + details[7].contents[0]["href"]

    return infoFilm


def get_wolf_quote():
    array_quotes = []
    req_quote = requests.get('https://statusas.ru/citaty-i-aforizmy/citaty-pro-zhivotnyx-i-zverej/citaty-i-memy-volka-auf.html')
    soup = bs4.BeautifulSoup(req_quote.text, "html.parser")
    result_find = soup.find('div', class_='p-15 full-image').find('div', class_='entry-content').select('p')
    for result in result_find:
        if (result.getText() != "") and not ("http" in result.getText()):
            array_quotes.append(result.getText().strip())
    count = random.randint(1, len(array_quotes)-1)
    return array_quotes[count]

def gen_insult():
        contents = requests.get('https://evilinsult.com/generate_insult.php?lang=en&type=json').json()
        # translator = Translator()
        # insult = translator.translate(contents['insult'], dest='ru')
        insult = contents['insult']
        return insult

def play_stone(bot, chat_id):
    all_actions = ["камень", "ножницы", "бумага"]
    action = random.choice (all_actions)
    if action == "камень":
        bot.send_message(chat_id, text="Камень")
        bot.send_message(chat_id, text="Ничья!")
    elif action == "ножницы":
        bot.send_message(chat_id, text="Ножницы")
        bot.send_message(chat_id, text="Вы победили!")
    else:
        bot.send_message(chat_id, text="Бумага")
        bot.send_message(chat_id, text="Вы проиграли! ")

def play_scissors(bot, chat_id):
    all_actions = ["камень", "ножницы", "бумага"]
    action = random.choice(all_actions)
    if action == "камень":
        bot.send_message(chat_id, text="Камень")
        bot.send_message(chat_id, text="Вы проиграли! ")
    elif action == "ножницы":
        bot.send_message(chat_id, text="Ножницы")
        bot.send_message(chat_id, text="Ничья! ")
    else:
        bot.send_message(chat_id, text="Бумага")
        bot.send_message(chat_id, text="Вы победили! ")

def play_paper(bot, chat_id):
    all_actions = ["камень", "ножницы", "бумага"]
    action = random.choice (all_actions)
    if action == "камень":
        bot.send_message(chat_id, text="Камень")
        bot.send_message(chat_id, text="Вы победили! ")
    elif action == "ножницы":
        bot.send_message(chat_id, text="Ножницы")
        bot.send_message(chat_id, text="Вы проиграли! ")
    else:
        bot.send_message(chat_id, text="Бумага")
        bot.send_message(chat_id, text="Ничья! ")


bot.polling(none_stop=True, interval=0)  # Запускаем бота

print()
