#     conn.autocommit = True
import webbrowser
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import psycopg2  # Бібліотека для підключення БД
import datetime
from PyQt5 import uic, QtWidgets, QtGui, QtPrintSupport, QtCore  # Бібліотека для підключення макету і віджетів
from PyQt5.QtWidgets import QApplication, QMessageBox, QLineEdit, \
    QPushButton, QFileDialog
from PyQt5.QtGui import QIcon  # Бібліотека для надання іконок
from PyQt5.QtCore import QTime, QDir, QUrl
# Завчасно створена глобальна зміна, для підключення БД
global conn
now = datetime.datetime.now()
# -------------------------------------------------
Form, Window = uic.loadUiType("Widgets\Connect.ui")
app = QApplication([])
# Пдіключення файлу з макетом інтерфейса до пайтона
window = Window()
form = Form()  # Екземпляр класу форми, щоб звертатися до певних елементів
form.setupUi(window)
msg = form.password.setEchoMode(QtWidgets.QLineEdit.Password)
# -------------------------------------------------

# Функція, що перевіряє введені логін та пароль
def check_login_and_pass():
    if form.login.displayText() == "" and form.password.displayText() == "":
        msg = form.password.setEchoMode(QtWidgets.QLineEdit.Password)
        msg = QMessageBox()
        msg.setWindowTitle("Помилка")
        msg.setText("Поля логіна та пароля не введені, переконайтеся у правильності введення!")
        msg.setWindowIcon(QIcon("images\error.png"))
        msg.setIcon(QMessageBox.Critical)
        x = msg.exec_()
    elif form.login.displayText() == "":
        msg = form.password.setEchoMode(QtWidgets.QLineEdit.Password)
        msg = QMessageBox()
        msg.setWindowTitle("Помилка")
        msg.setText("Поле для логіна не введене!")
        msg.setWindowIcon(QIcon("images\error.png"))
        msg.setIcon(QMessageBox.Critical)
        x = msg.exec_()
    elif form.password.displayText() == "":
        msg = form.password.setEchoMode(QtWidgets.QLineEdit.Password)
        msg = QMessageBox()
        msg.setWindowTitle("Помилка")
        msg.setText("Поле для пароля не введене!")
        msg.setWindowIcon(QIcon("images\error.png"))
        msg.setIcon(QMessageBox.Critical)
        x = msg.exec_()
    else:
        try:
            form.password.setEchoMode(QLineEdit.Normal)
            conn = psycopg2.connect(
                host="localhost",
                user=form.login.displayText(),
                password=form.password.displayText(),
                database="Marchenko",
                port=5432
            )
            form.password.setEchoMode(QLineEdit.Password)

            msg = QMessageBox()
            msg.setWindowTitle("Успішно!")
            msg.setText(f"Вітаю \"{form.login.displayText()}\", "f"вхід в базу "
                        f"даних здійснено успішно!")
            msg.setWindowIcon(QIcon("images\Information.png"))
            msg.setIcon(QMessageBox.Information)
            x = msg.exec_()
            # ----------------------------------------------------

            app.closeAllWindows()
            show_FormTable(conn)  # Викликаємо функцію, щоб показати інше вікно, передаємо в функцію підключення до БД
            return

        except Exception as ex:
            msg = form.password.setEchoMode(QtWidgets.QLineEdit.Password)
            msg = QMessageBox()
            msg.setWindowTitle("Помилка")
            msg.setText(f"Вхід \"{form.login.displayText()}\", "f" вхід невірний, перевірте правильніть даних!")
            msg.setWindowIcon(QIcon("images\error.png"))
            msg.setIcon(QMessageBox.Critical)
            x = msg.exec_()

def show_HeadForm():
    window.show()
    form.login.setPlaceholderText('Введіть Логін')
    form.password.setPlaceholderText('Введіть пароль')
    form.Enter.clicked.connect(check_login_and_pass)

    app.exec_()

Form_table, Window_table = uic.loadUiType("Widgets\Head.ui")
window_table = Window_table()
form_table = Form_table()
form_table.setupUi(window_table)

