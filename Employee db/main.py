import sqlite3

# Подключение к базе данных (файл или в памяти)
conn = sqlite3.connect('employees.db')
cursor = conn.cursor()

# Удалим таблицы, если они уже есть (для чистого запуска)
cursor.execute('DROP TABLE IF EXISTS Employees')
cursor.execute('DROP TABLE IF EXISTS FormerEmployees')
cursor.execute('DROP TABLE IF EXISTS NeverFiredEmployees')
cursor.execute('DROP TABLE IF EXISTS NotRehiredFormerEmployees')

# Создание таблицы текущих сотрудников
cursor.execute('''
CREATE TABLE Employees (
    EmployeeID INTEGER,
    FullName TEXT,
    Department TEXT
)
''')

# Создание таблицы бывших сотрудников
cursor.execute('''
CREATE TABLE FormerEmployees (
    EmployeeID INTEGER,
    FullName TEXT,
    Department TEXT
)
''')

# Примерные данные
current_employees = [
    (1, 'Пак Чпнель', 'Music'),
    (2, 'Ким Чонин', 'Music'),
    (3, 'О Сехун', 'Music'),
    (4, 'Ким Чунмен', 'Music'),
    
]

former_employees = [
    (1, 'Бен Бэкхен', 'Music'),
    (3, 'Ким Минсок', 'Music'),
    (6, 'Ким Чондэ', 'Music'),  # Ранее был в группе
    (7, 'До Кенсу', 'Music')  # Ранний участник
]

# Вставка данных
cursor.executemany('INSERT INTO Employees VALUES (?, ?, ?)', current_employees)
cursor.executemany('INSERT INTO FormerEmployees VALUES (?, ?, ?)', former_employees)

# Сотрудники, которые сейчас работают, но никогда не увольнялись
cursor.execute('''
CREATE TABLE NeverFiredEmployees AS
SELECT EmployeeID, FullName, Department
FROM Employees
EXCEPT
SELECT EmployeeID, FullName, Department
FROM FormerEmployees
''')

# Сотрудники, которые уволились и не были приняты снова
cursor.execute('''
CREATE TABLE NotRehiredFormerEmployees AS
SELECT EmployeeID, FullName, Department
FROM FormerEmployees
EXCEPT
SELECT EmployeeID, FullName, Department
FROM Employees
''')

conn.commit()
conn.close()
