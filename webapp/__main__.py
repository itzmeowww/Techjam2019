
from flask import Flask, jsonify, request
import math
from http import HTTPStatus
import re
app = Flask(__name__)

aliens_pos = {}
robots_pos = {}
robots_id = []

def makepos(body):
    first_pos = body['first_pos']
    second_pos = body['second_pos']

    if('x' in first_pos):
        fx = first_pos['x']
    elif('east' in first_pos):
        fx = first_pos['east']
    elif('west' in first_pos):
        fx = -first_pos['west']
    if('y' in first_pos):
        fy = first_pos['y']
    elif('north' in first_pos):
        fy = first_pos['north']
    elif('south' in first_pos):
        fy = -first_pos['south']
    else:
        all = (re.findall('\d+', first_pos))
        id = str(all[0])
        fx = robots_pos[id]['x']
        fy = robots_pos[id]['y']

        
    
    if('x' in second_pos):
        sx = second_pos['x']
    elif('east' in second_pos):
        sx = second_pos['east']
    elif('west' in second_pos):
        sx = -second_pos['west']
    if('y' in second_pos):
        sy = second_pos['y']
    elif('north' in second_pos):
        sy = second_pos['north']
    elif('south' in second_pos):
        sy = -second_pos['south']
    else:
        all = (re.findall('\d+', second_pos))
        id = str(all[0])
        sx = robots_pos[id]['x']
        sy = robots_pos[id]['y']
    
    return fx,fy,sx,sy


@app.route('/distance', methods=['POST'])
def distance():
    body = request.get_json()    
    fx,fy,sx,sy = makepos(body)
    dx = fx-sx
    dy = fy-sy
    if "metric" in body:
        metric = body['metric']
        if metric == "manhattan":
            distance = abs(dx) + abs(dy)
        if metric == "euclidean":
            distance = math.sqrt(dx*dx+dy*dy)
    else:
        distance = math.sqrt(dx*dx+dy*dy)
    
    distance = '%.3f' %distance
    
    return jsonify(distance = distance),HTTPStatus.OK



@app.route('/robot/<id>/position',methods=['PUT'])
def add_pos(id):
    body = request.get_json()
    robots_pos[str(id)] = body['position']
    #print(robots_pos[id])
    if str(id) not in robots_id:
        robots_id.append(str(id))
    return ' ', HTTPStatus.NO_CONTENT

@app.route('/robot/<id>/position',methods=['GET'])
def findpos(id):
    body = request.get_json()
    if str(id) in robots_pos:
        return jsonify(position=robots_pos[str(id)]), HTTPStatus.OK
    else:
        return '', HTTPStatus.NOT_FOUND

@app.route('/nearest',methods=['POST'])
def nearest():
    body = request.get_json()
    rx = body['ref_position']['x']
    ry = body['ref_position']['y'] 
    k = 1
    if 'k' in body:
        k = int(body['k'])
       
    minn = 1e9
    ret = []
    for id in robots_id:
        x = robots_pos[id]['x']
        y = robots_pos[id]['y']
        dx = rx-x
        dy = ry-y
        dis = math.sqrt(dx*dx+dy*dy)
        if dis < minn:
            minn = dis
            ret = [int(id)]
        elif dis == minn:
            if int(id) < ret[0]:
                ret = [int(id)]
        
    return jsonify(robot_ids = ret), HTTPStatus.OK

@app.route('/alien/<id>/report',methods=['POST'])
def report(id):
    body = request.get_json()
    temp = {}
    temp[str(body['robot_id'])] = body['distance']
    aliens_pos[id] = temp[str(body['robot_id'])]
    
    return '', HTTPStatus.OK

@app.route('/alien/<id>/position',methods=['GET'])
def alienpos(id):
    if len(aliens_pos[id]) <= 1:
        return '',HTTPStatus.FAILED_DEPENDENCY
    else:
        
        return '', HTTPStatus.OK, jsonify(position = jsonify(x = coorx, y = coory))


@app.route('/closestpair',methods=['GET'])
def closestpair():
    if len(robots_id) == 1:
        return '',HTTPStatus.FAILED_DEPENDENCY
    
    minn = 1e9

    for id1 in robots_id:
        x1 = robots_pos[id1]['x']
        y1 = robots_pos[id1]['y']
        for id2 in robots_id:
            if id1 == id2:
                continue
            x2 = robots_pos[id2]['x']
            y2 = robots_pos[id2]['y']
            dx = x1-x2
            dy = y1-y2
            dis = math.sqrt(dx*dx+dy*dy)
            if dis < minn:
                minn = dis
    minn = f"{float(minn):.3f}"
    return jsonify(distance=minn)


app.run(host='0.0.0.0',port=8000,debug=1)