# -*- coding: utf-8 -*-
# @Time    : 2025/5/12 10:25
# @Author  : wenyichao
# @File    : V2.0-增加PDF保存功能.py
# @Software: PyCharm 
# @Comment :

# -*- coding: utf-8 -*-
import os
import fitz
from PIL import Image, ImageFilter
import shutil


def sharpen_image(img):
    """ 图像锐化处理 """
    return img.filter(ImageFilter.SHARPEN).filter(ImageFilter.DETAIL)


os.makedirs('temp_pages', exist_ok=True)
os.makedirs('split_images', exist_ok=True)

ZOOM_RATIO = 4.0
TARGET_DPI = 600
ENHANCE_LEVEL = 2
SAVE_QUALITY = 95

pdf_files = [f for f in os.listdir() if f.lower().endswith('.pdf')]

for pdf in pdf_files:
    print(f"\n处理文件: {pdf}")
    try:
        doc = fitz.open(pdf)
        print(f"总页数: {doc.page_count}")

        for pg in range(doc.page_count):
            page = doc[pg]
            matrix = fitz.Matrix(ZOOM_RATIO, ZOOM_RATIO)
            pix = page.get_pixmap(matrix=matrix, dpi=TARGET_DPI, colorspace="RGB")
            img_path = os.path.join('temp_pages', f'{os.path.splitext(pdf)[0]}-{pg:03d}.png')
            pix.save(img_path)
            print(f"\r已转换: {pg + 1}/{doc.page_count}", end="")

        temp_files = [f for f in os.listdir('temp_pages') if f.endswith('.png')]
        for img_file in temp_files:
            img_path = os.path.join('temp_pages', img_file)
            with Image.open(img_path) as img:
                w, h = img.size

                left_img = sharpen_image(img.crop((0, 0, w // 2, h)))
                left_img.save(os.path.join('split_images', f"{os.path.splitext(img_file)[0]}_a.png"),
                              dpi=(TARGET_DPI, TARGET_DPI))

                right_img = sharpen_image(img.crop((w // 2, 0, w, h)))
                right_img.save(os.path.join('split_images', f"{os.path.splitext(img_file)[0]}_b.png"),
                               dpi=(TARGET_DPI, TARGET_DPI))

            print(f"已分割: {img_file}")

        # 生成PDF部分
        base_name = os.path.splitext(pdf)[0]
        split_images = []
        for f in os.listdir('split_images'):
            if f.startswith(f"{base_name}-") and (f.endswith('_a.png') or f.endswith('_b.png')):
                split_images.append(f)

        if split_images:
            split_images.sort()
            images = []
            try:
                for img_file in split_images:
                    img_path = os.path.join('split_images', img_file)
                    images.append(Image.open(img_path))

                output_pdf = f"{base_name}_split.pdf"
                images[0].save(output_pdf, save_all=True, append_images=images[1:], quality=SAVE_QUALITY)
                print(f"已生成PDF文件：{output_pdf}")
            finally:
                for img in images:
                    img.close()

    except Exception as e:
        print(f"处理 {pdf} 时出错: {str(e)}")
    finally:
        if 'doc' in locals():
            doc.close()

shutil.rmtree('temp_pages')
print("\n处理完成！分割结果保存在 split_images 目录")
