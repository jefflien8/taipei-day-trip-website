import datetime
import requests
from flask import *
from flask_cors import CORS
import pymysql
from pymysql import NULL
# from dbutils.pooled_db import PooledDB, SharedDBConnection
# import pymysql.cursors

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
# pool = PooledDB(
#     creator=pymysql,
#     maxconnections=6,
#     mincached=2,
#     maxcached=5,
#     maxshared=3,
#     blocking=True,
#     maxusage=None,
#     setsession=[],
#     ping=0,
#     host='localhost',
#     port=3306,
#     user='root',
#     passwd='123456',
#     database='website', 
#     charset='utf8',
#     Cursor=pymysql.cursors.DictCursor
# )
# conn = pool.connection()

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


@apiBlueprint.route("/api/user", methods=["GET"])
def userGet():
    if (session["name"] == None):
        return jsonify({"data":None})
    else:
        data={
            "data": {
                "id": session["id"],
                "name": session["name"],
                "email": session["email"]
                }
        }
        return jsonify(data)

@apiBlueprint.route("/api/user", methods=["POST"])
def userPost():
    data=request.get_json()
    newname=data["name"]
    newemail=data["email"]
    newpassword=data["password"]

    if (newname=="")|(newemail=="")|(newpassword==""):
        return jsonify({"error": True,"message": "請填寫完整"})

    sql='''SELECT `email` FROM `member` WHERE `email`=%s'''
    cursor.execute(sql,(newemail))
    result=cursor.fetchone()

    if(result !=None):
        return jsonify({"error": True,"message": "Email已經被註冊"})
        
    elif(result==None):
        sql='''INSERT INTO `member`(name,email,password) VALUE(%s,%s,%s)'''
        try:
            cursor.execute(sql,(newname,newemail,newpassword))
            db.commit()
        except:
            db.rollback()
            print('error')
        db.close
        
        return jsonify({"ok": True})
    else:
        return jsonify({"error": True,"message": "伺服器錯誤，請稍後再試"})


@apiBlueprint.route("/api/user", methods=["PATCH"])
def userPatch():
    data=request.get_json()
    email=data["email"]
    password=data["password"]

    sql='''SELECT `id`,`name`,`email` FROM `member` WHERE `email`=%s AND `password`=%s'''
    cursor.execute(sql,(email,password))
    result=cursor.fetchone()

    if(result!=None):
        session["id"]=result[0]
        session["name"]=result[1]
        session["email"]=result[2]
        session.permanent=True
        return jsonify({"ok": True})
    elif(result==None):
        return jsonify({"error": True,"message": "帳號或密碼錯誤"})
    else:
        return jsonify({"error": True,"message": "伺服器錯誤，請稍後再試"})


@apiBlueprint.route("/api/user", methods=["DELETE"])
def userDelete():
    session["id"]=None
    session["name"]=None
    session["email"]=None
    return jsonify({"ok": True})

@apiBlueprint.route("/api/booking", methods=["GET"])
def bookingGet():    
    if(session['name'] ==None):
        return jsonify({"error": True,"message": "未登入，拒絕存取"})

    sql = '''SELECT * FROM `shoppingCart` WHERE `member_id`=%s'''
    cursor.execute(sql,(session['id']))
    result=cursor.fetchone()
    print(result)
    if (result==None):
        return jsonify({"data":None})
    else:
        sql = '''SELECT `name`,`address` FROM `spot` WHERE `id`=%s '''
        cursor.execute(sql,(result[0]))
        attractionResult=cursor.fetchone()

        sql = '''SELECT `url` FROM `url` WHERE `url_id`=%s '''
        cursor.execute(sql,(result[0]))
        imageResult=cursor.fetchone()

        data={
                "data": {
                "attraction": {
                    "id": result[0],
                    "name": attractionResult[0],
                    "address":attractionResult[1] ,
                    "image": imageResult[0]
                },
                "date": result[1],
                "time": result[2],
                "price": int(result[3])
            }
        }
        return jsonify(data)


@apiBlueprint.route("/api/booking", methods=["POST"])
def bookingPost():
    data=request.get_json()
    attractionId=data["attractionId"]
    date=data["date"]
    time=data["time"]
    price=data["price"]

    sql='''INSERT INTO `shoppingCart`(attaction_id,date,time,price,member_id) 
        VALUE(%s,%s,%s,%s,%s)'''
    try:
        cursor.execute(sql,
        (attractionId,date,time,price,session['id']))
        db.commit()
        error=False
    except:
        db.rollback()
        error=True
        print('error')
    db.close

    sql='''UPDATE `shoppingCart` SET attaction_id=%s, date=%s, time=%s, price=%s 
        WHERE member_id=%s'''
    try:
        cursor.execute(sql,
        (attractionId,date,time,price,session['id']))
        db.commit()
        error=False
    except:
        db.rollback()
        error=True
        print('error')
    db.close
    
    if (error==True):
        return jsonify({"error": True,"message": "資料未選取完整！"})
    elif (error==False):
        return jsonify({"ok": True})
    elif (session["id"] == None):
        return jsonify({"error": True,"message": "未登入，拒絕存取"})
    else:
        return jsonify({"error": True,"message": "伺服器錯誤，請稍後再試"})

