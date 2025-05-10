import os
import cv2
import numpy as np
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox

# 흰색 픽셀 감지 기준
WHITE_THRESHOLD = 240
WHITE_MARGIN_RATIO = 0.95  

# 글로벌 변수로 선택된 폴더를 저장
base_folder = ""
destination_folder = ""

def has_full_white_margin(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return False
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, WHITE_THRESHOLD, 255, cv2.THRESH_BINARY)

    rows, cols = binary.shape
    top_white_ratio = np.mean(binary[0, :] == 255)
    bottom_white_ratio = np.mean(binary[-1, :] == 255)
    left_white_ratio = np.mean(binary[:, 0] == 255)
    right_white_ratio = np.mean(binary[:, -1] == 255)

    return (top_white_ratio >= WHITE_MARGIN_RATIO and bottom_white_ratio >= WHITE_MARGIN_RATIO and 
            left_white_ratio >= WHITE_MARGIN_RATIO and right_white_ratio >= WHITE_MARGIN_RATIO)

def get_final_subfolders(root_folder):
    final_folders = []
    for root, dirs, _ in os.walk(root_folder):
        if not dirs:
            final_folders.append(root)
    return final_folders

def rename_and_copy_images(base_folder, destination_folder):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    final_folders = get_final_subfolders(base_folder)

    for folder in final_folders:
        parent_folder_name = os.path.basename(folder)
        count = 1

        for filename in sorted(os.listdir(folder)):
            if filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif")):
                image_path = os.path.join(folder, filename)

                if has_full_white_margin(image_path):
                    ext = os.path.splitext(filename)[1]
                    new_filename = f"{parent_folder_name}-{count}{ext}"
                    new_path = os.path.join(folder, new_filename)

                    os.rename(image_path, new_path)
                    print(f"✅ 파일명 변경: {filename} → {new_filename}")

                    destination_path = os.path.join(destination_folder, new_filename)
                    shutil.copy2(new_path, destination_path)
                    print(f"📂 파일 복사: {new_filename} → {destination_folder}")

                    count += 1

def select_input_folder():
    global base_folder
    base_folder = filedialog.askdirectory(title="Input 폴더 선택")
    input_label.config(text=f"Input: {base_folder}")

def select_output_folder():
    global destination_folder
    destination_folder = filedialog.askdirectory(title="Output 폴더 선택")
    output_label.config(text=f"Output: {destination_folder}")

def start_processing():
    if base_folder and destination_folder:
        rename_and_copy_images(base_folder, destination_folder)
        messagebox.showinfo("완료", "파일명을 변경하고 복사했습니다.\n프로그램을 종료합니다.")
        root.quit()
    else:
        messagebox.showerror("오류", "Input과 Output 폴더를 모두 선택하세요.")

# 메인 윈도우 생성
root = tk.Tk()
root.title("Rename and Copy Tool")
root.geometry("500x300")

# 버튼 & 라벨 배치
tk.Button(root, text="Input 폴더 선택", command=select_input_folder, width=30, height=2).pack(pady=10)
input_label = tk.Label(root, text="Input: (선택되지 않음)")
input_label.pack()

tk.Button(root, text="Output 폴더 선택", command=select_output_folder, width=30, height=2).pack(pady=10)
output_label = tk.Label(root, text="Output: (선택되지 않음)")
output_label.pack()

tk.Button(root, text="실행", command=start_processing, width=30, height=2, bg="lightblue").pack(pady=20)

# 창 실행
root.mainloop()