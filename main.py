import curses
from game import Game

def init_colors():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_WHITE,  -1)  # белый
    curses.init_pair(2, curses.COLOR_RED,    -1)  # красный
    curses.init_pair(3, curses.COLOR_CYAN,   -1)  # выделение
    curses.init_pair(4, curses.COLOR_YELLOW, -1)  # статус

CARD_W = 7   # ширина включая рамку
CARD_H = 5
TOP_Y = 1
TAB_Y = TOP_Y + CARD_H + 2

STOCK_ZONE = 0
WASTE_ZONE = 1
FOUND_ZONE = [2, 3, 4, 5]
TAB_ZONE   = [6, 7, 8, 9, 10, 11, 12]

def zone_x(zone):
    if zone == STOCK_ZONE:
        return 2
    if zone == WASTE_ZONE:
        return 2 + CARD_W + 1
    if zone in FOUND_ZONE:
        i = zone - 2
        return 80 - 2 - (4 - i) * (CARD_W + 1)
    if zone in TAB_ZONE:
        i = zone - 6
        return 2 + i * (CARD_W + 1)

def draw_card(win, y, x, rank, suit, is_red, selected=False):
    white  = curses.color_pair(3 if selected else 1)
    if selected:
        white |= curses.A_BOLD
    red    = curses.color_pair(2)
    if selected:
        red |= curses.A_BOLD

    label = rank + suit   # напр. "7♦" или "10♥"
    inner = CARD_W - 2    # внутренняя ширина = 7

    # Верхняя линия: ┌ + label + дефисы + ┐
    dashes_top = inner - len(label)
    # Нижняя линия: └ + дефисы + label + ┘
    dashes_bot = inner - len(label)

    try:
        # Верхняя грань
        win.addstr(y, x,               "┌",           white)
        win.addstr(y, x + 1,           rank + suit,   red if is_red else white)
        win.addstr(y, x + 1 + len(label), "─" * dashes_top + "┐", white)

        # Средние строки
        win.addstr(y+1, x, "│" + " " * inner + "│", white)
        win.addstr(y+2, x, "│" + " " * inner + "│", white)
        win.addstr(y+3, x, "│" + " " * inner + "│", white)

        # Нижняя грань
        win.addstr(y+4, x,                         "└" + "─" * dashes_bot, white)
        win.addstr(y+4, x + 1 + dashes_bot,        rank + suit,             red if is_red else white)
        win.addstr(y+4, x + 1 + dashes_bot + len(label), "┘",              white)
    except curses.error:
        pass

def draw_face_down(win, y, x):
    dim = curses.color_pair(1) | curses.A_DIM
    try:
        win.addstr(y,   x, "┌─────┐", dim)
        win.addstr(y+1, x, "│/////│", dim)
        win.addstr(y+2, x, "│/////│", dim)
        win.addstr(y+3, x, "│/////│", dim)
        win.addstr(y+4, x, "└─────┘", dim)
    except curses.error:
        pass

def draw_empty(win, y, x, label="", cursor=False):
    attr = curses.color_pair(3 if cursor else 1) | curses.A_DIM
    try:
        win.addstr(y,   x, "┌─────┐", attr)
        win.addstr(y+1, x, "│     │", attr)
        win.addstr(y+2, x, f"│{label:^5}│", attr)
        win.addstr(y+3, x, "│     │", attr)
        win.addstr(y+4, x, "└─────┘", attr)
    except curses.error:
        pass

def draw_cursor_indicator(win, y, x):
    try:
        win.addstr(y + CARD_H, x + 4, "▲", curses.color_pair(3) | curses.A_BOLD)
    except curses.error:
        pass

def get_first_face_up(col):
    for i, c in enumerate(col):
        if c.face_up:
            return i
    return len(col) - 1

def check_deadlock(game):
    if game.stock or game.waste:
        return False
    for col in game.tableau:
        if col and col[-1].face_up:
            card = col[-1]
            for i in range(4):
                if game.can_place_on_foundation(card, i):
                    return False
            for j in range(7):
                if game.can_place_on_tableau(card, j):
                    return False
    return True

