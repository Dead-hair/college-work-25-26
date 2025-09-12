import sqlite3
import os

db_file = 'cinema.db'

# Удаляем старую базу, если есть
if os.path.exists(db_file):
    os.remove(db_file)

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Создаем таблицы
cursor.executescript("""
CREATE TABLE Genres (
    GenreID INTEGER PRIMARY KEY,
    GenreName TEXT
);

CREATE TABLE Movies (
    MovieID INTEGER PRIMARY KEY,
    Title TEXT,
    Year INTEGER,
    GenreID INTEGER,
    FOREIGN KEY (GenreID) REFERENCES Genres(GenreID)
);

CREATE TABLE Halls (
    HallID INTEGER PRIMARY KEY,
    HallName TEXT,
    Capacity INTEGER
);

CREATE TABLE Sessions (
    SessionID INTEGER PRIMARY KEY,
    MovieID INTEGER,
    HallID INTEGER,
    SessionDate TEXT,
    TicketPrice REAL,
    FOREIGN KEY (MovieID) REFERENCES Movies(MovieID),
    FOREIGN KEY (HallID) REFERENCES Halls(HallID)
);

CREATE TABLE Customers (
    CustomerID INTEGER PRIMARY KEY,
    FirstName TEXT,
    LastName TEXT,
    City TEXT
);

CREATE TABLE Tickets (
    TicketID INTEGER PRIMARY KEY,
    SessionID INTEGER,
    CustomerID INTEGER,
    SeatNumber TEXT,
    FOREIGN KEY (SessionID) REFERENCES Sessions(SessionID),
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
);
""")

# Заполняем таблицы
cursor.executemany("INSERT INTO Genres (GenreID, GenreName) VALUES (?, ?);", [
    (1, 'Боевик'),
    (2, 'Драма'),
    (3, 'Научная фантастика')
])

cursor.executemany("INSERT INTO Movies (MovieID, Title, Year, GenreID) VALUES (?, ?, ?, ?);", [
    (1, 'Космическая одиссея', 2025, 3),
    (2, 'Героическая сага', 2024, 1),
    (3, 'Истории жизни', 2023, 2)
])

cursor.executemany("INSERT INTO Halls (HallID, HallName, Capacity) VALUES (?, ?, ?);", [
    (1, 'Главный зал', 150)
])

cursor.executemany("INSERT INTO Sessions (SessionID, MovieID, HallID, SessionDate, TicketPrice) VALUES (?, ?, ?, ?, ?);", [
    (1, 1, 1, '2025-09-20 18:00:00', 1500),
    (2, 2, 1, '2025-09-21 20:00:00', 1500),
    (3, 3, 1, '2025-09-22 19:00:00', 1500),
    (4, 1, 1, '2025-09-23 18:30:00', 1500)
])

cursor.executemany("INSERT INTO Customers (CustomerID, FirstName, LastName, City) VALUES (?, ?, ?, ?);", [
    (1, 'Тэён', 'Ли', 'Сеул'),
    (2, 'Джонхён', 'Сё', 'Чикаго'),
    (3, 'Марк', 'Ли', 'Ванкувер'),
    (4, 'Тэиль', 'Мун', 'Сеул'),
    (5, 'Юта', 'Накамото', 'Осака')
])

tickets = [
    (1, 1, 1, 'A1'),
    (2, 2, 1, 'B2'),

    (3, 1, 2, 'A2'),
    (4, 2, 2, 'B3'),
    (5, 3, 2, 'C1'),
    (6, 4, 2, 'D4'),

    (7, 3, 3, 'C2'),
    (8, 2, 4, 'B4'),
    (9, 4, 5, 'D5'),
]

cursor.executemany("INSERT INTO Tickets (TicketID, SessionID, CustomerID, SeatNumber) VALUES (?, ?, ?, ?);", tickets)

conn.commit()

# SQL запрос, который выводит всю подробную информацию
query_all = """
SELECT
    M.Title AS 'Название фильма',
    G.GenreName AS 'Жанр',
    S.SessionDate AS 'Дата и время сеанса',
    C.FirstName AS 'Имя',
    C.LastName AS 'Фамилия',
    C.City AS 'Город',
    S.TicketPrice AS 'Цена билета'
FROM Tickets T
JOIN Sessions S ON T.SessionID = S.SessionID
JOIN Movies M ON S.MovieID = M.MovieID
JOIN Genres G ON M.GenreID = G.GenreID
JOIN Customers C ON T.CustomerID = C.CustomerID
ORDER BY S.SessionDate;
"""

cursor.execute(query_all)
rows = cursor.fetchall()

print("Все билеты с деталями:\n")
for row in rows:
    print(f"{row[0]}, {row[1]}, {row[2]}, {row[3]} {row[4]}, {row[5]}, Цена: {row[6]} тг")

# Запрос для нахождения клиентов с 2 и более билетами на разные сеансы
query_multi_tickets = """
SELECT 
    C.FirstName,
    C.LastName,
    COUNT(DISTINCT T.SessionID) AS SessionsCount
FROM Tickets T
JOIN Customers C ON T.CustomerID = C.CustomerID
GROUP BY T.CustomerID
HAVING SessionsCount >= 2;
"""

cursor.execute(query_multi_tickets)
multi_ticket_customers = cursor.fetchall()

print("\nКлиенты, купившие не менее 2 билетов на разные сеансы:\n")
for cust in multi_ticket_customers:
    print(f"{cust[0]} {cust[1]} — билетов на разные сеансы: {cust[2]}")

conn.close()
