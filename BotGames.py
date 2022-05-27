import requests
import re

activeGames = {} # для накапливания активных игр

def newGame(chatID, newGame):
    activeGames.update({chatID: newGame})
    return newGame

def getGame(chatID):
    return activeGames.get(chatID, None)

def stopGame(chatID):
    activeGames.pop(chatID, None)


class Card:
    emo_SPADES = "U0002660"
    emo_CLUBS = "U0002663"
    emo_HEARTS = "U0002665"
    emo_DIAMONDS = "U0002666"

    def __init__(self, card):
        if isinstance(card, dict):         # если словарь
            self.__card_JSON = card
            self.code = card["code"]
            self.suit = card["suit"]
            self.value = card["value"]
            self.cost = self.get_cost_card()
            self.color = self.get_color_card()
            self.__imagesPNG_URL = card["images"]["png"]
            self.__imagesSVG_URL = card["images"]["svg"]
        elif isinstance(card, str):       # если строка формата "2S"
            self.__card_JSON = None
            self.code = card

            value = card[0]
            if value == "0":
                self.value = "10"
            elif value == "J":
                self.value = "JACK"
            elif value == "Q":
                self.value = "QUEEN"
            elif value == "K":
                self.value = "KING"
            elif value == "A":
                self.value = "ACE"
            elif value == "X":
                self.value = "JOKER"
            else:
                self.value = value

            suit = card[1]

            if suit == "1":
                self.suit = ""
                self.color = "BLACK"
            elif suit == "2":
                self.suit = ""
                self.color = "RED"

            else:
                if suit == "S":
                    self.suit = "SPADES" # пики
                elif suit == "C":
                    self.suit = "CLUBS" # крести
                elif suit == "H":
                    self.suit = "HEARTS" # черви
                elif suit == "D":
                    self.suit = "DIAMONDS" # буби

            self.cost = self.get_cost_card()
            self.color = self.get_color_card()

    def get_cost_card(self):
        if self.value == "JACK":
            return 2
        elif self.value == "QUEEN":
            return 3
        elif self.value == "KING":
            return 4
        elif self.value == "ACE":
            return 11
        elif self.value == "JOKER":
            return 1
        elif self.value == "ACE":
            return 11
        else:
            return int(self.value)

    def get_color_card(self):
        if (self.suit == "SPADES") or (self.suit == "CLUBS"):
            return "BLACK"
        elif (self.suit == "HEARTS") or (self.suit == "DIAMONDS"):
            return "RED"

class Game21:
    def __init__(self, deck_count=1, jokers_enabled=False):
        new_pack = self.new_pack(deck_count, jokers_enabled) # создаем новую пачку из
        # deck-count-колод
        if new_pack is not None:
            self.pack_card = new_pack # сформированная колода
            self.remaining = new_pack["remaining"] # количество оставшихся карт
            self.card_in_game = [] # карты в игре
            self.arr_cards_URL = [] # URL кард игрока
            self.score = 0 # очки игрока
            self.status = None # статус игры: True - выигрыш, False - проигрыш
            # None - продолжается

    def new_pack(self, deck_count, jokers_enabled=False):
        txtJoker = "&jokers_enabled=true" if jokers_enabled else ""
        response = requests.get(f"https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count={deck_count}" + txtJoker)
        # создание стопки карт из deck-count колод по 52 карты
        if response.status_code != 200:
            return None
        pack_card = response.json()
        return pack_card
    def get_cards(self, card_count=1):
        if self.pack_card == None:
            return None
        if self.status != None: # игра закончена
            return None
        deck_id = self.pack_card["deck_id"]
        response = requests.get(f"https://deckofcardsapi.com/api/deck/{deck_id}/draw/?count={card_count}")
# достать из deck_id колоды card_count карт
        if response.status_code != 200:
            return False

        new_cards = response.json()
        if new_cards["success"] != True:
            return False
        self.remaining = new_cards["remaining"] # обновим к-во ост карт в колоде

        arr_newCards = []
        for card in new_cards["cards"]:
            card_obj = Card(card) # создаем объекты класса card
            arr_newCards.append(card_obj)
            self.card_in_game.append(card_obj)
            self.score = self.score + card_obj.cost
            self.arr_cards_URL.append(card["image"])
        if self.score > 21:
            self.status = False
            text_game = "Очков: " + str(self.score) + "ВЫ ПРОИГРАЛИ"

        elif self.score < 21:
            self.status = None
            text_game = "Очков: " + str(self.score) + "в колоде осталось карт:" + str(self.remaining)

        else:
            self.status = True
            text_game = "Очков: " + str(self.score) + "ВЫ ВЫИГРАЛИ!"

        return text_game