# Відображення вікна після авторизації, котра отримує підключення до БД
def show_FormTable(conn):
    window_table.show()

    def back_window():
        app.closeAllWindows()
        window.show()
        return

    form_table.Back.clicked.connect(lambda state: back_window())  # Натискаючи кнопку, ми перейдемо до вікна авторизації
    form_table.Next.clicked.connect(lambda state, x=conn: show_reports_window(x))
    form_table.After.clicked.connect(lambda state, x=conn: show_grafic_window(x))

    # Загальна функція, що відопвідає за занесення даних із БД по таблицях
    def show_table(name_table, name_table_form, type_str):
        with conn.cursor() as cur:
            sql = f"SELECT * FROM {name_table};"    # Створюємо запит на вибірку
            cur.execute(sql)                        # Зберігаємо результат
            length = len(cur.fetchall())+1          # Обраховуємо кількість рядків
            name_table_form.setRowCount(length)     # Створюємо обраховані рядки

            column = name_table_form.columnCount()  # Обрахунок колонок

            tableRow = 0                        # Лічильник для рідків
            cur.execute(sql)                    # Знову оброблюємо запит на вибірку
            i = 0                               # Лічильник для колонок
            for row in cur.fetchall():          # Передаємо змінній в циклі, значення таблиць по черзі
                while i < column:               # Створюємо цикл для колонок
                    if i < type_str:            # Якщо потрібно перетворити значення в рядки
                        name_table_form.setItem(tableRow, i, QtWidgets.QTableWidgetItem(str(row[i])))
                    else:                       # Інакше додаємо спочатку визначивши рядок, колонку а потім саме значення
                        name_table_form.setItem(tableRow, i, QtWidgets.QTableWidgetItem(str(row[i])))
                    i += 1                      # Додаємо одиничку до наступної колонки
                i = 0                           # Обнулюємо лічильник
                tableRow += 1                   # Додаємо до лічильника рядків
        return


    show_table("Category", form_table.table_Category, 0)
    show_table("Measurment_Unit", form_table.table_measurment_unit, 0)
    show_table("Optimal_value", form_table.table_Optimal_value, 0)
    show_table("MQTT_Server", form_table.table_MQTT_Server, 0)
    show_table("Station", form_table.table_Station, 0)
    show_table("Coordinates", form_table.table_Coordinates, 0)
    show_table("Favorite_station", form_table.table_Favorite, 0)
    show_table("MQTT_Unit", form_table.table_MQTT_Unit, 0)
    show_table("Measurment", form_table.table_Measurment, 0)

    # if conn:
    #     conn.close()
    #     print(":Information: PostgreSQL connection closed")

    app.exec_()
    return

Form_rep, Window_rep = uic.loadUiType("Widgets\Reports.ui")
window_rep = Window_rep()
form_rep = Form_rep()
form_rep.setupUi(window_rep)


