from flask import *
from flask_cors import CORS
import pymysql
apiBlueprint=Blueprint("api",__name__)
CORS(apiBlueprint)
db=pymysql.connect(
    host='localhost', 
    port=3306, 
    user='root', 
    passwd='12345678', 
    database='website', 
    charset='utf8'
    )
cursor=db.cursor()

@apiBlueprint.route("/api/attractions")
def api():
    page=request.args.get("page",0, type=int)
    keyword=request.args.get("keyword", None,type=str)
    if keyword ==None:
        sql='''SELECT * FROM `spot` ORDER BY `id` LIMIT %s,%s'''
        cursor.execute(sql,(page*12,12))
        result=cursor.fetchall()
        cursor.execute(sql,((page+1)*12,12))
        resultNext=cursor.fetchall()
        cursor.close
        resultNextLen=len(resultNext)
        data=[]
        for i in result:
            urlsql='''SELECT`url` FROM `url` WHERE `url_id`= %s'''
            cursor.execute(urlsql,(i[0]))
            urlResult=cursor.fetchall()
            cursor.close
            url=[url[0] for url in urlResult]
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
                "images":url
                })
        if resultNextLen==0:
            nextPage=None
            AllData={"nextPage":nextPage,
                "data":data
            }
            return jsonify(AllData)
        else:
            AllData={"nextPage":page+1,
                "data":data
            }
            return jsonify(AllData)

    elif keyword!=None:
        sql='''SELECT `id`,`name`,`category`,`description`,`address`,`transport`,
        `mrt`,`latitude`,`longitude`,`images`FROM `spot` WHERE `name` LIKE %s ORDER BY `id` LIMIT %s,%s'''
        cursor.execute(sql,("%"+keyword+"%",page*12,12))
        seachResult=cursor.fetchall()
        cursor.execute(sql,("%"+keyword+"%",(page+1)*12,12))
        seachResultNext=cursor.fetchall()
        cursor.close
        seachResultNextLen=len(seachResultNext)
        sreachData=[]
        for j in seachResult:
            urlsql='''SELECT`url` FROM `url` WHERE `url_id`= %s'''
            cursor.execute(urlsql,(j[0]))
            urlResult=cursor.fetchall()
            cursor.close
            url=[url[0] for url in urlResult]
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
                "images":url
                })
        if seachResultNextLen == 0:
            nextPage=None
            resultData={"nextPage":nextPage,
                "data":sreachData
            }
            return jsonify(resultData)
        else: 
            resultData={"nextPage":page+1,
            "data":sreachData
            }
            return jsonify(resultData)

    else:
        return {"error": True,"message": "伺服器錯誤，請稍後再試"}

@apiBlueprint.route("/api/attractions/<attractionId>")
def apiID(attractionId):
    sql='''SELECT `id`,`name`,`category`,`description`,`address`,`transport`,
    `mrt`,`latitude`,`longitude`,`images`FROM `spot` WHERE `id`=%s'''
    cursor.execute(sql,(attractionId))
    result=cursor.fetchone()
    cursor.close
    if result==None:
        return {"error": True,"message": "無此編號"}
    elif result!=None:
        urlsql='''SELECT`url` FROM `url` WHERE `url_id`= %s'''
        cursor.execute(urlsql,(result[0]))
        urlResult=cursor.fetchall()
        cursor.close
        url=[url[0] for url in urlResult]
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
                "images":url
             }
        }      
        return jsonify(Data)
    else:
        return {"error": True,"message": "伺服器錯誤，請稍後再試"}