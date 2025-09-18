import sqlite3
import os

# Удалим старую базу данных, чтобы начать с чистого листа
db_filename = 'test.db'
if os.path.exists(db_filename):
    os.remove(db_filename)

# Подключение к новой базе
conn = sqlite3.connect(db_filename)
cursor = conn.cursor()

# Создание таблиц
cursor.execute('''
CREATE TABLE Courses (
    course_id INTEGER PRIMARY KEY,
    course_title TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE Enrollments (
    enrollment_id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL,
    course_id INTEGER,
    enrollment_date TEXT,
    FOREIGN KEY(course_id) REFERENCES Courses(course_id)
)
''')

# Вставка данных в Courses
cursor.executemany('INSERT INTO Courses (course_id, course_title) VALUES (?, ?)', [
    (1, 'Python Basics'),
    (2, 'Data Science'),
    (3, 'Algorithms'),
    (4, 'Machine Learning'),
])

# Вставка данных в Enrollments (только для некоторых курсов)
cursor.executemany('INSERT INTO Enrollments (enrollment_id, student_id, course_id, enrollment_date) VALUES (?, ?, ?, ?)', [
    (1, 101, 1, '2025-09-01'),
    (2, 102, 2, '2025-09-02'),
])

conn.commit()

# SQL-запрос: найти курсы без регистраций
query = '''
SELECT c.course_id, c.course_title
FROM Courses c
LEFT JOIN Enrollments e ON c.course_id = e.course_id
WHERE e.enrollment_id IS NULL;
'''

cursor.execute(query)
results = cursor.fetchall()

# Вывод результатов
print("Курсы без регистраций:")
if results:
    for course_id, course_title in results:
        print(f"- {course_id}: {course_title}")
else:
    print("Все курсы имеют регистрации.")

# Закрытие соединения
conn.close()