def draw_game(win, game, zone, cursor_row, selected):
    win.clear()
    h, w = win.getmaxyx()
    suits_order = ['♠', '♥', '♦', '♣']

    # Stock
    x = zone_x(STOCK_ZONE)
    if game.stock:
        draw_face_down(win, TOP_Y, x)
        try:
            win.addstr(TOP_Y+2, x+2, f"{len(game.stock):^4}", curses.color_pair(1) | curses.A_DIM)
        except curses.error:
            pass
    else:
        draw_empty(win, TOP_Y, x, "↺", cursor=(zone == STOCK_ZONE))
    if zone == STOCK_ZONE:
        draw_cursor_indicator(win, TOP_Y, x)

    # Waste
    x = zone_x(WASTE_ZONE)
    sel = (selected and selected[0] == WASTE_ZONE)
    if game.waste:
        c = game.waste[-1]
        draw_card(win, TOP_Y, x, c.rank, c.suit, c.is_red(), selected=sel)
    else:
        draw_empty(win, TOP_Y, x, cursor=(zone == WASTE_ZONE))
    if zone == WASTE_ZONE:
        draw_cursor_indicator(win, TOP_Y, x)

    # Foundations
    for i, suit in enumerate(suits_order):
        fz = FOUND_ZONE[i]
        x = zone_x(fz)
        sel = (selected and selected[0] == fz)
        f = game.foundations[i]
        if f:
            c = f[-1]
            draw_card(win, TOP_Y, x, c.rank, c.suit, c.is_red(), selected=sel)
        else:
            draw_empty(win, TOP_Y, x, suit, cursor=(zone == fz))
        if zone == fz:
            draw_cursor_indicator(win, TOP_Y, x)

    # Tableau
    for i in range(7):
        tz = TAB_ZONE[i]
        x = zone_x(tz)
        col = game.tableau[i]

        if not col:
            draw_empty(win, TAB_Y, x, "K", cursor=(zone == tz))
            if zone == tz:
                draw_cursor_indicator(win, TAB_Y, x)
            continue

        for row, card in enumerate(col):
            y = TAB_Y + row * 2
            is_sel = selected and selected[0] == tz and row >= selected[1]
            is_cur = (zone == tz and row == cursor_row)
            if not card.face_up:
                draw_face_down(win, y, x)
            else:
                draw_card(win, y, x, card.rank, card.suit, card.is_red(),
                          selected=(is_sel or is_cur))

        if zone == tz:
            last_y = TAB_Y + (len(col) - 1) * 2
            draw_cursor_indicator(win, last_y, x)

    # Статус
    try:
        if selected:
            sz, sr = selected
            if sz == WASTE_ZONE:
                card_str = str(game.waste[-1])
            elif sz in TAB_ZONE:
                col = game.tableau[sz - 6]
                card_str = str(col[sr])
            else:
                card_str = "?"
            win.addstr(h-2, 2,
                       f"Выбрано: {card_str}   Enter=положить  Esc=отмена",
                       curses.color_pair(4))
        else:
            win.addstr(h-2, 2,
                       "← →: столбец  ↑ ↓: карта   Enter: взять/положить   A: foundation   Space: колода   Q: выход",
                       curses.color_pair(1) | curses.A_DIM)
    except curses.error:
        pass

def show_overlay(stdscr, lines, color_pair):
    h, w = stdscr.getmaxyx()
    max_len = max(len(l) for l in lines)
    sy = h // 2 - len(lines) // 2
    sx = w // 2 - max_len // 2
    for i, line in enumerate(lines):
        try:
            stdscr.addstr(sy + i, sx, line, color_pair)
        except curses.error:
            pass
    stdscr.refresh()

