import sqlite3
import os

# === Удалим базу, если она уже существует, для чистого запуска ===
if os.path.exists('students.db'):
    os.remove('students.db')

# === Подключение к файлу базы данных ===
conn = sqlite3.connect('students.db')
cursor = conn.cursor()

# === Создание таблиц ===

# Основная таблица студентов
cursor.execute('''
CREATE TABLE Students (
    StudentID INTEGER PRIMARY KEY,
    FirstName TEXT,
    LastName TEXT
);
''')

# Курсы
cursor.execute('''
CREATE TABLE Courses (
    CourseID INTEGER PRIMARY KEY,
    CourseName TEXT
);
''')

# Записи о зачислении
cursor.execute('''
CREATE TABLE Enrollments (
    EnrollmentID INTEGER PRIMARY KEY,
    StudentID INTEGER,
    CourseID INTEGER,
    FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
    FOREIGN KEY (CourseID) REFERENCES Courses(CourseID)
);
''')

# Новая таблица для студентов с фамилией на "И"
cursor.execute('''
CREATE TABLE FilteredStudents (
    StudentID INTEGER PRIMARY KEY,
    FirstName TEXT,
    LastName TEXT
);
''')

# === Данные студентов ===
students_data = [
    (1, 'Чунмен', 'Ким'),      
    (2, 'Бэкхен', 'Бен'),         
    (3, 'Чанель', 'Пак'),  
    (4, 'Кенсу', 'До'),          
    (5, 'Сехун', 'О'),       
    (6, 'Кай', 'Ким'),              
    (7, 'Сюмин', 'Ким'),        
    (8, 'Чен', 'Ким'), 
    # Персонажи аниме с фамилией на И
    (9, 'Итачи', 'Ичига'),
    (10, 'Идзуку', 'Изуку'),
    (11, 'Инуяша', 'Инуяша'),
]

# === Курсы ===
courses_data = [
    (1, 'Вокал'),
    (2, 'Танцы'),
    (3, 'Японский язык'),
]

# === Зачисления ===
enrollments_data = [
    (1, 1, 1),
    (2, 2, 2),
    (3, 3, 1),
    (4, 4, 3),
    (5, 5, 2),
    (6, 6, 1),
    (7, 7, 3),
    (8, 8, 2),
    (9, 1, 3),
    (10, 9, 1),
    (11, 10, 2),
    (12, 11, 3),
]

# === Заполнение основной базы ===
cursor.executemany('INSERT INTO Students VALUES (?, ?, ?);', students_data)
cursor.executemany('INSERT INTO Courses VALUES (?, ?);', courses_data)
cursor.executemany('INSERT INTO Enrollments VALUES (?, ?, ?);', enrollments_data)

# === Копируем студентов с фамилией на "И" в отдельную таблицу ===
cursor.execute('''
INSERT INTO FilteredStudents (StudentID, FirstName, LastName)
SELECT StudentID, FirstName, LastName
FROM Students
WHERE LastName LIKE 'И%';
''')

# === Сохраняем и закрываем ===
conn.commit()
conn.close()

print("✅ База 'students.db' создана.")
print("✅ Таблица 'FilteredStudents' заполнена студентами с фамилией на 'И'.")
