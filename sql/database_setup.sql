-- Создание базы данных
CREATE DATABASE Друзья_человека;
USE Друзья_человека;

-- Создание таблиц
CREATE TABLE Животные (
    id INT AUTO_INCREMENT PRIMARY KEY,
    тип ENUM('Домашнее', 'Вьючное') NOT NULL,
    имя VARCHAR(100) NOT NULL,
    дата_рождения DATE NOT NULL
);

CREATE TABLE Команды (
    id INT AUTO_INCREMENT PRIMARY KEY,
    животное_id INT NOT NULL,
    команда VARCHAR(100) NOT NULL,
    FOREIGN KEY (животное_id) REFERENCES Животные(id) ON DELETE CASCADE
);

CREATE TABLE Домашние_животные (
    id INT PRIMARY KEY,
    вид ENUM('Собака', 'Кошка', 'Хомяк') NOT NULL,
    FOREIGN KEY (id) REFERENCES Животные(id) ON DELETE CASCADE
);

CREATE TABLE Вьючные_животные (
    id INT PRIMARY KEY,
    вид ENUM('Лошадь', 'Верблюд', 'Осёл') NOT NULL,
    FOREIGN KEY (id) REFERENCES Животные(id) ON DELETE CASCADE
);

-- Заполнение таблиц
INSERT INTO Животные (тип, имя, дата_рождения) VALUES 
('Домашнее', 'Бобик', '2020-05-15'),
('Домашнее', 'Мурка', '2021-02-20'),
('Домашнее', 'Хома', '2022-10-10'),
('Вьючное', 'Буран', '2019-07-03'),
('Вьючное', 'Горбун', '2018-11-25'),
('Вьючное', 'Иа', '2020-12-12');

INSERT INTO Домашние_животные (id, вид) VALUES 
(1, 'Собака'),
(2, 'Кошка'),
(3, 'Хомяк');

INSERT INTO Вьючные_животные (id, вид) VALUES 
(4, 'Лошадь'),
(5, 'Верблюд'),
(6, 'Осёл');

INSERT INTO Команды (животное_id, команда) VALUES 
(1, 'Сидеть'),
(1, 'Лежать'),
(2, 'Кис-кис'),
(4, 'Но'),
(4, 'Шагом'),
(6, 'Иа');

-- Удаление верблюдов
DELETE FROM Животные WHERE id IN (SELECT id FROM Вьючные_животные WHERE вид = 'Верблюд');

-- Объединение лошадей и ослов
CREATE TABLE Лошади_и_ослы AS
SELECT ж.имя, вж.вид, ж.дата_рождения
FROM Животные ж
JOIN Вьючные_животные вж ON ж.id = вж.id
WHERE вж.вид IN ('Лошадь', 'Осёл');

-- Создание таблицы "молодые животные"
CREATE TABLE Молодые_животные AS
SELECT 
    ж.*,
    TIMESTAMPDIFF(MONTH, ж.дата_рождения, CURDATE()) AS возраст_в_месяцах
FROM 
    Животные ж
WHERE 
    TIMESTAMPDIFF(YEAR, ж.дата_рождения, CURDATE()) BETWEEN 1 AND 3;

-- Объединение всех таблиц
CREATE TABLE Все_животные AS
SELECT 
    ж.id,
    ж.тип,
    CASE 
        WHEN дж.id IS NOT NULL THEN дж.вид
        WHEN вж.id IS NOT NULL THEN вж.вид
    END AS вид,
    ж.имя,
    ж.дата_рождения,
    GROUP_CONCAT(к.команда SEPARATOR ', ') AS команды,
    'Животные' AS исходная_таблица
FROM 
    Животные ж
LEFT JOIN Домашние_животные дж ON ж.id = дж.id
LEFT JOIN Вьючные_животные вж ON ж.id = вж.id
LEFT JOIN Команды к ON ж.id = к.животное_id
GROUP BY ж.id;