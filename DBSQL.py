class DBSQL:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()
        self._ensure_all_tables()

    def _ensure_all_tables(self):
        """Создаёт все необходимые таблицы, если их нет (без перезаписи существующих данных)"""
        try:
            # Проверяем какие таблицы уже существуют
            self.__cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row[0] for row in self.__cur.fetchall()]

            # Таблица rooms
            if 'rooms' not in existing_tables:
                self.__cur.execute("""
                    CREATE TABLE rooms (
                        number INTEGER NOT NULL PRIMARY KEY,
                        price INTEGER
                    )
                """)
                # Добавляем номера комнат по умолчанию (101-110)
                for i in range(101, 111):
                    self.__cur.execute("INSERT INTO rooms (number, price) VALUES (?, ?)", (i, 5000))

            # Таблица guests
            if 'guests' not in existing_tables:
                self.__cur.execute("""
                    CREATE TABLE guests (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fio TEXT NOT NULL,
                        doc TEXT,
                        fiodocid TEXT,
                        born DATE,
                        phone TEXT
                    )
                """)

            # Таблица roombooks
            if 'roombooks' not in existing_tables:
                self.__cur.execute("""
                    CREATE TABLE roombooks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        numbook TEXT,
                        guest1 INTEGER NOT NULL,
                        fullpans1 INTEGER DEFAULT 0,
                        halfpans1 INTEGER DEFAULT 0,
                        breakfast1 INTEGER DEFAULT 0,
                        guest2 INTEGER,
                        fullpans2 INTEGER DEFAULT 0,
                        halfpans2 INTEGER DEFAULT 0,
                        breakfast2 INTEGER DEFAULT 0,
                        guest3 INTEGER,
                        fullpans3 INTEGER DEFAULT 0,
                        halfpans3 INTEGER DEFAULT 0,
                        breakfast3 INTEGER DEFAULT 0,
                        guest4 INTEGER,
                        fullpans4 INTEGER DEFAULT 0,
                        halfpans4 INTEGER DEFAULT 0,
                        breakfast4 INTEGER DEFAULT 0,
                        guest5 INTEGER,
                        fullpans5 INTEGER DEFAULT 0,
                        halfpans5 INTEGER DEFAULT 0,
                        breakfast5 INTEGER DEFAULT 0,
                        room INTEGER NOT NULL,
                        datestart DATE NOT NULL,
                        dateend DATE NOT NULL,
                        tour INTEGER DEFAULT 0,
                        transfer INTEGER DEFAULT 0,
                        price INTEGER NOT NULL,
                        prep INTEGER DEFAULT 0,
                        sumbook INTEGER NOT NULL,
                        comm TEXT
                    )
                """)

            # Таблица seasons
            if 'seasons' not in existing_tables:
                self.__cur.execute("""
                    CREATE TABLE seasons (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        start_date DATE NOT NULL,
                        end_date DATE NOT NULL,
                        base_price REAL NOT NULL DEFAULT 5000,
                        extra_person_price REAL NOT NULL DEFAULT 1000,
                        fullpans_price REAL NOT NULL DEFAULT 2500,
                        halfpans_price REAL NOT NULL DEFAULT 1500,
                        breakfast_price REAL NOT NULL DEFAULT 500
                    )
                """)
            else:
                # Миграция существующей таблицы seasons
                self.__cur.execute("PRAGMA table_info(seasons)")
                columns = [col[1] for col in self.__cur.fetchall()]
                if 'price_modifier' in columns and 'base_price' not in columns:
                    self.__cur.execute("ALTER TABLE seasons ADD COLUMN base_price REAL NOT NULL DEFAULT 5000")
                    self.__cur.execute("ALTER TABLE seasons ADD COLUMN extra_person_price REAL NOT NULL DEFAULT 1000")
                if 'fullpans_price' not in columns:
                    self.__cur.execute("ALTER TABLE seasons ADD COLUMN fullpans_price REAL NOT NULL DEFAULT 2500")
                if 'halfpans_price' not in columns:
                    self.__cur.execute("ALTER TABLE seasons ADD COLUMN halfpans_price REAL NOT NULL DEFAULT 1500")
                if 'breakfast_price' not in columns:
                    self.__cur.execute("ALTER TABLE seasons ADD COLUMN breakfast_price REAL NOT NULL DEFAULT 500")

            self.__db.commit()
        except Exception as e:
            print(f"Error ensuring tables: {e}")

    def get_seasons(self):
        """Получить все сезоны"""
        try:
            self.__cur.execute("""
                SELECT id, name, start_date, end_date, base_price, extra_person_price,
                       fullpans_price, halfpans_price, breakfast_price
                FROM seasons
                ORDER BY start_date
            """)
            return [dict(r) for r in self.__cur.fetchall()]
        except Exception as e:
            print(e)
            return []

    def add_season(self, name, start_date, end_date, base_price, extra_person_price,
                   fullpans_price, halfpans_price, breakfast_price):
        """Добавить новый сезон"""
        try:
            self.__cur.execute("""
                INSERT INTO seasons (name, start_date, end_date, base_price, extra_person_price,
                                     fullpans_price, halfpans_price, breakfast_price)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, start_date, end_date, base_price, extra_person_price,
                  fullpans_price, halfpans_price, breakfast_price))
            return True
        except Exception as e:
            print(e)
            return False

    def update_season(self, season_id, name, start_date, end_date, base_price, extra_person_price,
                      fullpans_price, halfpans_price, breakfast_price):
        """Обновить сезон"""
        try:
            self.__cur.execute("""
                UPDATE seasons
                SET name = ?, start_date = ?, end_date = ?, base_price = ?, extra_person_price = ?,
                    fullpans_price = ?, halfpans_price = ?, breakfast_price = ?
                WHERE id = ?
            """, (name, start_date, end_date, base_price, extra_person_price,
                  fullpans_price, halfpans_price, breakfast_price, season_id))
            return True
        except Exception as e:
            print(e)
            return False

    def delete_season(self, season_id):
        """Удалить сезон"""
        try:
            self.__cur.execute("DELETE FROM seasons WHERE id = ?", (season_id,))
            return True
        except Exception as e:
            print(e)
            return False

    def get_season_for_date(self, check_date):
        """Получить сезон для указанной даты"""
        try:
            self.__cur.execute("""
                SELECT name, base_price, extra_person_price,
                       fullpans_price, halfpans_price, breakfast_price
                FROM seasons
                WHERE ? BETWEEN start_date AND end_date
                LIMIT 1
            """, (check_date,))
            result = self.__cur.fetchone()
            if result:
                return dict(result)
            return {
                'name': 'Базовый',
                'base_price': 5000,
                'extra_person_price': 1000,
                'fullpans_price': 2500,
                'halfpans_price': 1500,
                'breakfast_price': 500
            }
        except Exception as e:
            print(e)
            return {
                'name': 'Базовый',
                'base_price': 5000,
                'extra_person_price': 1000,
                'fullpans_price': 2500,
                'halfpans_price': 1500,
                'breakfast_price': 500
            }

    def calculate_seasonal_price(self, start_date, end_date, guest_count=2):
        """Рассчитать цену с учётом сезонов и количества гостей"""
        try:
            from datetime import datetime, timedelta

            if isinstance(start_date, str):
                start = datetime.strptime(start_date[:10], '%Y-%m-%d').date()
            else:
                start = start_date.date() if hasattr(start_date, 'date') else start_date

            if isinstance(end_date, str):
                end = datetime.strptime(end_date[:10], '%Y-%m-%d').date()
            else:
                end = end_date.date() if hasattr(end_date, 'date') else end_date

            total_price = 0
            current = start
            delta = timedelta(days=1)

            while current < end:
                season = self.get_season_for_date(str(current))
                # Базовая цена за 1-2 человек
                daily_price = season['base_price']
                # Доплата за каждого гостя свыше 2
                if guest_count > 2:
                    daily_price += (guest_count - 2) * season['extra_person_price']
                total_price += daily_price
                current += delta

            return round(total_price, 2)
        except Exception as e:
            print(e)
            # Возвращаем простой расчёт без сезонов
            days = (end - start).days if hasattr(end, '__sub__') else 1
            return 5000 * days

    def makesearch(self, sstart, sdend):
        try:
            # Правильная проверка пересечения интервалов:
            # Два интервала [A,B] и [C,D] пересекаются если A < D AND B > C
            self.__cur.execute("""SELECT rooms.number FROM rooms WHERE rooms.number NOT IN (
                               SELECT roombooks.room FROM roombooks
                               WHERE ? < roombooks.dateend AND ? > roombooks.datestart
                               ) ORDER BY rooms.number""",
                               (sstart, sdend))
            res = [item['number'] for item in self.__cur.fetchall()]
            if res:
                return res
        except Exception as e:
            print(e)
            return 0
        return []

    def makesearchonadd(self, dates, datee, room):
        try:
            # Проверяем, свободна ли конкретная комната в заданный период
            self.__cur.execute("""SELECT rooms.number FROM rooms WHERE rooms.number NOT IN (
                               SELECT roombooks.room FROM roombooks
                               WHERE ? < roombooks.dateend AND ? > roombooks.datestart
                               ) AND rooms.number = ?
                               ORDER BY rooms.number""",
                               (dates, datee, room))
            res = [item['number'] for item in self.__cur.fetchall()]
            if str(res[0]) == str(room):
                return 0
            else:
                return 1
        except Exception as e:
            print(e)
            return 1

    def makesearchonupdate(self, dates, datee, numbook, room):
        try:
            # Проверяем доступность комнаты, исключая текущую бронь
            self.__cur.execute("""SELECT rooms.number FROM rooms WHERE rooms.number NOT IN (
                               SELECT roombooks.room FROM roombooks
                               WHERE ? < roombooks.dateend AND ? > roombooks.datestart
                               AND roombooks.numbook != ?
                               ) AND rooms.number = ?
                               ORDER BY rooms.number""",
                               (dates, datee, numbook, room))
            res = [item['number'] for item in self.__cur.fetchall()]
            if str(res[0]) == str(room):
                return 0
            else:
                return 1
        except Exception as e:
            print(e)
            return 1

    def makecheck(self, datebook, roombook):
        try:
            self.__cur.execute("""SELECT guests.fio, 
                                round(julianday(roombooks.dateend)) - round(julianday(?)) days, 
                                numbook, tour 
                                FROM roombooks
                                join guests on guests.id = roombooks.guest1
                                WHERE ((? between strftime('%Y-%m-%d',roombooks.datestart)
                                and strftime('%Y-%m-%d',roombooks.dateend)) and room = ?)
                                GROUP BY guests.fio
                                ORDER BY strftime('%d',roombooks.datestart)""",
                               (datebook, datebook, roombook))
            rowbook = self.__cur.fetchall()
            if rowbook:
                return list(rowbook)
        except Exception as e:
            print(e)
            return 0
        return []

    def addbook(self, numbook, guest1, guest2, guest3, guest4, guest5,
                sdate, edate, room, tour, transfer, price, prep, sumbook, sdatewl, edatewl, comm):
        try:
            rescheck = self.makesearchonadd(sdatewl, edatewl, room)
            if rescheck == 1:
                return 1
        except Exception as e:
            print(e)
            return 1
        try:
            bookskey1 = (guest1.Fullname + guest1.Born).replace(' ', '')
            bookskey2 = (guest2.Fullname + guest2.Born).replace(' ', '')
            bookskey3 = (guest3.Fullname + guest3.Born).replace(' ', '')
            bookskey4 = (guest4.Fullname + guest4.Born).replace(' ', '')
            bookskey5 = (guest5.Fullname + guest5.Born).replace(' ', '')
            if guest1.Fullname != '':
                self.__cur.execute("""INSERT INTO guests (id, fio, doc, fiodocid, born, phone) 
                                   VALUES (NULL, ?, ?, ?, ?, ?)""",
                                   (guest1.Fullname, guest1.Doc, bookskey1, guest1.Born, guest1.Phone))
            if guest2.Fullname != '':
                self.__cur.execute("""INSERT INTO guests (id, fio, doc, fiodocid, born, phone) 
                                   VALUES (NULL, ?, ?, ?, ?, ?)""",
                                   (guest2.Fullname, guest2.Doc, bookskey2, guest2.Born, guest2.Phone))
            if guest3.Fullname != '':
                self.__cur.execute("""INSERT INTO guests (id, fio, doc, fiodocid, born, phone) 
                                   VALUES (NULL, ?, ?, ?, ?, ?)""",
                                   (guest3.Fullname, guest3.Doc, bookskey3, guest3.Born, guest3.Phone))
            if guest4.Fullname != '':
                self.__cur.execute("""INSERT INTO guests (id, fio, doc, fiodocid, born, phone) 
                                   VALUES (NULL, ?, ?, ?, ?, ?)""",
                                   (guest4.Fullname, guest4.Doc, bookskey4, guest4.Born, guest4.Phone))
            if guest5.Fullname != '':
                self.__cur.execute("""INSERT INTO guests (id, fio, doc, fiodocid, born, phone) 
                                   VALUES (NULL, ?, ?, ?, ?, ?)""",
                                   (guest5.Fullname, guest5.Doc, bookskey5, guest5.Born, guest5.Phone))
            self.__cur.execute("""
                                INSERT INTO roombooks(id, numbook,
                                guest1, fullpans1, halfpans1, breakfast1,
                                guest2, fullpans2, halfpans2, breakfast2,
                                guest3, fullpans3, halfpans3, breakfast3,
                                guest4, fullpans4, halfpans4, breakfast4,
                                guest5, fullpans5, halfpans5, breakfast5,
                                room, datestart, dateend, tour, transfer, price, prep, sumbook, comm) 
                                VALUES(NULL, ?,
                                (SELECT id FROM guests WHERE fio = ? AND fiodocid = ?),
                                ?, ?, ?,
                                (SELECT id FROM guests WHERE fio = ? AND fiodocid = ?),
                                ?, ?, ?,
                                (SELECT id FROM guests WHERE fio = ? AND fiodocid = ?),
                                ?, ?, ?,
                                (SELECT id FROM guests WHERE fio = ? AND fiodocid = ?), 
                                ?, ?, ?,
                                (SELECT id FROM guests WHERE fio = ? AND fiodocid = ?), 
                                ?, ?, ?,
                                ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                               (numbook,
                                guest1.Fullname, bookskey1,
                                guest1.fullpans, guest1.halfpans, guest1.breakfast,
                                guest2.Fullname, bookskey2,
                                guest2.fullpans, guest2.halfpans, guest2.breakfast,
                                guest3.Fullname, bookskey3,
                                guest3.fullpans, guest3.halfpans, guest3.breakfast,
                                guest4.Fullname, bookskey4,
                                guest4.fullpans, guest4.halfpans, guest4.breakfast,
                                guest5.Fullname, bookskey5,
                                guest5.fullpans, guest5.halfpans, guest5.breakfast,
                                room, sdate, edate, tour, transfer, price, prep, sumbook, comm))
        except Exception as e:
            print(e)
            return 0
        return []

    def updatebook(self, numbook, guest1, guest2, guest3, guest4, guest5,
                   sdate, edate, room, tour, transfer, price, prep, sumbook, sdatewl, edatewl, comm):
        try:
            rescheck = self.makesearchonupdate(sdatewl, edatewl, numbook, room)
            if rescheck == 1:
                return 1
        except Exception as e:
            print(e)
            return 1
        try:
            bookskey1 = (guest1.Fullname + guest1.Born).replace(' ', '')
            bookskey2 = (guest2.Fullname + guest2.Born).replace(' ', '')
            bookskey3 = (guest3.Fullname + guest3.Born).replace(' ', '')
            bookskey4 = (guest4.Fullname + guest4.Born).replace(' ', '')
            bookskey5 = (guest5.Fullname + guest5.Born).replace(' ', '')
            if guest1.Fullname != '':
                self.__cur.execute("""INSERT INTO guests (id, fio, doc, fiodocid, born, phone) 
                                   VALUES (NULL, ?, ?, ?, ?, ?)""",
                                   (guest1.Fullname, guest1.Doc, bookskey1, guest1.Born, guest1.Phone))
            if guest2.Fullname != '':
                self.__cur.execute("""INSERT INTO guests (id, fio, doc, fiodocid, born, phone) 
                                   VALUES (NULL, ?, ?, ?, ?, ?)""",
                                   (guest2.Fullname, guest2.Doc, bookskey2, guest2.Born, guest2.Phone))
            if guest3.Fullname != '':
                self.__cur.execute("""INSERT INTO guests (id, fio, doc, fiodocid, born, phone) 
                                   VALUES (NULL, ?, ?, ?, ?, ?)""",
                                   (guest3.Fullname, guest3.Doc, bookskey3, guest3.Born, guest3.Phone))
            if guest4.Fullname != '':
                self.__cur.execute("""INSERT INTO guests (id, fio, doc, fiodocid, born, phone) 
                                   VALUES (NULL, ?, ?, ?, ?, ?)""",
                                   (guest4.Fullname, guest4.Doc, bookskey4, guest4.Born, guest4.Phone))
            if guest5.Fullname != '':
                self.__cur.execute("""INSERT INTO guests (id, fio, doc, fiodocid, born, phone) 
                                   VALUES (NULL, ?, ?, ?, ?, ?)""",
                                   (guest5.Fullname, guest5.Doc, bookskey5, guest5.Born, guest5.Phone))
            self.__cur.execute("""
                                UPDATE roombooks
                                SET numbook = ?,
                                guest1 = (SELECT id FROM guests WHERE fio = ? AND fiodocid = ?),
                                fullpans1 = ?,
                                halfpans1 = ?,
                                breakfast1 = ?,
                                guest2 = (SELECT id FROM guests WHERE fio = ? AND fiodocid = ?),
                                fullpans2 = ?,
                                halfpans2 = ?,
                                breakfast2 = ?,
                                guest3 = (SELECT id FROM guests WHERE fio = ? AND fiodocid = ?),
                                fullpans3 = ?,
                                halfpans3 = ?,
                                breakfast3 = ?,
                                guest4 = (SELECT id FROM guests WHERE fio = ? AND fiodocid = ?),
                                fullpans4 = ?,
                                halfpans4 = ?,
                                breakfast4 = ?,
                                guest5 = (SELECT id FROM guests WHERE fio = ? AND fiodocid = ?),
                                fullpans5 = ?,
                                halfpans5 = ?,
                                breakfast5 = ?,
                                room = ?,
                                datestart = ?,
                                dateend = ?,
                                tour = ?,
                                transfer = ?,
                                price = ?,
                                prep = ?,
                                sumbook = ?,
                                comm = ?
                                WHERE numbook = ?
                                """,
                               (str(numbook), guest1.Fullname, bookskey1,
                                guest1.fullpans, guest1.halfpans, guest1.breakfast,
                                guest2.Fullname, bookskey2,
                                guest2.fullpans, guest2.halfpans, guest2.breakfast,
                                guest3.Fullname, bookskey3,
                                guest3.fullpans, guest3.halfpans, guest3.breakfast,
                                guest4.Fullname, bookskey4,
                                guest4.fullpans, guest4.halfpans, guest4.breakfast,
                                guest5.Fullname, bookskey5,
                                guest5.fullpans, guest5.halfpans, guest5.breakfast,
                                int(room), sdate, edate, int(tour), int(transfer), int(price), int(prep),
                                int(sumbook), str(comm), str(numbook)))
        except Exception as e:
            print(e)
            return 0
        return []

    def checkbooks(self):
        try:
            self.__cur.execute("""SELECT * FROM rooms ORDER BY number""")
            row = [item['number'] for item in self.__cur.fetchall()]
            if row:
                return row
        except Exception as e:
            print(e)
            return 0
        return []

    def checkall(self, ds, de):
        try:
            self.__cur.execute("""SELECT rb.numbook, gu.fio, rb.room, gu.born, rb.price, rb.sumbook, 
                                rb.guest1, rb.guest2, rb.guest3, rb.guest4, rb.guest5,
                                (rb.fullpans1 + rb.fullpans2 + rb.fullpans3 + rb.fullpans4 + rb.fullpans5) as fullpans, 
                                (rb.halfpans1 + rb.halfpans2 + rb.halfpans3 + rb.halfpans4 + rb.halfpans5) as halfpans,
                                (rb.breakfast1 + rb.breakfast2 + rb.breakfast3 + rb.breakfast4 + rb.breakfast5) as bf,
                                rb.tour, rb.transfer, rb.comm
                                FROM roombooks rb 
                                join guests gu on gu.id = rb.guest1 or gu.id = rb.guest2 or 
                                gu.id = rb.guest3 or gu.id = rb.guest4 or gu.id = rb.guest5 
                                WHERE (rb.datestart and rb.dateend between ? and ?)
                                GROUP BY rb.numbook""",
                               (ds, de))
            row = self.__cur.fetchall()
            if row:
                return row
        except Exception as e:
            print(e)
            return 0
        return []

    def bookcancel(self, numbook):
        try:
            self.__cur.execute("""DELETE FROM roombooks WHERE numbook = ?""",
                               (numbook,))
        except Exception as e:
            print(e)
            return 0
        return []

    def get_statistics(self, start_date, end_date):
        """Получить статистику за период"""
        try:
            stats = {}

            # Общее количество бронирований и сумма
            self.__cur.execute("""
                SELECT COUNT(*) as total_bookings,
                       COALESCE(SUM(sumbook), 0) as total_revenue,
                       COALESCE(SUM(prep), 0) as total_prepaid,
                       COALESCE(AVG(price), 0) as avg_price
                FROM roombooks
                WHERE datestart >= ? AND datestart <= ?
            """, (start_date, end_date))
            row = self.__cur.fetchone()
            stats['total_bookings'] = row['total_bookings']
            stats['total_revenue'] = row['total_revenue']
            stats['total_prepaid'] = row['total_prepaid']
            stats['avg_price'] = round(row['avg_price'], 2)

            # Брони от туроператоров vs прямые
            self.__cur.execute("""
                SELECT tour, COUNT(*) as count
                FROM roombooks
                WHERE datestart >= ? AND datestart <= ?
                GROUP BY tour
            """, (start_date, end_date))
            tour_stats = {0: 0, 1: 0}
            for row in self.__cur.fetchall():
                tour_stats[row['tour']] = row['count']
            stats['direct_bookings'] = tour_stats[0]
            stats['tour_bookings'] = tour_stats[1]

            # Топ комнат по количеству бронирований
            self.__cur.execute("""
                SELECT room, COUNT(*) as count, SUM(sumbook) as revenue
                FROM roombooks
                WHERE datestart >= ? AND datestart <= ?
                GROUP BY room
                ORDER BY count DESC
                LIMIT 10
            """, (start_date, end_date))
            stats['top_rooms'] = [dict(r) for r in self.__cur.fetchall()]

            # Количество всех комнат для расчёта загрузки
            self.__cur.execute("SELECT COUNT(*) as count FROM rooms")
            total_rooms = self.__cur.fetchone()['count']

            # Расчёт загрузки (сколько комнато-дней занято)
            self.__cur.execute("""
                SELECT SUM(
                    julianday(MIN(dateend, ?)) - julianday(MAX(datestart, ?))
                ) as booked_days
                FROM roombooks
                WHERE dateend > ? AND datestart < ?
            """, (end_date, start_date, start_date, end_date))
            result = self.__cur.fetchone()
            booked_days = result['booked_days'] if result['booked_days'] else 0

            # Общее количество доступных комнато-дней
            from datetime import datetime
            d1 = datetime.strptime(start_date, '%Y-%m-%d')
            d2 = datetime.strptime(end_date, '%Y-%m-%d')
            total_days = (d2 - d1).days + 1
            total_room_days = total_rooms * total_days

            if total_room_days > 0:
                stats['occupancy'] = round((booked_days / total_room_days) * 100, 1)
            else:
                stats['occupancy'] = 0

            stats['total_rooms'] = total_rooms
            stats['total_days'] = total_days

            # Статистика по месяцам
            self.__cur.execute("""
                SELECT strftime('%Y-%m', datestart) as month,
                       COUNT(*) as bookings,
                       SUM(sumbook) as revenue
                FROM roombooks
                WHERE datestart >= ? AND datestart <= ?
                GROUP BY month
                ORDER BY month
            """, (start_date, end_date))
            stats['monthly'] = [dict(r) for r in self.__cur.fetchall()]

            return stats
        except Exception as e:
            print(e)
            return {}

    def get_calendar_data(self, start_date, end_date):
        """Получить данные для календарного вида"""
        try:
            # Получаем все комнаты
            self.__cur.execute("SELECT number FROM rooms ORDER BY number")
            rooms = [item['number'] for item in self.__cur.fetchall()]

            # Получаем все бронирования в указанном периоде
            self.__cur.execute("""
                SELECT rb.room, rb.datestart, rb.dateend, rb.numbook, rb.tour,
                       g.fio as guest_name
                FROM roombooks rb
                LEFT JOIN guests g ON rb.guest1 = g.id
                WHERE rb.datestart <= ? AND rb.dateend >= ?
                ORDER BY rb.room, rb.datestart
            """, (end_date, start_date))
            bookings = self.__cur.fetchall()

            return {'rooms': rooms, 'bookings': [dict(b) for b in bookings]}
        except Exception as e:
            print(e)
            return {'rooms': [], 'bookings': []}

    def get_current_year_bookings(self):
        """Получить актуальные брони текущего года"""
        try:
            from datetime import datetime
            current_year = datetime.now().year
            today = datetime.now().strftime('%Y-%m-%d')

            self.__cur.execute("""
                SELECT rb.numbook, rb.room, rb.datestart, rb.dateend,
                       g.fio as guest_name, rb.tour, rb.sumbook
                FROM roombooks rb
                LEFT JOIN guests g ON rb.guest1 = g.id
                WHERE strftime('%Y', rb.datestart) = ? OR strftime('%Y', rb.dateend) = ?
                ORDER BY rb.datestart DESC
                LIMIT 50
            """, (str(current_year), str(current_year)))

            return [dict(r) for r in self.__cur.fetchall()]
        except Exception as e:
            print(e)
            return []

    def viewbook(self, numbook):
        try:
            self.__cur.execute("""SELECT fio, rb.fullpans1 f, rb.halfpans1 h, rb.breakfast1 b, doc, born, phone
                                    FROM roombooks rb JOIN guests g on rb.guest1 = g.id WHERE rb.numbook = ?""",
                               (numbook,))
            rowguests = self.__cur.fetchall()
            self.__cur.execute("""SELECT fio, rb.fullpans2 f, rb.halfpans2 h, rb.breakfast2 b, doc, born, phone 
                                    FROM roombooks rb JOIN guests g on rb.guest2 = g.id WHERE rb.numbook = ?""",
                               (numbook,))
            rowguests += self.__cur.fetchall()
            self.__cur.execute("""SELECT fio, rb.fullpans3 f, rb.halfpans3 h, rb.breakfast3 b, doc, born, phone
                                    FROM roombooks rb JOIN guests g on rb.guest3 = g.id WHERE rb.numbook = ?""",
                               (numbook,))
            rowguests += self.__cur.fetchall()
            self.__cur.execute("""SELECT fio, rb.fullpans4 f, rb.halfpans4 h, rb.breakfast4 b, doc, born, phone
                                    FROM roombooks rb JOIN guests g on rb.guest4 = g.id WHERE rb.numbook = ?""",
                               (numbook,))
            rowguests += self.__cur.fetchall()
            self.__cur.execute("""SELECT fio, rb.fullpans5 f, rb.halfpans5 h, rb.breakfast5 b, doc, born, phone
                                    FROM roombooks rb JOIN guests g on rb.guest5 = g.id WHERE rb.numbook = ?""",
                               (numbook,))
            rowguests += self.__cur.fetchall()
            self.__cur.execute("""SELECT numbook, room, datestart ds, dateend de, tour, transfer, price, prep, sumbook, comm 
                                    FROM roombooks rb WHERE rb.numbook = ?""",
                               (numbook,))
            rowinfo = self.__cur.fetchall()
            if rowguests and rowinfo:
                return list(rowguests), list(rowinfo)
        except Exception as e:
            print(e)
            return 0
        return []
