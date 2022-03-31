from telebot import types


class Menu:
    hash = {} # накопление экземпляров класса
    cur_menu = None # текущее меню
    extendedParameters = {} # доп параметры для передачи в inline кнопки

    def __init__(self, name, buttons=None, parent=None, action=None):
        self.parent = parent
        self.name = name
        self.buttons = buttons
        self.action = action

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(*buttons) # звёздочка для распаковки списка!
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
    def getMenu(cls, name):
        menu = cls.hash.get(name)
        if menu != None:
            cls.cur_menu = menu
        return menu


m_main = Menu("Главное меню", buttons=["Развлечения", "Игры", "ДЗ", "Помощь"])
m_games = Menu("Игры", buttons=["Камень, ножницы, бумага", "Игра в 21", "Выход"], parent=m_main)
m_game_21 = Menu("Игра в 21", buttons=["Карту!", "Стоп!", "Выход"], parent=m_games, action="game_21")
m_game_rsp = Menu("Камень, ножницы, бумага", buttons=["Камень", "Ножницы", "Бумага", "Выход"], parent=m_games,
                  action="game_rsp")
m_DZ = Menu("ДЗ", buttons=["Задание 1", "Задание 2", "Задание 3", "Задание 4-5", "Задание 6", "Задание 7",
                           "Задание 8", "Задание 9", "Выход"], parent=m_main)
m_fun = Menu("Развлечения", buttons=["Прислать собаку", "Прислать анекдот", "Мудрость дня", "Generate insult", "Выход"],
             parent=m_main)
