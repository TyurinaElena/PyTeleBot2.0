from telebot import types
import pickle
import os

class KeyboardButton:
    def __init__(self, name, handler=None):
        self.name = name
        self.handler = handler

class Users:
    activeUsers = {}

    def __init__(self, chat_id, json):
        self.id = json["id"]
        self.isBot = json["is_bot"]
        self.firsrName = json["first_name"]
        self.userName = json["username"]
        self.languageCode = json["language_code"]
        self.__class__.activeUsers[chat_id] = self

    def __str__(self):
        return f"Name user: {self.firsrName}  id: {self.userName}  lang: {self.languageCode}"

    def getUserHTML(self):
        return f"Name user: {self.firsrName}  id: <a href='https://t.me/{self.userName}'>{self.userName}</a> lang: {self.languageCode}"

    @classmethod
    def getUser(cls, chat_id):
        return cls.activeUsers.get(chat_id)

class Menu:
    hash = {} # накопление экземпляров класса
    cur_menu = {} # текущее меню для каждого пользователя
    extendedParameters = {} # доп параметры для передачи в inline кнопки
    namePickleFile = "bot_curMenu.plk"

    def __init__(self, name, buttons=None, parent=None, handler=None):
        self.parent = parent
        self.name = name
        self.buttons = buttons
        self.handler = handler
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(*buttons) # звёздочка для распаковки списка
        self.markup = markup
        self.__class__.hash[name] = self # в классе содержится словарь со всеми экземплярами списка

    @classmethod
    def getExtPar(cls, id):
        return cls.extendedParameters.pop(id, None)

    @classmethod
    def setExtPar(cls, parameter):
        import uuid
        id = uuid.uuid4().hex
        cls.extendedParameters[id] = parameter
        return id

    @classmethod
    def getMenu(cls, chat_id, name):
        menu = cls.hash.get(name)
        if menu != None:
            cls.cur_menu[chat_id] = menu
            cls.saveCurMenu()
        return menu

    @classmethod
    def getCurMenu(cls, chat_id):
        return cls.cur_menu.get(chat_id)

    @classmethod
    def loadCurMenu(self):
        if os.path.exists(self.namePickleFile):
            with open(self.namePickleFile, 'rb') as pickle_in:
                self.cur_menu = pickle.load(pickle_in)
        else:
            self.cur_menu = {}

    @classmethod
    def saveCurMenu(self):
        with open(self.namePickleFile, 'wb') as pickle_out:
            pickle.dump(self.cur_menu, pickle_out)

def goto_menu(bot, chat_id, name_menu):
    # получение нужного элемента меню
    cur_menu = Menu.getCurMenu(chat_id)
    if name_menu == "Выход" and cur_menu != None and cur_menu.parent != None:
        target_menu = Menu.getMenu(chat_id, cur_menu.parent.name)
    else:
        target_menu = Menu.getMenu(chat_id, name_menu)

    if target_menu != None:
        bot.send_message(chat_id, text=target_menu.name, reply_markup=target_menu.markup)
        return target_menu
    else:
        return None


m_main = Menu("Главное меню", buttons=["Развлечения", "Игры", "ДЗ", "Помощь"])
m_games = Menu("Игры", buttons=["Камень, ножницы, бумага", "Крестики-нолики Multiplayer", "Игра в 21", "Угадай, кто?", "Выход"], parent=m_main)
m_game_21 = Menu("Игра в 21", buttons=["Карту!", "Стоп!", "Выход"], parent=m_games, handler="game_21")
m_game_rsp = Menu("Камень, ножницы, бумага", buttons=["Камень", "Ножницы", "Бумага", "Выход"], parent=m_games,
                  handler="game_rsp")
m_DZ = Menu("ДЗ", buttons=["Задание 1", "Задание 2", "Задание 3", "Задание 4-5", "Задание 6", "Задание 7",
                           "Задание 8", "Задание 9", "Выход"], parent=m_main)
m_fun = Menu("Развлечения", buttons=["quiz", "Прислать фильм", "Прислать собаку", "Прислать анекдот", "Мудрость дня", "Подобрать рецепт", "Выход"],
             parent=m_main)
