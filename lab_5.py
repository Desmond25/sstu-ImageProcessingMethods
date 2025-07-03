import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
                             QFileDialog, QHBoxLayout, QListWidget, QMessageBox)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer

class ImageVideoProcessor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image and Video Processing App")
        self.layout = QVBoxLayout()

        self.image_label = QLabel("Здесь будет изображение или видео")
        self.layout.addWidget(self.image_label)

        # Buttons
        self.btn_load_image = QPushButton("Загрузить изображение")
        self.btn_load_image.clicked.connect(self.load_image)
        self.layout.addWidget(self.btn_load_image)

        detector_layout = QHBoxLayout()
        for name in ["Harris", "SIFT", "SURF", "FAST"]:
            btn = QPushButton(f"Детектор {name}")
            btn.clicked.connect(lambda _, n=name: self.detect_keypoints(n))
            detector_layout.addWidget(btn)
        self.layout.addLayout(detector_layout)

        self.btn_load_multiple_images = QPushButton("Загрузить от 3 до 10 изображений")
        self.btn_load_multiple_images.clicked.connect(self.load_multiple_images)
        self.layout.addWidget(self.btn_load_multiple_images)

        self.btn_load_video_bg = QPushButton("Загрузить видео для вычитания фона")
        self.btn_load_video_bg.clicked.connect(self.load_video_bg_subtraction)
        self.layout.addWidget(self.btn_load_video_bg)

        self.btn_load_video_blur = QPushButton("Загрузить видео для размытия движущихся объектов")
        self.btn_load_video_blur.clicked.connect(self.load_video_blur_motion)
        self.layout.addWidget(self.btn_load_video_blur)

        self.setLayout(self.layout)

        self.image = None
        self.images = []

    def load_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выбрать изображение")
        if path:
            self.image = cv2.imread(path)
            self.display_image(self.image)

    def detect_keypoints(self, detector_type):
        if self.image is None:
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите изображение")
            return

        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        img_out = self.image.copy()

        if detector_type == "Harris":
            dst = cv2.cornerHarris(np.float32(gray), 2, 3, 0.04)
            img_out[dst > 0.01 * dst.max()] = [0, 0, 255]
        elif detector_type == "SIFT":
            sift = cv2.SIFT_create()
            kp = sift.detect(gray, None)
            img_out = cv2.drawKeypoints(img_out, kp, None)
        elif detector_type == "SURF":
            try:
                surf = cv2.xfeatures2d.SURF_create()
                kp = surf.detect(gray, None)
                img_out = cv2.drawKeypoints(img_out, kp, None)
            except AttributeError:
                QMessageBox.warning(self, "Ошибка", "SURF не поддерживается в вашей версии OpenCV. Убедитесь, что установлена opencv-contrib.")
                return
        elif detector_type == "FAST":
            fast = cv2.FastFeatureDetector_create()
            kp = fast.detect(gray, None)
            img_out = cv2.drawKeypoints(img_out, kp, None)

        self.display_image(img_out)

    def load_multiple_images(self):
        file_names, _ = QFileDialog.getOpenFileNames(self, "Выберите от 3 до 10 изображений", "", "Images (*.png *.jpg *.bmp)")
        if not (3 <= len(file_names) <= 10):
            QMessageBox.warning(self, "Ошибка", "Выберите от 3 до 10 изображений.")
            return

        self.images = [cv2.imread(f) for f in file_names]

        # Преобразуем изображения в серые и вычисляем дескрипторы SIFT
        sift = cv2.SIFT_create()
        descriptors = []
        for img in self.images:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            kp, des = sift.detectAndCompute(gray, None)
            descriptors.append(des)

        # Вычисляем схожесть между всеми парами
        bf = cv2.BFMatcher()
        best_score = -1
        idx_pair = (0, 1)
        for i in range(len(descriptors)):
            for j in range(i + 1, len(descriptors)):
                if descriptors[i] is None or descriptors[j] is None:
                    continue
                matches = bf.knnMatch(descriptors[i], descriptors[j], k=2)
                # Применим правило Лоу для отсеивания плохих матчей
                good = [m for m, n in matches if m.distance < 0.75 * n.distance]
                if len(good) > best_score:
                    best_score = len(good)
                    idx_pair = (i, j)

        # Приведение изображений к одинаковой высоте и цветности
        def ensure_color(img):
            if len(img.shape) == 2:
                return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            return img

        img1 = ensure_color(self.images[idx_pair[0]])
        img2 = ensure_color(self.images[idx_pair[1]])

        h = min(img1.shape[0], img2.shape[0])
        img1_resized = cv2.resize(img1, (img1.shape[1], h))
        img2_resized = cv2.resize(img2, (img2.shape[1], h))

        combined = np.hstack((img1_resized, img2_resized))

        # Показываем результат
        combined_rgb = cv2.cvtColor(combined, cv2.COLOR_BGR2RGB)
        h, w, ch = combined_rgb.shape
        bytes_per_line = ch * w
        q_img = QImage(combined_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        self.image_label.setPixmap(pixmap)
        self.image_label.adjustSize()

    def load_video_bg_subtraction(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выбрать видео")
        if path:
            cap = cv2.VideoCapture(path)
            fgbg = cv2.createBackgroundSubtractorMOG2()
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                fgmask = fgbg.apply(frame)
                cv2.imshow('Background Subtraction', fgmask)
                if cv2.waitKey(30) & 0xFF == 27:
                    break
            cap.release()
            cv2.destroyAllWindows()

    def load_video_blur_motion(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выбрать видео")
        if path:
            cap = cv2.VideoCapture(path)
            fgbg = cv2.createBackgroundSubtractorMOG2()
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                fgmask = fgbg.apply(frame)
                blurred = cv2.GaussianBlur(frame, (51, 51), 0)
                motion_blur = np.where(fgmask[..., None] > 0, blurred, frame)
                cv2.imshow('Motion Blur', motion_blur.astype(np.uint8))
                if cv2.waitKey(30) & 0xFF == 27:
                    break
            cap.release()
            cv2.destroyAllWindows()

    def display_image(self, img):
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(qimg))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageVideoProcessor()
    window.show()
    sys.exit(app.exec_())