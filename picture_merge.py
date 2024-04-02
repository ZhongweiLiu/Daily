from PIL import Image
import os

# 设置输入图片文件夹和输出文件夹的路径
input_folder = r'E:\桌面\3'
output_folder = r'E:\桌面\jpg'

# 确保输出文件夹存在
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 获取文件夹中的所有图片文件
image_files = [f for f in os.listdir(input_folder) if f.endswith('.jpg')]

# 按文件名排序图片文件
image_files.sort()


# 初始化新图的位置
x_offset = 0
y_offset = 0

for k in range(0, len(image_files), 9):
    # 获取第一张图片的宽度和高度
    set_image_path = os.path.join(input_folder, image_files[k])
    with Image.open(set_image_path) as first_image:
        image_width, image_height = first_image.size

    # 定义每个新图的宽度和高度
    new_image_width = 3 * image_width
    new_image_height = 3 * image_height


    # 创建一个新图
    new_image = Image.new('RGB', (new_image_width, new_image_height))

    for i in range(0, len(image_files), 9):
        x_offset = 0  # 重置 x_offset
        y_offset = 0  # 重置 y_offset

        for j in range(9):
            if i + j < len(image_files):
                image_path = os.path.join(input_folder, image_files[i + j])
                img = Image.open(image_path)
                # 将图像添加到新图时，指定坐标
                new_image.paste(img, (x_offset, y_offset))
                x_offset += image_width

                if x_offset == new_image_width:
                    x_offset = 0
                    y_offset += image_height

        # 保存新图
        new_image_name = f'new_image_{i // 9}.jpg'
        new_image.save(os.path.join(output_folder, new_image_name))

    # 保存新图
    new_image_name = f'new_image_{i // 9}.jpg'
    new_image.save(os.path.join(output_folder, new_image_name))

# 输出处理完成的消息
print(f'已成功创建{len(image_files) // 9}张新图。')
