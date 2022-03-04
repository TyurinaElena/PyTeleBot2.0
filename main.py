# Телеграм-бот v.002 - бот создаёт меню, присылает собачку, и анекдот
# Ссылка на бот: t.me/Tyurina_Elena_1MD15_bot

import telebot # pyTelegramBotAPI 4.3.1
from telebot import types

bot = telebot.TeleBot('5144148734:AAEL1qxIJIXxsHP7lkCwtL9Pb4cLHE3a4RM')

#функция, обрабатывающая команду /start
@bot.message_handler(commands=["start"])
def start(message, res=False):
    chat_id = message.chat.id

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("👋 Главное меню")
    btn2 = types.KeyboardButton("❓ Помощь")
    markup.add(btn1, btn2)

    bot.send_message(chat_id,
                     text = "Привет, {0.first_name}! Я - текстовый бот для курса "
                            "программирования на языке Пайтон!".format(
                         message.from_user), reply_markup=markup)

# Получение сообщений от юзера
@bot.message_handler(content_types=['text'])
def get_text_message(message):
    chat_id = message.chat.id
    ms_text = message.text

    if ms_text == "Главное меню" or ms_text == "👋 Главное меню" or ms_text == "Вернуться в главное меню":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Развлечения")
        btn2 = types.KeyboardButton("WEB-камера")
        btn3 = types.KeyboardButton("Управление")
        btn4 = types.KeyboardButton("Домашнее задание")
        back = types.KeyboardButton("Помощь")
        markup.add(btn1, btn2, btn3, btn4, back)
        bot.send_message(chat_id, text="Вы в главном меню", reply_markup=markup)

    elif ms_text == "Развлечения":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Прислать собаку")
        btn2 = types.KeyboardButton("Прислать анекдот")
        back = types.KeyboardButton("Вернуться в главное меню")
        markup.add(btn1, btn2, back)
        bot.send_message(chat_id, text="Развлечения", reply_markup=markup)

    elif ms_text == "/dog" or ms_text == "Прислать собаку":
        img = open('dog1.jpeg', 'rb')
        bot.send_photo(message.chat.id, img)

    elif ms_text == "Прислать анекдот":
        bot.send_message(chat_id, text="Заходит енот с ноутбуком в бар и заказывает виски. "
                                       "Бармен остолбенел, но приносит виски строчащему "
                                       "на ноутбуке еноту и говорит:\n— Вы… говорящий енот? "
                                       "Никогда такого не видел!\n— Я недавно приехал. Работу вот ищу."
                                       "\n— Может, вам в цирк работать пойти?\n— А зачем им программисты?")

    elif ms_text == "WEB-камера":
        bot.send_message(chat_id, text="Ещё не готово(((")

    elif ms_text == "Управление":
        bot.send_message(chat_id, text="Ещё не готово(((")

    elif ms_text == "Помощь" or ms_text == "/help":
        bot.send_message(chat_id, text="Автор: Тюрина Елена")
        key1 = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text="Напишите автору",
                                          url="https://t.me/helenatyurina")
        key1.add(btn1)
        img = open('1МД15_Тюрина_Елена.jpg', 'rb')
        bot.send_photo(message.chat.id, img, reply_markup=key1)

    elif ms_text == "Домашнее задание":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("1")
        btn2 = types.KeyboardButton("2")
        btn3 = types.KeyboardButton("3")
        btn4 = types.KeyboardButton("4")
        btn5 = types.KeyboardButton("5")
        btn6 = types.KeyboardButton("6")
        btn7 = types.KeyboardButton("7")
        btn8 = types.KeyboardButton("8")
        btn9 = types.KeyboardButton("9")
        btn10 = types.KeyboardButton("10")
        back = types.KeyboardButton("Вернуться в главное меню")
        markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9, btn10)
        bot.send_message(chat_id, text="Домашнее задание", reply_markup=markup)

    elif ms_text == "1":
        name = "Елена"
        bot.send_message(chat_id, text=name)
    elif ms_text == "2":
        name = "Елена"
        age = "20"
        bot.send_message(chat_id, text=f"Меня зовут {name}, мне {age} лет")
    elif ms_text == "3":
        name = "Елена"
        five_names = name * 4 + name
        bot.send_message(chat_id, text=five_names)
    elif ms_text == "4":
        pass
    elif ms_text == "5":
        pass
    elif ms_text == "6":
        pass
    elif ms_text == "7":
        pass
    elif ms_text == "8":
        pass
    elif ms_text == "9":
        pass
    elif ms_text == "10":
        pass

    else:
        bot.send_message(chat_id, text="Я вас слышу! Ваше сообщение: " + ms_text)

bot.polling(none_stop=True, interval=0) # Запускаем бота

print()