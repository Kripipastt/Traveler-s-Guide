import os
import sys
import webbrowser

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow
from all_interface.interface import Ui_MainWindow
from find_cultural_places import *
from Formatting_a_string import format_text_block


class MapWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.con = sqlite3.connect("database/places_db.db")
        self.places_to_visit = []
        self.select_index = 0
        self.z = 13
        self.center_coords = (39.741914, 54.629565)
        self.setupUi(self)
        self.get_cultural_places()
        self.getImage()
        self.comboBox.addItems(map(lambda x: f"({x[0]}) {x[1]}",
                                   self.con.cursor().execute("SELECT id, place_name FROM places").fetchall()))
        self.update_info()
        self.comboBox.currentIndexChanged.connect(self.update_info)
        self.pushButton.clicked.connect(self.open_website)
        self.addButton.clicked.connect(self.add_object)
        self.delButton.clicked.connect(self.del_object)

    # Смена текста на виджете и подсчёт времени
    def update_places_to_visit(self):
        self.textEdit.setText(", ".join(map(str, sorted(map(int, self.places_to_visit)))))
        time = 0
        for i in self.places_to_visit:
            time += self.con.cursor().execute(f'''SELECT "time_to_visit(in_minutes)" FROM type_of_place
            WHERE type_of_place.id == (SELECT places.type FROM places WHERE places.id = {i})''').fetchone()[0]
        if time and time < 60:
            self.label_time.setText(f"{str(time)} минут")
        elif time:
            self.label_time.setText(f"{str(time // 60)} час(а/ов)")
            if time % 60:
                self.label_time.setText(f"{self.label_time.text()} {str(time % 60)} минут")
        else:
            self.label_time.setText("")
        if time >= 480:
            self.label_warning.setText("Возможно, Вы не успеете посетить все места за один день!\nПридётся разделить экскурсию на несколько дней.")
        else:
            self.label_warning.setText("")

    # Добавление объекта в список посещения
    def add_object(self):
        object = self.comboBox.itemText(self.comboBox.currentIndex()).split()[0].replace("(", "").replace(")", "")
        if not (object in self.places_to_visit):
            self.places_to_visit.append(object)
        self.update_places_to_visit()

    # Удаление объекта из списка посещения
    def del_object(self):
        object = self.comboBox.itemText(self.comboBox.currentIndex()).split()[0].replace("(", "").replace(")", "")
        if object in self.places_to_visit:
            self.places_to_visit.remove(object)
        self.update_places_to_visit()

    # Получение координат и информации о культурных местах
    def get_cultural_places(self):
        self.coords, info = search(get_coords("Рязань"), "музей", 14)
        theaters = search(get_coords("Рязань"), "театр", 7)
        for i in range(len(theaters[0])):
            self.coords.append(theaters[0][i]), info.append(theaters[1][i])
        monuments = search(get_coords("Рязань"), "памятник", 7)
        for i in range(len(monuments[0])):
            self.coords.append(monuments[0][i]), info.append(monuments[1][i])
        fill_database(info)

    # Обновление карты
    def getImage(self):
        map_show(self.coords, ",".join(map(str, self.center_coords)), self.z)
        self.map_file = "image/map.png"
        self.image.setPixmap(QPixmap(self.map_file))

    # Обновление информации при выборе объекта
    def update_info(self):
        buttons = [self.label_name, self.label_address, self.label_phone, self.label_hours]
        info = self.con.cursor().execute(f'''SELECT place_name, address, telephone_number, working_hours FROM places
                WHERE id = {self.comboBox.itemText(self.comboBox.currentIndex()).split()[0].replace("(", "").replace(")", "")}''').fetchone()
        for i in range(len(buttons)):
            buttons[i].setText(format_text_block(info[i], 58))
        self.label_error.setText("")

    # Открытие вебсайта объекта при нажатии на соответствующую кнопку (если сайт есть)
    def open_website(self):
        url = self.con.cursor().execute(f'''SELECT url FROM places
                WHERE id = {self.comboBox.itemText(self.comboBox.currentIndex()).split()[0].replace("(", "").replace(")", "")}''').fetchone()[
            0]
        if url != "Не указано":
            webbrowser.open(url)
        else:
            self.label_error.setText("Сайт не найден")

    # Обработка событий нажатия клавиш (нужна для перемещения карты)
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageDown:
            if self.z - 1 > 11:
                self.z -= 1
                self.getImage()
        elif event.key() == Qt.Key_PageUp:
            if self.z + 1 < 16:
                self.z += 1
                self.getImage()
        elif event.key() == Qt.Key_Up:
            self.center_coords = (self.center_coords[0], self.center_coords[1] + 1 / self.z ** 2)
            self.getImage()
        elif event.key() == Qt.Key_Down:
            self.center_coords = (self.center_coords[0], self.center_coords[1] - 1 / self.z ** 2)
            self.getImage()
        elif event.key() == Qt.Key_Right:
            self.center_coords = (self.center_coords[0] + 2.5 / self.z ** 2, self.center_coords[1])
            self.getImage()
        elif event.key() == Qt.Key_Left:
            self.center_coords = (self.center_coords[0] - 2.5 / self.z ** 2, self.center_coords[1])
            self.getImage()

    # Удаление карты и закрытие подключения базы данных
    def closeEvent(self, event):
        self.con.close()
        os.remove(self.map_file)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = MapWidget()
    form.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
