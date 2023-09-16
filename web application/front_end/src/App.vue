<script setup>
import { Delete, Search, Upload,Download } from '@element-plus/icons-vue'
</script>
<template style="width: auto ">
  <div class="common-layout" style="width: 100vw ;height: 100vh">
    <el-container  >
      <el-header style="height: 10vh; display: flex; align-items: center;">
        <div class="title" style="margin: 0 auto;">Orientation Adjust Tool</div>
      </el-header>
      <el-container style="height: 85vh">
<!--        left-->
        <el-aside width="25vw " style="padding: 3px" >
            <el-header style="height: 70px; display: flex; align-items: center;">
              <div  style="margin: 0 auto;font-size: large">Image List</div>
            </el-header>

            <el-main style="padding: 5px ;align-content: center">
              <el-row style="margin-bottom: 10px;padding-left: 20px">
                <el-button type="primary" @click="openFileInput">
                  <el-icon class="el-icon--right"><Upload /></el-icon>Upload</el-button>
                <el-button type="success" :icon="Download" @click.prevent="downloadAllImages()">Download All</el-button>
                <el-button type="danger" :icon="Delete" @click.prevent="deleteAll()">Delete All</el-button>
                <div>
                  <input type="file" ref="fileInput" @change="handleFileUpload" accept="image/*" style="display: none" />
                </div>
              </el-row>

            <el-table :data="imageList" style="width: 100%">
              <!-- 添加每张图片的列 -->
              <el-table-column label="Image" width="65">
                <template v-slot="{ row }">
                  <img :src="`api/${row.original_url}`" alt="Image" style="max-width: 50px; max-height: 50px;" />
                </template>
              </el-table-column>
              <el-table-column label="Name" prop="name" width="200"></el-table-column>
              <el-table-column fixed="right" label="Operations" width="120">
                <template #default="scope">
                  <el-button-group>
                    <el-button :icon="Search" circle @click.prevent="showRow(scope.$index)"/>
                    <el-button type="success" :icon="Download" circle @click.prevent="downloadRow(scope.$index)" />
                    <el-button type="danger" :icon="Delete" circle @click.prevent="deleteRow(scope.$index)" />
                  </el-button-group>
                </template>
              </el-table-column>
            </el-table>
            </el-main>
        </el-aside>
<!--        center-->
        <el-main style="width: 55vw;padding: 0px ">
          <el-container>
            <el-aside style="width: 27.5vw">
              <el-container>
                <el-header style="height: 70px; display: flex; align-items: center; background-color: #E9EEF3">
                  <div  style="margin: 0 auto;font-size: large">Original Image</div>
                </el-header>
                <el-main style="height: 450px;padding: 5px">
                  <el-image
                      v-if="basicInformation.original_url"
                      :src="`/api/${basicInformation.original_url}`"
                      alt="Original Image"
                      style="width: 400px; height: 400px; margin-bottom: -150px"
                  ></el-image>
                </el-main>
              </el-container>
            </el-aside>
            <el-aside style="width: 27.5vw">
              <el-container>
                <el-header style="height: 70px; display: flex; align-items: center; background-color: #E9EEF3">
                  <div  style="margin: 0 auto;font-size: large">Adjusted Image</div>
                </el-header>
                <el-main style="height: 450px; padding: 5px">
                  <el-image
                      v-if="basicInformation.adjusted_url"
                      :src="`/api/${basicInformation.adjusted_url}`"
                      alt="Adjusted Image"
                      style="width: 400px; height: 400px; margin-bottom: -150px"
                  ></el-image>
                </el-main>
              </el-container>
            </el-aside>
          </el-container>
          <el-descriptions :title="`Image Name: ${basicInformation.name}`" :column="4" border  class="custom-descriptions"
          style="margin: 5px">
            <el-descriptions-item label="Original Shape">{{basicInformation.original_shape}}</el-descriptions-item>
            <el-descriptions-item label="Original Orientation">{{basicInformation.original_orientation}}</el-descriptions-item>
            <el-descriptions-item label="Adjusted Shape">{{basicInformation.adjust_shape}}</el-descriptions-item>
            <el-descriptions-item label="Adjusted Orientation">{{basicInformation.adjust_orientation}}</el-descriptions-item>
          </el-descriptions>

        </el-main>
<!--        right-->
        <el-aside width="20vw" style="padding: 3px">
          <el-header style="height: 70px; display: flex; align-items: center;">
            <div  style="margin: 0 auto;font-size: large">Instruction</div>
          </el-header>
<!--          Instruction-->
          <el-main style="padding: 5px ;align-content: center">
            <el-image  :src="'./assets/instruction.png'" alt="Original Image" style="margin-top: 10px"

          ></el-image>
          </el-main>
        </el-aside>
<!--        footer-->
      </el-container>
      <el-footer style="height: 5vh">
      </el-footer>
    </el-container>
  </div>
</template>
<script >

import axios from 'axios'

