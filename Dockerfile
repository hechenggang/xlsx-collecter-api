FROM python:3.9-alpine



WORKDIR /

# 修改源
RUN echo "http://mirrors.aliyun.com/alpine/latest-stable/main/" > /etc/apk/repositories && \
    echo "http://mirrors.aliyun.com/alpine/latest-stable/community/" >> /etc/apk/repositories
 
# 安装需要的软件
RUN apk update && \
    apk add --no-cache gcc g++ libc-dev libffi-dev


# COPY ./* /code/
COPY ./requirements.txt /requirements.txt

RUN pip install -i https://pypi.douban.com/simple/ -U pip 
RUN pip config set global.index-url https://pypi.douban.com/simple/
RUN pip install --no-cache-dir --upgrade -r /requirements.txt

EXPOSE 8080 

# ENV PYTHONPATH /code
# VOLUME [ "${pwd}:/code" ]
WORKDIR /code
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]


