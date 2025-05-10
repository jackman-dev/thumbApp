import os
import numpy as np
from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox

# 설정값
CROP_SIZE = 880
FINAL_SIZE = 1000
BACKGROUND_COLOR = (255, 255, 255)
OUTPUT_FORMAT = "JPEG"


def remove_white_background_pillow(img):
    """Pillow 이미지 객체를 받아서 흰색 배경 제외 제품 영역 감지"""
    gray = img.convert('L')
    np_gray = np.array(gray)

    # 흰색 기준 설정 (240 이상이면 흰색으로 간주)
    mask = np_gray < 240

    coords = np.argwhere(mask)
    if coords.size == 0:
        return None

    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0) + 1

    return (x0, y0, x1 - x0, y1 - y0)


def resize_and_pad(image_path, output_path):
    try:
        with Image.open(image_path) as img:
            original_width, original_height = img.size
            product_coords = remove_white_background_pillow(img)

            if product_coords:
                x, y, w, h = product_coords
            else:
                x, y, w, h = 0, 0, original_width, original_height

            img = img.crop((x, y, x + w, y + h))

            # 비율 유지해서 880 맞추기
            if w > h:
                new_width, new_height = CROP_SIZE, int(h * (CROP_SIZE / w))
            else:
                new_height, new_width = CROP_SIZE, int(w * (CROP_SIZE / h))

            img = img.resize((new_width, new_height), Image.LANCZOS)

            new_img = Image.new("RGB", (FINAL_SIZE, FINAL_SIZE), BACKGROUND_COLOR)
            paste_x = (FINAL_SIZE - new_width) // 2
            paste_y = (FINAL_SIZE - new_height) // 2
            new_img.paste(img, (paste_x, paste_y))

            new_img.save(output_path, OUTPUT_FORMAT)
            print(f"✅ 변환 완료: {output_path}")

    except Exception as e:
        print(f"❌ 오류 발생: {image_path} - {e}")


def select_folder_and_process():
    folder_selected = filedialog.askdirectory(title="변환할 이미지 폴더 선택")
    if not folder_selected:
        messagebox.showwarning("폴더 선택", "폴더를 선택하지 않았습니다.")
        return

    file_list = os.listdir(folder_selected)
    images = [f for f in file_list if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif"))]

    if not images:
        messagebox.showwarning("이미지 없음", "선택한 폴더에 변환할 이미지가 없습니다.")
        return

    for filename in images:
        input_path = os.path.join(folder_selected, filename)
        output_path = os.path.join(folder_selected, os.path.splitext(filename)[0] + ".jpg")
        resize_and_pad(input_path, output_path)

    messagebox.showinfo("완료", "🎉 모든 이미지 변환이 완료되었습니다!")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("이미지 변환기")
    root.geometry("300x150")

    button = tk.Button(root, text="폴더 선택하여 변환 시작", command=select_folder_and_process, height=2, width=25)
    button.pack(expand=True)

    root.mainloop()