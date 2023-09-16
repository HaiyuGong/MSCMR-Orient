import numpy as np
import pandas as pd
from torch.utils.data import Dataset
import torch
import os
import cv2


class My2DDataset(Dataset):
    def __init__(self, root_dir, img_ids, with_label = True,transform=None):
        self.root_dir   = root_dir
        self.img_ids=img_ids
        self.with_label = with_label
        self.transform  = transform

    def __len__(self):
        return len(self.img_ids)

    def __getitem__(self, idx):
        img_id = self.img_ids[idx]
        # print(img_id)

        #灰度图像
        img = cv2.imread(img_id,cv2.IMREAD_GRAYSCALE)
        img = img.transpose(1, 0)   #opencv和pytorch不太匹配，需要进行转换

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



        type=int(img_id[-5])
        lab=np.zeros(8)
        lab[type]=1

        output_img = output_img.astype('float32') / 255
        
        # print(111)
        # output_img = np.expand_dims(output_img, axis=0)
        # print(np.unique(output_img))
        return output_img, lab, {'img_id': img_id}
    