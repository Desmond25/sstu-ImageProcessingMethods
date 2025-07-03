import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, 
                             QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt


class MorphologyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Морфологические операции с изображениями")
        self.setGeometry(100, 100, 1000, 600)
        
        self.image = None
        self.processed_image = None
        
        self.initUI()
        
    def initUI(self):
        # Основной виджет и layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Левая панель (исходное изображение)
        left_panel = QVBoxLayout()
        self.original_label = QLabel("Исходное изображение")
        self.original_label.setAlignment(Qt.AlignCenter)
        self.original_label.setStyleSheet("border: 1px solid black;")
        left_panel.addWidget(self.original_label)
        
        load_btn = QPushButton("Загрузить изображение")
        load_btn.clicked.connect(self.load_image)
        left_panel.addWidget(load_btn)
        
        # Правая панель (обработанное изображение)
        right_panel = QVBoxLayout()
        self.processed_label = QLabel("Результат обработки")
        self.processed_label.setAlignment(Qt.AlignCenter)
        self.processed_label.setStyleSheet("border: 1px solid black;")
        right_panel.addWidget(self.processed_label)
        
        # Кнопки морфологических операций
        operations_layout = QHBoxLayout()
        
        btn_erode = QPushButton("Эрозия")
        btn_erode.clicked.connect(lambda: self.apply_morphology(cv2.MORPH_ERODE))
        operations_layout.addWidget(btn_erode)
        
        btn_dilate = QPushButton("Дилатация")
        btn_dilate.clicked.connect(lambda: self.apply_morphology(cv2.MORPH_DILATE))
        operations_layout.addWidget(btn_dilate)
        
        btn_open = QPushButton("Открытие")
        btn_open.clicked.connect(lambda: self.apply_morphology(cv2.MORPH_OPEN))
        operations_layout.addWidget(btn_open)
        
        btn_close = QPushButton("Закрытие")
        btn_close.clicked.connect(lambda: self.apply_morphology(cv2.MORPH_CLOSE))
        operations_layout.addWidget(btn_close)
        
        btn_gradient = QPushButton("Градиент")
        btn_gradient.clicked.connect(lambda: self.apply_morphology(cv2.MORPH_GRADIENT))
        operations_layout.addWidget(btn_gradient)
        
        right_panel.addLayout(operations_layout)
        
        # Добавляем панели в основной layout
        main_layout.addLayout(left_panel, 50)
        main_layout.addLayout(right_panel, 50)
        
    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Открыть изображение", "", 
                                                 "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_name:
            self.image = cv2.imread(file_name)
            if self.image is not None:
                self.display_image(self.image, self.original_label)
                self.processed_image = None
                self.processed_label.clear()
                self.processed_label.setText("Результат обработки")
    
    def apply_morphology(self, operation):
        if self.image is None:
            return
            
        # Создаем ядро для морфологических операций
        kernel = np.ones((5, 5), np.uint8)
        
        if operation == cv2.MORPH_ERODE:
            result = cv2.erode(self.image, kernel, iterations=1)
        elif operation == cv2.MORPH_DILATE:
            result = cv2.dilate(self.image, kernel, iterations=1)
        elif operation == cv2.MORPH_OPEN:
            result = cv2.morphologyEx(self.image, cv2.MORPH_OPEN, kernel)
        elif operation == cv2.MORPH_CLOSE:
            result = cv2.morphologyEx(self.image, cv2.MORPH_CLOSE, kernel)
        elif operation == cv2.MORPH_GRADIENT:
            result = cv2.morphologyEx(self.image, cv2.MORPH_GRADIENT, kernel)
        else:
            return
            
        self.processed_image = result
        self.display_image(result, self.processed_label)
    
    def display_image(self, image, label):
        if len(image.shape) == 2:  # Ч/б изображение
            qimage = QImage(image.data, image.shape[1], image.shape[0], 
                           image.shape[1], QImage.Format_Grayscale8)
        else:  # Цветное изображение
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qimage = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        
        pixmap = QPixmap.fromImage(qimage)
        label.setPixmap(pixmap.scaled(label.width(), label.height(), 
                                     Qt.KeepAspectRatio, Qt.SmoothTransformation))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MorphologyApp()
    window.show()
    sys.exit(app.exec_())