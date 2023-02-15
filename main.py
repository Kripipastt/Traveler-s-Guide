import sys

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPixmap
from all_interface.main_interface import Ui_MainWindow
from Screen_with_map import MapWidget


class MainWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.enter)
        self.label_2.setPixmap(QPixmap("image/ryazan.jpg"))

    def enter(self):
        self.window = MapWidget()
        self.window.show()
        self.close()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = MainWidget()
    form.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
