import json 
from model import StreetView
from flask import Flask, request
app = Flask(__name__)

streets = StreetView()

@app.route('/getPositions', methods = ['POST', 'GET'])
def getPositions():
    if request.method == 'POST':
        streets.step()
        info = streets.get_info()
        return info
    elif request.method == 'GET':
        info = streets.get_info()
        return info

if __name__ == '__main__':
    app.run(debug=True,port=8000)