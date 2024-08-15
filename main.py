grades = [[5, 3, 3, 5, 4], [2, 2, 2, 3], [4, 5, 5, 2], [4, 4, 3], [5, 5, 5, 4, 5]]
students = {'Johnny', 'Bilbo', 'Steve', 'Khendrik', 'Aaron'}
students_list = sorted(students)
print(students_list)
result = {}
#Объединяем списки students_list и grades с использованием zip()
for student, grades_list in zip(students_list, grades):
    average = sum(grades_list)/len(grades_list)
    #округляем до двух знаков после запятой
    average_grade = round(average, 2)
    #добавляем пару "ученик : средний бал" в словарь
    result[student] = average_grade
# Выводим результат
print("Средние баллы учеников")
for student, average in result.items():
    print(f"{student}: {average}")

