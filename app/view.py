import tkinter as tk
from tkinter import font
from PIL import Image, ImageTk

from .setup_frame import SetupFrame
from .monitor_frame import MonitorFrame
from .controller import Controller

class ImagePopup(tk.Toplevel):
    def __init__(self, image_np_original, image_np_processed):
        super().__init__()
        self.title("OCR 입력 이미지 비교 (왼쪽: 원본, 오른쪽: 전처리 후)")
        main_frame = tk.Frame(self)
        main_frame.pack(padx=10, pady=10)
        img_orig = Image.fromarray(image_np_original)
        self.img_tk_orig = ImageTk.PhotoImage(image=img_orig)
        label_orig = tk.Label(main_frame, image=self.img_tk_orig, text="원본", compound="top")
        label_orig.pack(side="left", padx=5)
        img_proc = Image.fromarray(image_np_processed)
        self.img_tk_proc = ImageTk.PhotoImage(image=img_proc)
        label_proc = tk.Label(main_frame, image=self.img_tk_proc, text="전처리 후 (OCR 입력)", compound="top")
        label_proc.pack(side="left", padx=5)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("채팅 자동화 봇")
        self.root.geometry("1000x600")
        self.SetupFrame = SetupFrame
        self.MonitorFrame = MonitorFrame
        self.default_font = font.Font(family="Malgun Gothic", size=10)
        self.controller = Controller(self)
        container = tk.Frame(root)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        for F in (self.SetupFrame, self.MonitorFrame):
            frame = F(container, self.controller)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(self.SetupFrame)
        self.root.after(100, self.controller.initialize_models)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def show_image_popup(self, image_np_original, image_np_processed):
        ImagePopup(image_np_original, image_np_processed)
        
    def set_ui_state(self, is_enabled):
        state = "normal" if is_enabled else "disabled"
        for frame_class in self.frames:
            if hasattr(self.frames[frame_class], 'set_ui_state'):
                self.frames[frame_class].set_ui_state(state)