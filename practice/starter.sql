-- Учебный старт для J08-J10. PostgreSQL 17.
-- Запускать только в отдельной учебной БД. Повторный запуск без очистки завершится ошибкой.
-- Это минимальная модель для запросов, не готовый алгоритм защиты вместимости.
BEGIN;

CREATE TABLE clients (
    id bigint PRIMARY KEY,
    full_name text NOT NULL,
    email text UNIQUE
);

CREATE TABLE sessions (
    id bigint PRIMARY KEY,
    title text NOT NULL,
    starts_at timestamptz NOT NULL,
    capacity integer NOT NULL CHECK (capacity > 0),
    description text,
    status text NOT NULL CHECK (status IN ('SCHEDULED', 'CANCELLED'))
);

CREATE TABLE bookings (
    id bigint PRIMARY KEY,
    client_id bigint NOT NULL REFERENCES clients(id),
    session_id bigint NOT NULL REFERENCES sessions(id),
    status text NOT NULL CHECK (status IN ('CONFIRMED', 'CANCELLED')),
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    UNIQUE (client_id, session_id)
);
-- Выбрана одна строка на пару клиент-занятие.
-- Повторная запись после отмены предполагает переход той же строки и отдельную историю.
-- Таблицу истории и её правила ученик добавляет в своём решении.

CREATE TABLE notification_attempts (
    id bigint PRIMARY KEY,
    booking_id bigint NOT NULL REFERENCES bookings(id),
    status text NOT NULL CHECK (status IN ('SENT', 'DELIVERED', 'FAILED')),
    attempted_at timestamptz NOT NULL,
    error_code text
);

INSERT INTO clients (id, full_name, email) VALUES
 (1, 'Анна Учебная', 'anna@example.com'),
 (2, 'Борис Учебный', 'boris@example.com'),
 (3, 'Вера Учебная', NULL),
 (4, 'Глеб Учебный', 'gleb@example.com'),
 (5, 'Дина Учебная', 'dina@example.com');

INSERT INTO sessions (id, title, starts_at, capacity, description, status) VALUES
 (10, 'Разговорный английский', '2026-11-01 12:00:00+03', 2, 'Группа A', 'SCHEDULED'),
 (11, 'Основы рисунка', '2026-11-01 18:00:00+03', 3, NULL, 'SCHEDULED'),
 (12, 'Практика SQL', '2026-11-02 19:00:00+03', 1, 'Последнее место', 'SCHEDULED'),
 (13, 'Керамика', '2026-11-03 15:00:00+03', 4, '', 'CANCELLED'),
 (14, 'Гитара', '2026-11-04 17:00:00+03', 2, 'Без записей', 'SCHEDULED');

INSERT INTO bookings (id, client_id, session_id, status, created_at, updated_at) VALUES
 (100, 1, 10, 'CONFIRMED', '2026-10-16 10:00:00+03', '2026-10-16 10:00:00+03'),
 (101, 2, 10, 'CONFIRMED', '2026-10-16 10:01:00+03', '2026-10-16 10:01:00+03'),
 (102, 3, 11, 'CANCELLED', '2026-10-16 11:00:00+03', '2026-10-17 09:00:00+03'),
 (103, 1, 11, 'CONFIRMED', '2026-10-16 12:00:00+03', '2026-10-16 12:00:00+03');

INSERT INTO notification_attempts (id, booking_id, status, attempted_at, error_code) VALUES
 (1000, 100, 'FAILED', '2026-10-16 10:00:01+03', 'PROVIDER_UNAVAILABLE'),
 (1001, 100, 'DELIVERED', '2026-10-16 10:00:10+03', NULL),
 (1002, 101, 'DELIVERED', '2026-10-16 10:01:03+03', NULL),
 (1003, 103, 'FAILED', '2026-10-16 12:00:01+03', 'PROVIDER_UNAVAILABLE');

COMMIT;

-- Контрольные ориентиры на этой фикстуре:
-- Клиентов: 5, занятий: 5, строк bookings: 4, активных записей: 3.
-- Активных записей занятия 10: 2; занятия 11: 1; остальных: 0.
-- Клиенты без активных записей: 3, 4, 5.
-- У записи 100 две попытки уведомления: JOIN может удвоить её при неверном подсчёте.
-- Даты фиксированные: фильтруйте относительно согласованного as_of, а не текущего now().
-- Ученику: добавьте свои занятия, историю, запросы и ограничения; готовых решений здесь нет.
