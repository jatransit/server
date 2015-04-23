import os
import sys
import json
import urllib
import model

from flask import Flask ,Response, jsonify
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for


from model import jutcRoute
from model import routeCoordinates
from model import trackedBus
from model import stop
from google.appengine.ext import ndb



# sys.path includes 'server/lib' due to appengine_config.py

app = Flask(__name__.split('.')[0])

@app.route('/')
@app.route('/<name>')
def home(name=None):
    """ Return template at application root URL."""
    name = "JaTransit"
    return render_template('index.html', name=name)
    
@app.route('/uploadform')
def formSubmit():
    return render_template('form.html')
    
@app.route('/upload', methods=['POST'])
def upload():    
    uploadtype = request.form['uploadType']
    file = request.files['document']    
    
    if uploadtype == "stops":
        results = stop.query()
        for result in results:
            result.key.delete()
                
        for line in file.readlines():
            nline = line.replace("\n", "")
            rline = nline.replace("\r", "")
            qline = rline.replace('\"','')
            dline = repr(qline.strip())
            data = rline.split(",")
            r =  model.stop(
                stop_id  = data[0],
                lat = data[1],
                long = data[2]
            )
            k = r.put()
    elif uploadtype == "routes":
        results = jutcRoute.query()
        for result in results:
            result.key.delete()
                
        for line in file.readlines():
            nline = line.replace("\n", "")
            rline = nline.replace("\r", "")
            qline = rline.replace('\"','')
            dline = repr(qline.strip())
            data = rline.split(",")
            r =  model.jutcRoute(
                route  = data[0],
                origin = data[1],
                via = data[2],
                destination = data[3],
                route_type = data[4]
            )
            k = r.put()
    elif uploadtype == "rcoordinates":
        results = routeCoordinates.query()
        for result in results:
            result.key.delete()
        
        var = 0
        max = 10
        index = 1
                
        for line in file.readlines():
            nline = line.replace("\n", "")
            rline = nline.replace("\r", "")
            qline = rline.replace('\"','')
            dline = repr(qline.strip())
            data = rline.split(",")
            
            route_num = data[0]
            coor = ""
            posIndex = 0
            for pos in range(1, len(data), 10):
                for x in range(pos, pos+10):
                    if x < len(data) and pos < len(data):
                        coor += data[x] + ","                
                    
                r =  model.routeCoordinates(
                    route  = route_num,
                    pos_index = posIndex,
                    coorList = coor
                )
                coor = ""
                k = r.put()
                index = index + 1
                posIndex = posIndex + 1
            
    elif uploadtype == "buses":
        results = trackedBus.query()
        for result in results:
            result.key.delete()
                
        for line in file.readlines():
            nline = line.replace("\n", "")
            rline = nline.replace("\r", "")
            qline = rline.replace('\"','')
            dline = repr(qline.strip())
            data = rline.split(",")
            r =  model.trackedBus(
                bus_id  = data[0],
                route_id = data[1],
                lat = data[2],
                long = data[3],
                velocity = data[4]
            )
            k = r.put()
    
    
    return "Complete"


@app.route('/routes')
def getRoutes():
    results = jutcRoute.query()
    tempData = []
    for result in results:
        datadict = {"route": result.route,"origin": result.origin,"via": result.via,"destination": result.destination,"route_type": result.route_type}
        tempData.append(datadict)
    d={}
    d["routes"] = tempData;
    out = json.dumps(d)
    resp = Response(response=out,status=200,mimetype="application/json")
    return resp

@app.route('/route/<id>')
def getRoute(id=None):
    results = jutcRoute.query(jutcRoute.route == id)
    tempData = []
    for result in results:
        datadict = {"route": result.route,"origin": result.origin,"via": result.via,"destination": result.destination,"route_type": result.route_type}
        tempData.append(datadict)
    d={}
    d["routes"] = tempData;
    out = json.dumps(d)
    resp = Response(response=out,status=200,mimetype="application/json")
    return resp


@app.route('/query/<query>')
def searchRoute(query=None):
    results = jutcRoute.query(ndb.OR(jutcRoute.route == query,
                           jutcRoute.origin == query,
                           jutcRoute.via == query,
                           jutcRoute.destination == query,
                           jutcRoute.route_type == query))
    tempData = []
    for result in results:
        datadict = {"route": result.route,"origin": result.origin,"via": result.via,"destination": result.destination,"route_type": result.route_type}
        tempData.append(datadict)
    d={}
    d["routes"] = tempData;
    out = json.dumps(d)
    resp = Response(response=out,status=200,mimetype="application/json")
    return resp
    
      
@app.route('/coordinates2')
def getCoordinates():
    results = routeCoordinates.query().order(routeCoordinates.pos_index)
    routeArrary = []
    tempData = []
    for result in results:
        if result.route not in routeArrary:
            routeArrary.append(result.route)
    
    for route_id in routeArrary:
        coor = ""        
        for result in results:
            if result.route == route_id:
                coor += result.coorList
                
        datadict = {"route": route_id ,"coordinates": coor}
        tempData.append(datadict)
    d={}
    d["routes"] = tempData;
    out = json.dumps(d)
    resp = Response(response=out,status=200,mimetype="application/json")
    return resp
    