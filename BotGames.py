import requests
import re
import threading
from telebot import types
import menuBot
import bs4

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

class TicTacToeMultiplayer:
    name = "Крестики-нолики (Мультиплеер)"
    text_rules = "Игроки по очереди ставят на свободные клетки поля 3×3 знаки (один всегда крестики, другой " \
                 "всегда нолики). Первый, выстроивший в ряд 3 своих фигуры по вертикали, горизонтали или диагонали, " \
                 "выигрывает. Первый ход делает игрок, ставящий крестики."

    class Player:

        def __init__(self, playerID, playerName):
            self.id = playerID
            self.gameMessage = None
            self.name = playerName
            self.scores = 0
            self.choices = []
            self.x_or_o = ""

        def __str__(self):
            return self.name

    def __init__(self, bot, chat_user):
        self.id = chat_user.id
        self.objBot = bot
        self.players = {}
        self.textGame = ""
        self.turnPlayerId = None
        self.winner = None
        self.buttons = {}  # словарь с кнопками (индекс: кнопка)
        self.createButtons()
        self.keyboard = types.InlineKeyboardMarkup(row_width=3)
        self.addPlayer(chat_user.id, chat_user.userName)

    def createButtons(self):
        for i in range(3):
            for j in range(3):
                self.buttons[f"{i+1}{j+1}"] = types.InlineKeyboardButton(text=" ",
                                              callback_data=f"tttMult|Choice-{i+1}{j+1}|" + menuBot.Menu.setExtPar(self))


    def addPlayer(self, playerID, playerName):
        newPlayer = self.Player(playerID, playerName)
        self.players[playerID] = newPlayer
        if len(self.players) < 2:
            self.players[playerID].x_or_o = "X"
            self.turnPlayerId = playerID
            keyboard = types.InlineKeyboardMarkup()
            btn = types.InlineKeyboardButton(text="Выход",
                                                  callback_data="tttMult|Exit|" + menuBot.Menu.setExtPar(self))
            keyboard.add(btn)
            self.objBot.send_message(playerID, text="Пожалуйста, подождите второго игрока", reply_markup=keyboard)
        else:
            for player in self.players.values():
                if player.id != playerID and player.x_or_o == "X":
                    self.players[playerID].x_or_o = "O"
                elif player.id != playerID and player.x_or_o == "O":
                    self.players[playerID].x_or_o = "X"
                    self.turnPlayerId = playerID
            self.newRound()
        return newPlayer

    def delPlayer(self, playerID):
        remotePlayer = self.players.pop(playerID)
        try:
            self.objBot.delete_message(chat_id=remotePlayer.id, message_id=remotePlayer.gameMessage.id)
        except:
            pass
        self.objBot.send_message(chat_id=remotePlayer.id, text="Вы вышли из игры!")
        menuBot.goto_menu(self.objBot, remotePlayer.id, "Игры")
        if len(self.players.values()) == 0:
            stopGame(self.id)

    def getPlayer(self, chat_userID):
        return self.players.get(chat_userID)

    def newRound(self):
        if len(self.players) > 1:
            for player in self.players.values():
                player.choices = []
                if self.winner != None:
                    if player.id == self.winner:
                        player.x_or_o = "X"
                        self.turnPlayerId = player.id
                    else:
                        player.x_or_o = "O"
            self.createButtons()
            self.keyboard = types.InlineKeyboardMarkup(row_width=3)
            for i in range(3):
                 self.keyboard.add(self.buttons[f"{i + 1}1"], self.buttons[f"{i + 1}2"], self.buttons[f"{i + 1}3"])
            self.setTextGame()
            btn = types.InlineKeyboardButton(text="Выход",
                                             callback_data="tttMult|Exit|" + menuBot.Menu.setExtPar(self))
            self.keyboard.add(btn)
            for player in self.players.values():
                if player.id == self.turnPlayerId:
                    text_individual = "ВАШ ХОД - " + player.x_or_o
                else:
                    text_individual = "ХОД СОПЕРНИКА - " + player.x_or_o
                gameMessage = self.objBot.send_message(player.id, text=self.textGame + text_individual,
                                                       reply_markup=self.keyboard)
                player.gameMessage = gameMessage
        else:
            self.keyboard = types.InlineKeyboardMarkup()
            btn = types.InlineKeyboardButton(text="Выход",
                                             callback_data="tttMult|Exit|" + menuBot.Menu.setExtPar(self))
            self.keyboard.add(btn)
            for player in self.players.values():
                self.objBot.send_message(player.id, text="Пожалуйста, подождите второго игрока", reply_markup=self.keyboard)

    def playerChoice(self, chat_userID, choice):
        player = self.getPlayer(chat_userID)
        if player.id == self.turnPlayerId and self.buttons[choice].text == " ":
            self.players[player.id].choices.append(choice)
            print(choice)
            print(type(choice))
            self.buttons[choice] = types.InlineKeyboardButton(text=player.x_or_o, callback_data=f"tttMult|Choice-{choice}|" + menuBot.Menu.setExtPar(self))
            for player2 in self.players.values():
                if player2.id != player.id:
                    self.turnPlayerId = player2.id
            self.keyboard = types.InlineKeyboardMarkup(row_width=3)
            for i in range(3):
                self.keyboard.add(self.buttons[f"{i + 1}1"], self.buttons[f"{i + 1}2"], self.buttons[f"{i + 1}3"])
            btn = types.InlineKeyboardButton(text="Выход",
                                             callback_data="tttMult|Exit|" + menuBot.Menu.setExtPar(self))
            self.keyboard.add(btn)
            isEndGame = self.findWinner(player.id)
            self.setTextGame()
            self.sendMessagesAllPlayers()
            if isEndGame == True:
                self.EndGame()
            print(isEndGame)


    def findWinner(self, playerID):
        num_of_choices = 0
        for player in self.players.values():
            num_of_choices += len(player.choices)
        player = self.getPlayer(playerID)
        isEndGame = False
        for i in range(3):
            if (f"{i+1}1" in player.choices) and (f"{i+1}2" in player.choices) and (f"{i+1}3" in player.choices) or \
                    (f"1{i+1}" in player.choices) and (f"2{i+1}" in player.choices) and (f"3{i+1}" in player.choices):
                isEndGame = True
                self.winner = playerID
                break
        if not isEndGame:
            if ("11" in player.choices) and ("22" in player.choices) and ("33" in player.choices) or \
                    ("13" in player.choices) and ("22" in player.choices) and ("31" in player.choices):
                isEndGame = True
                self.winner = playerID
        if not isEndGame:
            if num_of_choices == 9:
                isEndGame = True
                self.winner = None
        if isEndGame:
            self.turnPlayerId = None
            player.scores +=1
        return isEndGame


    def setTextGame(self):
        from prettytable import PrettyTable
        mytable = PrettyTable()
        mytable.field_names = ["Игрок", "Счёт"]  # имена полей таблицы
        for player in self.players.values():
            mytable.add_row(
                [player.name, player.scores])

        textGame = self.text_rules + "\n"
        textGame += mytable.get_string() + "\n\n"
        self.textGame = textGame



    def sendMessagesAllPlayers(self):
        for player in self.players.values():
            if len(self.players) > 1:
                if self.turnPlayerId == player.id:
                    text_individual = "ВАШ ХОД"
                else:
                    text_individual = "ХОД СОПЕРНИКА"
            self.objBot.edit_message_text(self.textGame + text_individual, chat_id=player.id, message_id=player.gameMessage.id,
                                          reply_markup=self.keyboard)
            print("успех")

    def EndGame(self):
        keyboard = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(text="Выход",
                                         callback_data="tttMult|Exit|" + menuBot.Menu.setExtPar(self))
        keyboard.add(btn)
        for player in self.players.values():
            if self.winner != None:
                if self.winner == player.id:
                    text_individual = "ВЫ ПОБЕДИЛИ!"
                else:
                    text_individual = "ВЫ ПРОИГРАЛИ!"
            else:
                text_individual = "НИЧЬЯ!"
            self.objBot.edit_message_text(text_individual + "\nНовый раунд через 10 секунд",
                                          chat_id=player.id, message_id=player.gameMessage.id,
                                          reply_markup=keyboard)
        timer = threading.Timer(10, self.newRound)
        timer.start()

