import random

SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
RED_SUITS = {'♥', '♦'}

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.face_up = False

    def is_red(self):
        return self.suit in RED_SUITS

    def value(self):
        return RANKS.index(self.rank)

    def __repr__(self):
        return f"{self.rank}{self.suit}"

class Game:
    def __init__(self):
        self.new_game()

    def new_game(self):
        deck = [Card(r, s) for s in SUITS for r in RANKS]
        random.shuffle(deck)

        # Tableau: 7 столбцов
        self.tableau = []
        for i in range(7):
            col = [deck.pop() for _ in range(i + 1)]
            col[-1].face_up = True
            self.tableau.append(col)

        # Остаток — в stock
        self.stock = deck
        self.waste = []

        # 4 foundation стопки (по одной на масть)
        self.foundations = [[] for _ in range(4)]

    def draw_from_stock(self):
        if self.stock:
            card = self.stock.pop()
            card.face_up = True
            self.waste.append(card)
        elif self.waste:
            # Переворачиваем waste обратно в stock
            self.waste.reverse()
            for c in self.waste:
                c.face_up = False
            self.stock = self.waste
            self.waste = []

    def can_place_on_tableau(self, card, target_col):
        col = self.tableau[target_col]
        if not col:
            return card.rank == 'K'
        top = col[-1]
        return (top.face_up and
                top.value() == card.value() + 1 and
                top.is_red() != card.is_red())

    def can_place_on_foundation(self, card, f_idx):
        f = self.foundations[f_idx]
        if not f:
            return card.rank == 'A'
        top = f[-1]
        return top.suit == card.suit and top.value() == card.value() - 1

    def is_won(self):
        return all(len(f) == 13 for f in self.foundations)