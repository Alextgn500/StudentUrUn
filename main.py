# Исходные данные
my_list = [42, 69, 322, 13, 0, 99, -5, 9, 8, 7, -6, 5]

# Инициализация индекса
index = 0

# Цикл while для перебора списка
while index < len(my_list):
    # Получаем текущий элемент
    current_element = my_list[index]

    # Проверяем условия
    if current_element < 0:
        break  # Прерываем цикл, если встретили отрицательное число
    elif current_element > 0:
        print(current_element)  # Выводим только положительные числа

    # Увеличиваем индекс
    index += 1
