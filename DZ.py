name = "Елена"
age = 20
def dz1(bot, chat_id):
    bot.send_message(chat_id, text=name)

def dz2(bot, chat_id):
    bot.send_message(chat_id, text=f"Здравствуйте! Меня зовут {name}, мне {age} лет")

def dz3(bot, chat_id):
    bot.send_message(chat_id, text=name*5)

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
    pass

def dz7(bot, chat_id):
    pass

def dz8(bot, chat_id):
    pass

def dz9(bot, chat_id):
    pass

def dz10(bot, chat_id):
    pass

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
        val = int(message.text)
        ResponseHandler(botQuestion, chat_id, val)
    except ValueError:
        botQuestion.send_message(chat_id, text="Можно вводить только целое число в десятичной системе счисления!"
                                               "\nПопробуйте снова")
        my_inputInt(botQuestion, chat_id, txtQuestion, ResponseHandler)
