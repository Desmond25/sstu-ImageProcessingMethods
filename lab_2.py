import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QFileDialog, QSlider, QComboBox)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class ImageProcessorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Processor")
        self.setGeometry(100, 100, 1200, 800)
        
        # Основные переменные
        self.original_image = None
        self.processed_image = None
        self.gray_image = None  # Отдельно храним серую версию
        self.is_gray = False
        self.base_image = None
        
        # Создаем главный виджет и layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QHBoxLayout(self.main_widget)
        
        # Левая панель (изображения)
        self.image_panel = QWidget()
        self.image_layout = QVBoxLayout(self.image_panel)
        
        # Правая панель (управление и гистограммы)
        self.control_panel = QWidget()
        self.control_layout = QVBoxLayout(self.control_panel)
        
        # Добавляем панели в главный layout
        self.main_layout.addWidget(self.image_panel, 70)
        self.main_layout.addWidget(self.control_panel, 30)
        
        # Инициализация UI
        self.init_image_ui()
        self.init_control_ui()
        
    def init_image_ui(self):
        self.original_label = QLabel("Original Image")
        self.original_label.setAlignment(Qt.AlignCenter)
        self.original_label.setMinimumSize(400, 300)
        
        self.processed_label = QLabel("Processed Image")
        self.processed_label.setAlignment(Qt.AlignCenter)
        self.processed_label.setMinimumSize(400, 300)
        
        self.image_layout.addWidget(self.original_label)
        self.image_layout.addWidget(self.processed_label)
        
    def init_control_ui(self):
        self.load_button = QPushButton("Load Image")
        self.load_button.clicked.connect(self.load_image)
        
        self.gray_button = QPushButton("Convert to Gray")
        self.gray_button.clicked.connect(self.convert_to_gray)
        
        self.hist_channel = QComboBox()
        self.hist_channel.addItems(["RGB", "Red", "Green", "Blue"])
        self.hist_channel.currentIndexChanged.connect(self.update_histograms)
        
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(0)
        self.brightness_slider.valueChanged.connect(self.adjust_image)
        
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(-100, 100)
        self.contrast_slider.setValue(0)
        self.contrast_slider.valueChanged.connect(self.adjust_image)
        
        self.saturation_slider = QSlider(Qt.Horizontal)
        self.saturation_slider.setRange(-100, 100)
        self.saturation_slider.setValue(0)
        self.saturation_slider.valueChanged.connect(self.adjust_image)
        
        self.linear_corr_button = QPushButton("Linear Correction")
        self.linear_corr_button.clicked.connect(self.apply_linear_correction)
        
        self.gamma_corr_button = QPushButton("Gamma Correction")
        self.gamma_corr_button.clicked.connect(self.apply_gamma_correction)
        
        self.original_hist_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.processed_hist_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        
        self.control_layout.addWidget(self.load_button)
        self.control_layout.addWidget(self.gray_button)
        self.control_layout.addWidget(QLabel("Histogram Channel:"))
        self.control_layout.addWidget(self.hist_channel)
        self.control_layout.addWidget(QLabel("Brightness:"))
        self.control_layout.addWidget(self.brightness_slider)
        self.control_layout.addWidget(QLabel("Contrast:"))
        self.control_layout.addWidget(self.contrast_slider)
        self.control_layout.addWidget(QLabel("Saturation:"))
        self.control_layout.addWidget(self.saturation_slider)
        self.control_layout.addWidget(self.linear_corr_button)
        self.control_layout.addWidget(self.gamma_corr_button)
        self.control_layout.addWidget(QLabel("Original Histogram:"))
        self.control_layout.addWidget(self.original_hist_canvas)
        self.control_layout.addWidget(QLabel("Processed Histogram:"))
        self.control_layout.addWidget(self.processed_hist_canvas)
        
    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image", "", 
                                                  "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_name:
            self.original_image = cv2.imread(file_name)
            if self.original_image is not None:
                self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
                self.processed_image = self.original_image.copy()
                self.base_image = self.original_image.copy()
                self.gray_image = None
                self.is_gray = False
                self.display_images()
                self.update_histograms()
                self.reset_sliders()
    
    def reset_sliders(self):
        self.brightness_slider.setValue(0)
        self.contrast_slider.setValue(0)
        self.saturation_slider.setValue(0)
    
    def display_images(self):
        if self.original_image is not None:
            # Original image
            h, w, ch = self.original_image.shape
            bytes_per_line = ch * w
            qimg = QImage(self.original_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.original_label.setPixmap(QPixmap.fromImage(qimg).scaled(
                self.original_label.width(), self.original_label.height(), 
                Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
            # Processed image
            if self.processed_image is not None:
                if len(self.processed_image.shape) == 2:  # Grayscale
                    h, w = self.processed_image.shape
                    bytes_per_line = w
                    qimg = QImage(self.processed_image.data, w, h, bytes_per_line, QImage.Format_Grayscale8)
                else:  # Color
                    h, w, ch = self.processed_image.shape
                    bytes_per_line = ch * w
                    qimg = QImage(self.processed_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                
                self.processed_label.setPixmap(QPixmap.fromImage(qimg).scaled(
                    self.processed_label.width(), self.processed_label.height(), 
                    Qt.KeepAspectRatio, Qt.SmoothTransformation))
    
    def convert_to_gray(self):
        if self.original_image is not None:
            self.gray_image = cv2.cvtColor(self.original_image, cv2.COLOR_RGB2GRAY)
            self.processed_image = self.gray_image.copy()
            self.is_gray = True
            self.display_images()
            self.update_histograms()
    
    def adjust_image(self):
        if self.original_image is None:
            return
            
        brightness = self.brightness_slider.value()
        contrast = self.contrast_slider.value()
        saturation = self.saturation_slider.value()
        
        if self.is_gray:
            # Для серого изображения работаем только с яркостью и контрастом
            self.processed_image = self.gray_image.copy()
        else:
            # Для цветного изображения применяем насыщенность
            self.processed_image = self.base_image.copy()
            hsv = cv2.cvtColor(self.processed_image, cv2.COLOR_RGB2HSV).astype(np.float32)
            h, s, v = cv2.split(hsv)
            
            saturation_factor = 1 + saturation / 100
            s = np.clip(s * saturation_factor, 0, 255)
            
            hsv = cv2.merge([h, s, v])
            self.processed_image = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
        
        # Применяем яркость и контраст ко всем изображениям
        alpha = 1 + contrast / 100
        beta = brightness
        self.processed_image = cv2.convertScaleAbs(self.processed_image, alpha=alpha, beta=beta)
        
        self.display_images()
        self.update_histograms()
    
    def apply_linear_correction(self):
        if not self.is_gray or self.processed_image is None:
            return
            
        # Линейная коррекция только для серых изображений
        img = self.processed_image.astype(np.float32)
        
        # Находим минимальное и максимальное значения
        min_val = np.min(img)
        max_val = np.max(img)
        
        # Если все пиксели одинаковые, ничего не делаем
        if min_val == max_val:
            return
            
        # Линейное растяжение гистограммы
        img = 255 * (img - min_val) / (max_val - min_val)
        self.processed_image = img.astype(np.uint8)
        
        self.display_images()
        self.update_histograms()
    
    def apply_gamma_correction(self):
        if not self.is_gray or self.processed_image is None:
            return
            
        # Гамма-коррекция только для серых изображений
        gamma = 1.5  # Можно сделать настраиваемым параметром
        img = self.processed_image.astype(np.float32) / 255.0
        img = np.power(img, 1.0/gamma)
        self.processed_image = (img * 255).astype(np.uint8)
        
        self.display_images()
        self.update_histograms()
    
    def update_histograms(self):
        if self.original_image is None:
            return
            
        channel = self.hist_channel.currentText()
        self.draw_histogram(self.original_image, self.original_hist_canvas, channel, "Original")
        
        if self.processed_image is not None:
            self.draw_histogram(self.processed_image, self.processed_hist_canvas, channel, "Processed")
    
    def draw_histogram(self, image, canvas, channel, title):
        canvas.figure.clear()
        ax = canvas.figure.add_subplot(111)
        
        if len(image.shape) == 2:  # Grayscale
            ax.hist(image.ravel(), 256, [0, 256], color='gray')
            ax.set_title(f"{title} (Gray)")
        else:  # Color
            if channel == "RGB":
                colors = ('r', 'g', 'b')
                for i, color in enumerate(colors):
                    hist = cv2.calcHist([image], [i], None, [256], [0, 256])
                    ax.plot(hist, color=color)
                ax.set_title(f"{title} (RGB)")
            else:
                channel_map = {"Red": 0, "Green": 1, "Blue": 2}
                i = channel_map[channel]
                color = channel.lower()[0]
                hist = cv2.calcHist([image], [i], None, [256], [0, 256])
                ax.plot(hist, color=color)
                ax.set_title(f"{title} ({channel})")
        
        ax.set_xlim([0, 256])
        canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageProcessorApp()
    window.show()
    sys.exit(app.exec_())