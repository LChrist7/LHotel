from datetime import date, timedelta, datetime
from openpyxl.styles import PatternFill
import sqlite3
import os
from openpyxl import Workbook
import DBSQL
from flask import Flask, render_template, url_for, request, g, redirect
import string
import sys
import webbrowser
import gclass


DATABASE = '/tmp/hotel.db'
DEBUG = False
SECRET_KEY = 'anua'


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


app = Flask(__name__, static_url_path="", static_folder=resource_path(
    'static'), template_folder=resource_path("templates"))

app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'hotel.db')))


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


# поменялась структура базы, надо изменить create
def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().execute(f.read())
    db.commit()
    db.close()


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


@app.route("/search", methods=["POST", "GET"])
def search():
    if request.method == 'POST':
        searchstart = datetime.fromisoformat(request.form['SearchStart'].replace('T', ' '))
        searchend = datetime.fromisoformat(request.form['SearchEnd'].replace('T', ' '))
        db = get_db()
        dbase = DBSQL.DBSQL(db)
        return render_template('search.html', rooms=dbase.makesearch(searchstart, searchend))
    else:
        return render_template('search.html')


@app.route("/cancel", methods=["POST", "GET"])
def cancel():
    if request.method == 'POST' and request.form['numcancel'] != '':
        db = get_db()
        dbase = DBSQL.DBSQL(db)
        dbase.bookcancel(request.form['numcancel'])
        db.commit()
        db.close()
        return redirect("/cancel")
    return render_template('cancel.html')