def show_reports_window(conn):
    app.closeAllWindows()
    window_rep.show()

    def back_window():
        app.closeAllWindows()
        window_table.show()
        form_rep.table_report_1.setRowCount(0)
        form_rep.label_head.setText('')

        form_rep.table_report_2.setRowCount(0)
        form_rep.label_head_2.setText('')
        return

    def delete_date_table(number):
        if number == 1:
            form_rep.table_report_1.setRowCount(0)
            form_rep.label_head.setText('')
        elif number == 2:
            form_rep.table_report_2.setRowCount(0)
            form_rep.label_head_2.setText('')
        return

    def load_report(isCombo):
        def add_date(sql):
            cur.execute(sql)  # Зберігаємо результат
            length = len(cur.fetchall()) + 1  # Обраховуємо кількість рядків
            form_rep.table_report_1.setRowCount(length)  # Створюємо обраховані рядки

            column = form_rep.table_report_1.columnCount()  # Обрахунок колонок

            name_row = ""
            tableRow = 0  # Лічильник для рідків
            cur.execute(sql)  # Знову оброблюємо запит на вибірку
            i = 0  # Лічильник для колонок
            for row in cur.fetchall():  # Передаємо змінній в циклі, значення таблиць по черзі
                while i < column:  # Створюємо цикл для колонок
                    if (tableRow > 0) and (row[i] == name_row) and i == 0:
                        form_rep.table_report_1.setItem(tableRow, i, QtWidgets.QTableWidgetItem(""))
                    elif (tableRow > 0) and (i == 1) and (form_rep.table_report_1.item(tableRow, 0).text() == ""):
                        form_rep.table_report_1.setItem(tableRow, i, QtWidgets.QTableWidgetItem(""))
                    else:
                        form_rep.table_report_1.setItem(tableRow, i, QtWidgets.QTableWidgetItem(str(row[i])))

                    i += 1  # Додаємо одиничку до наступної колонки
                i = 0  # Обнулюємо лічильник

                tableRow += 1  # Додаємо до лічильника рядків
                name_row = row[i]
            return

        with conn.cursor() as cur:
            if form_rep.combo_name_st.currentText() != "Список станцій" and isCombo:
                name_st = form_rep.combo_name_st.currentText()

                sql = "SELECT DISTINCT s.name_st as name_st, MIN(Measurment.time_of_measurment) as time, Measurment_Unit.title as titles\n" \
                      "FROM station as s, Measurment_Unit, measurment\n" \
                      "WHERE s.id_station = measurment.id_station AND\n" \
                      "measurment.id_measured_unit = Measurment_Unit.id_measured_unit AND\n" \
                      f"s.name_st = '{name_st}'\n" \
                      "GROUP BY name_st, titles\n" \
                      "ORDER BY name_st;"
                form_rep.label_head.setText(f'Список параметрів повітря підключеної станції "{name_st}"')
                add_date(sql)
            elif form_rep.combo_name_st.currentText() == "Список станцій" and isCombo:
                msg = QMessageBox()
                msg.setWindowTitle("Помилка")
                msg.setText(f"На жаль, але "
                            f"ви не можете побачити список, адже обрали 'Список станцій', оберіть назву станції!")
                msg.setWindowIcon(QIcon("images\Error.png"))
                msg.setIcon(QMessageBox.Critical)
                x = msg.exec_()
                return
            else:
                sql = "SELECT DISTINCT s.name_st as name_st, MIN(Measurment.time_of_measurment) as time, measurment_unit.title as titles\n" \
                      "FROM station as s, measurment_unit, measurment\n" \
                      "WHERE s.id_station = measurment.id_station AND\n" \
                      "measurment.id_measured_unit = measurment_unit.id_measured_unit \n" \
                      "GROUP BY name_st, titles\n" \
                      "ORDER BY name_st;"
                form_rep.label_head.setText('Список підключених станцій з параметрами повітря')
                add_date(sql)
        return

    def load_report_paramet_station():
        def add_date(sql):
            cur.execute(sql)  # Зберігаємо результат
            length = len(cur.fetchall()) + 1  # Обраховуємо кількість рядків
            form_rep.table_report_2.setRowCount(length)  # Створюємо обраховані рядки

            column = form_rep.table_report_2.columnCount()  # Обрахунок колонок

            name_row = ""
            tableRow = 0  # Лічильник для рідків
            cur.execute(sql)  # Знову оброблюємо запит на вибірку
            i = 0  # Лічильник для колонок
            for row in cur.fetchall():  # Передаємо змінній в циклі, значення таблиць по черзі
                while i < column:  # Створюємо цикл для колонок
                    form_rep.table_report_2.setItem(tableRow, i, QtWidgets.QTableWidgetItem(str(row[i])))

                    i += 1  # Додаємо одиничку до наступної колонки
                i = 0  # Обнулюємо лічильник

                tableRow += 1  # Додаємо до лічильника рядків
            return

        with conn.cursor() as cur:
            if form_rep.combo_name_st_2.currentText() != "Список станцій":
                name_st = form_rep.combo_name_st_2.currentText()
                start_date = form_rep.start_date.date().toPyDate()
                start_time = form_rep.start_time.time().toPyTime()
                start_datetime = str(start_date) + " " + str(start_time)

                end_date = form_rep.end_date.date().toPyDate()
                end_time = form_rep.end_time.time().toPyTime()
                end_datetime = str(end_date) + " " + str(end_time)
                sql = "SELECT Measurment_Unit.title as title,\n" \
                      "ROUND(MIN(CAST(measurment.value_m as numeric)), 2) as minimum,\n" \
                      "ROUND(AVG(CAST(measurment.value_m as numeric)), 2) as avarage,\n" \
                      "ROUND(MAX(CAST(measurment.value_m as numeric)), 2) as maximum\n" \
                      "FROM station as s, measurment, Measurment_Unit\n" \
                      "WHERE s.id_station = measurment.id_station AND\n" \
                      "measurment.id_measured_unit = Measurment_Unit.id_measured_unit AND\n" \
                      f"s.name_st = '{name_st}' AND\n" \
                      f"measurment.time_of_measurment BETWEEN '{start_datetime}' AND '{end_datetime}'\n" \
                      "GROUP BY title;"
                form_rep.label_head_2.setText(f'Вимірювання станцією "{name_st}"')
                add_date(sql)
                return
            elif form_rep.combo_name_st_2.currentText() == "Список станцій":
                msg = QMessageBox()
                msg.setWindowTitle("Помилка")
                msg.setText(f"На жаль,  "
                            f"список не відобразиться, не обрано станцію, оберіть назву станції!")
                msg.setWindowIcon(QIcon("images\Error.png"))
                msg.setIcon(QMessageBox.Critical)
                x = msg.exec_()
                return
        return

    form_rep.btn_back.clicked.connect(lambda state: back_window())
    form_rep.btn_load_report.clicked.connect(lambda state, x=False: load_report(x))
    form_rep.btn_load_report_2.clicked.connect(lambda state, x=True: load_report(x))
    form_rep.btn_load_report_3.clicked.connect(lambda state: load_report_paramet_station())
    form_rep.btn_clear_table.clicked.connect(lambda state: delete_date_table(1))
    form_rep.btn_clear_table_2.clicked.connect(lambda state, x=2: delete_date_table(2))

    index = form_rep.combo_name_st.findText("Список станцій")
    if not (int(index > -1)):
        form_rep.combo_name_st.addItem('Список станцій')

    index = form_rep.combo_name_st_2.findText("Список станцій")
    if not (int(index > -1)):
        form_rep.combo_name_st_2.addItem('Список станцій')

    with conn.cursor() as cur:
        sql = '''SELECT name_st FROM Station;'''

        cur.execute(sql)
        for date in cur.fetchall():
            station = form_rep.combo_name_st.findText(date[0])
            if not (int(station) > -1):
                form_rep.combo_name_st.addItem(date[0])

        cur.execute(sql)
        for date in cur.fetchall():
            station = form_rep.combo_name_st_2.findText(date[0])
            if not (int(station) > -1):
                form_rep.combo_name_st_2.addItem(date[0])

    form_rep.start_date.setDate(now)
    form_rep.end_date.setDate(now)

    time = QTime()
    time.setHMS(now.hour, now.minute, now.second)
    form_rep.start_time.setTime(time)
    form_rep.end_time.setTime(time)
