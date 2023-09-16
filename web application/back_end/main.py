import cv2
import torch
from typing import Union
import os
from pydantic import BaseModel
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware
import shutil
from PIL import Image
from io import BytesIO
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import adjust
from pathlib import Path

import tempfile

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

# 存储上传的图片的文件夹路径
upload_dir = "uploaded_images"
os.makedirs(upload_dir, exist_ok=True)
adjust_dir = "adjusted_images"
os.makedirs(adjust_dir, exist_ok=True)
# 配置图像文件存储目录
image_directory = "uploaded_images"


#初始加载图片列表
@app.get("/image_list")
async def get_image_list():
    image_list = []

    # 遍历图像文件目录，获取所有图像文件的文件名
    for filename in os.listdir(image_directory):
        if filename.endswith(".png"):  # 这里可以根据需要更改文件扩展名
            image_url = f"/uploadedImages/{filename}"  # 构造图像文件的URL
            image_list.append({"name": filename, 
                               "original_url": image_url,
                               "adjusted_url":f"/adjustedImages/{filename}"})

    # 构建包含图像列表的JSON响应
    response_data = {"images": image_list}
    return JSONResponse(content=response_data)


# 接受上传的图片
@app.post("/upload/")
async def upload_file(file: UploadFile):
    try:
        # 将上传的文件保存到指定目录
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        print("success")

        adjust.adjust("./uploaded_images/","./adjusted_images/",file.filename)

        # 这里可以执行任何你需要的图像处理操作

        return JSONResponse(content={"filename": file.filename}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
# 提供处理后的图片的访问接口
@app.get("/uploadedImages/{image_name}")
async def get_uploaded_image(image_name: str):
    image_path = os.path.join(upload_dir, image_name)
    # print(image_path)
    if os.path.exists(image_path):
        return FileResponse(image_path)
    else:
        return {"error": "Image not found"}

# 提供处理后的图片的访问接口
@app.get("/adjustedImages/{image_name}")
async def get_adjusted_image(image_name: str):
    image_path = os.path.join(adjust_dir, image_name)
    # print(image_path)
    if os.path.exists(image_path):
        return FileResponse(image_path)
    else:
        return {"error": "Image not found"}

@app.get("/image-info/{image_name}")
async def get_image_info(image_name: str):
    # 检查图片是否存在
    original_image_path = f"uploaded_images/{image_name}"  # 假设图片存放在 "images" 文件夹中
    # if not original_image_path.exists():
    #     return JSONResponse(status_code=404, content={"message": "Image not found"})

    # original_img = cv2.imread(original_image_path,cv2.IMREAD_GRAYSCALE)
    original_type,original_shape=adjust.get_orient("./uploaded_images/",image_name)
    adjust_type,adjust_shape=adjust.get_orient("./adjusted_images/",image_name)
    # 获取图片基本信息
    image_info = {
        "name": image_name,
        "original_shape": original_shape,
        "original_orientation":adjust.type_trans(original_type),
        "adjust_shape": adjust_shape,
        "adjust_orientation":adjust.type_trans(adjust_type),
        "original_url": f"/uploadedImages/{image_name}",
        "adjusted_url":f"/adjustedImages/{image_name}",
        # "size": image_path.stat().st_size,  # 图片文件大小
        # "mime_type": "image/jpeg"  # 根据实际情况设置 MIME 类型
    }
    return image_info

@app.delete("/deleteRow/{file_name}")
async def delete_file(file_name: str):
    # 构建文件的完整路径
    file_path1 = os.path.join(upload_dir, file_name)
    file_path2 = os.path.join(adjust_dir, file_name)
    # 检查文件是否存在
    if os.path.exists(file_path1) and os.path.exists(file_path2):
        try:
            # 删除文件
            os.remove(file_path1)
            os.remove(file_path2)
            return {"message": f"File {file_name} deleted successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        raise HTTPException(status_code=404, detail=f"File {file_name} not found")
    
@app.delete("/deleteAll")
async def delete_files():
    try:
        # 使用 shutil.rmtree 删除目录及其下的所有文件
        shutil.rmtree(upload_dir)
        shutil.rmtree(adjust_dir)
        # 创建一个空目录，以便稍后继续使用
        os.makedirs(upload_dir)
        os.makedirs(adjust_dir)
        
        return {"message": f"All files in directory {upload_dir},{adjust_dir} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/downloadAllImages")
async def download_images():
    try:
        # 创建一个临时目录来存放要压缩的图像文件
        with tempfile.TemporaryDirectory() as temp_dir:

            # 创建两个子目录
            sub_dir1 = Path(temp_dir) / upload_dir
            sub_dir2 = Path(temp_dir) / adjust_dir
            sub_dir1.mkdir()
            sub_dir2.mkdir()

            # 遍历第一个目录，复制文件到第一个子目录
            for file_name in Path(upload_dir).iterdir():
                shutil.copy(file_name, sub_dir1)
                # print(type(file_name))

            # 遍历第二个目录，复制文件到第二个子目录
            for file_name in Path(adjust_dir).iterdir():
                shutil.copy(file_name, sub_dir2)

            # 使用 shutil.make_archive 打包整个临时目录为ZIP文件
            shutil.make_archive(temp_dir, 'zip', temp_dir)

            # 获取压缩后的ZIP文件路径
            zip_file_path = f"{temp_dir}.zip"

            # 返回ZIP文件
            return FileResponse(zip_file_path, headers={"Content-Disposition": "attachment; filename=images.zip"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download-image/{image_name}")
async def download_image(image_name: str):
    try:
        # 创建一个临时目录来存放要压缩的图像文件
        with tempfile.TemporaryDirectory() as temp_dir:

            # 创建两个子目录
            sub_dir1 = Path(temp_dir) / upload_dir
            sub_dir2 = Path(temp_dir) / adjust_dir
            sub_dir1.mkdir()
            sub_dir2.mkdir()


            shutil.copy(Path(upload_dir)/image_name, sub_dir1)
            shutil.copy(Path(adjust_dir)/image_name, sub_dir2)

            # 使用 shutil.make_archive 打包整个临时目录为ZIP文件
            shutil.make_archive(temp_dir, 'zip', temp_dir)

            # 获取压缩后的ZIP文件路径
            zip_file_path = f"{temp_dir}.zip"

            # 返回ZIP文件
            return FileResponse(zip_file_path, headers={"Content-Disposition": f"attachment; filename={image_name}.zip"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))