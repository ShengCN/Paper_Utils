import os
import sys
from os.path import join

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow,QWidget, QAction, QFileDialog,QLabel, QPushButton, QSlider, QGridLayout, QGroupBox, QListWidget
from PyQt5.QtGui import QIcon, QPixmap, QImage

import matplotlib.pyplot as plt

import cv2
import numpy as np
from PIL import Image, ImageDraw 
import matplotlib.pyplot as plt
import time

def resize(img, max_size):
	old_shape = len(img.shape)
	h,w = img.shape[:2]
	if h > w:
		newh, neww = max_size, int(max_size * w/h)
	else:
		newh, neww = int(max_size * h / w), max_size
	ret = cv2.resize(img, (neww, newh), interpolation=cv2.INTER_AREA)
	if old_shape != len(ret.shape):
		return ret[..., np.newaxis]
	return ret

def set_qt_img(img, label):
	pixmap = QPixmap(img)
	label.setPixmap(pixmap)
	label.adjustSize()

def to_qt_img(np_img):
	if np_img.dtype != np.uint8:
		np_img = np.clip(np_img, 0.0, 1.0)
		np_img = np_img * 255.0
		np_img = np_img.astype(np.uint8)

	if len(np_img.shape) == 2:
		np_img = np_img[..., np.newaxis].repeat(3, axis=2)

	h, w, c = np_img.shape
	# bytesPerLine = 3 * w
	return QImage(np_img.data, w, h, 3 * w, QImage.Format_RGB888)

def update_img_widget(widget, img):
	set_qt_img(to_qt_img(img), widget)

def read_img(path):
	assert os.path.exists(path), 'Path <{}> does not exist'.format(path)
	img = plt.imread(path)[..., :3]

	if img.dtype == np.uint8:
		img = img/255.0

	return img