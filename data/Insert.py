import json
import pymysql
with open('~/repo/data/taipei-attractions.json', encoding="utf-8") as f:
    data=json.load(f)

db=pymysql.connect(
    host='localhost', 
    port=3306, 
    user='root', 
    passwd='12345678', 
    db='website', 
    charset='utf8'
    )
cursor=db.cursor()

list=data["result"]["results"]

sql='''INSERT INTO `URL`(url_id,url) VALUE(%s,%s)'''
for j in list:
    images=j['file'].lower().split('https') 
    for i in images:
        if i[-4:]=='.jpg':
            url='https'+i
            try:
                cursor.execute(sql,(j["RowNumber"],url))
                db.commit()
            except:
                db.rollback()
                print(j["RowNumber"])
                

sql='''INSERT INTO `spot`(id,name,category,description,address,transport,mrt,latitude,longitude,images) 
VALUE(%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
for i in list:
    try:
        cursor.execute(sql,(
            i["RowNumber"],i["stitle"],i["CAT2"],
            i["xbody"],i["address"],i["info"],
            i["MRT"],i["latitude"],i["longitude"],)
        )
        db.commit()
    except:
        db.rollback()
        print(i["RowNumber"])
    
