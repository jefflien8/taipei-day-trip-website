from flask import *
app=Blueprint(__name__)

@app.route("/api/attractions/{attractionId}")
def api():
    Data={
        "nextPage": 1,
        "data": {
            "id": 10,
            "name": "平安鐘",
            "category": "公共藝術",
            "description": "平安鐘祈求大家的平安，這是為了紀念 921 地震週年的設計",
            "address": "臺北市大安區忠孝東路 4 段 1 號",
            "transport": "公車：204、212、212直",
            "mrt": "忠孝復興",
            "latitude": 25.04181,
            "longitude": 121.544814,
            "images": [
                "http://140.112.3.4/images/92-0.jpg"
                ]
            }
        }
    return jsonify(Data)