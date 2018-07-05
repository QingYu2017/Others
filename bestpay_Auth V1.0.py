import requests as r,json
import cls_bestpay

pkey = cls_bestpay.obj_bestpay()
(identityNumber, merchantNo, mobilePhone, userName)=(pkey.identityNumber, pkey.merchantNo, pkey.mobilePhone, pkey.userName)
pkey.string = "identityNumber=%s&merchantNo=%s&mobilePhone=%s&userName=%s"%(identityNumber, merchantNo, mobilePhone, userName)
pkey.get_pkey()
sign=pkey.get_sign()
url="http://116.xxx.xxx.160:18002/mapi/gtsIdentityAutCa"
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