# МУЛЬТИПЛЕЕР МУЛЬТИПЛЕЕР МУЛЬТИПЛЕЕР МУЛЬТИПЛЕЕР МУЛЬТИПЛЕЕР МУЛЬТИПЛЕЕР МУЛЬТИПЛЕЕР

class Quiz_Multiplayer:
    round_duration = 60  # сек.
    name = "ЧГК (Мультиплеер)"
    text_rules = "<b>Игрокам будет представлено 10 вопросов. На ответ даётся 60 секунд, за " \
                 "правильный ответ игроку начисляется 1 балл.Победителем считается игрок, набравший наибольшее" \
                 "количество очков.\n"

    class Player:

        def __init__(self, playerID, playerName):
            self.id = playerID
            self.gameMessage = None
            self.name = playerName
            self.scores = 0
            self.answer = None
            self.result = ""

        def __str__(self):
            return self.name

    def __init__(self, bot, chat_user):
        self.id = chat_user.id
        self.roundNumber = 0  # счётчик сыгранных раундов
        self.objBot = bot
        self.players = {}
        self.gameTimeLeft = 0
        self.objTimer = None
        self.winner = None
        self.textGame = ""
        self.numberPlayers = 0
        self.addPlayer(chat_user.id, chat_user.userName)
        self.right_answer = ""
        self.round_text = ""

    def addPlayer(self, playerID, playerName):
        newPlayer = self.Player(playerID, playerName)
        self.players[playerID] = newPlayer
        self.numberPlayers += 1
        if self.numberPlayers > 1:
            self.startTimer()
            self.setTextGame()
            list_btn = []
            list_btn = types.InlineKeyboardButton(text="Выход",
                                                  callback_data="QuizM|Exit|" + Menu.setExtPar(self))
            keyboard.add(list_btn)
            gameMessage = self.objBot.send_message(playerID, text=self.textGame, reply_markup=keyboard)
            self.players[playerID].gameMessage = gameMessage
            self.sendMessagesAllPlayers([playerID])  # отправим всем остальным игрокам информацию о новом игроке
        else:
            list_btn = []
            list_btn = types.InlineKeyboardButton(text="Выход",
                                                  callback_data="QuizM|Exit|" + Menu.setExtPar(self))
            keyboard.add(list_btn)
            gameMessage = self.objBot.send_message(playerID, text=self.textGame + "Пожалуйста, подождите, пока не "
                                                                                  "присоединится кто-нибудь ещё!", reply_markup=keyboard)
            self.players[playerID].gameMessage = gameMessage
        return newPlayer

    def delPlayer(self, playerID):
        remotePlayer = self.players.pop(playerID)
        try:
            self.objBot.delete_message(chat_id=remotePlayer.id, message_id=remotePlayer.gameMessage.id)
        except:
            pass
        self.objBot.send_message(chat_id=remotePlayer.id, text="Вы вышли из игры!")
        goto_menu(self.objBot, remotePlayer.id, "Игры")
        if len(self.players.values()) == 0:
            stopGame(self.id)

    def getPlayer(self, chat_userID):
        return self.players.get(chat_userID)

    def newRound(self):
        self.roundNumber += 1
        for player in self.players.values():
            player.answer = None
        self.startTimer()  # запустим таймер игры (если таймер активен, сбросим его)
        self.round_text = f"Вопрос{self.roundNumber}:\n"
        req = requests.get('https://db.chgk.info/')
        if req.status_code == 200:
            soup = bs4.BeautifulSoup(req.text, "html.parser")
            result_find = soup.select('.random_question')
            whole_text = result_find[1].getText()
        else:
            return ""
        question = re.search(r'Вопрос [0-9]:(.*)Ответ', whole_text, re.DOTALL)
        question = question.group(0).replace('Вопрос 2: ', '')
        question = question.replace('\nОтвет', '')

        answer = re.search(r'Ответ:(.*)Комментарий', whole_text, re.DOTALL)
        answer = answer.group(0).replace('Ответ: ', '')
        answer = answer.replace('\nКомментарий', '')
        self.right_answer = answer

        self.round_text = self.round_text + question

    def looper(self):
        print("LOOP", self.objTimer)
        if self.gameTimeLeft > 0:
            self.setTextGame()
            self.sendMessagesAllPlayers()
            self.gameTimeLeft -= 1
            self.objTimer = threading.Timer(1, self.looper)
            self.objTimer.start()
        else:
            for player in self.players.values():
                if player.answer is None:
                    player.answer = "Ответа нет"
            self.findRoundResults()

    def startTimer(self):
        print("START")
        self.stopTimer()
        self.gameTimeLeft = self.round_duration
        self.looper()

    def stopTimer(self):
        print("STOP")
        self.gameTimeLeft = 0
        if self.objTimer is not None:
            self.objTimer.cancel()
            self.objTimer = None

    @classmethod


    def checkEndRound(self):
        isEndRound = True
        for player in self.players.values():
            isEndRound = isEndRound and player.answer != None
        return isEndRound

    # def playerAnswer(self, chat_userID, answer):
    #     player = self.getPlayer(chat_userID)
    #     player.answer = answer
    #     self.findWiner()
    #     self.sendMessagesAllPlayers()

    def findRoundResults(self):
        if self.checkEndRound():
            self.stopTimer()  # все успели сделать ход, таймер выключаем
            for player in self.players.values():
                if player.answer == self.right_answer:
                    player.scores += 1
                    player.result = "+"
                else:
                    player.result = "-"

        if self.roundNumber < 10:
            self.round_text = "Раунд закончен! Перерыв на 30 секунд"
            self.setTextGame()
            for player in self.players.values():
                player.answer = None
                player.result = ""
                player.gameMessage = None
            if self.checkEndGame() and len(self.players) > 0:  # начинаем новый раунд через 30 секунд
                self.objTimer = threading.Timer(30, self.newRound())
                self.objTimer.start()
        else:
            self.findWiner

    def setTextGame(self):
        from prettytable import PrettyTable
        mytable = PrettyTable()
        mytable.field_names = ["Игрок", "Счёт", "Результат"]  # имена полей таблицы
        for player in self.players.values():
            mytable.add_row(
                [player.name, player.scores, player.result])

        textGame = self.text_rules + "\n\n"
        textGame += "<code>" + mytable.get_string() + "</code>" + "\n\n"
        textGame += self.round_text

        self.textGame = textGame

    

    def sendMessagesAllPlayers(self, excludingPlayers=()):
        try:
            for player in self.players.values():
                if player.id not in excludingPlayers:
                    textIndividual = f"\n Ваш ответ: {player.answer}, ждём остальных!" if player.answer is not None else "\n"
                    massage_sent = self.objBot.edit_message_text(self.textGame + textIndividual, chat_id=player.id, message_id=player.gameMessage.id,
                                                     reply_markup=player.gameMessage.reply_markup)
                    if player.answer is None:
                        bot.register_next_step_handler(message_sent, getAnswer, player)
        except:
            pass
        def getAnswer(message, player):
            player.answer = message.text

