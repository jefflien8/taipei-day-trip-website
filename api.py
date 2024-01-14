import datetime
import requests
from flask import *
from flask_cors import CORS
import pymysql
from pymysql import NULL
from sqlalchemy import create_engine

apiBlueprint=Blueprint("api",__name__)
CORS(apiBlueprint)

engine = create_engine(
    'mysql+pymysql://root:12345678@localhost/website', pool_size=20, max_overflow=0)

@apiBlueprint.route("/api/attractions")
def api():
    page=request.args.get("page",0, type=int)
    keyword=request.args.get("keyword", None,type=str)
    if keyword ==None:
        sql='''SELECT * FROM `spot` ORDER BY `id` LIMIT %s,%s'''

        con1 = engine.connect()
        rows = con1.execute(sql,(page*12,12))
        result = rows.fetchall()
        row2 = con1.execute(sql,((page+1)*12,12))
        resultNext = row2.fetchall()
        con1.close()
        resultNextLen=len(resultNext)

        data=[]
        for i in result:
            urlsql='''SELECT`url` FROM `url` WHERE `url_id`= %s'''
            
            con1 = engine.connect()
            rows = con1.execute(urlsql,(i[0]))
            urlResult = rows.fetchall()
            con1.close()
            
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
        
        con1 = engine.connect()
        cursor = con1.execute(sql,(("%"+keyword+"%"),page*12,12))
        seachResult = cursor.fetchall()
        cursor = con1.execute(sql,(("%"+keyword+"%"),(page+1)*12,12))
        seachResultNext=cursor.fetchall()
        con1.close()
        seachResultNextLen=len(seachResultNext)
        sreachData=[]
        for j in seachResult:
            urlsql='''SELECT`url` FROM `url` WHERE `url_id`= %s'''
            con1 = engine.connect()
            cursor = con1.execute(urlsql,(j[0]))
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

    con1 = engine.connect()
    cursor=con1.execute(sql,(attractionId))
    result=cursor.fetchone()

    if result == []:
        return {"error": True,"message": "無此編號"}
    elif result != []:
        urlsql='''SELECT`url` FROM `url` WHERE `url_id`= %s'''

        cursor=con1.execute(urlsql,(result[0]))
        urlResult=cursor.fetchall()

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
    if not session:
        return jsonify({"data": None})
    else:
        name = session.get("name")
        user_id = session.get("id")
        email = session.get("email")
        data = {
            "data": {
                "id": user_id,
                "name": name,
                "email": email
            }
        }
        return jsonify(data)

@apiBlueprint.route("/api/user", methods=["POST"])
def userPost():
    data=request.get_json()
    newname=data["name"]
    newemail=data["email"]
    newpassword=data["password"]

    if (newname=="") or (newemail=="") or (newpassword==""):
        return jsonify({"error": True,"message": "請填寫完整"})

    sql='''SELECT `email` FROM `member` WHERE `email`=%s'''
    con1 = engine.connect()
    cursor=con1.execute(sql,(newemail))
    result=cursor.fetchone()

    if(result != None):
        return jsonify({"error": True,"message": "Email已經被註冊"})
        
    elif(result == None):
        sql='''INSERT INTO `member`(name,email,password) VALUE(%s,%s,%s)'''
        try:
            cursor = con1.execute(sql,(newname,newemail,newpassword))
        except:
            # db.rollback()
            print('error')
        con1.close()
        
        return jsonify({"ok": True})
    else:
        return jsonify({"error": True,"message": "伺服器錯誤，請稍後再試"})

@apiBlueprint.route("/api/user", methods=["PATCH"])
def userPatch():
    data=request.get_json()
    email=data["email"]
    password=data["password"]

    sql='''SELECT `id`,`name`,`email` FROM `member` WHERE `email`=%s AND `password`=%s'''
    con1 = engine.connect()
    cursor = con1.execute(sql,(email,password))
    result = cursor.fetchone()

    if(result != []):
        session["id"]=result[0]
        session["name"]=result[1]
        session["email"]=result[2]
        session.permanent=True
        return jsonify({"ok": True})
    elif(result == []):
        return jsonify({"error": True,"message": "帳號或密碼錯誤"})
    else:
        return jsonify({"error": True,"message": "伺服器錯誤，請稍後再試"})

@apiBlueprint.route("/api/user", methods=["DELETE"])
def userDelete():
    session.clear()
    return jsonify({"ok": True})

@apiBlueprint.route("/api/booking", methods=["GET"])
def bookingGet():    
    if(session['name'] ==None):
        return jsonify({"error": True,"message": "未登入，拒絕存取"})

    sql = '''SELECT * FROM `shoppingCart` WHERE `member_id`=%s'''
    
    con1 = engine.connect()
    cursor = con1.execute(sql,(session['id']))
    result = cursor.fetchone()

    if (result==None):
        return jsonify({"data":None})
    else:
        sql = '''SELECT `name`,`address` FROM `spot` WHERE `id`=%s '''
        
        con1 = engine.connect()
        cursor = con1.execute(sql,(result[0]))
        attractionResult=cursor.fetchone()

        sql = '''SELECT `url` FROM `url` WHERE `url_id`=%s '''

        con1 = engine.connect()
        cursor = con1.execute(sql,(result[0]))
        imageResult=cursor.fetchone()
        con1.close()
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

    sql_insert_update = '''
        INSERT INTO `shoppingCart` (member_id, attaction_id, date, time, price)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        attaction_id=VALUES(attaction_id),
        date=VALUES(date),
        time=VALUES(time),
        price=VALUES(price)
    '''
    con = engine.connect()
    error = False
    try:
        cursor = con.execute(sql_insert_update, (session['id'], attractionId, date, time, price))
        # db.commit()
    except Exception as e:
        # db.rollback()
        error = True
        print(f'Error during insert or update: {e}')
    con.close()

    if error:
        return jsonify({"error": True, "message": "資料未選取完整！"})
    elif session["id"] is None:
        return jsonify({"error": True, "message": "未登入，拒絕存取"})
    else:
        return jsonify({"ok": True})

@apiBlueprint.route("/api/booking", methods=["DELETE"])
def bookingDelete():
    if (session['id'] !=None):
        sql = '''DELETE FROM `shoppingCart` WHERE `member_id`=%s'''
        con1 = engine.connect()
        try:
            cursor = con1.execute(sql,(session['id']))
            # db.commit()
        except:
            # db.rollback()
            print('error')
        con1.close()

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
    con1 = engine.connect()        
    try:
        cursor = con1.execute(sql,(order_number,price,date,time,name,email,phone,1,attractionId,session['id']))
        #db.commit()
    except:
        #db.rollback()
        print('error')
    con1.close()

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
            cursor = con1.execute(sql,(0,resJson["order_number"]))
            #db.commit()
        except:
            #db.rollback()
            print('errorStatus')
            con1.close()
        
        sql = '''DELETE FROM `shoppingCart` WHERE `member_id`=%s'''
        try:
            cursor = con1.execute(sql,(0,session['id']))
            #db.commit()
        except:
            #db.rollback()
            print('errorDEL')
        con1.close()

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
    con1 = engine.connect()
    cursor = con1.execute(sql,(orderNumber))
    result=cursor.fetchone

    sql = '''SELECT `name`,`address` FROM `spot` WHERE `id`=%s'''
    cursor = con1.execute(sql,(result[8]))
    attractionResult=cursor.fetchone()

    sql = '''SELECT `url` FROM `url` WHERE `url_id`=%s '''
    cursor = con1.execute(sql,(result[8]))
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