def main(stdscr):
    curses.curs_set(0)
    init_colors()

    game = Game()
    zone = TAB_ZONE[0]
    cursor_row = 0
    selected = None

    TOP_ROW = [STOCK_ZONE, WASTE_ZONE] + FOUND_ZONE

    def clamp_row():
        nonlocal cursor_row
        if zone in TAB_ZONE:
            col = game.tableau[zone - 6]
            if col:
                min_r = get_first_face_up(col)
                cursor_row = max(min_r, min(cursor_row, len(col) - 1))
            else:
                cursor_row = 0
        else:
            cursor_row = 0

    while True:
        clamp_row()
        draw_game(stdscr, game, zone, cursor_row, selected)
        stdscr.refresh()

        if game.is_won():
            show_overlay(stdscr,
                ["                        ",
                 "   ПОБЕДА! Поздравляю!  ",
                 "   N = новая игра       ",
                 "   Q = выход            ",
                 "                        "],
                curses.color_pair(3) | curses.A_BOLD)
            while True:
                k = stdscr.getch()
                if k == ord('q') or k == ord('Q'): return
                if k == ord('n') or k == ord('N'):
                    game = Game(); selected = None
                    zone = TAB_ZONE[0]; cursor_row = 0
                    break
            continue

        if check_deadlock(game):
            show_overlay(stdscr,
                ["                        ",
                 "   Ходов больше нет...  ",
                 "   N = новая игра       ",
                 "   Q = выход            ",
                 "                        "],
                curses.color_pair(2) | curses.A_BOLD)
            while True:
                k = stdscr.getch()
                if k == ord('q') or k == ord('Q'): return
                if k == ord('n') or k == ord('N'):
                    game = Game(); selected = None
                    zone = TAB_ZONE[0]; cursor_row = 0
                    break
            continue

        key = stdscr.getch()

        if key == ord('q') or key == ord('Q'):
            break

        elif key == 27:
            selected = None

        elif key == curses.KEY_RIGHT:
            if zone in TOP_ROW:
                idx = TOP_ROW.index(zone)
                zone = TOP_ROW[min(idx + 1, len(TOP_ROW) - 1)]
            else:
                idx = TAB_ZONE.index(zone)
                zone = TAB_ZONE[min(idx + 1, len(TAB_ZONE) - 1)]
                col = game.tableau[zone - 6]
                cursor_row = len(col) - 1 if col else 0

        elif key == curses.KEY_LEFT:
            if zone in TOP_ROW:
                idx = TOP_ROW.index(zone)
                zone = TOP_ROW[max(idx - 1, 0)]
            else:
                idx = TAB_ZONE.index(zone)
                zone = TAB_ZONE[max(idx - 1, 0)]
                col = game.tableau[zone - 6]
                cursor_row = len(col) - 1 if col else 0

        elif key == curses.KEY_UP:
            if zone in TAB_ZONE:
                col = game.tableau[zone - 6]
                min_r = get_first_face_up(col) if col else 0
                if cursor_row <= min_r:
                    tab_idx = zone - 6
                    if tab_idx == 0:
                        zone = STOCK_ZONE
                    elif tab_idx == 1:
                        zone = WASTE_ZONE
                    else:
                        zone = FOUND_ZONE[min(tab_idx - 2, 3)]
                else:
                    cursor_row -= 1

        elif key == curses.KEY_DOWN:
            if zone in TOP_ROW:
                if zone == STOCK_ZONE:
                    tab_idx = 0
                elif zone == WASTE_ZONE:
                    tab_idx = 1
                else:
                    tab_idx = min(FOUND_ZONE.index(zone) + 2, 6)
                zone = TAB_ZONE[tab_idx]
                col = game.tableau[zone - 6]
                cursor_row = len(col) - 1 if col else 0
            elif zone in TAB_ZONE:
                col = game.tableau[zone - 6]
                if col:
                    cursor_row = min(len(col) - 1, cursor_row + 1)

        elif key == ord(' '):
            game.draw_from_stock()

        elif key == 10 or key == curses.KEY_ENTER:
            if zone == STOCK_ZONE:
                game.draw_from_stock()

            elif selected is None:
                if zone == WASTE_ZONE and game.waste:
                    selected = (WASTE_ZONE, 0)
                elif zone in TAB_ZONE:
                    col = game.tableau[zone - 6]
                    if col and col[cursor_row].face_up:
                        selected = (zone, cursor_row)

            else:
                src_zone, src_row = selected
                cards = [game.waste[-1]] if src_zone == WASTE_ZONE else game.tableau[src_zone - 6][src_row:]
                moved = False

                if zone in TAB_ZONE and zone != src_zone:
                    dst_col = zone - 6
                    if game.can_place_on_tableau(cards[0], dst_col):
                        if src_zone == WASTE_ZONE:
                            game.waste.pop()
                        else:
                            src_col = src_zone - 6
                            game.tableau[src_col] = game.tableau[src_col][:src_row]
                            if game.tableau[src_col] and not game.tableau[src_col][-1].face_up:
                                game.tableau[src_col][-1].face_up = True
                        game.tableau[dst_col].extend(cards)
                        cursor_row = len(game.tableau[dst_col]) - 1
                        moved = True

                elif zone in FOUND_ZONE:
                    f_idx = zone - 2
                    if len(cards) == 1 and game.can_place_on_foundation(cards[0], f_idx):
                        if src_zone == WASTE_ZONE:
                            game.waste.pop()
                        else:
                            src_col = src_zone - 6
                            game.tableau[src_col].pop()
                            if game.tableau[src_col] and not game.tableau[src_col][-1].face_up:
                                game.tableau[src_col][-1].face_up = True
                        game.foundations[f_idx].append(cards[0])
                        moved = True

                selected = None

        elif key == ord('a') or key == ord('A'):
            if zone == WASTE_ZONE and game.waste:
                card, src = game.waste[-1], 'waste'
            elif zone in TAB_ZONE:
                col = game.tableau[zone - 6]
                card, src = (col[-1], 'tab') if col else (None, None)
            else:
                card = None

            if card:
                for i in range(4):
                    if game.can_place_on_foundation(card, i):
                        if src == 'waste':
                            game.waste.pop()
                        else:
                            col = game.tableau[zone - 6]
                            col.pop()
                            if col and not col[-1].face_up:
                                col[-1].face_up = True
                        game.foundations[i].append(card)
                        break

curses.wrapper(main)