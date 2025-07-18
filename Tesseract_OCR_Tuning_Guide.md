# Tesseract OCR 정확도 향상 가이드

이 문서는 Tesseract OCR 엔진의 한글 인식률을 높이기 위해 우리 프로젝트에서 적용한 다양한 기법들을 정리합니다.

## 1. 이미지 전처리 (Preprocessing)

Tesseract는 **크고, 깨끗하며, 흑백 대비가 명확한** 이미지에서 가장 좋은 성능을 보입니다. `app/utils.py`의 `preprocess_image` 함수는 원본 스크린샷을 Tesseract가 가장 좋아하는 형태로 가공하는 역할을 합니다.

```python
# app/utils.py

def preprocess_image(image_np):
    # 1. 색상 공간 변환 (RGB -> BGR -> Grayscale)
    image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
    gray_image = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

    # 2. 노이즈 제거 (Median Blur)
    # 이미지의 작은 점 같은 노이즈를 효과적으로 제거합니다.
    denoised_image = cv2.medianBlur(gray_image, 3)

    # 3. 이미지 확대 (Scaling)
    # 작은 글씨 인식을 위해 이미지 크기를 2배로 키웁니다. 인식률에 가장 큰 영향을 줄 수 있습니다.
    height, width = denoised_image.shape
    resized_image = cv2.resize(denoised_image, (width*2, height*2), interpolation=cv2.INTER_CUBIC)

    # 4. 선명도 향상 (Sharpening)
    # 글자의 경계선을 뚜렷하게 만들어 흐릿한 글씨를 보정합니다.
    sharpening_kernel = np.array([[-1, -1, -1],
                                  [-1,  9, -1],
                                  [-1, -1, -1]])
    sharpened_image = cv2.filter2D(resized_image, -1, sharpening_kernel)

    # 5. 이진화 (Binarization)
    # 최종적으로 이미지를 흑과 백으로만 구성되도록 변경합니다.
    # THRESH_OTSU는 최적의 임계값을 자동으로 찾아줍니다.
    _, binary_image = cv2.threshold(sharpened_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Tesseract에 전달하기 위해 다시 3채널 이미지로 변환합니다.
    final_image = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2BGR)
    
    return final_image
```

## 2. Tesseract 실행 옵션 최적화

`pytesseract`를 통해 Tesseract를 호출할 때, `config` 옵션을 주어 동작 방식을 제어할 수 있습니다. 가장 중요한 옵션은 **페이지 분석 모드(Page Segmentation Mode, `--psm`)** 입니다.

```python
# app/ocr.py

# --psm <숫자> 옵션으로 분석 방식을 지정
custom_config = r'--oem 3 --psm 11' 
text = pytesseract.image_to_string(image_np, lang='kor+eng', config=custom_config)
```

### 주요 PSM 값
- **`--psm 3` (기본값):** 완전 자동 페이지 분석. (일반적인 문서에 적합)
- **`--psm 6`:** 이미지를 하나의 통일된 텍스트 블록으로 간주. (단락, 문단 형태에 적합)
- **`--psm 7`:** 이미지를 한 줄의 텍스트로 간주. (한 줄짜리 채팅에 효과적)
- **`--psm 11`:** 흩어져 있는 텍스트를 최대한 찾아냄. (여러 위치에 텍스트가 있는 채팅창에 시도해볼 만함)

## 3. OCR 모델 파인튜닝 (궁극의 방법)

위 방법들로도 정확도가 부족할 경우, 우리가 수집한 데이터로 Tesseract 모델 자체를 재학습시키는 파인튜닝을 진행할 수 있습니다. 이 과정은 매우 복잡하며, 별도의 전문적인 과정이 필요합니다.

1.  **학습 데이터 생성:** `이미지`와 `정답.box` 파일(글자와 좌표 정보) 쌍을 대량으로 준비합니다. (`create_box_files.py`가 이 과정의 첫 단계를 자동화합니다.)
2.  **훈련 실행:** Tesseract의 커맨드라인 훈련 도구를 사용하여 새로운 `kor.traineddata` 파일을 생성합니다.
3.  **적용:** 생성된 `traineddata` 파일을 Tesseract의 `tessdata` 폴더에 넣고 OCR을 실행합니다.

이 방법은 우리 프로젝트의 범위를 넘어서지만, 최고의 성능을 내기 위한 궁극적인 해결책입니다.