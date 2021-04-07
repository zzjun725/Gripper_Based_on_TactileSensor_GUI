from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QVBoxLayout, QPushButton,QStackedLayout
import sys


class FormA(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.btnPress = QPushButton("Table AAAA")
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.btnPress)
        self.setStyleSheet("background-color:green;")


class FormB(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.btnPress = QPushButton("Table BBBB")
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.btnPress)
        self.setStyleSheet("background-color:red;")

class TextEditDemo(QWidget):
    def __init__(self, parent=None):
        super(TextEditDemo, self).__init__(parent)
        self.setWindowTitle("QStackedLayout 例子")
        self.resize(300, 270)
        # 创建堆叠布局

        self.btnPress1 = QPushButton("FormA")
        self.btnPress2 = QPushButton("FormB")

        self.form1 = FormA()
        self.form2 = FormB()


        widget = QWidget()
        self.stacked_layout = QStackedLayout()
        widget.setLayout(self.stacked_layout)
        widget.setStyleSheet("background-color:grey;")
        self.stacked_layout.addWidget(self.form1)
        self.stacked_layout.addWidget(self.form2)

        layout = QVBoxLayout()
        layout.addWidget(widget)
        layout.addWidget(self.btnPress1)
        layout.addWidget(self.btnPress2)

        self.setLayout(layout)
        self.btnPress1.clicked.connect(self.btnPress1_Clicked)
        self.btnPress2.clicked.connect(self.btnPress2_Clicked)


    def btnPress1_Clicked(self):
        self.stacked_layout.setCurrentIndex(0)

    def btnPress2_Clicked(self):
        self.stacked_layout.setCurrentIndex(1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = TextEditDemo()
    win.show()
    sys.exit(app.exec_())