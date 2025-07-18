import os
import textwrap

# 프로젝트 구조와 파일 내용을 딕셔너리로 정의합니다.
project_files = {
    # README 파일
    "README.md": textwrap.dedent("""
        # 채팅 자동화 봇 프로젝트

        이 프로젝트는 특정 채팅창을 OCR로 읽어 상황을 파악하고,
        AI 언어 모델을 통해 적절한 응답을 자동으로 타이핑하는 프로그램입니다.

        ## 실행 방법
        1. 가상환경 생성: `python -m venv venv`
        2. 가상환경 활성화: `source venv/bin/activate` (macOS/Linux) 또는 `.\\venv\\Scripts\\activate` (Windows)
        3. 필요 라이브러리 설치: `pip install -r requirements.txt`
        4. 프로그램 실행: `python app/main.py`
    """),

    # 필요 라이브러리 목록
    "requirements.txt": textwrap.dedent("""
        # GUI
        # tkinter는 파이썬 기본 내장 라이브러리입니다.

        # OCR
        easyocr
        
        # 스크린샷 및 이미지 처리
        Pillow
        mss

        # AI 모델
        transformers
        torch
    """),

    # 설정 및 데이터 파일
    "config/config.json": textwrap.dedent("""
        {
          "response_rules": {
            "수업중": {
              "response_type": "RANDOM",
              "responses": ["네, 집중하겠습니다.", "알겠습니다."]
            },
            "쉬는시간": {
              "response_type": "FIXED",
              "responses": ["네, 쉬는 시간!"]
            },
            "출석": {
              "response_type": "RANDOM",
              "responses": ["출석", "출첵!", "네"]
            }
          }
        }
    """),
    "config/training_data.jsonl": textwrap.dedent("""
        {"image_path": "", "text": "수업 시작하겠습니다", "label": "수업중"}
        {"image_path": "", "text": "다들 집중하세요", "label": "수업중"}
        {"image_path": "", "text": "잠깐 쉬었다가 하죠", "label": "쉬는시간"}
        {"image_path": "", "text": "10분 뒤에 다시 시작하겠습니다", "label": "쉬는시간"}
        {"image_path": "", "text": "출석 부를게요", "label": "출석"}
        {"image_path": "", "text": "다들 이름 남겨주세요", "label": "출석"}
    """),

    # 애플리케이션 소스 코드
    "app/__init__.py": "",
    "app/main.py": textwrap.dedent("""
        import tkinter as tk
        from .view import App

        def main():
            try:
                root = tk.Tk()
                app = App(root)
                root.mainloop()
            except Exception as e:
                print(f"오류가 발생했습니다: {e}")

        if __name__ == "__main__":
            main()
    """),
    "app/view.py": textwrap.dedent("""
        import tkinter as tk
        from tkinter import font
        from .setup_frame import SetupFrame
        from .monitor_frame import MonitorFrame

        class App:
            def __init__(self, root):
                self.root = root
                self.root.title("채팅 자동화 봇")
                self.root.geometry("800x600")

                self.default_font = font.Font(family="Malgun Gothic", size=10)

                container = tk.Frame(root)
                container.pack(side="top", fill="both", expand=True)
                container.grid_rowconfigure(0, weight=1)
                container.grid_columnconfigure(0, weight=1)

                self.frames = {}
                for F in (SetupFrame, MonitorFrame):
                    frame = F(container, self)
                    self.frames[F] = frame
                    frame.grid(row=0, column=0, sticky="nsew")

                self.show_frame(SetupFrame)

            def show_frame(self, cont):
                frame = self.frames[cont]
                frame.tkraise()
    """),
    "app/setup_frame.py": textwrap.dedent("""
        import tkinter as tk

        class SetupFrame(tk.Frame):
            def __init__(self, parent, controller):
                super().__init__(parent)
                self.controller = controller

                label = tk.Label(self, text="여기는 초기 설정 화면입니다.", font=controller.default_font)
                label.pack(pady=10, padx=10)
                
                # 예시: 모니터링 화면으로 전환하는 버튼
                from .monitor_frame import MonitorFrame
                switch_button = tk.Button(self, text="설정 완료하고 모니터링 시작",
                                          command=lambda: controller.show_frame(MonitorFrame))
                switch_button.pack()
    """),
    "app/monitor_frame.py": textwrap.dedent("""
        import tkinter as tk

        class MonitorFrame(tk.Frame):
            def __init__(self, parent, controller):
                super().__init__(parent)
                self.controller = controller
                
                label = tk.Label(self, text="여기는 메인 모니터링 화면입니다.", font=controller.default_font)
                label.pack(pady=10, padx=10)

                # 예시: 설정 화면으로 돌아가는 버튼
                from .setup_frame import SetupFrame
                switch_button = tk.Button(self, text="설정 화면으로 돌아가기",
                                          command=lambda: controller.show_frame(SetupFrame))
                switch_button.pack()
    """),
    "app/controller.py": textwrap.dedent("""
        # 이 파일은 추후에 구체적인 로직으로 채워질 예정입니다.
        class Controller:
            def __init__(self, view):
                self.view = view

            def load_config(self):
                print("설정 파일을 로드합니다.")
                pass

            def start_monitoring(self):
                print("모니터링을 시작합니다.")
                pass

            def stop_monitoring(self):
                print("모니터링을 중지합니다.")
                pass
            
            def save_capture(self, image, text, label):
                print(f"캡처된 데이터를 저장합니다: {text}, {label}")
                pass
    """),
    "app/ocr.py": textwrap.dedent("""
        # 이 파일은 추후에 실제 OCR 라이브러리를 이용한 코드로 채워질 예정입니다.
        def get_text_from_image(image):
            # 현재는 더미 텍스트를 반환합니다.
            print("OCR 기능 호출됨 (현재는 더미 데이터 반환)")
            return "이것은 캡처된 채팅 내용입니다."
    """),
    "app/ai_model.py": textwrap.dedent("""
        # 이 파일은 추후에 실제 언어 모델을 이용한 코드로 채워질 예정입니다.
        def predict_situation(text):
            # 현재는 더미 라벨과 정확도를 반환합니다.
            print("AI 모델 기능 호출됨 (현재는 더미 데이터 반환)")
            return "수업중", 0.95 
    """),
    "app/utils.py": textwrap.dedent("""
        # 이 파일은 추후에 스크린샷 등 공용 함수로 채워질 예정입니다.
        def take_screenshot(region):
            # region: (left, top, width, height)
            print(f"{region} 영역의 스크린샷을 캡처합니다.")
            return None # 실제 이미지 객체를 반환해야 함
    """),
}

def create_project_structure():
    """프로젝트 폴더 구조와 기본 파일들을 생성합니다."""
    print("프로젝트 구조 생성을 시작합니다...")

    # 파일 생성
    for file_path, content in project_files.items():
        # 파일이 속한 폴더부터 생성
        dir_name = os.path.dirname(file_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        
        # 파일 생성 및 내용 쓰기
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  - 파일 생성: {file_path}")

    # 데이터 저장용 빈 폴더 생성
    os.makedirs("captured_data", exist_ok=True)
    print("  - 폴더 생성: captured_data/")
    
    print("\n프로젝트 구조 생성이 완료되었습니다!")
    print("다음 단계를 진행해 주세요:")
    print("1. 터미널에서 가상환경을 생성하고 활성화하세요.")
    print("2. `pip install -r requirements.txt` 명령어로 라이브러리를 설치하세요.")
    print("3. `python app/main.py` 명령어로 프로그램을 실행하여 기본 창이 뜨는지 확인하세요.")

if __name__ == "__main__":
    create_project_structure()