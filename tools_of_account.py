# coding:utf-8


from time import time as timestamp

import requests


# 用户校验
CODE_CACHE = {}
def code_online_check(user_id,user_key,split_string):
    # 通过 account.imhcg.cn 的 api 来校验账户
    try:
        resp = requests.get("https://account.imhcg.cn/api/user?code={}".format("{}{}{}".format(user_id,split_string,user_key))).json()
        if resp["code"] == 200:
            CODE_CACHE[user_id] = {"user_key":user_key,"ts":round(timestamp())}
            return 200,resp["user"]["user_email"]
        else: 
            return resp["code"],resp["errmsg"]
    except Exception as e:
        return 500,str(e)

def code_check(code):
    split_string = "-"
    if len(code) != 129: 
        return 400,"@code 长度不正确"
    if split_string not in code:
        return 400,"@code 格式不正确"
    user_id, user_key = code.split(split_string)
    if user_id in CODE_CACHE:
        # 仅在用户键对应缓存存在，且缓存的密钥正确，且缓存时间未过期情况下使用缓存
        if user_key == CODE_CACHE[user_id]["user_key"]:
            if (round(timestamp()) - CODE_CACHE[user_id]["ts"]) < 60*60:
                return 200,[user_id,user_key]
    # 缓存无法使用时，使用账户系统api进行校验
    status,result = code_online_check(user_id,user_key,split_string)
    if status == 200:
        return 200,[user_id,user_key]
    else: 
        return 500,result
