import time
import random as rnd
import view as v
import model as mdl
from functools import wraps

rnd.seed(time.perf_counter())

def input_error(func):
    '''
    Декоратор для обробки помилок користувача при взаємодії з функціями.
    Він перехоплює помилки KeyError, ValueError, IndexError і повертає відповідні повідомлення.
    Також повертає булеве значення, якщо функція завершується успішно, щоб сигналізувати про потребу зберегти зміни.
    '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result if result else False
        except KeyError:
            v.error("Контакту не знайдено.")
        except ValueError:
            v.error("Введіть ім’я та номер телефону через пробіл.")
        except IndexError:
            v.error("Команда введена без необхідних аргументів.")
        return False
    return wrapper

def parse_input(cmd: str) -> tuple[str, list[str]]:
    '''Розділяє введену команду на ключове слово і список аргументів'''
    parts = cmd.split()
    command = parts[0].lower()
    args = parts[1:] if len(parts) > 1 else []
    return command, args

def sanitize_input(name: str, number: str):
    '''
    Функція очищення імені/номера від заборонених символів для збереження в CSV.
    Замінює символи ',', '"' та інші небажані символи на підкреслення '_'.
    Повертає кортеж (очищене_ім'я, очищений_номер).
    Виводить повідомлення лише якщо хоча б один елемент було змінено.
    '''
    msg_parts = []
    if any(c in name for c in [',', '"']):
        name = ''.join('_' if c in [',', '"'] else c for c in name)
        msg_parts.append("Ім’я")
    if any(c in number for c in [',', '"']):
        number = ''.join('_' if c in [',', '"'] else c for c in number)
        msg_parts.append("номер")
    if msg_parts:
        prefix = " та ".join(msg_parts).capitalize()
        note = f"{prefix} містить недопустимі символи. Їх буде замінено на нижнє підкреслення '_'"
        v.warn(note)
    return name, number

def get_cmd() -> str:
    '''Отримання команди від користувача через view (MVC підхід)'''
    return v.ask().strip()

def quit(args=None, contacts=None):
    '''Стандартне завершення роботи'''
    v.info("До побачення 👋")
    exit(0)

def hello(args=None, contacts=None):
    '''Привітання користувача при запуску'''
    v.lines_clean()
    options = (
        'Привіт! Чим можу допомогти?', 'Вітаю! Я тут, щоб допомогти.', 'Добрий день! Я до ваших послуг.',
        'Привіт, як справи?', 'Гей, як ся маєш?', 'Привіт-привіт! Що треба? 😉', 'Гей! Чекаю на твої команди.',
        'Йо! Що сьогодні робимо?', 'О, привітулі!', 'Слухаю уважно 🤖', 'Чим можу допомогти, друже?',
        'Вітаю! Як можу бути корисним?', 'Добрий день! Що вас цікавить?', 'Ласкаво прошу! Чим можу допомогти?',
        'Сервіс активовано. Що вам потрібно?', 'Біп-буп! Робобот до ваших послуг! 🤖',
        'Завантаження ввічливості... 100% – Привіт!', 'Хтось викликав штучний інтелект? 👀',
        'Привіт, людська істото! Що потрібно?', 'Хей! Давай працювати! 🚀', 'Здоровенькі були! Що треба?',
        'Поїхали! Я готовий до роботи!', 'Готовий до виклику! Що потрібно?', 'Я тут! Почнімо.',
        'Адресна книга відкрита! Що робимо?', 'Запити приймаються! Чим допомогти?',
        'Когось шукаємо? Я готовий!', 'Контакти? Команди? Що цікавить?', 'Починаємо роботу. Введіть команду.'
    )
    v.info(options[rnd.randint(0, len(options) - 1)])
    v.lines += 1

@input_error
def add_contact(args, contacts):
    '''Додати контакт (якщо ім’я ще не існує)'''
    if len(args) != 2:
        raise ValueError
    name, number = sanitize_input(*args)
    if name in contacts:
        v.contact_already_exists(name)
        return False
    contacts[name] = number
    v.contact_added(name, number)
    return True

@input_error
def change_contact(args, contacts):
    '''Змінити номер для існуючого контакта'''
    if len(args) != 2:
        raise KeyError
    name, number = sanitize_input(*args)
    if name not in contacts:
        raise KeyError
    contacts[name] = number
    v.contact_changed(name, number)
    return True

@input_error
def remove_contact(args, contacts:dict):
    '''Видалити контакт з адресної книги'''
    if len(args) != 1:
        raise IndexError
    name = args[0]
    if name not in contacts:
        raise KeyError
    contacts.pop(name)
    v.contact_deleted(name)
    return True

@input_error
def show_phone(args, contacts):
    '''Показати номер для зазначеного контакта'''
    if len(args) != 1:
        raise IndexError
    name = args[0]
    if name not in contacts:
        raise KeyError
    v.contact_found(name, contacts[name])

def show_all(args=None, contacts=None):
    '''Показати всі контакти'''
    if not contacts:
        v.contacts_not_found()
    else:
        v.show_all_contacts(contacts)

def help(args=None, contacts=None):
    '''Показати довідку (справку)'''
    v.show_help()

def unknown_command(cmd: str):
    '''Обробка неправильної команди'''
    v.lines_clean()
    v.unknown_command(cmd)
    v.lines += 1

COMMANDS = {
    'hi': hello,
    'hello': hello,
    'привіт': hello,
    'quit': quit,
    'exit': quit,
    'close': quit,
    'add': add_contact,
    'change': change_contact,
    'remove': remove_contact,
    'phone': show_phone,
    'all': show_all,
    'clr': v.clear_screen,
    '?': help
}

def execute(command: str, args: list[str], contacts: dict):
    '''Виконує команду, зберігаючи зміни при необхідності'''
    handler = COMMANDS.get(command)
    if handler:
        was_changed = handler(args, contacts)
        if command in ('add', 'change', 'remove') and was_changed:
            mdl.save_contacts(contacts)
    else:
        unknown_command(command)
