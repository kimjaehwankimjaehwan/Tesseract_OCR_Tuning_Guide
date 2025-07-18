import traceback
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

class AIProcessor:
    def __init__(self):
        self.classifier = None
        self.is_ready = False
        print("AIProcessor 인스턴스 생성됨. 모델은 아직 로딩되지 않음.")

    def initialize(self):
        if self.classifier is not None:
            self.is_ready = True
            return

        print("최종 AI 모델 로딩 시작...")
        try:
            model_path = "finetuning_data/final_attendance_model"
            tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=False)
            model = AutoModelForSequenceClassification.from_pretrained(model_path)
            
            self.classifier = pipeline(
                "text-classification",
                model=model,
                tokenizer=tokenizer
            )
            print("최종 AI 모델 로딩 완료.")
        except Exception as e:
            print(f"AI 모델 로딩 중 심각한 오류 발생: {e}")
            self.classifier = lambda x: [{'label': '모델 로딩 실패', 'score': 0.0}]
        
        self.is_ready = True

    def predict_situation(self, text):
        if not self.is_ready: return "모델 로딩 안됨", 0.0
        if not text: return "내용 없음", 0.0
        try:
            prediction = self.classifier(text)
            top_prediction = prediction[0]
            label = top_prediction['label']
            confidence = top_prediction['score']
            return label, confidence
        except Exception as e:
            print("AI 예측 중 오류 발생! 상세 정보:")
            traceback.print_exc()
            return "예측 오류", 0.0

ai_processor = AIProcessor()