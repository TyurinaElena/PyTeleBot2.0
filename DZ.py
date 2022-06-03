
name = "Елена"
age = 20
# uname = ""


def dz1(bot, chat_id):
    bot.send_message(chat_id, text=name)


def dz2(bot, chat_id):
    bot.send_message(chat_id, text=f"Здравствуйте! Меня зовут {name}, мне {age} лет")


def dz3(bot, chat_id):
    bot.send_message(chat_id, text=name * 5)


def dz45(bot, chat_id):
    dz45_ResponseHandler1 = lambda user_name: my_inputInt(bot, chat_id, f"Здравствуйте, {user_name.text}! "
                                                                        f"Сколько Вам лет?", dz45_ResponseHandler2)

    def dz45_ResponseHandler2(bot, chat_id, user_age):
        if user_age < 30:
            bot.send_message(chat_id, text="Всего лишь! Вы умны не по годам!")
        else:
            bot.send_message(chat_id, text="А выглядите на 25!")

    my_input(bot, chat_id, "Как вас зовут?", dz45_ResponseHandler1)


def dz6(bot, chat_id):
    dz6_ResponseHandler = lambda user_name: bot.send_message(chat_id, text=f"От первой до предпоследней: {user_name.text[:-1]}\n"
                                                                           f"Задом наперёд: {user_name.text[::-1]}\n"
                                                                           f"Первые пять: {user_name.text[:5]}")
    my_input(bot, chat_id, "Введите Ваше имя", dz6_ResponseHandler)

def dz7(bot, chat_id):
    def dz7_ResponseHandler1(user_name):
        global uname
        uname = user_name.text
        my_inputInt(bot, chat_id, f"Здравствуйте, {uname}! Сколько Вам лет?", dz7_ResponseHandler2)

    def dz7_ResponseHandler2(bot, chat_id, user_age):
        bot.send_message(chat_id, text=f"Длина Вашего имени - {len(uname)} символов")
        digit1 = user_age // 100
        digit2 = user_age // 10 % 10
        digit3 = user_age % 10
        if (digit1 == 0) and (digit2 == 0):
            product_of_numbers = digit3
            result = "Количество цифр Вашего возраста - 1"
        elif (digit1 == 0) and (digit2 != 0):
            product_of_numbers = digit2 * digit3
            result = "Количество цифр Вашего возраста - 2"
        else:
            product_of_numbers = digit1 * digit2 * digit3
            result = "Количество цифр Вашего возраста - 3"
        summ_of_numbers = digit1 + digit2 + digit3
        result += "\nСумма цифр возраста равна " + str(summ_of_numbers)
        result += "\nПроизведение цифр равно" + str(product_of_numbers)
        bot.send_message(chat_id, text=result)

    my_input(bot, chat_id, "Как вас зовут?", dz7_ResponseHandler1)


def dz8(bot, chat_id):
    dz8_ResponseHandler = lambda user_name:bot.send_message(chat_id, text=f"{user_name.text.lower()}\n{user_name.text.upper()}\n{user_name.text.capitalize()}\n"
                                       f"{user_name.text.capitalize().swapcase()}")

    my_input(bot, chat_id, "Как вас зовут?", dz8_ResponseHandler)


def dz9(bot, chat_id):
    def dz9_ResponseHandler(bot, chat_id, answer):
        if answer == 6:
            bot.send_message(chat_id, text="Правильно!")
        else:
            bot.send_message(chat_id, text="Не правильно! Правильный ответ: 6")

    my_inputInt(bot, chat_id, "Сколько будет 2+2*2?", dz9_ResponseHandler)

def my_input(bot, chat_id, txt, ResponseHandler):
    message = bot.send_message(chat_id, text=txt)
    bot.register_next_step_handler(message, ResponseHandler)


def my_inputInt(bot, chat_id, txt, ResponseHandler):
    message = bot.send_message(chat_id, text=txt)
    bot.register_next_step_handler(message, my_inputInt_SecondPart, botQuestion=bot, txtQuestion=txt,
                                   ResponseHandler=ResponseHandler)


def my_inputInt_SecondPart(message, botQuestion, txtQuestion, ResponseHandler):
    chat_id = message.chat.id
    try:
        if message.content_type != "text":
            raise ValueError
        val = int(message.text)
        ResponseHandler(botQuestion, chat_id, val)
    except ValueError:
        botQuestion.send_message(chat_id, text="Можно вводить только целое число в десятичной системе счисления!"
                                               "\nПопробуйте снова")
        my_inputInt(botQuestion, chat_id, txtQuestion, ResponseHandler)
