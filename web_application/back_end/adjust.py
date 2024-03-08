import cv2
import os
import MyNet 

import numpy as np
import torch

from PIL import Image, ImageOps
def img_reverse_trans(img,type):
    if type==0: 
        return img
    elif type==1:
        return ImageOps.mirror(img)
    elif type ==2:
        return ImageOps.flip(img)
    elif type ==3:
        return img.rotate(180)
    elif type ==4:
        return img.transpose(Image.Transpose.ROTATE_90).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    elif type ==5:
        return img.rotate(90)  #changed
    elif type ==6:
        return img.rotate(270) #changed
    elif type ==7:
        return img.transpose(Image.Transpose.ROTATE_270).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    else:
        print('error')
        return 0
def type_trans(type):
    if type==0: 
        return '000'
    elif type==1:
        return '001'
    elif type ==2:
        return '010'
    elif type ==3:
        return '011'
    elif type ==4:
        return '100'
    elif type ==5:
        return '101'
    elif type ==6:
        return '110'
    elif type ==7:
        return '111'
    else:
        print('error')
        return 0
    
def get_orient(original_dir,image_name):
    #加载模型
    model=MyNet.MyNet()
    best_model_name="./model/epoch99_loss0.0.pth"
    model.load_state_dict(torch.load(best_model_name, map_location=torch.device('cpu')))

    #准备图片
    #灰度图像
    img_path=os.path.join(original_dir,image_name)
    # print(img_path)
    original_img = cv2.imread(img_path,cv2.IMREAD_GRAYSCALE).transpose(1, 0)   #opencv和pytorch不太匹配，需要进行转换
    
    # original_img = original_img.transpose(1, 0)   #opencv和pytorch不太匹配，需要进行转换
    img=original_img
        # 目标尺寸
    target_height = 480
    target_width = 480
    # 获取原始图像的高度和宽度
    original_width, original_height = img.shape
    # 创建一个目标大小的空白图像
    output_img = np.zeros((target_width, target_height), dtype=img.dtype)
    # 计算尺寸调整后的图像区域
    x_start = max(0, (original_width - target_width) // 2)
    x_end = min(original_width, x_start + target_width)
    y_start = max(0, (original_height - target_height) // 2)
    y_end = min(original_height, y_start + target_height)
    # 裁剪和填充图像数据
    cropped_data = img[x_start:x_end, y_start:y_end]
    output_img[:cropped_data.shape[0], :cropped_data.shape[1]] = cropped_data

    image_array = output_img
    output_img=np.zeros((3,480,480))

    output_img[2,:,:]=image_array

    min_value = 0
    pp=np.percentile(image_array, 80)
    max_value = pp if pp>0 else 1
    # print(60,max_value)
    mapped_min = 0
    mapped_max = 254
    array=image_array
    # 使用clip函数将值限制在指定范围内
    clipped_array = np.clip(array, min_value, max_value)
    # 进行线性映射
    mapped_array = (clipped_array - min_value) * (mapped_max - mapped_min) / (max_value - min_value) + mapped_min
    # 对大于阈值的值进行特殊映射
    mapped_array[array > max_value] = 255
    # 将映射后的值四舍五入为整数
    mapped_array = np.round(mapped_array).astype(int)
    output_img[0,:,:]=mapped_array

    min_value = 0
    max_value = np.percentile(image_array, 95)
    # print(80,max_value)
    mapped_min = 0
    mapped_max = 254
    array=image_array
    # 使用clip函数将值限制在指定范围内
    clipped_array = np.clip(array, min_value, max_value)
    # 进行线性映射
    mapped_array = (clipped_array - min_value) * (mapped_max - mapped_min) / (max_value - min_value) + mapped_min
    # 对大于阈值的值进行特殊映射
    mapped_array[array > max_value] = 255
    # 将映射后的值四舍五入为整数
    mapped_array = np.round(mapped_array).astype(int)
    output_img[1,:,:]=mapped_array

    output_img = output_img.astype('float32') / 255
    input_img = np.expand_dims(output_img, axis=0)
    
    #预测
    output=model(torch.tensor(input_img))

    # print(output)
    # 在第二维度（列）上找到每行的最大值的索引
    max_indices = torch.argmax(output, dim=1)
    # print(max_indices[0].item())
    type=max_indices[0].item()
    # print(original_img)
    return type,original_img.shape


def adjust(original_dir,adjust_dir,image_name):

    #灰度图像
    img_path=os.path.join(original_dir,image_name)
    # print(img_path)
    original_img = cv2.imread(img_path,cv2.IMREAD_GRAYSCALE)
    type,_=get_orient(original_dir,image_name)
    img_reverse_trans(Image.fromarray(original_img),type).save(os.path.join(adjust_dir, image_name))
