# POST, GET
# http://127.0.0.1:5000/theChallenge?name=Alex&last=Pozos
import mesa
from model import BoidFlockers
from flask import Flask, request
import json

app = Flask(__name__)

@app.route('/theChallenge')

def theChallenge():
    if request.method == 'GET':
        name = request.args.get('name')
        return 'Welcome, %s' %name
        
    else: 
        name = request.form['name']
        return 'Invalid Method. Please use GET instead'
    
   
if __name__ == '__main__':
    app.run(debug=True,port=8000)