my_list = [42, 69, 322, 13, 0, 99, -5, 9, 8, 7, -6, 5]

# Первая часть: до первого отрицательного числа
index = 0
while index < len(my_list) and my_list[index] >= 0:
    if my_list[index] > 0:
        print("Положительное число до отрицательного:", my_list[index])
    index += 1

# Вторая часть: после первого отрицательного числа
if index < len(my_list):
    print("Найдено отрицательное число:", my_list[index])
    index += 1
    while index < len(my_list):
        if my_list[index] > 0:
            print("Положительное число после отрицательного:", my_list[index])
        index += 1

print("Просмотр списка завершен")


