const Database = require('better-sqlite3');

// Создаем/открываем БД
const db = new Database('online_library.db');

// Удаляем таблицы, если они уже существуют
db.exec(`
  DROP TABLE IF EXISTS Reviews;
  DROP TABLE IF EXISTS Books;
  DROP TABLE IF EXISTS Genres;
  DROP TABLE IF EXISTS Authors;
  DROP TABLE IF EXISTS Users;
`);

// Таблица Users
db.exec(`
  CREATE TABLE Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    registration_date TEXT NOT NULL
  );
`);

// Таблица Authors
db.exec(`
  CREATE TABLE Authors (
    author_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    birth_year INTEGER
  );
`);

// Таблица Genres
db.exec(`
  CREATE TABLE Genres (
    genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
  );
`);

// Таблица Books
db.exec(`
  CREATE TABLE Books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    publish_year INTEGER,
    author_id INTEGER,
    genre_id INTEGER,
    FOREIGN KEY (author_id) REFERENCES Authors(author_id),
    FOREIGN KEY (genre_id) REFERENCES Genres(genre_id)
  );
`);

// Таблица Reviews
db.exec(`
  CREATE TABLE Reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    book_id INTEGER,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    review_date TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (book_id) REFERENCES Books(book_id)
  );
`);

// Вставка данных — Authors
db.exec(`
  INSERT INTO Authors (full_name, birth_year) VALUES
    ('Достоевский Фёдор Михайлович', 1821),
    ('Лев Толстой', 1828),
    ('Мидина Мирай', 1990),
    ('Джоан Роулинг', 1965),
    ('Колсон Уайтхед', 1969),
    ('Харуки Мураками', 1949),
    ('Салли Руни', 1991);
`);

// Вставка данных — Genres
db.exec(`
  INSERT OR IGNORE INTO Genres (name) VALUES
    ('Роман'),
    ('Фантастика'),
    ('Романтика'),
    ('Детектив'),
    ('Антиутопия'),
    ('Историческая проза'),
    ('Социальная драма'),
    ('Магический реализм'),
    ('Философская проза'),
    ('Сюрреализм'),
    ('Современная проза'),
    ('Роман о взаимоотношениях');
`);

// Вставка данных — Users
db.exec(`
  INSERT INTO Users (name, email, password, registration_date) VALUES
    ('Алексей Иванов', 'alex@example.com', 'pass123', '2023-01-15'),
    ('Мария Смирнова', 'maria@example.com', 'secure456', '2023-03-10'),
    ('Иван Петров', 'ivan@example.com', 'qwerty789', '2023-05-22');
`);

// Вставка данных — Books 
db.exec(`
  INSERT INTO Books (title, publish_year, author_id, genre_id) VALUES
    ('Преступление и наказание', 1866, 1, 1),
    ('Война и мир', 1869, 2, 1),
    ('Воскресни за 40 дней', 2021, 3, 5),
    ('Гарри Поттер и философский камень', 1997, 4, 3),
    ('Гарри Поттер и Тайная комната', 1998, 4, 3),
    ('Подземная железная дорога', 2016, 5, (SELECT genre_id FROM Genres WHERE name = 'Историческая проза')),
    ('Никелевые мальчики', 2019, 5, (SELECT genre_id FROM Genres WHERE name = 'Социальная драма')),
    ('Норвежский лес', 1987, 6, (SELECT genre_id FROM Genres WHERE name = 'Магический реализм')),
    ('Нормальные люди', 2018, 7, (SELECT genre_id FROM Genres WHERE name = 'Современная проза'));
`);

// Вставка данных — Reviews 
db.exec(`
  INSERT INTO Reviews (user_id, book_id, rating, comment, review_date) VALUES
    (1, 1, 5, 'Великолепное произведение. Заставляет задуматься.', '2023-06-01'),
    (2, 5, 4, 'Немного затянуто, но интересно.', '2023-08-10'),
    (3, 4, 5, 'Обожаю этот мир волшебства!', '2023-07-05'),
    (2, 2, 5, 'Классика русской литературы. Читаю с удовольствием.', '2023-08-01'),
    (1, 3, 5, 'Современная философия и надежда. Очень понравилось.', '2023-09-01'),
    (2, 6, 5, 'Сильная и трогательная история.', '2024-01-10'),
    (3, 7, 4, 'Очень важная тема, хорошо написано.', '2024-01-15'),
    (1, 8, 5, 'Глубокая философия и стиль.', '2024-02-20'),
    (2, 9, 5, 'Тонкое описание чувств и отношений.', '2024-03-05');
`);

console.log('📦 База данных успешно создана и заполнена.');


// =====================================
// 📌 SELECT 1: Все рецензии на книгу "Воскресни за 40 дней"
const reviewsForBook = db.prepare(`
  SELECT Users.name AS user_name, Reviews.rating, Reviews.comment, Reviews.review_date
  FROM Reviews
  JOIN Users ON Reviews.user_id = Users.user_id
  JOIN Books ON Reviews.book_id = Books.book_id
  WHERE Books.title = ?
`).all('Воскресни за 40 дней');

console.log('\n📘 Все рецензии на книгу "Воскресни за 40 дней":');
reviewsForBook.forEach(r => {
  console.log(`- ${r.user_name} [${r.review_date}]: ${r.rating} ★ — ${r.comment}`);
});


// =====================================
// 📌 SELECT 2: Книги с рейтингом выше 4.0
const highRatedBooks = db.prepare(`
  SELECT Books.title, AVG(Reviews.rating) AS avg_rating
  FROM Reviews
  JOIN Books ON Reviews.book_id = Books.book_id
  GROUP BY Books.book_id
  HAVING avg_rating > 4.0
`).all();

console.log('\n🌟 Книги с рейтингом выше 4.0:');
highRatedBooks.forEach(b => {
  console.log(`- ${b.title}: ${b.avg_rating.toFixed(2)} ★`);
});


// =====================================
// 📌 SELECT 3: Книги жанра "Современная проза"
const booksByGenre = db.prepare(`
  SELECT Books.title, Authors.full_name AS author
  FROM Books
  JOIN Genres ON Books.genre_id = Genres.genre_id
  JOIN Authors ON Books.author_id = Authors.author_id
  WHERE Genres.name = ?
`).all('Современная проза');

console.log('\n🧙 Книги жанра "Современная проза":');
booksByGenre.forEach(b => {
  console.log(`- ${b.title} (автор: ${b.author})`);
});
