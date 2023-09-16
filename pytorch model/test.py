import torch
from torch.utils.data import DataLoader
import os
from glob import glob
from sklearn.model_selection import train_test_split
import time
import dataset2d
import MyNet 
from validate import validate


def test(data_dir,best_model_name):
    model=MyNet.MyNet()
    
    model.load_state_dict(torch.load(best_model_name))

    #加载模型到gpu或cpu
    model.cuda()

    # data_dir="./dataset_trans_v2/LGE"
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

    train_img_ids,val_img_ids, test_img_ids=[],[],[]
    for i in train_patient_ids:
        train_img_ids+=glob(os.path.join(data_dir, f'{i}_*.png'))
    # train_img_ids = [os.path.splitext(os.path.basename(p))[0][:-4] for p in train_img_ids]
    for i in val_patient_ids:
        val_img_ids+=glob(os.path.join(data_dir, f'{i}_*.png'))
    # val_img_ids = [os.path.splitext(os.path.basename(p))[0][:-4] for p in val_img_ids]
    for i in test_patient_ids:
        test_img_ids+=glob(os.path.join(data_dir, f'{i}_*.png'))
    # test_img_ids = [os.path.splitext(os.path.basename(p))[0][:-4] for p in test_img_ids]

    # train_img_ids=[f"{i}_C0_slice_3_trans_6.png"]



    test_data=dataset2d.My2DDataset(root_dir=data_dir,img_ids=test_img_ids)
    test_loader=DataLoader(test_data,batch_size=20, shuffle=False, num_workers=0)
    
    start_time=time.time()
    test_loss= validate(test_loader, model)
  
    torch.cuda.empty_cache()
    end_time=time.time()


    print(f"test_loss: {test_loss:.4f}, ",end=" ")
    print(f"用时{(end_time-start_time):.2f}秒")

die_list=['./dataset_trans/T2','./dataset_trans/LGE','./dataset_trans/C0']
best_model_name="./modelC0_v2/epoch99_loss0.0.pth"
for i in die_list:
    test(i,best_model_name)
