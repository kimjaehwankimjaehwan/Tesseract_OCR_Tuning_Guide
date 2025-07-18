import os
import tkinter as tk
import easyocr  # easyocr 임포트
from PIL import Image, ImageDraw, ImageFont, ImageGrab

def select_and_capture_area():
    """
    사용자가 마우스로 영역을 선택하게 하고, 해당 영역을 캡처하여
    임시 파일로 저장한 뒤 파일 경로를 반환합니다.
    """
    print("화면 영역 선택을 시작합니다. 화면 왼쪽 위 모서리를 클릭하고 오른쪽 아래로 드래그하세요.")
    
    root = tk.Tk()
    root.withdraw()
    
    toplevel = tk.Toplevel(root)
    toplevel.attributes("-fullscreen", True)
    toplevel.attributes("-alpha", 0.3)
    toplevel.configure(bg="black")
    canvas = tk.Canvas(toplevel, cursor="cross")
    canvas.pack(fill="both", expand=True)
    
    coords = {}
    temp_image_path = "temp_capture.png"

    def on_press(event):
        coords['x1'] = event.x
        coords['y1'] = event.y
        coords['rect'] = None

    def on_drag(event):
        if coords.get('rect'):
            canvas.delete(coords['rect'])
        coords['rect'] = canvas.create_rectangle(
            coords['x1'], coords['y1'], event.x, event.y, 
            outline='red', width=2
        )

    def on_release(event):
        coords['x2'] = event.x
        coords['y2'] = event.y
        toplevel.destroy()
        root.quit()

    canvas.bind("<ButtonPress-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)

    root.mainloop()

    if all(k in coords for k in ['x1', 'y1', 'x2', 'y2']):
        x1 = min(coords['x1'], coords['x2'])
        y1 = min(coords['y1'], coords['y2'])
        x2 = max(coords['x1'], coords['x2'])
        y2 = max(coords['y1'], coords['y2'])

        if x1 == x2 or y1 == y2:
            print("오류: 유효한 영역이 선택되지 않았습니다 (너비 또는 높이가 0).")
            return None

        print(f"선택된 영역: ({x1}, {y1}, {x2}, {y2})")
        print("스크린샷을 캡처합니다...")
        screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        screenshot.save(temp_image_path)
        print(f"임시 파일 저장 완료: {temp_image_path}")
        return temp_image_path
    else:
        print("영역이 선택되지 않았습니다.")
        return None


def run_ocr_on_file(image_path):
    """
    지정된 이미지 파일에 대해 EasyOCR을 실행하고 결과를 출력 및 시각화합니다.
    """
    if not image_path:
        return

    print("="*50)
    print("EasyOCR 분석을 시작합니다.")
    print(f"분석 대상 이미지: {image_path}")
    print("="*50)

    try:
        # --- 핵심 수정: EasyOCR 모델 초기화 ---
        print("EasyOCR 모델을 로딩 중입니다... (첫 실행 시 시간이 걸릴 수 있습니다)")
        reader = easyocr.Reader(['ko', 'en'])
        print("EasyOCR 모델 로딩 완료.")
    except Exception as e:
        print(f"모델 로딩 중 오류 발생: {e}")
        return

    print("\nOCR 탐지를 시작합니다...")
    # --- 핵심 수정: EasyOCR의 readtext 함수 사용 ---
    result = reader.readtext(image_path)
    print("OCR 탐지 완료.")

    print("\n--- 감지된 텍스트 결과 ---")
    if result:
        # --- 핵심 수정: EasyOCR 결과 형식에 맞게 파싱 ---
        for idx, (bbox, text, prob) in enumerate(result):
            print(f"[{idx+1}] 텍스트: {text} (신뢰도: {prob:.4f})")
    else:
        print("감지된 텍스트가 없습니다.")
    
    print("---------------------------\n")

    print("결과를 이미지에 그려서 보여줍니다...")
    try:
        image = Image.open(image_path).convert('RGB')
        draw = ImageDraw.Draw(image)
        font_path = os.path.join(os.environ['WINDIR'], 'Fonts', 'malgun.ttf')
        font = ImageFont.truetype(font_path, 15)

        if result:
            for (bbox, text, prob) in result:
                # EasyOCR의 bbox는 [[x1,y1], [x2,y1], [x2,y2], [x1,y2]] 형식
                (top_left, top_right, bottom_right, bottom_left) = bbox
                
                draw.polygon([top_left, top_right, bottom_right, bottom_left], outline='red', width=2)
                
                # 텍스트 그리기
                draw.text((top_left[0], top_left[1] - 20), f"{text} ({prob:.2f})", font=font, fill='red')
        
        image.show()
        print("테스트 완료.")
    except Exception as e:
        print(f"결과 시각화 중 오류 발생: {e}")


if __name__ == '__main__':
    temp_image_file = select_and_capture_area()
    run_ocr_on_file(temp_image_file)