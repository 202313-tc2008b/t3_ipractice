import json 
from model import StreetView

from flask import Flask, request
app = Flask(__name__)

streets = StreetView()

@app.route('/getPositions', methods = ['POST', 'GET'])
def getPositions():
    if request.method == 'POST':
        num = request.args.get('num')
        streets.step()
        p2 = streets.get_info()
        return "('positions :['"+str(p2)+"])"
    
def arraysToJSON(ar):
    result = []
    for i in ar:
        temp = []
        temp.append(i[0])
        temp.append(i[1])
        result.append(json.dumps(temp))
    return result

if __name__ == '__main__':
    p1 = streets.get_info()
    print(p1)
    streets.step()
    print()