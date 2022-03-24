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

bot = telebot.TeleBot('5144148734:AAEL1qxIJIXxsHP7lkCwtL9Pb4cLHE3a4RM')

# функция, обрабатывающая команды
@bot.message_handler(commands=["start"])
def start(message, res=False):
    txt_message = f"Привет, {message.from_user.first_name}! Я - текстовый бот для курса " \
                  f"программирования на языке Пайтон!"
    bot.send_message(chat_id, text=txt_message, reply_markup=Menu.getMenu("Главное меню").markup)
    # chat_id = message.chat.id
    #
    # markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # btn1 = types.KeyboardButton("👋 Главное меню")
    # btn2 = types.KeyboardButton("❓ Помощь")
    # markup.add(btn1, btn2)
    #
    # bot.send_message(chat_id,
    #                  text="Привет, {0.first_name}! Я - текстовый бот для курса программирования "
    #                       "на языке Пайтон!".format(message.from_user), reply_markup=markup)

# Получение сообщений от юзера
@bot.message_handler(content_types=['text'])
def get_text_message(message):
    global game21

    chat_id = message.chat.id
    ms_text = message.text

    result = goto_menu(chat_id,ms_text) # попробуем использовать текст, как команду меню, и войти в меню
    if result == True:
        return #вошли в подменю, обработка не требуется

    if Menu.cur_menu != None and ms_text in Menu.cur_menu.buttons:

        if ms_text == ms_text == "Помощь":
            send_help(chat_id)

        elif ms_text == "Прислать собаку":
            bot.send_photo(chat_id, photo=get_dogURL(), caption="Вот тебе собачка!")

        elif ms_text == "Прислать анекдот":
            bot.send_message(chat_id, text=get_anekdot())

        elif ms_text == "Угадай, кто?":
            get_ManOrNot(chat_id)
        elif ms_text == "Карту"
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

        elif ms_text == "Задание 1":
            DZ.dz1(bot, chat_id)

        elif ms_text == "Задание 2":
            DZ.dz2(bot, chat_id)

        elif ms_text == "Задание 3":
            DZ.dz3(bot, chat_id)

        elif ms_text == "Задание 4":
            DZ.dz4(bot, chat_id)

        elif ms_text == "Задание 5":
            DZ.dz5(bot, chat_id)

        elif ms_text == "Задание 6":
            DZ.dz6(bot, chat_id)

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
    bot.send_photo(message.chat.id, img, reply_markup=key1)

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
        url = r.json()
        url = r_json['url']
    return url




