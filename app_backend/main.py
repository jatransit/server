import os
import sys
import json
import urllib
import model

from flask import Flask ,Response, jsonify
from flask import render_template

from model import route
from model import stop
from model import jutcRoute
from model import routeCoordinates
from google.appengine.ext import ndb



# sys.path includes 'server/lib' due to appengine_config.py

app = Flask(__name__.split('.')[0])

@app.route('/')
@app.route('/<name>')
def home(name=None):
    """ Return template at application root URL."""
    name = "JaTransit"
    return render_template('index.html', name=name)

@app.route('/load_jutc_routes')
def loadJutcRoutes():
    results = jutcRoute.query()
    for result in results:
        result.key.delete()
            
    f= open('jutc_routes.txt','r')
    for line in f.readlines():
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
    
    
@app.route('/load_coordinates')
def loadCoordinates():
    results = routeCoordinates.query()
    for result in results:
        result.key.delete()
            
    f= open('route_coordinates.txt','r')
    for line in f.readlines():
        nline = line.replace("\n", "")
        rline = nline.replace("\r", "")
        qline = rline.replace('\"','')
        dline = repr(qline.strip())
        data = rline.split(",")
        
        route_num = data[0]
        coor = ""
        for x in range(1, len(data)):
            coor += data[x] + ","
            
            
        r =  model.routeCoordinates(
            route  = route_num,
            coordinates = coor
        )
        k = r.put()
    return "Complete"
    
@app.route('/coordinates')
def getCoordinates():
    results = routeCoordinates.query()
    tempData = []
    for result in results:
        datadict = {"route": result.route,"coordinates": result.coordinates}
        tempData.append(datadict)
    d={}
    d["routes"] = tempData;
    out = json.dumps(d)
    resp = Response(response=out,status=200,mimetype="application/json")
    return resp
    
@app.route('/coordinates2')
def getCoordinates2():
    tempData = []
    results = routeCoordinates.query()
    for result in results:
        result.key.delete()
            
    f= open('route_coordinates.txt','r')
    for line in f.readlines():
        nline = line.replace("\n", "")
        rline = nline.replace("\r", "")
        qline = rline.replace('\"','')
        dline = repr(qline.strip())
        data = rline.split(",")
        
        route_num = data[0]
        coor = ""
        for x in range(1, len(data)):
            coor += data[x] + ","
            
        datadict = {"route": route_num,"coordinates": coor}
        tempData.append(datadict)
    d={}
    d["routes"] = tempData;
    out = json.dumps(d)
    resp = Response(response=out,status=200,mimetype="application/json")
    return resp