@app.route("/check", methods=["POST", "GET"])
def check():
    if request.method == 'POST' and "checkstart" in request.form:
        workbook = Workbook()
        sheet = workbook.active
        sheet.freeze_panes = sheet['B2']
        db = get_db()
        dbase = DBSQL.DBSQL(db)
        rooms = dbase.checkbooks()
        for i in range(1, len(rooms) + 1):
            sheet['A' + str(i + 1)] = rooms[i - 1]
        letters = list(string.ascii_uppercase)
        letters.extend([i + b for i in letters for b in letters])
        letters.pop(0)
        start_date = date.fromisoformat(request.form['checkstart'])
        end_date = date.fromisoformat(request.form['checkend'])
        delta = timedelta(days=1)
        alldelta = end_date - start_date
        alldelta = alldelta.days
        for j in letters[0:alldelta + 1]:
            sheet[j + str(1)] = str(start_date)
            sheet.column_dimensions[j].width = 15
            start_date += delta
        for m in range(2, len(rooms) + 2):
            for j in letters[0:alldelta + 1]:
                roomv = sheet['A' + str(m)].value
                datev = sheet[j + str(1)].value
                sqlres = dbase.makecheck(datev, roomv)
                if sqlres and len(sqlres) == 1:
                    red_background = PatternFill(fill_type='solid', fgColor="FFC7CE")
                    sheet[j + str(m)] = sqlres[0].split(" ")[0]
                    sheet[j + str(m)].fill = red_background
                if sqlres and len(sqlres) == 2:
                    sheet.column_dimensions[j].width = 23
                    red_background = PatternFill(fill_type='solid', fgColor="FFC7CE")
                    sheet[j + str(m)] = sqlres[0].split(" ")[0] + ' - ' + sqlres[1].split(" ")[0]
                    sheet[j + str(m)].fill = red_background
        try:
            workbook.save(filename="График.xlsx")
            db.close()
        except PermissionError:
            db.close()
            return '<h2>Файл отчета открыт, чтобы выгрузить новый отчет закройте файл</h2>'
        return redirect('/check')

    if request.method == 'POST' and "allcheckstart" in request.form:
        workbookall = Workbook()
        sheetall = workbookall.active
        db = get_db()
        dbaseall = DBSQL.DBSQL(db)
        row = dbaseall.checkall(request.form['allcheckstart'], request.form['allcheckend'])
        db.close()
        letters = list(string.ascii_uppercase)
        letters.extend([i + b for i in letters for b in letters])
        sheetall.column_dimensions['B'].width = 45
        sheetall.column_dimensions['C'].width = 12
        sheetall.column_dimensions['D'].width = 20
        sheetall.column_dimensions['H'].width = 16
        sheetall.column_dimensions['I'].width = 13
        sheetall.column_dimensions['L'].width = 16
        sheetall.column_dimensions['M'].width = 50
        i = 0
        k = 2
        sheetall['A1'] = '№ заявки'
        sheetall['B1'] = 'ФИО'
        sheetall['C1'] = '№ комнаты'
        sheetall['D1'] = 'Дата рождения'
        sheetall['E1'] = 'Цена'
        sheetall['F1'] = 'Сумма'
        sheetall['G1'] = 'Гостей'
        sheetall['H1'] = 'Полный пансион'
        sheetall['I1'] = 'Полупансион'
        sheetall['J1'] = 'Завтрак'
        sheetall['K1'] = 'Трансфер'
        sheetall['L1'] = 'От туроператора'
        sheetall['M1'] = 'Комментарий'
        for item in row:
            sumg = 0
            for j in letters[0:6]:
                sheetall[j + str(k)] = item[i]
                i += 1
            for numguest in range(6, 11):
                if item[numguest]:
                    sumg += 1
            sheetall[letters[6] + str(k)] = sumg
            sheetall[letters[7] + str(k)] = item[11]
            sheetall[letters[8] + str(k)] = item[12]
            sheetall[letters[9] + str(k)] = item[13]
            if item[14] == 1:
                sheetall[letters[10] + str(k)] = 'Нужен'
            if item[15] == 1:
                sheetall[letters[11] + str(k)] = 'Да'
            sheetall[letters[12] + str(k)] = item[16]
            k += 1
            i = 0
        try:
            workbookall.save(filename="Все_бронирования.xlsx")
        except PermissionError:
            return '<h2>Файл отчета открыт, чтобы выгрузить новый отчет закройте файл</h2>'
        return redirect('/check')
    return render_template('check.html')


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == 'POST' and 'FullName1' in request.form:
        sumbook = (datetime.fromisoformat(request.form['DateEnd'].replace('T', ' ')) -
                   datetime.fromisoformat(request.form['DateStart'].replace('T', ' '))).days * int(request.form['Price'])
        startdatedef = datetime.fromisoformat(request.form['DateStart'].replace('T', ' '))
        enddatedef = datetime.fromisoformat(request.form['DateEnd'].replace('T', ' '))
        db = get_db()
        dbase = DBSQL.DBSQL(db)
        guest1 = gclass.GClass()
        guest2 = gclass.GClass()
        guest3 = gclass.GClass()
        guest4 = gclass.GClass()
        guest5 = gclass.GClass()
        guest1.createguest1(request.form)
        guest2.createguest2(request.form)
        guest3.createguest3(request.form)
        guest4.createguest4(request.form)
        guest5.createguest5(request.form)
        if 'Transfer' in request.form and request.form['Transfer'] == 'on':
            transfer = 1
        else:
            transfer = 0
        if 'Tour' in request.form and request.form['Tour'] == 'on':
            tour = 1
        else:
            tour = 0
        resadd = dbase.addbook(guest1, guest2, guest3, guest4, guest5,
                               startdatedef, enddatedef, request.form['Room'],
                               tour, transfer, request.form['Price'],
                               sumbook, str(startdatedef), str(enddatedef), request.form['Comm'])
        db.commit()
        db.close()
        if resadd == 1:
            return '<h2>Бронь не может быть создана. Комната занята в эти даты</h2>'
        if resadd == 0:
            return '<h2>Бронь не может быть создана. Произошла ошибка</h2>'
        return redirect('/')
    else:
        return render_template('index.html')


if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:5000/')
    app.run()
