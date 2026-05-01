import curses

def draw_card(win, y, x, rank, suit, is_red, selected=False):
    color = curses.color_pair(2 if is_red else 1)
    border = curses.color_pair(3) if selected else curses.color_pair(1)
    
    # Рамка карты (5 строк x 9 символов)
    win.attron(border)
    win.addstr(y,   x, "┌───────┐")
    win.addstr(y+1, x, "│       │")
    win.addstr(y+2, x, "│       │")
    win.addstr(y+3, x, "│       │")
    win.addstr(y+4, x, "└───────┘")
    win.attroff(border)
    
    # Содержимое
    label = f"{rank}{suit}"
    win.attron(color)
    win.addstr(y+1, x+1, label)           # верхний левый
    win.addstr(y+2, x+3, suit)            # центр
    win.addstr(y+3, x+7-len(label), label) # нижний правый
    win.attroff(color)

def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED,   curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_CYAN,  curses.COLOR_BLACK)
    
    stdscr.clear()
    
    # Тестовые карты
    cards = [
        (2, 2,  "A",  "♠", False),
        (2, 13, "K",  "♥", True),
        (2, 24, "10", "♦", True),
        (2, 35, "J",  "♣", False),
    ]
    
    selected = 0
    
    while True:
        stdscr.clear()
        stdscr.addstr(0, 2, "← → выбор карты   Q выход", curses.color_pair(1))
        
        for i, (y, x, rank, suit, is_red) in enumerate(cards):
            draw_card(stdscr, y, x, rank, suit, is_red, selected=(i == selected))
        
        stdscr.addstr(8, 2, f"Выбрана: {cards[selected][2]}{cards[selected][3]}", curses.color_pair(1))
        
        stdscr.refresh()
        
        key = stdscr.getch()
        if key == ord('q') or key == ord('Q'):
            break
        elif key == curses.KEY_RIGHT:
            selected = (selected + 1) % len(cards)
        elif key == curses.KEY_LEFT:
            selected = (selected - 1) % len(cards)

curses.wrapper(main)