# -----------------------------------------------------------------------
def callback_worker(bot, cur_user, cmd, par, call):
    chat_id = call.message.chat.id
    message_id = call.message.id

    if cmd == "newGame":
        # bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)  # удалим кнопки начала игры из чата
        bot.delete_message(chat_id, message_id)
        newGame(chat_id, Quiz_Multiplayer(bot, cur_user))
        bot.answer_callback_query(call.id)

    elif cmd == "Join":
        # bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)  # удалим кнопки начала игры из чата
        bot.delete_message(chat_id, message_id)
        QuizMult = Menu.getExtPar(par)
        if QuizMult is None:  # если наткнулись на кнопку, которой быть не должно
            return
        else:
            QuizMult.addPlayer(cur_user.id, cur_user.userName)
        bot.answer_callback_query(call.id)

    elif cmd == "Exit":
        bot.delete_message(chat_id, message_id)
        QuizMult = Menu.getExtPar(par)
        if QuizMult is not None:
            QuizMult.delPlayer(cur_user.id)
        goto_menu(bot, chat_id, "Игры")
        bot.answer_callback_query(call.id)

    # elif "Choice-" in cmd:
    #     QuizMult = Menu.getExtPar(par)
    #     if QuizMult is None:  # если наткнулись на кнопку, которой быть не должно - удалим её из чата
    #         bot.delete_message(chat_id, message_id)
    #     else:
    #         choice = cmd[7:]
    #         QuizMult.playerChoice(cur_user.id, choice)
    #     bot.answer_callback_query(call.id)

# -----------------------------------------------------------------------

    if __name__ == "__main__":
        print("Этот код должен использоваться только в качестве модуля!")