# //////////////////////////
    def load_for_PDF(number: int, table: object):
        path = QFileDialog.getSaveFileName(table, 'Save Files', QDir.homePath() + "/report.pdf", "PDF files (*.pdf)")
        filename = path[0]

        w = table
        model = w.model()

        printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.PrinterResolution)
        printer.setOutputFormat(QtPrintSupport.QPrinter.PdfFormat)
        printer.setPaperSize(QtPrintSupport.QPrinter.A4)
        printer.setOrientation(QtPrintSupport.QPrinter.Landscape)
        printer.setOutputFileName(filename)

        doc = QtGui.QTextDocument()

        html = """<html>
                            <head>
                                <style>
                                    table, th, td {
                                         border: 1px black;
                                         empty-cells: hide;
                                    }
                                    th{
                                        background-color: #ffffff; 
                                        color: #000505;
                                    }
                                    td{
                                        background-color: #ffffff; 
                                        color: #000505;
                                    }
                                    table{
                                        margin-left: 200px
                                    }
                                    h3{
                                        text-align: center;
                                    }
                                    p{
                                       text-align: right;
                                    }
                                </style>
                            </head>"""
        if number == 1:
            html += f"<h3>{form_rep.label_head.text()}</h3><br>"
        else:
            html += f"<h3>{form_rep.label_head_2.text()}</h3><br>"

        html += "<table border=\"1\"><thead>"
        html += "<tr>"
        for c in range(model.columnCount()):
            html += "<th>{}</th>".format(model.headerData(c, QtCore.Qt.Horizontal))

        html += "</tr></thead>"
        html += "<tbody>"
        for r in range(model.rowCount()):
            html += "<tr>"
            for c in range(model.columnCount()):
                html += "<td>{}</td>".format(model.index(r, c).data() or "")
            html += "</tr>"
        html += "</tbody></table><br>"
        html += f"<p>{now.year}/{now.month}/{now.day} {now.hour}:{now.minute}</p>"
        doc.setHtml(html)
        doc.setPageSize(QtCore.QSizeF(printer.pageRect().size()))
        doc.print_(printer)

        webbrowser.open_new(filename)


    form_rep.btn_load_for_pdf.clicked.connect(lambda state, x=2, y=form_rep.table_report_1: load_for_PDF(x, y))
    form_rep.btn_load_for_pdf_2.clicked.connect(lambda state, x=1, y=form_rep.table_report_2: load_for_PDF(x, y))
    # *********************************************************************

Form_gra, Window_gra = uic.loadUiType("Widgets\grafic.ui")
window_gra = Window_gra()
form_gra = Form_gra()
form_gra.setupUi(window_gra)

