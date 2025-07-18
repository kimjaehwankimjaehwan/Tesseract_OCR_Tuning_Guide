import numpy as np
import cv2
from PIL import ImageGrab

def take_screenshot(region):
    """
    지정된 영역의 스크린샷을 찍어 numpy 배열로 반환합니다. (Pillow 사용)
    """
    if region is None:
        return None
        
    x1, y1, x2, y2 = region
    try:
        screenshot_pil = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        # Pillow 이미지 객체를 numpy 배열로 변환
        return np.array(screenshot_pil)
    except Exception as e:
        print(f"스크린샷 캡처 중 오류 발생: {e}")
        return None

def preprocess_image(image_np):
    """
    OCR 정확도를 높이기 위해 이미지를 전처리합니다. (강화된 버전)
    """
    # Pillow의 RGB 이미지를 OpenCV의 BGR 순서로 변환
    image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
    
    # 그레이스케일로 변환
    gray_image = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

    # 이미지 확대 (작은 글씨 인식률 향상)
    height, width = gray_image.shape
    resized_image = cv2.resize(gray_image, (width*2, height*2), interpolation=cv2.INTER_CUBIC)

    # 선명도 향상 (Sharpening)
    sharpening_kernel = np.array([[-1, -1, -1],
                                  [-1,  9, -1],
                                  [-1, -1, -1]])
    sharpened_image = cv2.filter2D(resized_image, -1, sharpening_kernel)

    # 이진화 (Thresholding)
    _, binary_image = cv2.threshold(sharpened_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # 흑백(1채널) 이미지를 다시 컬러(3채널) 형식으로 변환하여 반환
    final_image = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2BGR)
    
    return final_image