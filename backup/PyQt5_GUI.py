from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QMainWindow, QWidget
import pyqtgraph as pg
import numpy as np
import sys


class TestWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self)
        # 设置窗体尺寸
        self.setGeometry(100, 100, 1800, 900)
        # 添加一个按钮和一个PlotWidget
        self.draw_fig_btn = QPushButton("绘图")
        self.draw_fig_btn.setFixedWidth(100)
        self.plt = pg.PlotWidget()
        self.plt.showGrid(x=True, y=True)
        # 将两个Widget垂直排列布局
        # MainWindow的主体内容要通过一个widget包裹在一起，通过self.setCentralWidget设置
        centralWidget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.draw_fig_btn)
        main_layout.addWidget(self.plt)
        centralWidget.setLayout(main_layout)
        # 应用上述布局
        self.setCentralWidget(centralWidget)
        # 为[绘图]按钮注册一个回调函数
        self.draw_fig_btn.clicked.connect(self.draw_fig_btn_cb)

    def draw_fig_btn_cb(self):
        # [绘图]按钮回调函数
        x = np.linspace(-5 * np.pi, 5 * np.pi, 500)
        y = 0.5 * np.sin(x)
        self.plt.plot(x, y, pen="r")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    qb = TestWindow()
    qb.show()
    sys.exit(app.exec_())