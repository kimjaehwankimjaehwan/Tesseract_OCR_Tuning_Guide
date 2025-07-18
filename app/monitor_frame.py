import tkinter as tk
from tkinter import font
from tkinter.scrolledtext import ScrolledText

class MonitorFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        control_frame = tk.Frame(main_frame)
        control_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=5)

        self.start_button = tk.Button(control_frame, text="모니터링 시작", 
                                      command=self.controller.start_monitoring)
        self.start_button.pack(side='left', padx=5)

        self.stop_button = tk.Button(control_frame, text="모니터링 중지", 
                                     command=self.controller.stop_monitoring)
        self.stop_button.pack(side='left', padx=5)
        
        self.last_capture_button = tk.Button(control_frame, text="마지막 캡처 보기",
                                             command=self.controller.show_last_capture)
        self.last_capture_button.pack(side='left', padx=15)

        tuning_frame = tk.Frame(control_frame)
        tuning_frame.pack(side='right', padx=5)

        self.ocr_tuning_button = tk.Button(tuning_frame, text="OCR 튜닝",
                                           command=self.controller.open_ocr_tuning_window)
        self.ocr_tuning_button.pack(side='left', padx=5)

        self.lm_tuning_button = tk.Button(tuning_frame, text="언어모델 튜닝",
                                          command=self.controller.tune_language_model)
        self.lm_tuning_button.pack(side='left', padx=5)
        
        self.exit_button = tk.Button(tuning_frame, text="프로그램 종료",
                                     command=self.controller.exit_program)
        self.exit_button.pack(side='left', padx=5)
        
        ocr_display_frame = tk.LabelFrame(main_frame, text="실시간 OCR 텍스트")
        ocr_display_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        
        self.ocr_text_widget = tk.Text(ocr_display_frame, state='disabled', height=10, 
                                       font=("Malgun Gothic", 12))
        self.ocr_text_widget.pack(fill='both', expand=True, padx=5, pady=5)

        right_panel = tk.Frame(main_frame)
        right_panel.grid(row=1, column=1, sticky="nsew", padx=(5, 0))
        right_panel.rowconfigure(2, weight=1) # 로그창이 늘어날 수 있도록 행 가중치 변경
        right_panel.columnconfigure(0, weight=1)

        # --- AI 예측 결과를 보여줄 새로운 프레임 ---
        ai_display_frame = tk.LabelFrame(right_panel, text="AI 최종 판단")
        ai_display_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        self.ai_main_label_var = tk.StringVar(value="대기 중...")
        self.ai_main_label = tk.Label(ai_display_frame, textvariable=self.ai_main_label_var, 
                                      font=("Malgun Gothic", 20, "bold"), fg="#00008B")
        self.ai_main_label.pack(pady=10, padx=10)
        # ----------------------------------------
        
        info_frame = tk.LabelFrame(right_panel, text="실시간 정보")
        info_frame.grid(row=1, column=0, sticky="ew") # AI 표시창 아래로 이동
        
        region_label = tk.Label(info_frame, text="[선택 영역]:")
        region_label.pack(side='left', padx=5)
        self.region_var = tk.StringVar(value="설정 필요")
        self.region_label = tk.Label(info_frame, textvariable=self.region_var, fg="purple")
        self.region_label.pack(side='left', padx=5)

        # 기존의 작은 AI 분석 라벨은 신뢰도 점수만 표시하도록 변경
        ai_confidence_label = tk.Label(info_frame, text="[확신도]:")
        ai_confidence_label.pack(side='left', padx=15)
        self.ai_confidence_var = tk.StringVar(value="N/A")
        self.ai_confidence_label = tk.Label(info_frame, textvariable=self.ai_confidence_var, fg="green")
        self.ai_confidence_label.pack(side='left', padx=5)

        log_frame = tk.LabelFrame(right_panel, text="작업 로그")
        log_frame.grid(row=2, column=0, sticky="nsew", pady=(5,0)) # 정보창 아래로 이동
        
        self.log_text = ScrolledText(log_frame, state='disabled', height=10)
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)
    
    def set_ui_state(self, state):
        self.start_button.config(state=state)
        self.stop_button.config(state=state)
        self.last_capture_button.config(state=state)
        self.ocr_tuning_button.config(state=state)
        self.lm_tuning_button.config(state=state)
        self.exit_button.config(state=state)

    def add_log(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + '\\n')
        self.log_text.config(state='disabled')
        self.log_text.see(tk.END)

    def update_ocr_text(self, text):
        self.ocr_text_widget.config(state='normal')
        self.ocr_text_widget.delete('1.0', tk.END)
        self.ocr_text_widget.insert(tk.END, text)
        self.ocr_text_widget.config(state='disabled')

    def update_ai_prediction(self, label, confidence):
        """새로운 AI 예측 결과 표시창을 업데이트하는 함수"""
        self.ai_main_label_var.set(label)
        self.ai_confidence_var.set(f"{confidence:.2f}")