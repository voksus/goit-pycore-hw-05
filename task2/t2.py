from typing import Callable, Generator
import re

print("\033[H\033[J", end='')  # Переміщує курсор у верхній лівий кут і очищує екран

def generator_numbers(text: str):
    for num in re.findall(r"\d+\.\d+", text):
        yield float(num)  # Повертаємо кожне знайдене число по черзі

def sum_profit(text: str, func: Callable[[str], Generator[float, None, None]]) -> float:
    return sum(func(text))


text = "Загальний дохід працівника складається з декількох частин: 1000.01 як основний дохід, доповнений додатковими надходженнями 27.45 і 324.00 доларів."
gen = generator_numbers(text)

total_income = sum_profit(text, generator_numbers)
print(f"Загальний дохід: {total_income}")