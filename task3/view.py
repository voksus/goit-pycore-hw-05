import os
import shutil

# Константи кольорів (ANSI-коди):
COL_RESET  = '\033[0m'    # Стандартний колір
COL_RED    = '\033[31m'   # Червоний
COL_YELLOW = '\033[33m'   # Жовтий
COL_BLUE   = '\033[34m'   # Синій
COL_GRAY   = '\033[2;37m' # Фіолетовий
COL_CYAN   = '\033[36m'   # Бірюзовий
# Константи для скрол-бара:
BACK_BLUE        = '\033[44m'   # Синій фон
SCROLL_ARROW_UP  = BACK_BLUE + "▲" + COL_RESET
SCROLL_ARROW_DN  = BACK_BLUE + "▼" + COL_RESET
SCROLL_BAR_EMPTY = COL_BLUE + "░" + COL_RESET
SCROLL_BAR_CUR   = COL_CYAN + "█" + COL_RESET

current_start = 0  # Індекс першого відображеного рядка

# Перевірка розміру терміналу щоб контролювати інтерактивний вивід логів (рекомендовано не менше ніж 80×24 символів)
def get_terminal_size():
    """Повертає ширину та висоту терміналу у символах."""
    try:
        size = shutil.get_terminal_size(fallback=(80, 24))  # Значення за замовчуванням (80x24)
    except AttributeError:
        size = os.get_terminal_size(fallback=(80, 24))
    return size.columns, size.lines

cols, rows = get_terminal_size()

# Максимальна кількість рядків логів, що одночасно відображаються
MAX_ROWS_ON_SCREEN = min(20, rows - 4) # Розмір блоку виводу залежить від розміру консолі, але не більше 20 рядків

def view_interactive_log(logs: dict[int:str]):
    """
    Відображає інтерфейс скролінгу логів у терміналі.
    """
    total_logs = len(logs)

    if total_logs == 0:
        print("═" * 120)
        print(f"{COL_YELLOW}(Логів немає){COL_RESET}")
        print("═" * 120)
        return

    print(f"╒{"═" * 4}╡{COL_GRAY} Керування: ↑↓ / PgUp PgDn / Esc для виходу {COL_RESET}╞{"═" * (cols - 53)}╕")

    def draw_screen(start=MAX_ROWS_ON_SCREEN+1):
        # Переміщення курсора у верхню ліву точку для оновлення екрану
        print(f"\r{'\033[A' * start}", end='')
        minimum = min(current_start + MAX_ROWS_ON_SCREEN, total_logs)
        for i in range(current_start, minimum):
            # Визначення символів скрол-бару:
            if i - current_start == 0:
                sb = SCROLL_ARROW_UP    # Верхня стрілка
            elif i - current_start == MAX_ROWS_ON_SCREEN - 1:
                sb = SCROLL_ARROW_DN    # Нижня стрілка
            else:
                sb = SCROLL_BAR_EMPTY   # Порожнє місце на скрол-барі

            # Позиція повзунка на скрол-барі:
            scroll_pos = round((current_start / (total_logs - MAX_ROWS_ON_SCREEN)) * (MAX_ROWS_ON_SCREEN - 3)) + 1
            if i - current_start == scroll_pos:
                sb = SCROLL_BAR_CUR     # Повзунок скрол-бару

            print(f"{sb} {logs[i]}")

        # Вивід інформації про поточну позицію перегляду логів
        pos = f"{current_start+1}-{min(current_start + MAX_ROWS_ON_SCREEN, total_logs)} з {total_logs}"
        print(f"╘{"═" * 4}╡ {COL_CYAN}{pos:^20}{COL_RESET}╞{"═"*(cols - 30)}╛")

    def interactive_win():
        import msvcrt  # Для перехоплення клавіатури (під Windows)
        import ctypes

        global current_start

        # Приховуємо курсор у консолі
        handle = ctypes.windll.kernel32.GetStdHandle(-11)
        class CONSOLE_CURSOR_INFO(ctypes.Structure):
            _fields_ = [("dwSize", ctypes.c_int), ("bVisible", ctypes.c_bool)]
        cursor_info = CONSOLE_CURSOR_INFO()
        ctypes.windll.kernel32.GetConsoleCursorInfo(handle, ctypes.byref(cursor_info))
        cursor_info.bVisible = False
        ctypes.windll.kernel32.SetConsoleCursorInfo(handle, ctypes.byref(cursor_info))

        draw_screen(0)
        while True:
            key = msvcrt.getch()
            
            if key == b'\x1b':  # Esc
                break
            elif key == b'H':  # Стрілка вгору
                if current_start > 0:
                    current_start -= 1
            elif key == b'P':  # Стрілка вниз
                if current_start < total_logs - MAX_ROWS_ON_SCREEN:
                    current_start += 1
            elif key == b'\x49':  # PgUp
                current_start = max(0, current_start - MAX_ROWS_ON_SCREEN)
            elif key == b'\x51':  # PgDn
                current_start = min(total_logs - MAX_ROWS_ON_SCREEN, current_start + MAX_ROWS_ON_SCREEN)
            draw_screen()

        # Відновлює курсор
        cursor_info.bVisible = True
        ctypes.windll.kernel32.SetConsoleCursorInfo(handle, ctypes.byref(cursor_info))

    def interactive_unix(stdscr):
        import curses  # Для перехоплення клавіатури (під Linux/macOS)

        global current_start
        curses.curs_set(0)  # Приховуємо курсор
        draw_screen(0)
        while True:
            key = stdscr.getch()
            
            if key == 27:  # Esc
                break
            elif key == curses.KEY_UP:
                if current_start > 0:
                    current_start -= 1
            elif key == curses.KEY_DOWN:
                if current_start < total_logs - MAX_ROWS_ON_SCREEN:
                    current_start += 1
            elif key == curses.KEY_PPAGE:
                current_start = max(0, current_start - MAX_ROWS_ON_SCREEN)
            elif key == curses.KEY_NPAGE:
                current_start = min(total_logs - MAX_ROWS_ON_SCREEN, current_start + MAX_ROWS_ON_SCREEN)
            draw_screen()

    if os.name == 'nt':
        interactive_win()
    else:
        curses.wrapper(interactive_unix)

# Запуск головного модуля у випадку якщо забув переключитись на нього у VS Code
if __name__ == "__main__":
    import t3
    t3.main()