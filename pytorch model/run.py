import torch
import torch.backends.cudnn as cudnn
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms
import torch.nn.functional as F
from torch.utils.data import DataLoader
import os
from glob import glob
import pandas as pd
from sklearn.model_selection import train_test_split
import time

import dataset2d
import MyNet 
from validate import validate
from train import train

def main():
    optimizer = 'Adam'  
    lr = 0.003
    weight_decay = 0.0001
    min_lr = 0.00001
    epochs=100

    # print(config['model'])
    model=MyNet.MyNet()
    #加载模型到gpu或cpu
    # model.cuda()

    data_dir="./dataset_trans/C0"
    print(data_dir)

    imageList=os.listdir(data_dir)  #查找匹配指定模式的文件名
    patient_ids = list(set([file_name.split("_")[0] for file_name in imageList]))

    train_patient_ids, remaining_patient_ids = train_test_split(patient_ids, test_size=0.4, random_state=42)
    val_patient_ids, test_patient_ids = train_test_split(remaining_patient_ids, test_size=0.5, random_state=42)
    train_patient_ids=['patient22', 'patient40', 'patient14', 'patient36', 'patient12', 'patient32', 'patient18', 'patient21', 'patient25', 'patient39', 'patient20', 'patient44', 'patient29', 'patient4', 'patient38', 'patient41', 'patient3', 'patient13', 'patient19', 'patient15', 'patient7', 'patient17', 'patient28', 'patient6', 'patient27', 'patient43', 'patient24']
    val_patient_ids=['patient5', 'patient34', 'patient45', 'patient9', 'patient33', 'patient8', 'patient1', 'patient16', 'patient23']
    test_patient_ids=['patient37', 'patient2', 'patient11', 'patient31', 'patient30', 'patient10', 'patient35', 'patient42', 'patient26']

    # print(train_patient_ids)
    # print(val_patient_ids)
    # print(test_patient_ids)
    print(len(train_patient_ids))
    print(len(val_patient_ids))
    print(len(test_patient_ids))

    train_img_ids,val_img_ids, test_img_ids=[],[],[]
    for i in train_patient_ids:
        train_img_ids+=glob(os.path.join(data_dir, f'{i}_*.png'))
    for i in val_patient_ids:
        val_img_ids+=glob(os.path.join(data_dir, f'{i}_*.png'))
    for i in test_patient_ids:
        test_img_ids+=glob(os.path.join(data_dir, f'{i}_*.png'))

    print(len(train_img_ids))
    print(len(val_img_ids))
    print(len(test_img_ids))

    train_data=dataset2d.My2DDataset(root_dir=data_dir,img_ids=train_img_ids)
    val_data=dataset2d.My2DDataset(root_dir=data_dir,img_ids=val_img_ids)
    train_loader=DataLoader(train_data,batch_size=60, shuffle=True, num_workers=4)
    val_loader=DataLoader(val_data,batch_size=60, shuffle=False, num_workers=4)

    
    #参数params和优化器optimizer
    params = filter(lambda p: p.requires_grad, model.parameters())  #过滤模型参数进行，仅保留requires_grad=True 的参数
    if optimizer == 'Adam':
        optimizer = optim.Adam(
            params, lr=lr, weight_decay=weight_decay)
    # elif optimizer == 'SGD':
    #     optimizer = optim.SGD(params, lr=lr, momentum=momentum,
    #                           nesterov=nesterov, weight_decay=weight_decay)
    else:
        raise NotImplementedError("optimizer error!")

    best_loss=99
    #记录loss变化
    for epoch in range(1,epochs+1):
        start_time=time.time()
        
        # train for one epoch
        train_loss=train(train_loader, model, optimizer)
        val_loss= validate(val_loader, model)

        if val_loss<=best_loss:
            best_loss=val_loss
            model_path="./modelC0_v2/"
            os.makedirs(model_path,exist_ok=True)
            torch.save(model.state_dict(),model_path+'epoch{}_loss{}.pth'.format(epoch,val_loss))

        torch.cuda.empty_cache()
        end_time=time.time()
        
        print('Epoch [%d/%d]' % (epoch, epochs),f"train_loss: {train_loss:.4f}, ",end=" ")
        print(f"val_loss: {val_loss:.4f}, ",end=" ")
        print(f"用时{(end_time-start_time):.2f}秒")
main()