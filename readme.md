### 通过上传 xlsx 表格模板来生成一个可以分享的采集表单。

1. 上传采集标题和 .xlsx 到服务端，解析为 json 对象，解析出需要采集的字段标签[input:string,input:int,input:float]，初始化一个数据表用来存放采集数据