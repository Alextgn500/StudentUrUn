# Функция для выполнения проверки
def check_equal_numbers(a, b, c):
    if a == b == c:
        return 3
    elif a == b or b == c or a == c:
        return 2
    else:
        return 0

# Сценарий 1: Все числа разные
print("Сценарий 1: Все числа разные")
first, second, third = 123,456,789
result = check_equal_numbers(first, second, third)
print(f"Числа: {first}, {second}, {third}")
print(f"Результат: {result}\n")

# Сценарий 2: Два числа равны
print("Сценарий 2: Два числа равны")
first, second, third = 42,69,42
result = check_equal_numbers(first, second, third)
print(f"Числа: {first}, {second}, {third}")
print(f"Результат: {result}\n")

# Сценарий 3: Все числа равны
print("Сценарий 3: Все числа равны")
first, second, third = 5, 5, 5
result = check_equal_numbers(first, second, third)
print(f"Числа: {first}, {second}, {third}")
print(f"Результат: {result}")











