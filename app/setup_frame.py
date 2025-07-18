import tkinter as tk
from tkinter import messagebox

class SetupFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.selected_region = None

        self.configure(bg="#f0f0f0")

        info_label = tk.Label(self, text="OCR로 모니터링할 영역을 설정해주세요.",
                              font=controller.view.default_font, bg="#f0f0f0")
        info_label.pack(pady=(20, 5))

        self.region_button = tk.Button(self, text="화면 영역 선택하기",
                                  font=controller.view.default_font,
                                  command=self.select_ocr_region)
        self.region_button.pack(pady=5)

        self.region_info_label = tk.Label(self, text="선택된 영역: 없음",
                                          font=controller.view.default_font, bg="#f0f0f0", fg="blue")
        self.region_info_label.pack(pady=5)

        self.start_button = tk.Button(self, text="설정 완료하고 모니터링 시작",
                                      font=controller.view.default_font,
                                      command=controller.proceed_to_monitoring,
                                      state="disabled")
        self.start_button.pack(pady=20)

    def set_ui_state(self, state):
        self.region_button.config(state=state)
        if state == 'disabled':
            self.start_button.config(state=state)

    def select_ocr_region(self):
        messagebox.showinfo("영역 선택 안내", "확인 버튼을 누른 후, 모니터링할 영역의 왼쪽 위 모서리를 클릭하고 오른쪽 아래 모서리까지 드래그해주세요.")
        toplevel = tk.Toplevel(self.controller.view.root)
        toplevel.attributes("-fullscreen", True)
        toplevel.attributes("-alpha", 0.3)
        toplevel.configure(bg="black")
        canvas = tk.Canvas(toplevel, cursor="cross")
        canvas.pack(fill="both", expand=True)
        start_x, start_y = None, None
        rect = None
        def on_press(event):
            nonlocal start_x, start_y
            start_x, start_y = event.x, event.y
        def on_drag(event):
            nonlocal rect
            if rect:
                canvas.delete(rect)
            rect = canvas.create_rectangle(start_x, start_y, event.x, event.y, outline='red', width=2, fill="white")
        
        def on_release(event):
            x1 = min(start_x, event.x)
            y1 = min(start_y, event.y)
            x2 = max(start_x, event.x)
            y2 = max(start_y, event.y)
            self.selected_region = (x1, y1, x2, y2)
            self.region_info_label.config(text=f"선택된 영역: {self.selected_region}")
            
            # --- 핵심 수정: .reader 대신 .is_ready 확인 ---
            if self.controller.ocr_engine.is_ready and self.controller.ai_engine.is_ready:
                self.start_button.config(state="normal")
            
            toplevel.destroy()

        canvas.bind("<ButtonPress-1>", on_press)
        canvas.bind("<B1-Motion>", on_drag)
        canvas.bind("<ButtonRelease-1>", on_release)