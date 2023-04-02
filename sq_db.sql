CREATE TABLE IF NOT EXISTS books (
    id integer PRIMARY KEY AUTOINCREMENT,
    fio text NOT NULL,
    doc text NOT NULL,
    room integer NOT NULL,
    datestart date NOT NULL,
    dateend date NOT NULL,
    price integer NOT NULL,
    sumbook integer NOT NULL
);

CREATE TABLE IF NOT EXISTS rooms (
    number integer NOT NULL,
    price integer NOT NULL
);

CREATE TABLE IF NOT EXISTS roombooks (
    id integer PRIMARY KEY AUTOINCREMENT,
    room integer NOT NULL,
    datestart date NOT NULL,
    dateend date NOT NULL
);

