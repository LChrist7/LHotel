from datetime import date, timedelta, datetime
from flask import Flask, render_template, url_for, request, g, redirect
from openpyxl import Workbook
from openpyxl.styles import PatternFill
import os
import sqlite3
import DBSQL
import string
import sys
import webbrowser
import gclass


def get_app_dir():
    """Возвращает директорию для хранения данных приложения"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller: используем директорию где лежит exe файл
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


DATABASE = os.path.join(get_app_dir(), 'hotel.db')
DEBUG = False
SECRET_KEY = 'anua'


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


app = Flask(__name__, static_url_path="", static_folder=resource_path(
    'static'), template_folder=resource_path("templates"))
app.config.from_object(__name__)


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


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
    numbook = request.args.get('numbook', '')
    return render_template('cancel.html', numbook=numbook)


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
        memfio = ''
        for j in letters[0:alldelta + 1]:
            sheet[j + str(1)] = str(start_date)
            sheet.column_dimensions[j].width = 20
            start_date += delta
        for m in range(2, len(rooms) + 2):
            for j in letters[0:alldelta + 1]:
                roomv = sheet['A' + str(m)].value
                datev = sheet[j + str(1)].value
                sqlres = dbase.makecheck(datev, roomv)
                if sqlres and len(sqlres) == 1:
                    if sqlres[0]['tour'] == 1:
                        background = PatternFill(fill_type='solid', fgColor="9FC5E8")
                    else:
                        background = PatternFill(fill_type='solid', fgColor="FFC7CE")
                    try:
                        if sqlres[0]['fio'] != '' and sheet[j + str(m)].value is None:
                            sheet[j + str(m)] = sqlres[0]['numbook'] + ' ' + sqlres[0]['fio'].split(" ")[0]
                            sheet[j + str(m)].fill = background
                            # sheet.merge_cells(str(j + str(m)) + ':' + str(letters[letters.index(j)
                            #                                                     + int(sqlres[0]['days'])] + str(m)))
                    except AttributeError as e:
                        print(e)
                if sqlres and len(sqlres) == 2:
                    sheet.column_dimensions[j].width = 23
                    if sqlres[1]['tour'] == 1:
                        background = PatternFill(fill_type='solid', fgColor="9FC5E8")
                    else:
                        background = PatternFill(fill_type='solid', fgColor="FFC7CE")
                    sheet[j + str(m)] = (sqlres[0]['numbook'] + ' ' + sqlres[0]['fio'].split(" ")[0] +
                                         ' - ' + sqlres[1]['numbook'] + ' ' + sqlres[1]['fio'].split(" ")[0])
                    sheet[j + str(m)].fill = background
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
        sheetall.column_dimensions['C'].width = 14
        sheetall.column_dimensions['B'].width = 45
        sheetall.column_dimensions['C'].width = 12
        sheetall.column_dimensions['D'].width = 20
        sheetall.column_dimensions['H'].width = 16
        sheetall.column_dimensions['I'].width = 13
        sheetall.column_dimensions['L'].width = 16
        sheetall.column_dimensions['M'].width = 50
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
        sheetall['K1'] = 'От туроператора'
        sheetall['L1'] = 'Трансфер'
        sheetall['M1'] = 'Комментарий'
        i, k = 0, 2
        for item in row:
            sumg = 0
            for j in letters[0:6]:
                sheetall[j + str(k)] = item[i]
                i += 1
            for numguest in range(6, 11):
                if item[numguest]:
                    sumg += 1
            sheetall[letters[6] + str(k)] = sumg
            if item[11] == 0:
                sheetall[letters[7] + str(k)] = ''
            else:
                sheetall[letters[7] + str(k)] = item[11]
            if item[12] == 0:
                sheetall[letters[8] + str(k)] = ''
            else:
                sheetall[letters[8] + str(k)] = item[12]
            if item[13] == 0:
                sheetall[letters[9] + str(k)] = ''
            else:
                sheetall[letters[9] + str(k)] = item[13]
            if item[14] == 1:
                sheetall[letters[10] + str(k)] = 'Да'
            if item[15] == 1:
                sheetall[letters[11] + str(k)] = 'Нужен'
            sheetall[letters[12] + str(k)] = item[16]
            k += 1
            i = 0
        try:
            workbookall.save(filename="Все_бронирования.xlsx")
        except PermissionError:
            return '<h2>Файл отчета открыт, чтобы выгрузить новый отчет закройте файл</h2>'
        return redirect('/check')
    return render_template('check.html')


@app.route("/change", methods=["POST", "GET"])
def change():
    if request.method == 'POST' and 'numchange' in request.form and request.form['numchange']:
        db = get_db()
        dbase = DBSQL.DBSQL(db)
        context = list(dbase.viewbook(request.form['numchange']))
        try:
            guests = list(context[0])
        except IndexError:
            return "<h2>Брони с таким номером не существует</h2>"
        info = list(context[1])
        return render_template('change.html', guest1=dict(guests[0]),
                               guest2=(dict(guests[1]) if len(guests) > 1 else []),
                               guest3=(dict(guests[2]) if len(guests) > 2 else []),
                               guest4=(dict(guests[3]) if len(guests) > 3 else []),
                               guest5=(dict(guests[4]) if len(guests) > 4 else []),
                               info=dict(info[0]), sumdiff=int(info[0]['sumbook'] - info[0]['prep']))
    if request.method == 'POST' and 'FullName1' in request.form and request.form['FullName1']:
        db = get_db()
        dbase = DBSQL.DBSQL(db)
        startdatedef = datetime.fromisoformat(request.form['DateStart'].replace('T', ' '))
        enddatedef = datetime.fromisoformat(request.form['DateEnd'].replace('T', ' '))

        # Подсчёт количества гостей и питания
        guest_count = 0
        fullpans_count = 0
        halfpans_count = 0
        breakfast_count = 0
        for i in range(1, 6):
            if request.form.get(f'FullName{i}'):
                guest_count += 1
                if request.form.get(f'fullpans{i}') == 'on':
                    fullpans_count += 1
                if request.form.get(f'halfpans{i}') == 'on':
                    halfpans_count += 1
                if request.form.get(f'breakfast{i}') == 'on':
                    breakfast_count += 1

        # Расчёт с учётом сезонов
        sumbook = dbase.calculate_full_booking_price(
            str(startdatedef.date()), str(enddatedef.date()),
            guest_count=max(guest_count, 1),
            fullpans_count=fullpans_count,
            halfpans_count=halfpans_count,
            breakfast_count=breakfast_count
        )

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
        resadd = dbase.updatebook(request.form['numchange2'], guest1, guest2, guest3, guest4, guest5,
                                  startdatedef, enddatedef, request.form['Room'],
                                  tour, transfer, request.form['Price'], request.form['Prep'],
                                  sumbook, str(startdatedef), str(enddatedef), request.form['Comm'])
        db.commit()
        db.close()
        if resadd == 1:
            return '<h2>Бронь не может быть создана. Комната занята в эти даты</h2>'
        if resadd == 0:
            return '<h2>Бронь не может быть создана. Произошла ошибка</h2>'
        return redirect("/change")
    else:
        db = get_db()
        dbase = DBSQL.DBSQL(db)
        bookings = dbase.get_current_year_bookings()
        return render_template('change.html', guest1=[], guest2=[], guest3=[], guest4=[], guest5=[],
                               info=[], sumdiff=0, bookings=bookings, now=datetime.now())


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == 'POST' and 'FullName1' in request.form:
        startdatedef = datetime.fromisoformat(request.form['DateStart'].replace('T', ' '))
        enddatedef = datetime.fromisoformat(request.form['DateEnd'].replace('T', ' '))
        db = get_db()
        dbase = DBSQL.DBSQL(db)

        # Подсчёт количества гостей и питания
        guest_count = 0
        fullpans_count = 0
        halfpans_count = 0
        breakfast_count = 0
        for i in range(1, 6):
            if request.form.get(f'FullName{i}'):
                guest_count += 1
                if request.form.get(f'fullpans{i}') == 'on':
                    fullpans_count += 1
                if request.form.get(f'halfpans{i}') == 'on':
                    halfpans_count += 1
                if request.form.get(f'breakfast{i}') == 'on':
                    breakfast_count += 1

        # Расчёт с учётом сезонов
        sumbook = dbase.calculate_full_booking_price(
            str(startdatedef.date()), str(enddatedef.date()),
            guest_count=max(guest_count, 1),
            fullpans_count=fullpans_count,
            halfpans_count=halfpans_count,
            breakfast_count=breakfast_count
        )

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
        resadd = dbase.addbook(request.form['Numbook'], guest1, guest2, guest3, guest4, guest5,
                               startdatedef, enddatedef, request.form['Room'],
                               tour, transfer, request.form['Price'], request.form['Prep'],
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


@app.route("/seasons", methods=["GET", "POST"])
def seasons():
    db = get_db()
    dbase = DBSQL.DBSQL(db)

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add':
            name = request.form.get('name')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            base_price = float(request.form.get('base_price', 5000))
            extra_person_price = float(request.form.get('extra_person_price', 1000))
            fullpans_price = float(request.form.get('fullpans_price', 2500))
            halfpans_price = float(request.form.get('halfpans_price', 1500))
            breakfast_price = float(request.form.get('breakfast_price', 500))
            dbase.add_season(name, start_date, end_date, base_price, extra_person_price,
                             fullpans_price, halfpans_price, breakfast_price)
            db.commit()

        elif action == 'update':
            season_id = int(request.form.get('season_id'))
            name = request.form.get('name')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            base_price = float(request.form.get('base_price', 5000))
            extra_person_price = float(request.form.get('extra_person_price', 1000))
            fullpans_price = float(request.form.get('fullpans_price', 2500))
            halfpans_price = float(request.form.get('halfpans_price', 1500))
            breakfast_price = float(request.form.get('breakfast_price', 500))
            dbase.update_season(season_id, name, start_date, end_date, base_price, extra_person_price,
                                fullpans_price, halfpans_price, breakfast_price)
            db.commit()

        elif action == 'delete':
            season_id = int(request.form.get('season_id'))
            dbase.delete_season(season_id)
            db.commit()

        return redirect('/seasons')

    seasons_list = dbase.get_seasons()
    return render_template('seasons.html', seasons=seasons_list)


@app.route("/api/seasonal-price", methods=["POST"])
def api_seasonal_price():
    """API для расчёта цены с учётом сезонов, количества гостей и питания"""
    import json
    from datetime import datetime, timedelta
    db = get_db()
    dbase = DBSQL.DBSQL(db)

    data = request.get_json() if request.is_json else request.form
    start_date = data.get('start_date', '')
    end_date = data.get('end_date', '')
    guest_count = int(data.get('guest_count', 2))
    fullpans_count = int(data.get('fullpans_count', 0))
    halfpans_count = int(data.get('halfpans_count', 0))
    breakfast_count = int(data.get('breakfast_count', 0))

    if start_date and end_date:
        # Расчёт с учётом периода (разные сезоны)
        try:
            start = datetime.strptime(start_date[:10], '%Y-%m-%d').date()
            end = datetime.strptime(end_date[:10], '%Y-%m-%d').date()

            if end <= start:
                return json.dumps({'error': 'Дата выезда должна быть позже даты заезда', 'total': 0})

            total_accommodation = 0
            total_meals = 0
            current = start
            delta = timedelta(days=1)
            nights = 0
            seasons_used = []

            while current < end:
                season = dbase.get_season_for_date(str(current))

                # Проживание за эту ночь
                daily_accommodation = season['base_price']
                if guest_count > 2:
                    daily_accommodation += (guest_count - 2) * season['extra_person_price']
                total_accommodation += daily_accommodation

                # Питание за эту ночь
                fullpans_price = season.get('fullpans_price', 2500)
                halfpans_price = season.get('halfpans_price', 1500)
                breakfast_price = season.get('breakfast_price', 500)

                daily_meals = (fullpans_count * fullpans_price +
                              halfpans_count * halfpans_price +
                              breakfast_count * breakfast_price)
                total_meals += daily_meals

                # Учёт использованных сезонов
                if season['name'] not in seasons_used:
                    seasons_used.append(season['name'])

                current += delta
                nights += 1

            total = total_accommodation + total_meals

            return json.dumps({
                'total': total,
                'total_accommodation': total_accommodation,
                'total_meals': total_meals,
                'nights': nights,
                'seasons_used': seasons_used,
                'guest_count': guest_count,
                'fullpans_count': fullpans_count,
                'halfpans_count': halfpans_count,
                'breakfast_count': breakfast_count
            })
        except Exception as e:
            return json.dumps({'error': str(e), 'total': 0})

    elif start_date:
        # Расчёт только за одни сутки (для отображения цены за ночь)
        season = dbase.get_season_for_date(start_date)
        if season:
            base_price = season['base_price']
            extra_person_price = season['extra_person_price']
            fullpans_price = season.get('fullpans_price', 2500)
            halfpans_price = season.get('halfpans_price', 1500)
            breakfast_price = season.get('breakfast_price', 500)

            accommodation = base_price
            if guest_count > 2:
                accommodation += extra_person_price * (guest_count - 2)

            meals = (fullpans_count * fullpans_price +
                    halfpans_count * halfpans_price +
                    breakfast_count * breakfast_price)

            daily_total = accommodation + meals

            return json.dumps({
                'daily_total': daily_total,
                'accommodation': accommodation,
                'meals': meals,
                'season_name': season['name'],
                'base_price': base_price,
                'extra_person_price': extra_person_price,
                'fullpans_price': fullpans_price,
                'halfpans_price': halfpans_price,
                'breakfast_price': breakfast_price
            })

    return json.dumps({'daily_total': 0, 'total': 0})


@app.route("/stats", methods=["GET", "POST"])
def stats():
    today = date.today()
    # По умолчанию статистика за текущий год
    if request.method == 'POST':
        start_date = request.form.get('start_date', f'{today.year}-01-01')
        end_date = request.form.get('end_date', str(today))
    else:
        start_date = request.args.get('start_date', f'{today.year}-01-01')
        end_date = request.args.get('end_date', str(today))

    db = get_db()
    dbase = DBSQL.DBSQL(db)
    statistics = dbase.get_statistics(start_date, end_date)

    return render_template('stats.html',
                           stats=statistics,
                           start_date=start_date,
                           end_date=end_date)


@app.route("/calendar", methods=["GET", "POST"])
def calendar():
    today = date.today()
    # По умолчанию показываем текущий месяц
    if request.method == 'POST':
        year = int(request.form.get('year', today.year))
        month = int(request.form.get('month', today.month))
    else:
        year = int(request.args.get('year', today.year))
        month = int(request.args.get('month', today.month))

    # Первый и последний день месяца
    first_day = date(year, month, 1)
    if month == 12:
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)

    db = get_db()
    dbase = DBSQL.DBSQL(db)
    calendar_data = dbase.get_calendar_data(str(first_day), str(last_day))

    # Формируем список дней месяца
    days = []
    current = first_day
    while current <= last_day:
        days.append(current)
        current += timedelta(days=1)

    # Подготавливаем данные для отображения с объединёнными ячейками
    room_rows = {}
    for room in calendar_data['rooms']:
        room_rows[room] = []
        day_idx = 0

        while day_idx < len(days):
            day = days[day_idx]
            day_str = day.strftime('%Y-%m-%d')

            # Ищем бронь которая начинается или продолжается в этот день
            booking_found = None
            for booking in calendar_data['bookings']:
                if booking['room'] == room:
                    bstart = booking['datestart'][:10] if booking['datestart'] else ''
                    bend = booking['dateend'][:10] if booking['dateend'] else ''
                    # Бронь активна от заезда до выезда включительно
                    if bstart <= day_str <= bend:
                        booking_found = booking
                        break

            if booking_found:
                bstart = booking_found['datestart'][:10]
                bend = booking_found['dateend'][:10]
                start_date_obj = datetime.strptime(bstart, '%Y-%m-%d').date()
                end_date_obj = datetime.strptime(bend, '%Y-%m-%d').date()

                # Определяем начало отображения (не раньше первого дня месяца)
                display_start = max(start_date_obj, first_day)
                # Определяем конец отображения (не позже последнего дня месяца)
                display_end = min(end_date_obj, last_day)

                # colspan - количество дней отображения
                colspan = (display_end - display_start).days + 1

                # Получаем фамилию
                guest_name = booking_found.get('guest_name', '')
                surname = guest_name.split(' ')[0] if guest_name else ''
                numbook = booking_found.get('numbook', '')
                is_tour = booking_found.get('tour', 0) == 1

                # Определяем позицию ячейки в брони
                is_first = (day == start_date_obj)  # Первая ячейка (заезд)
                is_last = (display_end == end_date_obj)  # Последняя ячейка (выезд)

                room_rows[room].append({
                    'type': 'booking',
                    'colspan': colspan,
                    'numbook': numbook,
                    'surname': surname,
                    'is_tour': is_tour,
                    'is_first': is_first,
                    'is_last': is_last,
                    'booking': booking_found
                })
                day_idx += colspan
            else:
                room_rows[room].append({
                    'type': 'empty',
                    'colspan': 1
                })
                day_idx += 1

    # Названия месяцев
    month_names = ['', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                   'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']

    return render_template('calendar.html',
                           rooms=calendar_data['rooms'],
                           room_rows=room_rows,
                           days=days,
                           year=year,
                           month=month,
                           month_name=month_names[month],
                           today=today)


if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:5000/')
    app.run()
