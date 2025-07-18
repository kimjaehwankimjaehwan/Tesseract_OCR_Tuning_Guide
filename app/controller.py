import json
import os
import threading
import csv
import traceback
import time 
from tkinter import messagebox
from datetime import datetime
from pathlib import Path
from PIL import Image

from .ocr import ocr_processor
from .ai_model import ai_processor
from . import utils
from .overlay import OverlayWindow
from .tuning_window import OCRTuningWindow

class Controller:
    def __init__(self, view):
        self.view = view
        self.ocr_engine = ocr_processor
        self.ai_engine = ai_processor
        self.is_monitoring = False
        self.monitoring_job = None
        self.last_detected_text = ""
        self.overlay = None
        
        self.last_captured_image = None
        self.last_processed_image = None
        self.last_ocr_result = None
        self.last_saved_image_path = None
        
        self.capture_dir = Path("captured_data")
        self.capture_dir.mkdir(exist_ok=True)
        
        finetuning_dir = Path("finetuning_data")
        finetuning_dir.mkdir(exist_ok=True)
        self.ground_truth_path = finetuning_dir / "ground_truth.csv"

    def initialize_models(self):
        """백그라운드에서 모델들을 초기화합니다."""
        self.view.set_ui_state(False)
        self.view.frames[self.view.MonitorFrame].add_log("AI 모델 백그라운드 로딩 시작...")
        
        ocr_thread = threading.Thread(target=self.ocr_engine.initialize, daemon=True)
        ocr_thread.start()
        
        ai_thread = threading.Thread(target=self.ai_engine.initialize, daemon=True)
        ai_thread.start()
        
        self.view.root.after(100, self.check_model_loading_status)

    def check_model_loading_status(self):
        """두 모델이 모두 준비 완료 신호를 보냈는지 확인합니다."""
        if self.ocr_engine.is_ready and self.ai_engine.is_ready:
            self.view.frames[self.view.MonitorFrame].add_log("모든 AI 모델 준비 완료. 사용 가능합니다.")
            self.view.set_ui_state(True)
        else:
            self.view.root.after(500, self.check_model_loading_status)

    def proceed_to_monitoring(self):
        """설정 화면에서 모니터링 화면으로 전환하는 중간다리 역할."""
        monitor_frame = self.view.frames[self.view.MonitorFrame]
        setup_frame = self.view.frames[self.view.SetupFrame]
        region = setup_frame.selected_region
        
        if region:
            monitor_frame.region_var.set(str(region))
        else:
            monitor_frame.region_var.set("오류: 영역 설정 필요")

        self.view.show_frame(self.view.MonitorFrame)

    def start_monitoring(self):
        """모니터링 시작"""
        if self.is_monitoring: return
        setup_frame = self.view.frames[self.view.SetupFrame]
        region = setup_frame.selected_region
        if not region:
            self.view.frames[self.view.MonitorFrame].add_log("오류: OCR 영역이 설정되지 않았습니다.")
            return
        if self.overlay: self.overlay.destroy()
        self.overlay = OverlayWindow(region)
        self.last_detected_text = ""
        self.is_monitoring = True
        log_message = "컨트롤러: 모니터링 시작됨."
        self.view.frames[self.view.MonitorFrame].add_log(log_message)
        self._monitoring_step()

    def stop_monitoring(self):
        """모니터링 중지"""
        if not self.is_monitoring: return
        if self.monitoring_job:
            self.view.root.after_cancel(self.monitoring_job)
            self.monitoring_job = None
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None
        self.is_monitoring = False
        log_message = "컨트롤러: 모니터링 중지됨."
        self.view.frames[self.view.MonitorFrame].add_log(log_message)
        print("모니터링을 중지합니다.")

    def _monitoring_step(self):
        """실제 모니터링 작업을 수행하는 내부 메소드"""
        monitor_frame = self.view.frames[self.view.MonitorFrame]
        try:
            if not self.is_monitoring: return
            
            start_time = time.time()
            setup_frame = self.view.frames[self.view.SetupFrame]
            region = setup_frame.selected_region
            if not region: return
            
            screenshot_original = utils.take_screenshot(region)
            if screenshot_original is None:
                monitor_frame.add_log("오류: 스크린샷 캡처에 실패했습니다.")
                self.monitoring_job = self.view.root.after(3000, self._monitoring_step)
                return

            screenshot_processed = utils.preprocess_image(screenshot_original)
            self.last_captured_image = screenshot_original
            self.last_processed_image = screenshot_processed
            detected_text, ocr_result = self.ocr_engine.get_text_from_image(screenshot_processed)
            ocr_time = time.time() - start_time
            monitor_frame.add_log(f"OCR 처리 시간: {ocr_time:.2f}초")
            self.last_ocr_result = ocr_result
            monitor_frame.update_ocr_text(detected_text if detected_text else "텍스트 없음")
            
            if detected_text and detected_text != self.last_detected_text:
                monitor_frame.add_log(f"새로운 OCR 텍스트 감지: {detected_text}")
                self.last_detected_text = detected_text

                ai_label, confidence = self.ai_engine.predict_situation(detected_text)
                
                final_label = ai_label
                if ai_label == '출석체크중':
                    attendance_keywords = ["출석", "출첵"]
                    is_keyword_present = any(keyword in detected_text for keyword in attendance_keywords)
                    if not is_keyword_present:
                        final_label = '대기중'
                        monitor_frame.add_log(f"AI 판단 보정: 키워드 미포함으로 '{ai_label}' -> '{final_label}'")
                
                # 개선된 UI 업데이트 함수를 호출
                monitor_frame.update_ai_prediction(final_label, confidence)
                self.save_capture(screenshot_original, detected_text, final_label)
            
            self.monitoring_job = self.view.root.after(3000, self._monitoring_step)
        except Exception as e:
            error_details = traceback.format_exc()
            log_message = f"모니터링 중 심각한 오류 발생: {e}"
            print(log_message)
            print(error_details)
            monitor_frame.add_log(log_message)
            monitor_frame.add_log("모니터링을 중지합니다.")
            self.stop_monitoring()

    def save_capture(self, image_np, text, label):
        """캡처된 이미지와 텍스트, AI 라벨을 CSV 파일에 기록합니다."""
        try:
            date_folder = self.capture_dir / datetime.now().strftime('%Y-%m-%d')
            date_folder.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            image_filename = f"capture_{timestamp}.png"
            image_path = date_folder / image_filename
            Image.fromarray(image_np).save(image_path)
            
            write_header = not self.ground_truth_path.exists()
            with open(self.ground_truth_path, 'a', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                if write_header:
                    writer.writerow(["image_path", "text", "ai_label"])
                writer.writerow([str(image_path).replace('\\', '/'), text, label])
            
            monitor_frame = self.view.frames[self.view.MonitorFrame]
            monitor_frame.add_log(f"튜닝 데이터 저장됨: {self.ground_truth_path}")
        except Exception as e:
            error_log = f"데이터 저장 오류: {e}"
            print(error_log)
            self.view.frames[self.view.MonitorFrame].add_log(error_log)
            
    def show_last_capture(self):
        """'마지막 캡처 보기' 버튼 클릭 시, 원본과 전처리 이미지를 팝업으로 띄웁니다."""
        if self.last_captured_image is not None and self.last_processed_image is not None:
            self.view.show_image_popup(self.last_captured_image, self.last_processed_image)
        else:
            self.view.frames[self.view.MonitorFrame].add_log("표시할 캡처 정보가 없습니다.")
            
    def open_ocr_tuning_window(self):
        """'OCR 튜닝' 버튼 클릭 시 호출. 튜닝 창을 엽니다."""
        OCRTuningWindow(self.view.root, self)

    def tune_language_model(self):
        """'언어모델 튜닝' 버튼 클릭 시 호출."""
        messagebox.showinfo("알림", "언어모델 튜닝 기능은 현재 개발 중입니다.")
    
    def exit_program(self):
        """'프로그램 종료' 버튼 클릭 시 호출."""
        if messagebox.askokcancel("프로그램 종료", "정말로 프로그램을 종료하시겠습니까?"):
            if self.overlay:
                self.overlay.destroy()
            self.view.root.destroy()
            
    def load_config(self):
        """(미구현) 설정 파일을 불러오는 함수"""
        print("설정 파일을 로드합니다.")
        pass