@apiBlueprint.route("/api/booking", methods=["DELETE"])
def bookingDelete():
    if (session['id'] !=None):
        sql = '''DELETE FROM `shoppingCart` WHERE `member_id`=%s'''
        try:
            cursor.execute(sql,(session['id']))
            db.commit()
        except:
            db.rollback()
            print('error')
        db.close

        return jsonify({"ok": True})
    else:
        return jsonify({"error": True,"message": "未登入，拒絕存取"})

@apiBlueprint.route("/getSession", methods=["GET"])
def getSession():
    print(session.get("name"))
    return jsonify({"name": session.get("name"),"email": session.get("email")})

@apiBlueprint.route("/api/orders", methods=["POST"])
def orders():
    if (session['id'] ==None):
        return jsonify({"error": True,"message": "未登入，拒絕存取"})
    data=request.get_json()
    prime=data["prime"]
    price=data["order"]["price"]

    attraction=data["order"]["trip"]["attraction"]
    attractionId=attraction["id"]
    # attractionName=attraction["name"]
    # attractionAddress=attraction["address"]
    # attractionImage=attraction["image"]

    date=data["order"]["trip"]["date"]
    time=data["order"]["trip"]["time"]

    name=data["order"]["contact"]["name"]
    email=data["order"]["contact"]["email"]
    phone=data["order"]["contact"]["phone"]

    time=datetime.datetime.now()
    order_number=time.strftime("%Y%m%d%H%M%S")

    sql = '''INSERT INTO `order`(number,price,date,time,name,email,phone,status,attaction_id,member_id) 
        VALUE(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
    try:
        cursor.execute(sql,(order_number,price,date,time,name,email,phone,1,attractionId,session['id']))
        db.commit()
    except:
        db.rollback()
        print('error')
    db.close

    postData = {
        "prime": prime,
        "partner_key": "partner_CXf97Wp1tX1bMOfBoykSltkmX70GmbJgG5EFV2HRh0kk9cBWPynfnNeZ",
        "merchant_id": "jefflien8_CTBC",
        "amount": price,
        "details": "Test",
        "order_number": order_number,
        "cardholder": {
            "phone_number": phone,
            "name": name,
            "email": email,
        },
        "remember": False
    }

    headers = {
        "Content-Type": "application/json",
        "x-api-key": "partner_CXf97Wp1tX1bMOfBoykSltkmX70GmbJgG5EFV2HRh0kk9cBWPynfnNeZ"
    }

    res = requests.post('https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime', data=json.dumps(postData), headers=headers)
    resJson = json.loads(res.content)
    print(resJson)

    resData = {
        "data":{
            "number": resJson["order_number"],
            "payment": {
                "status": resJson["status"],
                "message": resJson["msg"]
            }
        }
    }

    if resJson["status"] == 0:
        sql = '''UPDATE `order` SET `status`=%s WHERE `number`=%s'''
        try:
            cursor.execute(sql,(0,resJson["order_number"]))
            db.commit()
        except:
            db.rollback()
            print('errorStatus')
        db.close
        
        sql = '''DELETE FROM `shoppingCart` WHERE `member_id`=%s'''
        try:
            cursor.execute(sql,(session['id']))
            db.commit()
        except:
            db.rollback()
            print('errorDEL')
        db.close

        return jsonify(resData)
    elif resJson["status"] == 1:
        resData = {
            "data":{
                "number": resJson["order_number"],
                "payment": {
                    "status": resJson["status"],
                    "message": resJson["msg"]
                }
            }
        }
        return jsonify(resData)

    else:
        return jsonify({"error": True,"message": "訂單建立失敗！"})



@apiBlueprint.route("/api/orders/<orderNumber>", methods=["GET"])
def ordersNum(orderNumber):
    if(session['name'] ==None):
        return jsonify({"error": True,"message": "未登入，拒絕存取"})

    sql = '''SELECT `number`,`price`,`date`,`time`,`name`,`email`,`phone`,`status`,`attaction_id` FROM order WHERE `number`=%s'''
    cursor.execute(sql,(orderNumber))
    result=cursor.fetchone

    sql = '''SELECT `name`,`address` FROM `spot` WHERE `id`=%s'''
    cursor.execute(sql,(result[8]))
    attractionResult=cursor.fetchone()

    sql = '''SELECT `url` FROM `url` WHERE `url_id`=%s '''
    cursor.execute(sql,(result[8]))
    imageResult=cursor.fetchone()

    if result==None:
            return jsonify({'data':None})
    else:
        orderData={
            "data": {
                "number": result[0],
                "price": result[1],
                "trip": {
                    "attraction": {
                        "id": result[8],
                        "name": attractionResult[0],
                        "address":attractionResult[1] ,
                        "image": imageResult[0]
                    },
                "date": result[2],
                "time": result[3]
                },
                "contact": {
                    "name": result[4],
                    "email": result[5],
                    "phone": result[6]
                },
                "status": result[7]
            }
        }
        return jsonify(orderData)