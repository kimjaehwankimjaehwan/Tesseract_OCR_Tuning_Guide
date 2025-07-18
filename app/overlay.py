import tkinter as tk
# import win32gui   # 테스트를 위해 잠시 비활성화
# import win32con   # 테스트를 위해 잠시 비활성화

class OverlayWindow:
    def __init__(self, region, border_color="red", border_width=2):
        """
        모니터링 영역을 표시하는 오버레이 창을 생성합니다.
        (클릭 통과 기능이 비활성화된 테스트 버전)
        """
        self.root = tk.Toplevel()
        x1, y1, x2, y2 = region
        width = x2 - x1
        height = y2 - y1

        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.geometry(f"{width}x{height}+{x1}+{y1}")

        trans_color = '#abcdef'
        self.root.attributes("-transparentcolor", trans_color)
        
        canvas = tk.Canvas(self.root, bg=trans_color, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        canvas.create_rectangle(0, 0, width, height, 
                                outline=border_color, width=border_width)

        # --- 클릭 통과 기능 비활성화 ---
        # self.root.after(10, self.set_click_through)
    
    # def set_click_through(self):
    #     """클릭-스루 속성 설정 (테스트를 위해 잠시 비활성화)"""
    #     try:
    #         hwnd = self.root.winfo_id()
    #         l_styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    #         win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 
    #                                l_styles | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED)
    #     except Exception as e:
    #         print(f"클릭-스루 설정 오류: {e}")

    def destroy(self):
        """오버레이 창을 닫습니다."""
        self.root.destroy()