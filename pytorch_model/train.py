import torch
import torch.nn.functional as F
import os
import pandas as pd

def train( train_loader, model, optimizer):

    lossList,channel_loss_list=[],[]
    model.train()

    for data in train_loader:

        inputs=data[0]  #[batch_num,?,channel,480,480]
        labels=data[1]  #[batch_num,?,class_num,288,288]
        # print(inputs.shape) 
        # print(labels.shape)
        
        inputs, labels = inputs.cuda(), labels.cuda()
        inputs = inputs.to(torch.float32)  # 将输入数据转换为float32类型
      
        # output = F.softmax(model(inputs),dim=1)
        output = model(inputs)

        # 计算损失
        loss = F.cross_entropy(output, labels)
        # 计算交叉熵损失
        loss_per_sample = F.cross_entropy(output, labels, reduction='none')

        lossList+=loss_per_sample.clone().cpu().detach().numpy().tolist()

        # compute gradient and do optimizing step
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    return sum(lossList)/len(lossList)



    

    
