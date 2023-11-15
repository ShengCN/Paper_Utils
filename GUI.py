import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QFileDialog, QAction, QColorDialog 
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QCheckBox, QAction, QFileDialog,QLabel, QPushButton, QSlider, QGridLayout, QGroupBox, QListWidget, QRadioButton, QPushButton,QLineEdit,QComboBox
from PyQt5.QtGui import QPixmap, QColor
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
import pandas as pd
import random

from Image_ZoomIn import zoom_in 
from utils import update_img_widget, read_img
import numpy as np



class myList(QListWidget):
    def __init__(self,  parent=None):
        """ Initialize the list view with a directory

        :returns:

        """
        super().__init__()
        self.initUI()
        self.parent = parent


    def initUI(self):
        """ Initialize the list view with a directory

        :param dir: path to the directory
        :returns:

        """
        self.itemClicked.connect(self.on_item_click)
        self.itemDoubleClicked.connect(self.doubleclick_item)


    def on_item_click(self, item):
        name = item.text()
        print('You clicked file: ', name)


    def doubleclick_item(self, item):
        name = item.text()
        print('You clicked file: ', name)

        color = QColor(self.openColorDialog())

        self.parent.update_current_zoomin(name, color)


    def openColorDialog(self):
        color = QColorDialog.getColor()

        if color.isValid():
            print(f'Selected Color: {color.name()}')
            return color.name()



class ImageWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.pressed = False


    def initUI(self):
        self.setWindowTitle('Image Viewer')
        self.setGeometry(300, 300, 800, 600)

        # Menu Bar for Opening Image
        openImage = QAction('Open Image', self)
        openImage.setShortcut('Ctrl+O')
        openImage.triggered.connect(self.openFile)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openImage)

        # Label to Display Image
        self.imageLabel = QLabel(self)
        self.imageLabel.setAlignment(Qt.AlignCenter)


        # Right side of the UI shows several buttons
        # List show all the labels 
        self.listWidget = myList(parent = self)
        self.listWidget.setFixedWidth(200)
        self.listWidget.addItem('0')
        self.zoom_in_dict = {'0': None}
        self.cur_color = QColor('#FF0000') 
        self.cur_zoom_in = '0' 

        # Button to add one label frame 
        self.add_button = QPushButton('Add', self)
        self.add_button.clicked.connect(self.add_btn_clicked)


        self.img_group = QGroupBox("Image", self)
        self.ctrl_group = QGroupBox("Control", self)

        # image group
        img_layout = QGridLayout()
        img_layout.addWidget(self.imageLabel, 0, 0, 1, 1)
        self.img_group.setLayout(img_layout)

        # control group
        ctrl_layout = QGridLayout()
        ctrl_layout.addWidget(self.listWidget, 0, 0, 1, 1)
        ctrl_layout.addWidget(self.add_button, 1, 0, 1, 1)
        self.ctrl_group.setLayout(ctrl_layout)


        # list group
        Hlayout = QtWidgets.QHBoxLayout()
        Hlayout.addWidget(self.img_group)
        Hlayout.addWidget(self.ctrl_group)

        self.center_widget = QWidget(self)
        self.center_widget.setLayout(Hlayout)
        self.setCentralWidget(self.center_widget)


    def update_current_zoomin(self, name, color):
        print('Update', name, color)
        self.cur_zoom_in = name

        if self.cur_zoom_in not in self.zoom_in_dict:
            self.zoom_in_dict[self.cur_zoom_in] = [None, None, color]

        zoom_in_detail = self.zoom_in_dict[self.cur_zoom_in] 
        if zoom_in_detail is None:
            return

        self.zoom_in_dict[self.cur_zoom_in][2] = color
        print('New color', self.zoom_in_dict[self.cur_zoom_in][2])

        self.update_crop_render()


    def add_btn_clicked(self):
        id = self.listWidget.count() 
        self.listWidget.addItem(str(id))

        # set select
        self.listWidget.setCurrentRow(id)
        self.cur_color = QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.zoom_in_dict[str(id)] = [None, None, self.cur_color]

        self.cur_zoom_in = str(id)


    def openFile(self):
        imagePath, _ = QFileDialog.getOpenFileName()
        if imagePath:
            self.cur_main_img = read_img(imagePath)
            update_img_widget(self.imageLabel, self.cur_main_img)


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            print("Mouse pressed at position:", event.pos())
            self.topleft = event.pos()
            self.pressed = True


    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            print("Mouse released at position:", event.pos())
            self.pressed = False

            # update current zoom in
            self.zoom_in_dict[self.cur_zoom_in] = [self.topleft, self.bottomright, self.cur_color] 


    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            print("Mouse moved at position:", event.pos())
            self.bottomright = event.pos()

            self.zoom_in_dict[self.cur_zoom_in] = [self.topleft, self.bottomright, self.cur_color] 

            self.update_crop_render()


    def update_crop_render(self):
        cur_img = self.cur_main_img.copy()

        for k, v in self.zoom_in_dict.items():
            if v is not None:
                topleft, bottomright, color = v
                print(k, topleft, bottomright, color)
                cur_img = self.update_cropping(cur_img, topleft, bottomright, color=color)
        
        update_img_widget(self.imageLabel, cur_img)


    def update_cropping(self, img, topleft, bottomright, padding = 10, color=[0, 0, 0]):
        if topleft is None or bottomright is None:
            return img

        pos = [topleft.y(), topleft.x()]
        hpatch, wpatch = bottomright.y() - topleft.y(), bottomright.x() - topleft.x()

        hpatch, wpatch = max(1, hpatch), max(1, wpatch)

        r = color.red()
        g = color.green()
        b = color.blue()

        # Normalize and convert to NumPy array
        color_array = np.array([r, g, b]) / 255.0
        print(color_array)
        ret, patch = zoom_in(img, pos, boundary_params={'hpatch': hpatch, 'wpatch': wpatch, 'padding': padding, 'color': color_array})

        return ret




if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageWindow()
    ex.show()
    sys.exit(app.exec_())