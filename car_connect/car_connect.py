#coding=utf-8
from flask import Flask,request,jsonify,Response
from flask_sqlalchemy import SQLAlchemy
# import readImg
import os
import base64
import random
app = Flask(__name__)
app.config['SECRET_KEY'] = 'helloworld'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:seansean@localhost:3306/car'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

locate = '/home/sean/PycharmProjects/car_connect/imge/'

class User(db.Model):
    __tablename__ = 'users'
    # users = db.relationship('User')
    id = db.Column(db.Integer,primary_key=True)
    plate = db.Column(db.String(30))
    img = db.Column(db.BLOB)
    address = db.Column(db.String(50))
    type = db.Column(db.Integer)
    time = db.Column(db.Integer)

@app.route('/',methods=['POST'])
def handle_image():
    content = request.get_json(force=True)

    time = content['time']
    post_img = content['img'][0]
    img_name = str(str(time)+str(random.randint(0,65535)))
    # img_name = '1'
    img = open(locate+img_name+'.jpg','wb')
    # img = open('q.jpg','wb')
    img_temp = base64.b64decode(post_img)
    img.write(img_temp)

    address = content['address']
    # plate = readImg.read_img()
    import hyperlpr.pipline as pp
    import cv2
    read_img = cv2.imread(locate+img_name+'.jpg')

    plate_temp = pp.SimpleRecognizePlate(read_img)
    # print plate
    plate = '识别失败'
    if plate != None and plate != []:
        plate = plate_temp[0]
    user = User(img = img_name+'.jpg',type = 1,time = time,address = address,plate = plate)
    db.session.add(user)
    db.session.commit()
    search_res = User.query.filter_by(address = address,time = time).first()
    id = search_res.id
    address = search_res.address
    img = "http://101.132.144.11/getImg/"+img_name
    time = search_res.time
    img.close()
        #失败之后对图片进行删除
        # count = search(plate)
    if plate != '识别失败':
        result = jsonify({'res':'success','address':address,'time':time,'plate':plate,'id':id,'img':img})
    else:
        result = jsonify({'res': 'fail', 'address': address, 'time': time, 'plate': plate, 'id': id,'img':img})
    return result

@app.route('/searchAll')
def searchAll():
    search_res = User.query.filter_by(type = 1).all()
    print search_res
    res = []
    dicts = {}
    for temp in search_res:
        print temp.plate
        dicts['plate'] = temp.plate
        dicts['id'] = temp.id
        dicts['img'] = temp.img
        dicts['address'] = temp.address
        dicts['time'] = temp.time
        res.append(dicts.copy())
    if len(res) == 0:
        return jsonify({'res':'none'})
    return jsonify(res)

@app.route('/search',methods=['POST'])
def search():
    content = request.get_json(force=True)
    id = content['id']
    search_res  = User.query.filter_by(id = id).all()
    search_res =search_res[0]
    res = {'plate':search_res.plate,'id':search_res.id,'img':search_res.img,'address':search_res.address,'time':search_res.time}
    return jsonify(res)

@app.route('/changePlate',methods=['POST'])
def change_plate():
    content = request.get_json(force=True)
    id = content['id']
    print content
    search_res = User.query.filter_by(id = id).first()
    print content['plate']
    search_res.plate = content['plate']
    db.session.commit()
    return jsonify({'res':'success'})

@app.route('/searchByPlate',methods=['POST'])
def searchByPlate():
    content = request.get_json(force=True)
    plate = content['plate']
    search_res = User.query.filter_by(plate = plate).all()
    res = []
    dicts = {}
    for temp in search_res:
        dicts['plate'] = temp.plate
        dicts['id'] = temp.id
        dicts['img'] = temp.img
        dicts['address'] = temp.address
        dicts['time'] = temp.time
        res.append(dicts.copy())
    if len(res) == 0:
        return jsonify({'res':'none'})
    return jsonify(res)



@app.route('/delete',methods = ['POST'])
def delete():
    content = request.get_json(force=True)
    id = content['id']
    search_res = User.query.filter_by(id=id).first()
    if search_res is not None:
        db.session.delete(search_res)
        db.session.commit()
        return jsonify({'res':'success'})
    return jsonify({'res':'fail'})

@app.route('/getImg/<imgAddress>')
def getImg(imgAddress):
    if os.path.exists(locate+imgAddress) is True:
        img = file(locate+imgAddress.format(imgAddress))
        resp = Response(img,mimetype='image/jpeg')
        return resp
    else:
        return jsonify({'res':'fail'})



if __name__ == '__main__':
    # handle_imagereferenced()
    db.create_all()
    app.run(debug = True)

