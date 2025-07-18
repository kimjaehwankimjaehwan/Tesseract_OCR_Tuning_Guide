import tkinter as tk
from tkinter import font, messagebox, filedialog
import csv
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageTk

class OCRTuningWindow(tk.Toplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.title("OCR 튜닝")
        self.geometry("900x700")
        
        self.controller = controller
        self.csv_path = self.controller.ground_truth_path
        
        self.data = []
        self.current_index = 0

        self.index_label = tk.Label(self)
        self.path_label = tk.Label(self)
        self.image_label = tk.Label(self)
        self.text_widget = tk.Text(self)
        self.prev_button = tk.Button(self)
        self.next_button = tk.Button(self)
        
        self.build_ui()
        self.load_data()
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def build_ui(self):
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        top_frame = tk.Frame(main_frame)
        top_frame.pack(fill="x", pady=5)
        self.index_label = tk.Label(top_frame, text="0 / 0", font=("Malgun Gothic", 10, "bold"))
        self.index_label.pack(side="left")
        self.path_label = tk.Label(top_frame, text="image_path: ", anchor="w")
        self.path_label.pack(side="left", padx=10)
        self.image_label = tk.Label(main_frame, text="이미지 로딩 중...")
        self.image_label.pack(fill="both", expand=True, pady=5)
        text_frame = tk.LabelFrame(main_frame, text="text (수정 가능)")
        text_frame.pack(fill="x", pady=5)
        self.text_widget = tk.Text(text_frame, height=8, font=("Malgun Gothic", 11))
        self.text_widget.pack(fill="x", expand=True, padx=5, pady=5)
        bottom_frame = tk.Frame(main_frame)
        bottom_frame.pack(fill="x", pady=10)
        self.prev_button = tk.Button(bottom_frame, text="< 이전", width=10, command=self.go_to_previous)
        self.prev_button.pack(side="left", padx=5)
        self.next_button = tk.Button(bottom_frame, text="다음 >", width=10, command=self.go_to_next)
        self.next_button.pack(side="right", padx=5)
        save_button = tk.Button(bottom_frame, text="전체 저장", width=15, command=self.save_all_changes)
        save_button.pack(expand=True)
    
    def load_data(self):
        try:
            if not self.csv_path.exists():
                self.image_label.config(text="수집된 데이터가 없습니다.\n메인 프로그램에서 모니터링을 시작하여 데이터를 수집해주세요.")
                return

            with open(self.csv_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                self.data = list(reader)
            
            if self.data:
                self.display_record(0)
            else:
                self.image_label.config(text="CSV 파일에 데이터가 없습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"CSV 파일 로딩 중 오류 발생:\n{e}")
            self.destroy()

    def display_record(self, index):
        if not (0 <= index < len(self.data)): return
        self.current_index = index
        record = self.data[index]
        self.index_label.config(text=f"{self.current_index + 1} / {len(self.data)}")
        self.path_label.config(text=f"image_path: {record.get('image_path', 'N/A')}")
        try:
            img_path = Path(record['image_path'])
            img = Image.open(img_path)
            w, h = img.size
            new_w = 800
            new_h = int(new_w * (h/w))
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            self.image_label.config(image=img_tk)
            self.image_label.image = img_tk
        except Exception as e:
            self.image_label.config(image=None, text=f"이미지 로드 오류:\n{record.get('image_path', 'N/A')}\n{e}")
            self.image_label.image = None
        self.text_widget.config(state="normal")
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert("1.0", record.get("text", ""))
        self.text_widget.config(state="normal")
        self.prev_button.config(state="normal" if self.current_index > 0 else "disabled")
        self.next_button.config(state="normal" if self.current_index < len(self.data) - 1 else "disabled")

    def _update_current_record_in_memory(self):
        if self.data:
            current_text = self.text_widget.get("1.0", tk.END).strip()
            self.data[self.current_index]['text'] = current_text

    def go_to_next(self):
        self._update_current_record_in_memory()
        if self.current_index < len(self.data) - 1:
            self.display_record(self.current_index + 1)
    
    def go_to_previous(self):
        self._update_current_record_in_memory()
        if self.current_index > 0:
            self.display_record(self.current_index - 1)

    def save_all_changes(self):
        self._update_current_record_in_memory()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"ground_truth_{timestamp}.csv"
        save_path = self.csv_path.parent / new_filename
        try:
            with open(save_path, 'w', newline='', encoding='utf-8-sig') as f:
                # --- 핵심 수정: 저장할 필드 목록을 명시적으로 정의 ---
                fieldnames = ["image_path", "text", "ai_label"]
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                # extrasaction='ignore' 옵션 덕분에 self.data에 예상치 못한 필드가 있어도 무시하고 저장함
                writer.writerows(self.data)
            
            messagebox.showinfo("저장 완료", f"수정된 내용이 아래 경로에 저장되었습니다:\n{save_path}")
            if messagebox.askyesno("파인튜닝", "저장된 파일로 OCR 모델 파인튜닝을 진행하시겠습니까?\n(시간이 오래 걸릴 수 있습니다)"):
                messagebox.showinfo("알림", "파인튜닝 기능은 현재 개발 중입니다.")
        except Exception as e:
            messagebox.showerror("저장 오류", f"파일 저장 중 오류가 발생했습니다:\n{e}")

    def on_closing(self):
        print("튜닝 창 닫힘")
        self.destroy()