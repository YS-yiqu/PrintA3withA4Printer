# -*- coding: utf-8 -*-
import os
import fitz
from PIL import Image, ImageFilter  # 新增ImageFilter
import shutil


# 新增锐化函数
def sharpen_image(img):
    """ 图像锐化处理 """
    return img.filter(ImageFilter.SHARPEN).filter(ImageFilter.DETAIL)


# 创建输出目录
os.makedirs('temp_pages', exist_ok=True)
os.makedirs('split_images', exist_ok=True)

# ============ 核心优化配置 ============
ZOOM_RATIO = 4.0    # 提升至4倍缩放 (测试范围3.0-8.0)
TARGET_DPI = 600    # 输出分辨率升级 (测试范围300-1200)
ENHANCE_LEVEL = 2    # 锐化强度 (1-3)
SAVE_QUALITY = 95    # 保存质量 (PNG:0-9越小越好, JPG:1-95越大越好)
# ====================================


pdf_files = [f for f in os.listdir() if f.lower().endswith('.pdf')]

for pdf in pdf_files:
    print(f"\n处理文件: {pdf}")
    try:
        doc = fitz.open(pdf)
        print(f"总页数: {doc.page_count}")

        # ============ PDF转图片部分 ============
        for pg in range(doc.page_count):
            page = doc[pg]
            # 使用优化后的渲染参数
            matrix = fitz.Matrix(ZOOM_RATIO, ZOOM_RATIO)
            pix = page.get_pixmap(
                matrix=matrix,
                dpi=TARGET_DPI,
                colorspace="RGB"
            )
            img_path = os.path.join('temp_pages', f'{os.path.splitext(pdf)[0]}-{pg:03d}.png')
            pix.save(img_path)
            print(f"\r已转换: {pg + 1}/{doc.page_count}", end="")
        # =====================================

        # ============ 图片分割部分 ============
        temp_files = [f for f in os.listdir('temp_pages') if f.endswith('.png')]
        for img_file in temp_files:
            img_path = os.path.join('temp_pages', img_file)
            with Image.open(img_path) as img:
                w, h = img.size

                # 左半部分（新增锐化处理）
                left_img = sharpen_image(img.crop((0, 0, w // 2, h)))  # 添加在这里
                left_img.save(os.path.join('split_images', f"{os.path.splitext(img_file)[0]}_a.png"))

                # 右半部分（新增锐化处理）
                right_img = sharpen_image(img.crop((w // 2, 0, w, h)))  # 添加在这里
                right_img.save(os.path.join('split_images', f"{os.path.splitext(img_file)[0]}_b.png"))

            print(f"已分割: {img_file}")
        # =====================================

    except Exception as e:
        print(f"处理 {pdf} 时出错: {str(e)}")
    finally:
        if 'doc' in locals():
            doc.close()

# 清理临时文件
shutil.rmtree('temp_pages')
print("\n处理完成！分割结果保存在 split_images 目录")
