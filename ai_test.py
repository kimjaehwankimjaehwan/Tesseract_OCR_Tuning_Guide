from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import os

def run_ai_test():
    """
    파인튜닝된 AI 모델을 로드하여, 테스트 문장들에 대한 예측을 수행합니다.
    """
    # 1. 우리가 훈련시킨 최종 모델이 있는 폴더 경로
    model_path = "finetuning_data/final_attendance_model"

    if not os.path.exists(model_path):
        print(f"오류: 모델 폴더를 찾을 수 없습니다 - {model_path}")
        print("train.py를 실행하여 모델을 먼저 훈련시켜주세요.")
        return

    print("="*50)
    print(f"AI 모델 테스트를 시작합니다: {model_path}")
    print("="*50)

    # 2. 모델과 토크나이저 로드
    try:
        print("AI 모델 로딩 중...")
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForSequenceClassification.from_pretrained(model_path)
        classifier = pipeline("text-classification", model=model, tokenizer=tokenizer)
        print("AI 모델 로딩 완료.")
    except Exception as e:
        print(f"모델 로딩 중 오류 발생: {e}")
        return

# 3. 테스트할 문장 목록 (새로운 버전)
    test_sentences = [
        # --- '출석체크중'을 기대하는 문장 ---
        "18번 이정재 출석",
        "저 왔어요",
        "네네",
        
        # --- '강의중'을 기대하는 문장 ---
        "자, 오늘 진도는 4장입니다",
        "이 내용은 시험에 안 나옵니다",
        "다들 잘 따라오고 있죠?",

        # --- '질문자발생'을 기대하는 문장 ---
        "교수님, 방금 그 설명 다시 부탁드립니다",
        "이해가 안 가서 질문드립니다",
        "혹시 15번 학생 출석했나요?", # '출석'이 있지만 질문이므로 AI가 헷갈릴 수 있음 (중요 테스트)

        # --- '민원발생'을 기대하는 문장 ---
        "화면이 계속 버퍼링 걸려요",
        "교수님 마이크에서 지지직 소리가 나요",
        "채팅이 너무 빨라서 못 읽겠어요"
    ]
    
    
    print("\n--- AI 분석 결과 ---")
    # 4. 각 문장에 대해 예측 수행 및 결과 출력
    for text in test_sentences:
        prediction = classifier(text)[0]
        label = prediction['label']
        score = prediction['score']
        print(f"입력: '{text}'  ->  예측: '{label}' (확신도: {score:.2f})")
    
    print("---------------------\n")
    print("테스트 완료.")


if __name__ == '__main__':
    run_ai_test()