def show_grafic_window(conn):
    app.closeAllWindows()
    window_gra.show()

    figure = plt.figure()
    canvas = FigureCanvas(figure)

    form_gra.frame_grafic.hide()
    form_gra.frame_grafic_2.hide()
    form_gra.frame_grafic_3.hide()
    form_gra.frame_grafic_4.hide()

    def back_window():
        app.closeAllWindows()
        window_table.show()

        form_gra.frame_grafic.hide()
        form_gra.table_grafic.setRowCount(0)
        form_gra.frame_grafic_2.hide()
        form_gra.table_grafic_2.setRowCount(0)
        form_gra.frame_grafic_3.hide()
        form_gra.table_grafic_3.setRowCount(0)
        form_gra.frame_grafic_4.hide()
        form_gra.table_grafic_4.setRowCount(0)

    def clear():
        form_gra.frame_grafic.hide()
        form_gra.table_grafic.setRowCount(0)

    def clear_2():
        form_gra.frame_grafic_2.hide()
        form_gra.table_grafic_2.setRowCount(0)

    def clear_3():
        form_gra.frame_grafic_3.hide()
        form_gra.table_grafic_3.setRowCount(0)

    def clear_4():
        form_gra.frame_grafic_4.hide()
        form_gra.table_grafic_4.setRowCount(0)

    def view_grafic():
        city = []
        titles = []
        def add_date(sql):
            cur.execute(sql)  # Зберігаємо результат

            length = len(cur.fetchall()) + 1  # Обраховуємо кількість рядків
            form_gra.table_grafic.setRowCount(length)  # Створюємо обраховані рядки

            column = form_gra.table_grafic.columnCount()  # Обрахунок колонок

            tableRow = 0  # Лічильник для рідків
            cur.execute(sql)  # Знову оброблюємо запит на вибірку
            i = 0  # Лічильник для колонок
            for row in cur.fetchall():  # Передаємо змінній в циклі, значення таблиць по черзі
                while i < column:  # Створюємо цикл для колонок
                    if i == 0:
                        city.append(row[i])
                    elif i == 1:
                        titles.append(row[i])
                    form_gra.table_grafic.setItem(tableRow, i, QtWidgets.QTableWidgetItem(str(row[i])))
                    i += 1  # Додаємо одиничку до наступної колонки
                i = 0  # Обнулюємо лічильник

                tableRow += 1  # Додаємо до лічильника рядків
            return

        with conn.cursor() as cur:
            if form_gra.combo_title.currentText() != "Параметри повітря":
                title = form_gra.combo_title.currentText()
                start_date = form_gra.start_date.date().toPyDate()
                start_time = form_gra.start_time.time().toPyTime()
                start_datetime = str(start_date) + " " + str(start_time)

                end_date = form_gra.end_date.date().toPyDate()
                end_time = form_gra.end_time.time().toPyTime()
                end_datetime = str(end_date) + " " + str(end_time)
                sql = "SELECT s.city, MAX(me.value_m)\n" \
                      "FROM station as s, measurment as me, measurment_unit as unit, optimal_value as op, category as cat\n" \
                      "WHERE me.id_measured_unit = unit.id_measured_unit AND\n" \
                      "me.id_station = s.id_station AND\n" \
                      "unit.id_measured_unit = op.id_measured_unit AND\n" \
                      "op.id_category = cat.id_category AND\n" \
                      f"unit.title = '{title}' AND\n" \
                      "cat.definition = 'Poor' AND\n" \
                      "me.value_m >= op.bottom_border AND\n" \
                      f"me.time_of_measurment BETWEEN '{start_datetime}' AND '{end_datetime}'\n" \
                      "GROUP BY s.city;"
                add_date(sql)

                figure.clear()
                form_gra.frame_grafic.show()

                horizontalLayout = QtWidgets.QHBoxLayout(form_gra.frame_grafic)
                horizontalLayout.setObjectName('horizontalLayout')

                horizontalLayout.addWidget(canvas)

                plt.bar(city, titles, color='pink', width=0.4)
                plt.text(city[0], titles[0], titles[0])

                plt.xlabel("Cities where stations are located")
                plt.ylabel('Value of measurements')
                plt.title(
                    f"Максимальні значення, що були зафіксовані для твердих частинок {title} по кожному місту\n"
                    f"в період з {start_datetime} до {end_datetime}", fontsize='8')
                canvas.draw()
            elif form_gra.combo_title.currentText() == "Параметри повітря":
                msg = QMessageBox()
                msg.setWindowTitle("Помилка")
                msg.setText(f"Перепршую, але "
                            f"ви не можете виконати дію, адже обрали 'Параметри повітря', оберіть якийсь параметр!")
                msg.setWindowIcon(QIcon("images\Error.png"))
                msg.setIcon(QMessageBox.Critical)
                x = msg.exec_()
                return

    def view_grafic_2():
        values = []
        def add_date(sql):
            cur.execute(sql)  # Зберігаємо результат

            length = len(cur.fetchall()) + 1  # Обраховуємо кількість рядків
            form_gra.table_grafic_2.setRowCount(length)  # Створюємо обраховані рядки

            column = form_gra.table_grafic_2.columnCount()  # Обрахунок колонок

            tableRow = 0  # Лічильник для рідків
            cur.execute(sql)  # Знову оброблюємо запит на вибірку
            i = 0  # Лічильник для колонок
            for row in cur.fetchall():  # Передаємо змінній в циклі, значення таблиць по черзі
                while i < column:  # Створюємо цикл для колонок
                    values.append(row[i])
                    form_gra.table_grafic_2.setItem(tableRow, i, QtWidgets.QTableWidgetItem(str(row[i])))
                    i += 1  # Додаємо одиничку до наступної колонки
                i = 0  # Обнулюємо лічильник

                tableRow += 1  # Додаємо до лічильника рядків
            return

        with conn.cursor() as cur:
            if form_gra.combo_name_st.currentText() != "Список станцій":
                station = form_gra.combo_name_st.currentText()

                sql = f"SELECT DISTINCT (SELECT qeuary_2('{station}', 'PM2.5', 'Poor')) as Шкідливий,\n" \
                      f"(SELECT qeuary_2('{station}', 'PM2.5', 'Very Poor')) as Дуже_шкідливий,\n" \
                      f"(SELECT qeuary_2('{station}', 'PM2.5', 'Severe')) as Дуже_тяжкий\n" \
                      "FROM station as s, measurment as me, measurment_unit as unit, optimal_value as op, category as cat\n" \
                      "WHERE me.id_measured_unit = unit.id_measured_unit AND\n" \
                      "me.id_station = s.id_station AND\n" \
                      "unit.id_measured_unit = op.id_measured_unit AND\n" \
                      "op.id_category = cat.id_category;"

                add_date(sql)

                figure.clear()
                form_gra.frame_grafic_2.show()

                horizontalLayout1 = QtWidgets.QHBoxLayout(form_gra.frame_grafic_2)
                horizontalLayout1.setObjectName('horizontalLayout1')

                horizontalLayout1.addWidget(canvas)

                plt.bar(['Poor', 'Very Poor', 'Severe'], values, color='brown', width=0.4)
                plt.text('Poor', values[0], values[0])
                plt.text('Very Poor', values[1], values[1])
                plt.text('Severe', values[2], values[2])

                plt.xlabel("The level of harmful particles")
                plt.ylabel('Number of average daily values')
                plt.title(
                    f"Кількість середньодоюових значень твердих частинок PM2.5, що відносяться до шкідливого рівню\n"
                    f"на станції {station}", fontsize='8')
                canvas.draw()
            elif form_gra.combo_name_st.currentText() == "Список станцій":
                msg = QMessageBox()
                msg.setWindowTitle("Помилка")
                msg.setText(f"На жаль, fkt"
                            f"ви не можете виконати дію, адже обрали 'Список станцій', оберіть назву станції!")
                msg.setWindowIcon(QIcon("images\Error.png"))
                msg.setIcon(QMessageBox.Critical)
                x = msg.exec_()
                return

    def view_grafic_3():
        values = []
        def add_date(sql):
            cur.execute(sql)  # Зберігаємо результат

            length = len(cur.fetchall()) + 1  # Обраховуємо кількість рядків
            form_gra.table_grafic_3.setRowCount(length)  # Створюємо обраховані рядки

            column = form_gra.table_grafic_3.columnCount()  # Обрахунок колонок

            tableRow = 0  # Лічильник для рідків
            cur.execute(sql)  # Знову оброблюємо запит на вибірку
            i = 0  # Лічильник для колонок
            for row in cur.fetchall():  # Передаємо змінній в циклі, значення таблиць по черзі
                while i < column:  # Створюємо цикл для колонок
                    values.append(row[i])
                    form_gra.table_grafic_3.setItem(tableRow, i, QtWidgets.QTableWidgetItem(str(row[i])))
                    i += 1  # Додаємо одиничку до наступної колонки
                i = 0  # Обнулюємо лічильник

                tableRow += 1  # Додаємо до лічильника рядків
            return

        with conn.cursor() as cur:
            if form_gra.combo_name_st_2.currentText() != "Список станцій":
                station = form_gra.combo_name_st_2.currentText()

                sql = f"SELECT DISTINCT (SELECT qeuary_3_4('{station}','Sulfur dioxide(SO2)','Excellent')) as Чудовий,\n" \
                      f"(SELECT qeuary_3_4('{station}','Sulfur dioxide(SO2)','Fine')) as Добрий,\n" \
                      f"(SELECT qeuary_3_4('{station}','Sulfur dioxide(SO2)','Moderate')) as Помірний,\n" \
                      f"(SELECT qeuary_3_4('{station}','Sulfur dioxide(SO2)','Poor')) as Шкідливий,\n" \
                      f"(SELECT qeuary_3_4('{station}','Sulfur dioxide(SO2)','Very Poor')) as Дуже_шкідливий,\n" \
                      f"(SELECT qeuary_3_4('{station}','Sulfur dioxide(SO2)','Severe')) as Дуже_тяжкий\n" \
                      "FROM station as s, measurment as me, measurment_unit as unit, optimal_value as op, category as cat\n" \
                      "WHERE me.id_measured_unit = unit.id_measured_unit AND\n" \
                      "me.id_station = s.id_station AND\n" \
                      "unit.id_measured_unit = op.id_measured_unit AND\n" \
                      "op.id_category = cat.id_category;"

                add_date(sql)

                figure.clear()
                form_gra.frame_grafic_3.show()

                horizontalLayout2 = QtWidgets.QHBoxLayout(form_gra.frame_grafic_3)
                horizontalLayout2.setObjectName('horizontalLayout2')

                horizontalLayout2.addWidget(canvas)

                plt.bar(['Excellent', 'Fine', 'Moderate', 'Poor', 'Very Poor', 'Severe'], values,
                        color='magenta', width=0.4)
                plt.text('Excellent', values[0], values[0])
                plt.text('Fine', values[1], values[1])
                plt.text('Moderate', values[2], values[2])
                plt.text('Poor', values[3], values[3])
                plt.text('Very Poor', values[4], values[4])
                plt.text('Severe', values[5], values[5])

                plt.xlabel("Particle level")
                plt.ylabel('Number of optimal values')
                plt.title(
                    f"Критерії оптимальних значень діоксиду сірки (SO2), що відповідає критеріям\n"
                    f"на станції {station}", fontsize='8')
                canvas.draw()
            elif form_gra.combo_name_st_2.currentText() == "Список станцій":
                msg = QMessageBox()
                msg.setWindowTitle("Помилка")
                msg.setText(f"На жаль, fkt"
                            f"ви не можете виконати дію, адже обрали 'Список станцій', оберіть назву станції!")
                msg.setWindowIcon(QIcon("images\Error.png"))
                msg.setIcon(QMessageBox.Critical)
                x = msg.exec_()
                return

    def view_grafic_4():
        values = []

        def add_date(sql):
            cur.execute(sql)  # Зберігаємо результат

            length = len(cur.fetchall()) + 1  # Обраховуємо кількість рядків
            form_gra.table_grafic_4.setRowCount(length)  # Створюємо обраховані рядки

            column = form_gra.table_grafic_4.columnCount()  # Обрахунок колонок

            tableRow = 0  # Лічильник для рідків
            cur.execute(sql)  # Знову оброблюємо запит на вибірку
            i = 0  # Лічильник для колонок
            for row in cur.fetchall():  # Передаємо змінній в циклі, значення таблиць по черзі
                while i < column:  # Створюємо цикл для колонок
                    values.append(row[i])
                    form_gra.table_grafic_4.setItem(tableRow, i, QtWidgets.QTableWidgetItem(str(row[i])))
                    i += 1  # Додаємо одиничку до наступної колонки
                i = 0  # Обнулюємо лічильник

                tableRow += 1  # Додаємо до лічильника рядків
            return

        with conn.cursor() as cur:
            if form_gra.combo_name_st_3.currentText() != "Список станцій":
                station = form_gra.combo_name_st_3.currentText()

                sql = f"SELECT DISTINCT (SELECT qeuary_3_4('{station}','Carbon monoxide(CO)','Excellent')) as Чудовий,\n" \
                      f"(SELECT qeuary_3_4('{station}','Carbon monoxide(CO)','Fine')) as Добрий,\n" \
                      f"(SELECT qeuary_3_4('{station}','Carbon monoxide(CO)','Moderate')) as Помірний\n" \
                      "FROM station as s, measurment as me, measurment_unit as unit, optimal_value as op, category as cat\n" \
                      "WHERE me.id_measured_unit = unit.id_measured_unit AND\n" \
                      "me.id_station = s.id_station AND\n" \
                      "unit.id_measured_unit = op.id_measured_unit AND\n" \
                      "op.id_category = cat.id_category;"

                add_date(sql)

                figure.clear()
                form_gra.frame_grafic_4.show()

                horizontalLayout3 = QtWidgets.QHBoxLayout(form_gra.frame_grafic_4)
                horizontalLayout3.setObjectName('horizontalLayout3')

                horizontalLayout3.addWidget(canvas)

                plt.bar(['Excellent', 'Fine', 'Moderate'], values,
                        color='coral', width=0.4)
                plt.text('Excellent', values[0], values[0])
                plt.text('Fine', values[1], values[1])
                plt.text('Moderate', values[2], values[2])

                plt.xlabel("Particle level")
                plt.ylabel('Number of optimal values')
                plt.title(
                    f"Критерії оптимальних значень чадного газу (CO), що відповідає критеріям\n"
                    f"на станції {station}", fontsize='8')
                canvas.draw()
            elif form_gra.combo_name_st_3.currentText() == "Список станцій":
                msg = QMessageBox()
                msg.setWindowTitle("Помилка")
                msg.setText(f"Перепршую, fkt"
                            f"ви не можете виконати дію, адже обрали 'Список станцій', оберіть назву станції!")
                msg.setWindowIcon(QIcon("images\Error.png"))
                msg.setIcon(QMessageBox.Critical)
                x = msg.exec_()
                return

    form_gra.btn_back.clicked.connect(lambda state: back_window())
    form_gra.btn_grafic.clicked.connect(lambda state: view_grafic())
    form_gra.btn_grafic_2.clicked.connect(lambda state: view_grafic_2())
    form_gra.btn_grafic_3.clicked.connect(lambda state: view_grafic_3())
    form_gra.btn_grafic_4.clicked.connect(lambda state: view_grafic_4())
    form_gra.btn_clear.clicked.connect(lambda state: clear())
    form_gra.btn_clear_2.clicked.connect(lambda state: clear_2())
    form_gra.btn_clear_3.clicked.connect(lambda state: clear_3())
    form_gra.btn_clear_4.clicked.connect(lambda state: clear_4())

    # Значення для випадаючого списка -------------------------
    index = form_gra.combo_title.findText("Параметри повітря")
    pm2 = form_gra.combo_title.findText("PM2.5")
    pm10 = form_gra.combo_title.findText("PM10")
    if not (int(index > -1)) and not (int(pm2) > -1) and not (int(pm10) > - 1):
        form_gra.combo_title.addItem('Параметри повітря')
        form_gra.combo_title.addItem('PM2.5')
        form_gra.combo_title.addItem('PM10')
        # ---------------------------------------------------------

    index = form_gra.combo_name_st.findText("Список станцій")
    if not (int(index > -1)):
        form_gra.combo_name_st.addItem('Список станцій')

    with conn.cursor() as cur:
        sql = '''SELECT name_st FROM Station;'''

        cur.execute(sql)
        for date in cur.fetchall():
            station = form_gra.combo_name_st.findText(date[0])
            if not (int(station) > -1):
                form_gra.combo_name_st.addItem(date[0])

    index = form_gra.combo_name_st_2.findText("Список станцій")
    if not (int(index > -1)):
        form_gra.combo_name_st_2.addItem('Список станцій')

    with conn.cursor() as cur:
        sql = '''SELECT name_st FROM Station;'''

        cur.execute(sql)
        for date in cur.fetchall():
            station = form_gra.combo_name_st_2.findText(date[0])
            if not (int(station) > -1):
                form_gra.combo_name_st_2.addItem(date[0])

    index = form_gra.combo_name_st_3.findText("Список станцій")
    if not (int(index > -1)):
        form_gra.combo_name_st_3.addItem('Список станцій')

    with conn.cursor() as cur:
        sql = '''SELECT name_st FROM Station;'''

        cur.execute(sql)
        for date in cur.fetchall():
            station = form_gra.combo_name_st_3.findText(date[0])
            if not (int(station) > -1):
                form_gra.combo_name_st_3.addItem(date[0])
    # Встановлення дати і часу --------------------------------
    form_gra.start_date.setDate(now)
    form_gra.end_date.setDate(now)
    time = QTime()
    time.setHMS(now.hour, now.minute, now.second)
    form_gra.start_time.setTime(time)
    form_gra.end_time.setTime(time)

    app.exec_()

show_HeadForm()  # Виклик функції, щоб показати головне вікно