import { ref } from 'vue'
import dayjs from 'dayjs'
export default {
  data() {
    return {
      imageList: [], // 存储图像信息的数组
      user: null,
      originalImageUrl: null,
      adjustImageUrl: null,
      src: 'https://cube.elemecdn.com/6/94/4d3ea53c084bad6931a56d5158a48jpeg.jpeg',
      basicInformation:{},
    }
  },
  created() {
    // 在组件创建时发送异步请求获取图像信息
    this.fetchImageList();
  },

  methods: {

    async fetchImageList() {
      try {
        const response = await axios.get("/api/image_list"); // 发送GET请求获取图像列表
        this.imageList = response.data.images; // 将图像列表保存到组件的数据属性中
        const  response2=await  axios.get("/api/image-info/"+this.imageList[0]["name"])
        this.basicInformation=response2.data
      } catch (error) {
        console.error("Error fetching image list:", error);
      }
    },

    async  showRow(index) {
      const  response=await  axios.get("/api/image-info/"+this.imageList[index].name)
      this.basicInformation=response.data
    },

    async  deleteRow(index) {
      console.log(index)
      console.log(this.imageList[index].name);
      await axios.delete("/api/deleteRow/"+this.imageList[index].name);
      await this.fetchImageList();
      // this.tableData.splice(index, 1);
    },
    async deleteAll(){
      await axios.delete("/api/deleteAll");
      await this.fetchImageList();
      this.basicInformation={};
    },

    openFileInput() {
      // 触发隐藏的文件输入框
      this.$refs.fileInput.click();
    },
    async handleFileUpload(event) {
      const file = event.target.files[0];
      if (file) {
        const formData = new FormData();
        formData.append("file", file);

        try {
          const response = await fetch("/api/upload/", {
            method: "POST",
            body: formData,
          });
          if (response.ok) {
            const data = await response.json();
            await this.fetchImageList();
            const  response2=await  axios.get("/api/image-info/"+data.filename)
            this.basicInformation=response2.data

          } else {
            console.error("Image upload failed.");
          }
        } catch (error) {
          console.error("Error:", error);
        }
      }
    },
    async downloadAllImages() {
      try {
        const response = await axios.get('/api/downloadAllImages', {
          responseType: 'blob', // 设置响应类型为二进制数据
        });

        // 创建一个Blob对象
        const blob = new Blob([response.data], { type: 'application/zip' });

        // 创建一个临时的URL，用于下载
        const url = window.URL.createObjectURL(blob);

        // 创建一个<a>元素并模拟点击以触发下载
        const a = document.createElement('a');
        a.href = url;
        a.download = 'all_mages.zip'; // 下载的文件名
        a.click();
        // 释放临时URL
        window.URL.revokeObjectURL(url);
      } catch (error) {
        console.error('Error downloading images', error);
      }
    },
    async  downloadRow(index) {
      const image_name=this.imageList[index].name
      try {
        const response = await axios.get("/api/download-image/"+image_name, {
          responseType: 'blob', // 设置响应类型为二进制数据
        });

        // 创建一个Blob对象
        const blob = new Blob([response.data], { type: 'application/zip' });

        // 创建一个临时的URL，用于下载
        const url = window.URL.createObjectURL(blob);

        // 创建一个<a>元素并模拟点击以触发下载
        const a = document.createElement('a');
        a.href = url;
        a.download = image_name+'.zip'; // 下载的文件名
        a.click();
        // 释放临时URL
        window.URL.revokeObjectURL(url);
      } catch (error) {
        console.error('Error downloading images', error);
      }

    },

  }
}
</script>

<style scoped>

.el-row {
  margin-bottom: 20px;
}
.el-row:last-child {
  margin-bottom: 0;
}
.el-col {
  border-radius: 4px;
}

.grid-content {
  border-radius: 4px;
  min-height: 36px;
}

.custom-descriptions {
  height: 10px; /* 设置标题的高度 */
  line-height: 50px; /* 让标题的文本垂直居中 */
  margin-left: 30px;
}

.my-label {
  background: var(--el-color-success-light-9);
}
.my-content {
  background: var(--el-color-danger-light-9);
}

.title {
  font-size: 24px; /* 设置字体大小 */
  font-weight: bold; /* 加粗字体 */
  color: brown; /* 设置字体颜色 */
  /* 其他字体样式属性，如字体样式、行高等，根据需要添加 */
}


.el-header, .el-footer {
  background-color: #B3C0D1;
  color: #333;
  text-align: center;
  line-height: 60px;
}

.el-aside {
  background-color: #D3DCE6;
  color: #181818;
  text-align: center;
  line-height: 200px;
}

.el-main {
  background-color: #E9EEF3;
  color: #333;
  text-align: center;
  line-height: 160px;
}

body > .el-container {
  margin-bottom: 40px;
}

.el-container:nth-child(5) .el-aside,
.el-container:nth-child(6) .el-aside {
  line-height: 260px;
}

.el-container:nth-child(7)  {
  line-height: 320px;
}

</style>
