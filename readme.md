### ### 这是简单表单的后端
通过上传 xlsx 表格模板来生成一个带简单用户管理的可以分享的 Web 采集表单，并可以原格式导出带有数据的 xlsx 表格文件。

[示例地址](https://xlsx-collecter.imhcg.cn)


---


### 可以通过 Docker 快速部署

```
git clone https://github.com/hechenggang/xlsx-collecter-api.git

docker build -t xlsx_collecter:v1 .

docker run -it -d -p 8085:8080 -v this_dir:/code xlsx_collecter:v1
```

