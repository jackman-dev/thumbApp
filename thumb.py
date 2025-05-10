import os
import numpy as np
from PIL import Image, ImageChops
import tkinter as tk
from tkinter import filedialog, messagebox

# 고정값
OUTPUT_FORMAT = "JPEG"

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def remove_white_background_pillow(img):
    gray = img.convert('L')
    np_gray = np.array(gray)
    mask = np_gray < 240
    coords = np.argwhere(mask)
    if coords.size == 0:
        return None
    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0) + 1
    return (x0, y0, x1 - x0, y1 - y0)

def resize_and_pad(image_path, output_path, crop_size, final_width, final_height, background_color):
    try:
        with Image.open(image_path).convert("RGB") as img:
            original_width, original_height = img.size
            product_coords = remove_white_background_pillow(img)
            if product_coords:
                x, y, w, h = product_coords
            else:
                x, y, w, h = 0, 0, original_width, original_height

            img = img.crop((x, y, x + w, y + h))

            if w > h:
                new_width, new_height = crop_size, int(h * (crop_size / w))
            else:
                new_height, new_width = crop_size, int(w * (crop_size / h))

            img = img.resize((new_width, new_height), Image.LANCZOS)

            new_img = Image.new("RGB", (final_width, final_height), background_color)

            # 이미지 위치
            paste_x = (final_width - new_width) // 2
            paste_y = (final_height - new_height) // 2

            # 배경에서 해당 위치 크롭해서 붙여넣기용 영역 준비
            background_crop = new_img.crop((paste_x, paste_y, paste_x + new_width, paste_y + new_height))

            # 다크 효과 적용
            blended = ImageChops.multiply(background_crop, img)
            new_img.paste(blended, (paste_x, paste_y))

            new_img.save(output_path, OUTPUT_FORMAT, quality=95, subsampling=0)
            print(f"✅ 변환 완료: {output_path}")

    except Exception as e:
        print(f"❌ 오류 발생: {image_path} - {e}")

def select_folder_and_process():
    folder_selected = filedialog.askdirectory(title="변환할 이미지 폴더 선택")
    if not folder_selected:
        messagebox.showwarning("폴더 선택", "폴더를 선택하지 않았습니다.")
        return

    try:
        crop_size = int(entry_crop.get())
        final_width = int(entry_final_width.get())
        final_height = int(entry_final_height.get())
        background_hex = entry_bgcolor.get()
        background_color = hex_to_rgb(background_hex)
    except ValueError:
        messagebox.showerror("입력 오류", "숫자 또는 색상 코드를 올바르게 입력하세요.")
        return

    file_list = os.listdir(folder_selected)
    images = [f for f in file_list if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif"))]

    if not images:
        messagebox.showwarning("이미지 없음", "선택한 폴더에 변환할 이미지가 없습니다.")
        return

    for filename in images:
        input_path = os.path.join(folder_selected, filename)
        output_path = os.path.join(folder_selected, os.path.splitext(filename)[0] + ".jpg")
        resize_and_pad(input_path, output_path, crop_size, final_width, final_height, background_color)

    messagebox.showinfo("완료", "🎉 모든 이미지 변환이 완료되었습니다!")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("이미지 변환기")
    root.geometry("340x360")

    label_crop = tk.Label(root, text="제품 영역 크기 (예: 880):")
    label_crop.pack()
    entry_crop = tk.Entry(root)
    entry_crop.insert(0, "880")
    entry_crop.pack()

    label_final_width = tk.Label(root, text="최종 가로 크기 (예: 1000):")
    label_final_width.pack()
    entry_final_width = tk.Entry(root)
    entry_final_width.insert(0, "1000")
    entry_final_width.pack()

    label_final_height = tk.Label(root, text="최종 세로 크기 (예: 1000):")
    label_final_height.pack()
    entry_final_height = tk.Entry(root)
    entry_final_height.insert(0, "1000")
    entry_final_height.pack()

    label_bgcolor = tk.Label(root, text="배경 색상 HEX (예: #ffffff):")
    label_bgcolor.pack()
    entry_bgcolor = tk.Entry(root)
    entry_bgcolor.insert(0, "#ffffff")
    entry_bgcolor.pack()

    button = tk.Button(root, text="폴더 선택하여 변환 시작", command=select_folder_and_process, height=2, width=25)
    button.pack(pady=15)

    root.mainloop()
