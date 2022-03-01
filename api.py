
from flask import *
import pymysql
apiBlueprint=Blueprint("api",__name__)
db=pymysql.connect(
    host='localhost', 
    port=3306, 
    user='root', 
    passwd='123456', 
    db='website', 
    charset='utf8'
    )
cursor=db.cursor()

@apiBlueprint.route("/api/attractions")
def api():
    page=request.args.get("page",0, type=int)
    keyword=request.args.get("keyword", None,type=str)
    if keyword ==None:
        sql='''SELECT `id`,`name`,`category`,`description`,`address`,`transport`,
            `mrt`,`latitude`,`longitude`,`images`FROM `spot` ORDER BY `id` LIMIT %s,%s'''
        cursor.execute(sql,(page*12,page+12))
        result=cursor.fetchall()
        data=[]
        for i in result:
            data.append({
                "id":i[0],
                "name":i[1],
                "category":i[2],
                "description":i[3],
                "address":i[4],
                "transport":i[5],
                "mrt":i[6],
                "latitude":i[7],
                "longitude":i[8],
                "images":[
                    i[9]
                    ]
                })

        AllData={"nextPage":page+1,
            "data":data
        }
        return jsonify(AllData)

    elif keyword!=None:
        sql='''SELECT `id`,`name`,`category`,`description`,`address`,`transport`,
        `mrt`,`latitude`,`longitude`,`images`FROM `spot` WHERE `name` LIKE %s ORDER BY `id` LIMIT %s,%s'''
        cursor.execute(sql,("%"+keyword+"%",page*12,page+12))
        seachResult=cursor.fetchall()
        sreachData=[]
        for j in seachResult:
            sreachData.append({
                "id":j[0],
                "name":j[1],
                "category":j[2],
                "description":j[3],
                "address":j[4],
                "transport":j[5],
                "mrt":j[6],
                "latitude":j[7],
                "longitude":j[8],
                "images":[
                    j[9]
                    ]
                })
        resultData={"nextPage":page+1,
            "data":sreachData
        }
        return jsonify(resultData)


@apiBlueprint.route("/api/attractions/<attractionId>")
def apiID(attractionId):
    sql='''SELECT `id`,`name`,`category`,`description`,`address`,`transport`,
    `mrt`,`latitude`,`longitude`,`images`FROM `spot` WHERE `id`=%s'''
    cursor.execute(sql,(attractionId))
    result=cursor.fetchone()
    if result==None:
        return {"error": True,"message": "無此編號"}
    else:
        Data={
            "data": {
                "id": result[0],
                "name": result[1],
                "category": result[2],
                "description": result[3],
                "address": result[4],
                "transport": result[5],
                "mrt": result[6],
                "latitude": result[7],
                "longitude":result[8],
                "images": [
                    result[9]
                    ]
             }
        }      
        return jsonify(Data)