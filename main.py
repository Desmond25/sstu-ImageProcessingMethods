import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import os
import math

class ImageViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Viewer with Color Models")
        self.root.geometry("900x600")
        
        # Инициализация всех атрибутов
        self.image = None
        self.tk_image = None
        self.color_boxes = {}
        self.tooltip_labels = {}
        self.color_values = {}
        self.info_labels = {}
        
        self.create_widgets()

    def create_widgets(self):
        # Main content frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Image display frame
        self.image_frame = ttk.LabelFrame(self.main_frame, text="Image Preview")
        self.image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.canvas = tk.Canvas(self.image_frame, bg="#f0f0f0", bd=0, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Motion>", self.show_pixel_color)
        self.canvas.bind("<Leave>", self.clear_color_display)

        # Bottom frame for loading button
        self.load_btn = ttk.Button(self.image_frame, text="Load Image", command=self.load_image)
        self.load_btn.pack(side=tk.BOTTOM, pady=5)

        # Color models frame (right side)
        self.color_frame = ttk.LabelFrame(self.main_frame, text="Color Models")
        self.color_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(0,5), pady=5)
        
        # Create color model displays
        color_models = ["RGB", "CMYK", "HSL", "HSV", "LAB", "YCbCr"]
        for model in color_models:
            frame = ttk.Frame(self.color_frame)
            frame.pack(fill=tk.X, padx=5, pady=3)
            
            lbl = ttk.Label(frame, text=f"{model}:", width=6)
            lbl.pack(side=tk.LEFT)
            
            color_box = tk.Canvas(frame, width=22, height=22, bg="#f0f0f0", bd=0, highlightthickness=0)
            color_box.create_rectangle(1, 1, 21, 21, outline="black")
            color_box.pack(side=tk.LEFT, padx=2)
            self.color_boxes[model] = color_box
            
            value_label = ttk.Label(frame, text="", width=20)
            value_label.pack(side=tk.LEFT)
            self.color_values[model] = value_label
            
            # Tooltip events
            color_box.bind("<Enter>", lambda e, m=model: self.show_tooltip(m))
            color_box.bind("<Leave>", self.hide_tooltip)

        # Info frame at bottom
        self.info_frame = ttk.LabelFrame(self.root, text="Image Info")
        self.info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create info labels
        info_items = ["Size", "Resolution", "Color Depth", "Format", "File Size"]
        for i, info in enumerate(info_items):
            frame = ttk.Frame(self.info_frame)
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            lbl_name = ttk.Label(frame, text=f"{info}:", width=12, anchor=tk.W)
            lbl_name.pack(side=tk.LEFT)
            
            lbl_value = ttk.Label(frame, text="", anchor=tk.W)
            lbl_value.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.info_labels[info] = lbl_value

        # Tooltip window
        self.tooltip = ttk.Label(self.root, text="", background="lightyellow", 
                               padding=5, relief="solid", borderwidth=1)
        self.tooltip.place_forget()

    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        if not file_path:
            return

        try:
            self.image = Image.open(file_path)
            
            # Calculate display size while maintaining aspect ratio
            canvas_width = self.image_frame.winfo_width() - 20
            canvas_height = self.image_frame.winfo_height() - 20
            img_width, img_height = self.image.size
            
            ratio = min(canvas_width/img_width, canvas_height/img_height)
            new_size = (int(img_width * ratio), int(img_height * ratio))
            
            resized_image = self.image.resize(new_size, Image.LANCZOS)
            self.tk_image = ImageTk.PhotoImage(resized_image)

            self.canvas.delete("all")
            self.canvas.config(width=new_size[0], height=new_size[1])
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

            self.update_image_info(file_path)
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to load image: {str(e)}")

    def update_image_info(self, file_path):
        # File size
        file_size = os.path.getsize(file_path) / 1024  # KB
        self.info_labels["File Size"].config(text=f"{file_size:.2f} KB")

        # Resolution
        width, height = self.image.size
        self.info_labels["Resolution"].config(text=f"{width} × {height}")

        # Color depth
        mode_to_depth = {
            "1": 1, "L": 8, "P": 8, "RGB": 24, 
            "RGBA": 32, "CMYK": 32, "YCbCr": 24, 
            "I": 32, "F": 32
        }
        color_depth = mode_to_depth.get(self.image.mode, "N/A")
        self.info_labels["Color Depth"].config(text=f"{color_depth} bits")

        # Format
        self.info_labels["Format"].config(text=self.image.format)

        # Dimensions
        self.info_labels["Size"].config(text=f"{width} × {height} px")

    def show_pixel_color(self, event):
        if not self.image:
            return

        x, y = event.x, event.y
        if x < 0 or y < 0 or x >= self.tk_image.width() or y >= self.tk_image.height():
            return

        # Get pixel color from original image (not resized)
        orig_x = int(x * (self.image.width / self.tk_image.width()))
        orig_y = int(y * (self.image.height / self.tk_image.height()))
        
        try:
            pixel = self.image.getpixel((orig_x, orig_y))
            if isinstance(pixel, int):  # Grayscale
                r = g = b = pixel
            elif len(pixel) == 4:  # RGBA
                r, g, b, _ = pixel
            else:
                r, g, b = pixel[:3]

            # Update color displays
            self.update_color_displays(r, g, b)
        except Exception as e:
            print(f"Error getting pixel color: {e}")

    def clear_color_display(self, event=None):
        for model in self.color_boxes:
            self.color_boxes[model].delete("all")
            self.color_boxes[model].config(bg="#f0f0f0")
            self.color_values[model].config(text="")

    def update_color_displays(self, r, g, b):
        # RGB
        rgb_text = f"{r}, {g}, {b}"
        self.update_color_box("RGB", f"#{r:02x}{g:02x}{b:02x}", rgb_text)

        # CMYK
        c, m, y, k = self.rgb_to_cmyk(r, g, b)
        cmyk_text = f"{c:.2f}, {m:.2f}, {y:.2f}, {k:.2f}"
        self.update_color_box("CMYK", f"#{r:02x}{g:02x}{b:02x}", cmyk_text)

        # HSL
        h, s, l = self.rgb_to_hsl(r, g, b)
        hsl_text = f"{h:.1f}°, {s:.1%}, {l:.1%}"
        self.update_color_box("HSL", f"#{r:02x}{g:02x}{b:02x}", hsl_text)

        # HSV
        h, s, v = self.rgb_to_hsv(r, g, b)
        hsv_text = f"{h:.1f}°, {s:.1%}, {v:.1%}"
        self.update_color_box("HSV", f"#{r:02x}{g:02x}{b:02x}", hsv_text)

        # LAB (simplified)
        l, a, b_lab = self.rgb_to_lab(r, g, b)
        lab_text = f"{l:.1f}, {a:.1f}, {b_lab:.1f}"
        self.update_color_box("LAB", f"#{r:02x}{g:02x}{b:02x}", lab_text)

        # YCbCr
        y, cb, cr = self.rgb_to_ycbcr(r, g, b)
        ycbcr_text = f"{y:.1f}, {cb:.1f}, {cr:.1f}"
        self.update_color_box("YCbCr", f"#{r:02x}{g:02x}{b:02x}", ycbcr_text)

    def update_color_box(self, model, color, text):
        box = self.color_boxes[model]
        box.delete("all")
        box.create_rectangle(1, 1, 21, 21, fill=color, outline="black")
        self.color_values[model].config(text=text)

    def show_tooltip(self, model):
        if model in self.color_values:
            text = self.color_values[model].cget("text")
            if text:
                self.tooltip.config(text=f"{model}: {text}")
                x, y = self.root.winfo_pointerxy()
                self.tooltip.place(x=x+10, y=y+10)

    def hide_tooltip(self, event=None):
        self.tooltip.place_forget()

    # Color conversion functions
    def rgb_to_cmyk(self, r, g, b):
        if (r, g, b) == (0, 0, 0):
            return 0, 0, 0, 1
        c = 1 - r / 255
        m = 1 - g / 255
        y = 1 - b / 255
        k = min(c, m, y)
        c = (c - k) / (1 - k) if (1 - k) != 0 else 0
        m = (m - k) / (1 - k) if (1 - k) != 0 else 0
        y = (y - k) / (1 - k) if (1 - k) != 0 else 0
        return c, m, y, k

    def rgb_to_hsl(self, r, g, b):
        r, g, b = r / 255, g / 255, b / 255
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        h = s = l = (max_val + min_val) / 2

        if max_val != min_val:
            d = max_val - min_val
            s = d / (2 - max_val - min_val) if l > 0.5 else d / (max_val + min_val)
            if max_val == r:
                h = (g - b) / d + (6 if g < b else 0)
            elif max_val == g:
                h = (b - r) / d + 2
            else:
                h = (r - g) / d + 4
            h /= 6
        return round(h * 360, 1), round(s, 3), round(l, 3)

    def rgb_to_hsv(self, r, g, b):
        r, g, b = r / 255, g / 255, b / 255
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        h = s = v = max_val

        d = max_val - min_val
        s = 0 if max_val == 0 else d / max_val

        if max_val != min_val:
            if max_val == r:
                h = (g - b) / d + (6 if g < b else 0)
            elif max_val == g:
                h = (b - r) / d + 2
            else:
                h = (r - g) / d + 4
            h /= 6
        return round(h * 360, 1), round(s, 3), round(v, 3)

    def rgb_to_lab(self, r, g, b):
        # Simplified conversion (accurate conversion requires XYZ space)
        l = 0.2126 * r + 0.7152 * g + 0.0722 * b
        a = 1.4749 * (0.2215 * r - 0.3390 * g + 0.1175 * b) + 128
        b_lab = 0.6245 * (0.1949 * r + 0.6057 * g - 0.8006 * b) + 128
        return round(l / 2.55, 1), round(a - 128, 1), round(b_lab - 128, 1)

    def rgb_to_ycbcr(self, r, g, b):
        y = 0.299 * r + 0.587 * g + 0.114 * b
        cb = 128 - 0.168736 * r - 0.331264 * g + 0.5 * b
        cr = 128 + 0.5 * r - 0.418688 * g - 0.081312 * b
        return round(y, 1), round(cb, 1), round(cr, 1)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageViewerApp(root)
    root.mainloop()