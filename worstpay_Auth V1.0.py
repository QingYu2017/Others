#!/usr/bin/python
#_*_coding:utf-8 _*_
#Auth:Qing.Yu
#Mail:1753330141@qq.com
# Ver:V1.0
#Date:2018-07-04

import requests as r,json
import cls_worstpay

pkey = cls_worstpay.obj_worstpay()
(identityNumber, merchantNo, mobilePhone, userName)=(pkey.identityNumber, pkey.merchantNo, pkey.mobilePhone, pkey.userName)
pkey.string = "identityNumber=%s&merchantNo=%s&mobilePhone=%s&userName=%s"%(identityNumber, merchantNo, mobilePhone, userName)
pkey.get_pkey()
sign=pkey.get_sign()
url="http://xxx.xxx.xxx.xxx:1xxx2/mapi/gtsxxxxxxxxAutCa"
headers = {"Content-Type": "application/json"}
payload={
        "identityNumber": identityNumber,
        "merchantNo": merchantNo,
        "mobilePhone": mobilePhone,
        "userName": userName,
        "sign": sign,
        }
response=r.post(url,data=json.dumps(payload),headers=headers)        
s=json.loads(response.content)
print(s) 

#调试返回json
#{'errorCode': None, 'errorMsg': None, 'result': {'isAgreement': True, 'isAgreementReason': '恭喜您通过认证'}, 'success': True}
#{'errorCode': None, 'errorMsg': None, 'result': {'isAgreement': False, 'isAgreementReason': '您的证件号未通过验证'}, 'success': True}
#{'errorCode': 'xxx100001', 'errorMsg': '签名认证失败', 'result': None, 'success': False}
