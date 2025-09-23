import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Очистка (если таблицы уже существуют)
cursor.execute('DROP TABLE IF EXISTS WebUsers')
cursor.execute('DROP TABLE IF EXISTS AppUsers')
cursor.execute('DROP TABLE IF EXISTS BothUsers')

# Создание таблиц
cursor.execute('''
CREATE TABLE WebUsers (
    UserID INTEGER,
    UserName TEXT
)
''')

cursor.execute('''
CREATE TABLE AppUsers (
    UserID INTEGER,
    UserName TEXT
)
''')

# Примерные данные
web_users = [
    (1, 'Taeyong'),
    (2, 'Mark'),
    (3, 'Jaehyun'),
    (4, 'Yuta')
]

app_users = [
    (2, 'Mark'),
    (3, 'Jaehyun'),
    (5, 'Johnny'),
    (6, 'Haechan')
]

# Вставка данных
cursor.executemany('INSERT INTO WebUsers VALUES (?, ?)', web_users)
cursor.executemany('INSERT INTO AppUsers VALUES (?, ?)', app_users)

# Создание таблицы с общими пользователями
cursor.execute('''
CREATE TABLE BothUsers AS
SELECT UserID, UserName
FROM WebUsers
INTERSECT
SELECT UserID, UserName
FROM AppUsers
''')

conn.commit()
conn.close()