# -----------------------------------------------------------------------
def callback_worker(bot, cur_user, cmd, par, call):
    chat_id = call.message.chat.id
    message_id = call.message.id

    if cmd == "newGame":
        # bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)  # удалим кнопки начала игры из чата
        bot.delete_message(chat_id, message_id)
        newGame(chat_id, TicTacToeMultiplayer(bot, cur_user))
        bot.answer_callback_query(call.id)

    elif cmd == "Join":
        # bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)  # удалим кнопки начала игры из чата
        bot.delete_message(chat_id, message_id)
        tttMult = menuBot.Menu.getExtPar(par)
        if tttMult is None:  # если наткнулись на кнопку, которой быть не должно
            return
        else:
            tttMult.addPlayer(cur_user.id, cur_user.userName)
        bot.answer_callback_query(call.id)

    elif cmd == "Exit":
        bot.delete_message(chat_id, message_id)
        tttMult = menuBot.Menu.getExtPar(par)
        if tttMult is not None:
            tttMult.delPlayer(cur_user.id)
        menuBot.goto_menu(bot, chat_id, "Игры")
        bot.answer_callback_query(call.id)

    elif "Choice-" in cmd:
        tttMult = menuBot.Menu.getExtPar(par)
        if tttMult is None:  # если наткнулись на кнопку, которой быть не должно - удалим её из чата
            bot.delete_message(chat_id, message_id)
        else:
            choice = cmd[7:]
            tttMult.playerChoice(cur_user.id, choice)
        bot.answer_callback_query(call.id)
# -----------------------------------------------------------------------

    if __name__ == "__main__":
        print("Этот код должен использоваться только в качестве модуля!")