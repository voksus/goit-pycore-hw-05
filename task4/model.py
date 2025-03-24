import csv
from typing import Dict

# Типова структура контактів
ContactBook = Dict[str, str]

# Шлях до файлу збереження
DATA_FILE = "contacts.csv"

def load_contacts() -> ContactBook:
    """
    Завантажити контакти з CSV-файлу.
    Якщо файл не існує або виникає помилка — повертається порожній словник.
    """
    contacts: ContactBook = {}
    try:
        with open(DATA_FILE, mode="r", encoding="utf-8", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) == 2:
                    name, phone = row
                    contacts[name] = phone
    except FileNotFoundError:
        return {}
    except Exception:
        return {}
    return contacts

def save_contacts(contacts: ContactBook) -> None:
    """
    Зберегти контакти у CSV-файл.
    """
    with open(DATA_FILE, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        for name, phone in contacts.items():
            writer.writerow([name, phone])

def add_contact(contacts: ContactBook, name: str, phone: str) -> None:
    """
    Додати новий контакт або перезаписати існуючий.
    """
    contacts[name] = phone

def change_contact(contacts: ContactBook, name: str, phone: str) -> None:
    """
    Змінити номер телефону для існуючого контакту.
    Якщо ім'я не знайдене — кидається виняток KeyError.
    """
    if name not in contacts:
        raise KeyError("Contact not found")
    contacts[name] = phone

def remove_contact(contacts: ContactBook, name: str) -> None:
    """
    Видалити контакт за іменем. Якщо не знайдено — KeyError.
    """
    if name not in contacts:
        raise KeyError("Contact not found")
    del contacts[name]

def get_phone(contacts: ContactBook, name: str) -> str:
    """
    Отримати номер телефону за іменем. Якщо не знайдено — KeyError.
    """
    if name not in contacts:
        raise KeyError("Contact not found")
    return contacts[name]
