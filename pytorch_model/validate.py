import torch
import torch.nn.functional as F
import os
import pandas as pd



def validate( val_loader, model):

    lossList,channel_loss_list=[],[]
    total_num,right_num=0,0
    model.eval()
    with torch.no_grad():
        for data in val_loader:
            inputs=data[0]  #[batch_num,?,channel,480,480]
            labels=data[1]  #[batch_num,?,class_num,288,288]
            # print(inputs.shape) 
            # print(labels.shape)
            
            inputs, labels = inputs.cuda(), labels.cuda()
            inputs = inputs.to(torch.float32)  # 将输入数据转换为float32类型
        
            # output = F.softmax(model(inputs),dim=1)
            output = model(inputs)

            
            # 在第二维度（列）上找到每行的最大值的索引
            max_indices = torch.argmax(output, dim=1)

            # 创建一个与input_tensor相同形状的零张量
            output_tensor = torch.zeros_like(output)

            # 使用max_indices将每行的最大值位置设置为1
            output_tensor[range(output.size(0)), max_indices] = 1
            
            output=output_tensor.cuda()

            # 检查两个张量的形状是否相同
            if output.shape != labels.shape:
                print("张量形状不相同")
            else:
                # 通过逐行比较两个张量来检查相等的行数
                equal_rows = (output == labels).all(dim=1)
                
                # 计算相等行的数量
                num_equal_rows = equal_rows.sum().item()
                
                right_num+=num_equal_rows
                total_num+=output.shape[0]

            # # 计算损失
            # loss = F.cross_entropy(output, labels)
            # # 计算交叉熵损失
            # loss_per_sample = F.cross_entropy(output, labels, reduction='none')

            # lossList+=loss_per_sample.clone().cpu().detach().numpy().tolist()


    # print(right_num,total_num)
    return 1-right_num/total_num



    

    
