import tkinter as tk
import platform
import ctypes
from .view import App

def set_dpi_awareness():
    """
    Windows 환경에서 DPI 인식을 설정하여 좌표 왜곡을 방지합니다.
    """
    if platform.system() == "Windows":
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except AttributeError:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except AttributeError:
                print("경고: DPI 인식 설정을 할 수 없습니다.")
        except Exception as e:
            print(f"DPI 인식 설정 중 오류 발생: {e}")

def main():
    """
    프로그램의 메인 함수입니다.
    GUI를 초기화하고 실행합니다.
    """
    set_dpi_awareness()
    
    try:
        root = tk.Tk()
        app = App(root)
        root.mainloop()
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()