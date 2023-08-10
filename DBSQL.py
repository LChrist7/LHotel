class DBSQL:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def makesearch(self, sstart, sdend):
        try:
            self.__cur.execute("""SELECT rooms.number FROM rooms WHERE rooms.number NOT IN (select roombooks.room 
                               from roombooks where (? between roombooks.datestart and roombooks.dateend or 
                               ? between roombooks.datestart and roombooks.dateend)) ORDER BY rooms.number""",
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
            self.__cur.execute("""SELECT rooms.number FROM rooms WHERE rooms.number NOT IN (select roombooks.room 
                               from roombooks where (? between roombooks.datestart and roombooks.dateend or 
                               ? between roombooks.datestart and roombooks.dateend)) 
                               and rooms.number == ?
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
            self.__cur.execute("""SELECT rooms.number FROM rooms WHERE rooms.number NOT IN (select roombooks.room 
                               from roombooks where (? between roombooks.datestart and roombooks.dateend or 
                               ? between roombooks.datestart and roombooks.dateend) and roombooks.numbook != ?) 
                               and rooms.number == ?
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
                                    FROM roombooks rb JOIN guests g on rb.guest3 = g.id WHERE rb.numbook = ?""",
                               (numbook,))
            rowguests += self.__cur.fetchall()
            self.__cur.execute("""SELECT fio, rb.fullpans5 f, rb.halfpans5 h, rb.breakfast5 b, doc, born, phone
                                    FROM roombooks rb JOIN guests g on rb.guest3 = g.id WHERE rb.numbook = ?""",
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
