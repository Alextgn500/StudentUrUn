
# Создаем телефонную книгу
numbers = [1234567, 1234568, 1234569, 1234570, 1234571]
names = {'Jonny', 'Bilbo', 'Steve', 'Khendrik', 'Aaron'}

# Сортируем имена в алфавитном порядке
names_list = sorted(names)

# Создаем словарь, связывающий имя и номер телефона
phone_book = {}
for i, name in enumerate(names_list):
    phone_book[name] = numbers[i]

# Выводим телефонную книгу
for name, number in phone_book.items():
    print(f"{name}: {number}")

