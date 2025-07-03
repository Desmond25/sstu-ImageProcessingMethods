import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, 
                             QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout, 
                             QGridLayout, QSizePolicy, QFrame)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt

class ImageProcessingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Обработка изображений")
        self.setGeometry(100, 100, 1200, 800)
        
        self.original_image = None
        self.processed_image = None
        
        # Фиксированные параметры масок
        self.MOTION_BLUR_SIZE = 15  # размер для размытия в движении
        self.MEDIAN_FILTER_SIZE = 5  # размер для медианного фильтра (нечетное)
        
        self.initUI()
        
    def initUI(self):
        # Основной виджет и layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Панель с изображениями
        images_panel = QHBoxLayout()
        
        # Левая панель (исходное изображение)
        left_panel = QVBoxLayout()
        self.original_label = QLabel("Исходное изображение")
        self.original_label.setAlignment(Qt.AlignCenter)
        self.original_label.setStyleSheet("border: 1px solid black;")
        self.original_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_panel.addWidget(self.original_label)
        
        load_btn = QPushButton("Загрузить изображение")
        load_btn.clicked.connect(self.load_image)
        left_panel.addWidget(load_btn)
        
        # Правая панель (обработанное изображение)
        right_panel = QVBoxLayout()
        self.processed_label = QLabel("Результат обработки")
        self.processed_label.setAlignment(Qt.AlignCenter)
        self.processed_label.setStyleSheet("border: 1px solid black;")
        self.processed_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_panel.addWidget(self.processed_label)
        
        reset_btn = QPushButton("Сброс")
        reset_btn.clicked.connect(self.reset_image)
        right_panel.addWidget(reset_btn)
        
        # Добавляем панели с изображениями
        images_panel.addLayout(left_panel, 50)
        images_panel.addLayout(right_panel, 50)
        main_layout.addLayout(images_panel, 80)  # 80% пространства для изображений
        
        # Горизонтальная линия разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)
        
        # Панель кнопок операций
        buttons_panel = QGridLayout()
        
        # Первый ряд кнопок
        btn_sharpen = QPushButton("Повысить резкость")
        btn_sharpen.clicked.connect(self.sharpen_image)
        buttons_panel.addWidget(btn_sharpen, 0, 0)
        
        btn_motion_blur = QPushButton("Размытие в движении")
        btn_motion_blur.clicked.connect(self.motion_blur)
        buttons_panel.addWidget(btn_motion_blur, 0, 1)
        
        btn_emboss = QPushButton("Тиснение")
        btn_emboss.clicked.connect(self.emboss_image)
        buttons_panel.addWidget(btn_emboss, 0, 2)
        
        # Второй ряд кнопок
        btn_median = QPushButton("Медианная фильтрация")
        btn_median.clicked.connect(self.median_filter)
        buttons_panel.addWidget(btn_median, 1, 0)
        
        btn_canny = QPushButton("Детектор Canny")
        btn_canny.clicked.connect(self.canny_edge)
        buttons_panel.addWidget(btn_canny, 1, 1)
        
        btn_roberts = QPushButton("Оператор Робертса")
        btn_roberts.clicked.connect(self.roberts_edge)
        buttons_panel.addWidget(btn_roberts, 1, 2)
        
        main_layout.addLayout(buttons_panel, 20)  # 20% пространства для кнопок
        
    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Открыть изображение", "", 
                                                 "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_name:
            self.original_image = cv2.imread(file_name)
            if self.original_image is not None:
                self.display_image(self.original_image, self.original_label)
                self.processed_image = None
                self.processed_label.clear()
                self.processed_label.setText("Результат обработки")
    
    def sharpen_image(self):
        if self.original_image is None:
            return
            
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])
        
        sharpened = cv2.filter2D(self.original_image, -1, kernel)
        self.processed_image = sharpened
        self.display_image(sharpened, self.processed_label)
    
    def motion_blur(self):
        if self.original_image is None:
            return
            
        # Фиксированный размер ядра для размытия в движении
        size = self.MOTION_BLUR_SIZE
        kernel = np.zeros((size, size))
        kernel[int((size-1)/2), :] = np.ones(size)
        kernel /= size
        
        motion_blurred = cv2.filter2D(self.original_image, -1, kernel)
        self.processed_image = motion_blurred
        self.display_image(motion_blurred, self.processed_label)
    
    def emboss_image(self):
        if self.original_image is None:
            return
            
        kernel = np.array([[0, -1, -1],
                          [1,  0, -1],
                          [1,  1,  0]])
        
        embossed = cv2.filter2D(self.original_image, -1, kernel) + 128
        self.processed_image = embossed
        self.display_image(embossed, self.processed_label)
    
    def median_filter(self):
        if self.original_image is None:
            return
            
        # Фиксированный размер медианного фильтра
        size = self.MEDIAN_FILTER_SIZE
        median_filtered = cv2.medianBlur(self.original_image, size)
        self.processed_image = median_filtered
        self.display_image(median_filtered, self.processed_label)
    
    def canny_edge(self):
        if self.original_image is None:
            return
            
        gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        self.processed_image = edges_rgb
        self.display_image(edges_rgb, self.processed_label)
    
    def roberts_edge(self):
        if self.original_image is None:
            return
            
        gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        
        kernel_x = np.array([[1, 0], [0, -1]])
        kernel_y = np.array([[0, 1], [-1, 0]])
        
        grad_x = cv2.filter2D(gray, cv2.CV_64F, kernel_x)
        grad_y = cv2.filter2D(gray, cv2.CV_64F, kernel_y)
        
        grad = np.sqrt(grad_x**2 + grad_y**2)
        grad = np.uint8(grad / grad.max() * 255)
        
        edges_rgb = cv2.cvtColor(grad, cv2.COLOR_GRAY2BGR)
        self.processed_image = edges_rgb
        self.display_image(edges_rgb, self.processed_label)
    
    def reset_image(self):
        if self.original_image is not None:
            self.processed_image = None
            self.processed_label.clear()
            self.processed_label.setText("Результат обработки")
    
    def display_image(self, image, label):
        if len(image.shape) == 2:  # Ч/Б изображение
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
        
        # Обновляем текст метки
        if label == self.original_label:
            label.setText("")
        elif label == self.processed_label:
            label.setText("")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageProcessingApp()
    window.show()
    sys.exit(app.exec_())