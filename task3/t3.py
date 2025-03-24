import collections
import sys
import view
from enum import Enum
from typing import List, Dict, Set

# Константи для кольорів (ANSI-коди)
COL_RESET      = '\033[0m'      # Стандартний колір
COL_RED        = '\033[31m'     # Червоний
COL_GREEN      = '\033[32m'     # Зелений
COL_YELLOW     = '\033[33m'     # Жовтий
COL_BLUE       = '\033[34m'     # Синій
COL_GRAY       = '\033[30m'     # Сірий
COL_INV_YELLOW = '\033[1;7;33m' # Інверсний жовтий жирний (на зеленому фоні)
COL_INV_RED    = '\033[41m'     # Інверсний червоний (на червоному фоні)
COL_INV_GREEN  = '\033[1;42m'   # Інверсний зелений жирний (на зеленому фоні)

print("\033[H\033[J", end='')  # Переміщує курсор у верхній лівий кут і очищує екран

# Рівні логування
class LogLevel(Enum):
    CRITICAL = ("CRITICAL", COL_INV_RED)  # Інверсний червоний
    FATAL    = ("FATAL",    COL_INV_RED)  # Інверсний червоний
    ERROR    = ("ERROR",    COL_RED)      # Червоний
    WARN     = ("WARN",     COL_YELLOW)   # Жовтий
    INFO     = ("INFO",     COL_GREEN)    # Зелений
    DEBUG    = ("DEBUG",    COL_BLUE)     # Синій
    TRACE    = ("TRACE",    COL_RESET)    # Стандартний
    VERBOSE  = ("VERBOSE",  COL_RESET)    # Стандартний

    @property
    def color(self):
        return self.value[1]

    @property
    def label(self):
        return self.value[0]

    @classmethod
    def from_string(cls, level_str: str):
        level = next(filter(lambda lvl: lvl.label == level_str, cls), None)
        if level is not None:
            return level
        raise ValueError("Невідомий рівень логування")

# Завантаження логів із файлу
def load_logs(file_path: str) -> List[str]:
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()
        return lines
    except FileNotFoundError:
        print(f"{COL_RED}❌ Файл {COL_YELLOW}{file_path}{COL_RED} не знайдено!{COL_RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{COL_RED}❌ Невідома помилка:\n{e}{COL_RESET}")
        sys.exit(0)

# Парсинг окремого рядка логу
def parse_log_line(line: str) -> dict:
    parts = line.strip().split(maxsplit=3)
    if len(parts) < 4:
        raise ValueError("Некоректний формат рядка логу")

    timestamp, level_str, description = f"{parts[0]} {parts[1]}", parts[2], parts[3]

    try:
        log_level = LogLevel.from_string(level_str)
    except ValueError:
        raise ValueError("Невідомий рівень логування")

    return {"timestamp": timestamp, "level": log_level, "description": description}

# Фільтрація логів за рівнями
def filter_logs_by_level(logs: Dict[int, Dict], levels: Set[LogLevel]) -> Dict[int, Dict]:
    return {new_index: log for new_index, log in enumerate(log for log in logs.values() if "level" in log and log["level"] in levels)}

# Обгортка для форматування логів з кольорами
def format_logs_with_colors(logs: Dict[int, Dict], include_invalid: bool = False) -> Dict[int, str]:
    formatted_logs = {}
    for index, log in logs.items():
        if "level" in log:
            level : LogLevel = log["level"]
            formatted_logs[index] = f"{log['timestamp']} {level.color}{level.label:5}{COL_RESET} {log['description']}\033[K"
        elif include_invalid:
            formatted_logs[index] = f"{COL_RED}!Некоректний запис!{COL_GRAY} : — : {COL_YELLOW}{log['raw']}\033[K{COL_RESET}"
    return formatted_logs

# Підрахунок кількості логів за рівнями
def count_logs_by_level(logs: Dict[int, Dict]) -> Dict[LogLevel, int]:
    counter = collections.Counter(log["level"] for log in logs.values() if "level" in log and isinstance(log["level"], LogLevel))
    return dict(counter)

# Виведення статистики
def display_log_counts(counts: Dict[LogLevel, int]):
    print("╔══════════════════╤═══════════╗")
    print("║ Рівень логування │ Кількість ║")
    print("╟──────────────────┼───────────╢")

    # Сортуємо рівні за порядком у LogLevel
    sorted_levels = [lvl for lvl in LogLevel if lvl in counts]
    
    for level in sorted_levels:
        count = counts[level]
        print(f"║ {level.color}{level.label:<16}{COL_RESET} │ {level.color}{count:<9}{COL_RESET} ║")

    print("╚══════════════════╧═══════════╝")

def main():
    args = sys.argv[1:]

    if not args or "--help" in args or "-h" in args:
        print(f"╔{'═' * 65}╗")
        print(f"║  {COL_GREEN}Використання: python t3.py <file.log> [--all | --level LEVEL]  {COL_RESET}║")
        print(f"║  {COL_YELLOW}Приклад:{COL_RESET} python t3.py logfile.log --level ERROR')              {COL_RESET}║")
        print(f"╚{'═' * 65}╝")
        sys.exit()

    file_path = args[0]
    logs_raw = [line for line in load_logs(file_path) if line.strip()]

    parsed_logs : dict[int,str] = {}
    incorrect_count = 0

    for idx, line in enumerate(logs_raw):
        try:
            parsed_logs[idx] = parse_log_line(line)
        except ValueError:
            parsed_logs[idx] = {"raw": line.strip()}
            incorrect_count += 1

    counts = count_logs_by_level(parsed_logs)
    display_log_counts(counts)

    if incorrect_count:
        print(f"{COL_INV_YELLOW} Увага! Файл містить некоректні рядки. Кількість: {incorrect_count} шт. {COL_RESET}")

    if any(arg in args for arg in ["--all", "-a", "ALL"]):
        print(f"\n{COL_INV_GREEN} Деталі логів (всі записи файлу): {COL_RESET}")
        filtered_logs = format_logs_with_colors(parsed_logs, include_invalid=True)

        # ====ІНТЕРАКТИВНИЙ ВИВІД В КОНСОЛЬ (СКРОЛІНГ КЛАВІАТУРОЮ)=====
        view.view_interactive_log(filtered_logs)
        # =============================================================
    elif "--level" in args:
        level_index = args.index("--level") + 1
        if level_index < len(args):
            level_strs = map(str.upper, args[level_index:])
            try:
                levels = {LogLevel.from_string(level_str) for level_str in level_strs}
                # Фільтрація логів по типам
                filtered_logs = filter_logs_by_level(parsed_logs, levels)
                print(f"\n{COL_INV_GREEN} Рівні: {', '.join(level.label for level in levels)}. Деталі логів: {COL_RESET}")
                # Мапінг логів: перетворення значення внутрішнього словника на кольоровий рядок
                filtered_logs = format_logs_with_colors(filtered_logs)

                # ІНТЕРАКТИВНИЙ ВИВІД В КОНСОЛЬ (СКРОЛІНГ КЛАВІАТУРОЮ)
                view.view_interactive_log(filtered_logs)
                # ====================================================
            except ValueError:
                print(f"{COL_RED}Помилка: невідомий рівень логування в списку '{', '.join(level_strs)}'{COL_RESET}")
                sys.exit(1)
        else:
            print(f"{COL_RED}Помилка: рівень логування не вказано після '--level'{COL_RESET}")
            sys.exit(1)

if __name__ == "__main__":
    main()