#     if ms_text == "Главное меню" or ms_text == "👋 Главное меню" or ms_text == "Вернуться в главное меню":
#         markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#         btn1 = types.KeyboardButton("Развлечения")
#         btn2 = types.KeyboardButton("WEB-камера")
#         btn3 = types.KeyboardButton("Управление")
#         btn4 = types.KeyboardButton("Домашнее задание")
#         back = types.KeyboardButton("Помощь")
#         markup.add(btn1, btn2, btn3, btn4, back)
#         bot.send_message(chat_id, text="Вы в главном меню", reply_markup=markup)
#
#     elif ms_text == "Развлечения":
#         markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#         btn1 = types.KeyboardButton("Прислать собаку")
#         btn2 = types.KeyboardButton("Прислать анекдот")
#         btn3 = types.KeyboardButton("Мудрость дня")
#         btn4 = types.KeyboardButton("Generate insult")
#         back = types.KeyboardButton("Вернуться в главное меню")
#         markup.add(btn1, btn2, btn3, btn4, back)
#         bot.send_message(chat_id, text="Развлечения", reply_markup=markup)
#
#     elif ms_text == "/dog" or ms_text == "Прислать собаку":
#         contents = requests.get('https://random.dog/woof.json').json()
#         urlDOG = contents['url']
#         bot.send_photo(chat_id, photo=urlDOG, caption="Вот тебе собачка!")
#
#     elif ms_text == "Прислать анекдот":
#         bot.send_message(chat_id, text=get_anekdot())
#
#     elif ms_text == "Generate insult":
#         contents = requests.get('https://evilinsult.com/generate_insult.php?lang=en&type=json').json()
#         insult = contents['insult']
#         bot.send_message(chat_id, text=insult)
#
#     elif ms_text == "Мудрость дня":
#         bot.send_message(chat_id, text=get_wolf_quote() + "🐺")
#
#     elif ms_text == "WEB-камера":
#         bot.send_message(chat_id, text="Ещё не готово(((")
#
#     elif ms_text == "Управление":
#         bot.send_message(chat_id, text="Ещё не готово(((")
#
#     elif ms_text == "Помощь" or ms_text == "/help":
#         bot.send_message(chat_id, text="Автор: Тюрина Елена")
#         key1 = types.InlineKeyboardMarkup()
#         btn1 = types.InlineKeyboardButton(text="Напишите автору",
#                                           url="https://t.me/helenatyurina")
#         key1.add(btn1)
#         img = open('1МД15_Тюрина_Елена.jpg', 'rb')
#         bot.send_photo(message.chat.id, img, reply_markup=key1)
#
#     elif ms_text == "Домашнее задание":
#         markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#         btn1 = types.KeyboardButton("1")
#         btn2 = types.KeyboardButton("2")
#         btn3 = types.KeyboardButton("3")
#         btn45 = types.KeyboardButton("4-5")
#         btn6 = types.KeyboardButton("6")
#         btn7 = types.KeyboardButton("7")
#         btn8 = types.KeyboardButton("8")
#         btn9 = types.KeyboardButton("9")
#         btn10 = types.KeyboardButton("10")
#         btn11 = types.KeyboardButton("Вернуться в главное меню")
#         markup.add(btn1, btn2, btn3, btn45, btn6, btn7, btn8, btn9, btn10, btn11)
#         bot.send_message(chat_id, text="Домашнее задание", reply_markup=markup)
#     #
#     elif ms_text == "1":
#         name = "Елена"
#         bot.send_message(chat_id, text=name)
#     elif ms_text == "2":
#         name = "Елена"
#         age = "20"
#         bot.send_message(chat_id, text=f"Меня зовут {name}, мне {age} лет")
#     elif ms_text == "3":
#         name = "Елена"
#         five_names = name * 4 + name
#         bot.send_message(chat_id, text=five_names)
#     elif ms_text == "4-5":
#         pass
#         # user_name = input("Enter your name: ")
#         # if " " in user_name:
#         #     print("Only name is required!")
#         #     exit()
#         # user_age = input("Enter your age: ")
#         # print("Hello, " + user_name + "!")
#         # try:
#         #     user_age = int(user_age)
#         # except ValueError:
#         #     print("Age entered incorrectly: it should be number")
#         #     exit()
#         # if (user_age <= 0) or (user_age > 150):
#         #     print("Age entered incorrectly: it should be strictly between 0 and 150")
#         #     exit()
#         # if (user_age >= 18) and (user_age < 30):
#         #     print("Age doesn't mean anything if you are not some cheese or wine")
#         # elif user_age < 18:
#         #     print("Hey, kiddo! Isn't it time for bed now?")
#         # else:
#         #     print("Everyone gets to be young once, and your turn is over :(")
#
#     elif ms_text == "6":
#         pass
#     elif ms_text == "7":
#         pass
#     elif ms_text == "8":
#         pass
#     elif ms_text == "9":
#         pass
#     elif ms_text == "10":
#         pass
#
#     else:
#         bot.send_message(chat_id, text="Я вас слышу! Ваше сообщение: " + ms_text)
#
#
# def get_anekdot():
#     array_anekdots = []
#     req_anek = requests.get('http://anekdotme.ru/random')
#     soup = bs4.BeautifulSoup(req_anek.text, "html.parser")
#     result_find = soup.select('.anekdot_text')
#     for result in result_find:
#         array_anekdots.append(result.getText().strip())
#     return array_anekdots[0]
#
#
# def get_wolf_quote():
#
#     array_quotes = []
#     req_quote = requests.get('https://statusas.ru/citaty-i-aforizmy/citaty-pro-zhivotnyx-i-zverej/citaty-i-memy-volka-auf.html')
#     soup = bs4.BeautifulSoup(req_quote.text, "html.parser")
#     result_find = soup.find('div', class_='p-15 full-image').find('div', class_='entry-content').select('p')
#     for result in result_find:
#         if (result.getText() != "") and not ("http" in result.getText()):
#             array_quotes.append(result.getText().strip())
#     count = random.randint(1, len(array_quotes)-1)
#     return array_quotes[count]

bot.polling(none_stop=True, interval=0)  # Запускаем бота

print()
