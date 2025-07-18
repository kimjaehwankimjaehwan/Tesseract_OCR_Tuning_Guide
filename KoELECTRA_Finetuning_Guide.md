# KoELECTRA 언어 모델 파인튜닝 가이드

이 문서는 범용 KoELECTRA 모델을 우리가 원하는 특정 작업('출석중', '강의중' 등 상황 분류)에 맞게 전문가로 재교육시키는 **파인튜닝(Fine-tuning)** 과정을 정리합니다.

## 1. 데이터 준비: `final_gt.csv`

AI 모델의 성능은 데이터의 양과 질에 의해 결정됩니다. 좋은 모델을 만들기 위해서는 좋은 데이터가 필수적입니다.

-   **파일 형식:** `text`와 `ai_label` 두 개의 열을 가진 CSV 파일
-   **데이터 품질 원칙:**
    1.  **품질 (Quality):** `text` 열의 내용은 OCR 오류가 모두 수정된, 완벽한 '정답' 텍스트여야 합니다.
    2.  **균형 (Balance):** 각 `ai_label` (예: '출석체크중', '강의중')에 해당하는 데이터의 개수가 비슷해야 모델이 한쪽으로 치우치지 않습니다.
    3.  **다양성 (Diversity):** 각 라벨에 대해, 실제 상황에서 발생할 수 있는 다양한 문장 표현을 포함해야 합니다.
    4.  **반례 (Counter-example):** AI가 헷갈리기 쉬운 데이터(예: 숫자가 있지만 출석이 아닌 문장)를 '대기중'과 같은 올바른 라벨로 알려주어, 모델의 판단력을 날카롭게 만들어야 합니다.

**샘플 `final_gt.csv`:**
```csv
text,ai_label
1번 홍길동,출석체크중
네,출석체크중
다들 과제는 하셨나요,대기중
1번 문제가 이해가 안돼요,대기중
소리가 안 들립니다,민원발생
```

## 2. 파인튜닝 스크립트: `train.py`

우리가 만든 `fine_tuning_ocr/train.py` 스크립트는 아래와 같은 순서로 동작합니다.

1.  **데이터 로드:** `pandas`로 `final_gt.csv` 파일을 읽고, `datasets` 라이브러리를 사용해 AI가 학습하기 좋은 형태로 변환합니다.
2.  **데이터 분할:** 전체 데이터를 훈련용(80%)과 검증용(20%)으로 자동 분할합니다.
3.  **토크나이저 로드:** `beomi/KcELECTRA-base` 모델이 사용하는 '단어 분리기'(Tokenizer)를 불러옵니다.
4.  **사전 학습 모델 로드:** `beomi/KcELECTRA-base`라는, 한국어를 미리 학습한 범용 '대학생' 모델을 불러옵니다. 이때, 우리가 분류할 라벨의 개수(`num_labels`)를 알려주어 모델의 최종 출력층을 우리 문제에 맞게 새로 구성합니다.
5.  **훈련 실행:** `Trainer` 객체가 훈련용 데이터로 모델을 재학습(파인튜닝)시킵니다. 이 과정에서 모델은 우리 데이터에 특화된 전문가가 됩니다.
6.  **평가 및 저장:** 훈련이 끝난 뒤, 검증용 데이터로 모델의 최종 성능(정확도 등)을 평가하고, 완성된 모델을 `final_attendance_model`과 같은 폴더에 저장합니다.

## 3. 실행 방법

1.  `fine_tuning_ocr` 폴더에 잘 만들어진 `final_gt.csv` 파일을 준비합니다.
2.  `train.py` 파일 상단의 `output_model_dir` 변수를 원하는 모델 폴더 이름으로 수정합니다.
3.  터미널에서 `fine_tuning_ocr` 폴더로 이동한 뒤, 아래 명령어를 실행합니다.
    ```bash
    python train.py
    ```

## 4. 튜닝된 모델 메인 프로그램에 적용하기

훈련이 완료되어 새로운 모델 폴더(예: `final_attendance_model`)가 생성되면, `app/ai_model.py` 파일의 `model_path` 변수를 이 새 폴더 경로로 수정해주면 됩니다.

```python
# app/ai_model.py 의 일부
# ...
model_path = "fine_tuning_ocr/final_attendance_model" # 이 부분을 새 모델 폴더 이름으로 변경
# ...
```