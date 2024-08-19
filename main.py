numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

# Создаем пустые списки для простых и не простых чисел
primes = []
not_primes = []

# Перебираем числа из списка numbers
for num in numbers:
    # Отмечаем число как простое изначально (флаг)
    is_prime = True

    # Проверяем, является ли число простым
    if num > 1:
        for i in range(2, int(num ** 0.5) + 1):
            if num % i == 0:
                is_prime = False
                break  # Оптимизация: прерываем цикл, если нашли делитель
    else:
        is_prime = False  # 1 не является простым числом

    # Добавляем число в соответствующий список
    if is_prime:
        primes.append(num)
    elif num != 1:  # Исключаем 1 из списка not_primes
        not_primes.append(num)

# Выводим результаты
print("Простые числа:", primes)
print("Не простые числа:", not_primes)

