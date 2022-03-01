import json
import pymysql
with open('data/taipei-attractions.json', encoding="utf-8") as f:
    data=json.load(f)

db=pymysql.connect(
    host='localhost', 
    port=3306, 
    user='root', 
    passwd='123456', 
    db='website', 
    charset='utf8'
    )
cursor=db.cursor()

list=data["result"]["results"]
# id="_id"
# name="stitle"
# category="CAT2"
# description="xbody"
# address="address"
# transport="info"
# mrt="MRT"
# latitude="latitude"
# longitude="longitude"
# image="file"   

# for j in list:
#     images=j['file'].lower().split('https')
#     for i in images:
#         if i[-4:]=='.jpg':
#             print('https'+i)

sql='''INSERT INTO `spot`(id,name,category,description,address,transport,mrt,latitude,longitude,images) 
VALUE(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
for i in list:
    try:
        cursor.execute(sql,(
            i["RowNumber"],i["stitle"],i["CAT2"],
            i["xbody"],i["address"],i["info"],
            i["MRT"],i["latitude"],i["longitude"],i["file"])
        )
        db.commit()
    except:
        db.rollback()
        print(i["RowNumber"])
    
