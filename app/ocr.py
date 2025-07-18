import os
import pytesseract
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import re

# Tesseract 실행 파일 경로 직접 지정
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class OCRProcessor:
    def __init__(self):
        """Tesseract OCR 프로세서 초기화"""
        self.is_ready = False
        self.font = None
        print("Tesseract OCR 프로세서가 준비되었습니다.")
        self.initialize()

    def initialize(self):
        """Tesseract는 별도의 초기화 과정이 필요 없으므로, 바로 준비 완료 상태로 변경합니다."""
        self.initialize_font()
        self.is_ready = True
        print("Tesseract는 즉시 사용 가능합니다.")
        pass

    def initialize_font(self):
        """시각화에 사용할 폰트를 로드합니다."""
        font_path = os.path.join(os.environ['WINDIR'], 'Fonts', 'malgun.ttf')
        try:
            self.font = ImageFont.truetype(font_path, 15)
        except IOError:
            self.font = ImageFont.load_default()

    def get_text_from_image(self, image_np):
        """Numpy 배열 형태의 이미지에서 텍스트를 추출하고 후처리를 적용합니다."""
        if not self.is_ready: return "OCR 엔진 준비 안됨", None
        if image_np is None: return "", None
        
        try:
            # --- 핵심 수정 1: Tesseract의 PSM 모드를 11로 변경 ---
            # --psm 11 옵션은 흩어져 있는 텍스트를 찾는 데 더 효과적일 수 있습니다.
            custom_config = r'--oem 3 --psm 11'
            raw_text = pytesseract.image_to_string(image_np, lang='kor+eng', config=custom_config)
            
            # --- 핵심 수정 2: 후처리 로직 추가 ---
            # Tesseract 결과에서 불필요한 공백과 특수문자를 제거하고, 줄바꿈을 정리합니다.
            lines = raw_text.strip().split('\n')
            # 비어있지 않은 줄들만 모아서, 앞뒤 공백을 제거
            processed_lines = [line.strip() for line in lines if line.strip()]
            # 정리된 줄들을 하나의 공백으로 이어붙여 최종 문장을 만듭니다.
            final_text = ' '.join(processed_lines)
            # -----------------------------------------

            return final_text, None
            
        except pytesseract.TesseractNotFoundError:
            error_msg = "오류: Tesseract가 설치되지 않았거나 지정된 경로가 잘못되었습니다."
            return error_msg, None
        except Exception as e:
            error_msg = f"Tesseract 오류: {e}"
            return error_msg, None

    def draw_ocr_results(self, image_np, ocr_results):
        """현재 버전에서는 원본 이미지를 그대로 반환합니다."""
        return image_np

# 다른 파일에서 가져다 쓸 수 있도록 인스턴스 생성
ocr_processor = OCRProcessor()