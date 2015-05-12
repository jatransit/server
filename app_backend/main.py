import os
import sys
import json
import urllib
import model
import math

from flask import Flask ,Response, jsonify
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for

from model import jutcRoute
from model import routeCoordinates
from model import trackedBus
from model import stop
from model import number
from google.appengine.ext import ndb



# sys.path includes 'server/lib' due to appengine_config.py

app = Flask(__name__.split('.')[0])

            
@app.route('/tasks/simulate')
def simulate():
    buses = trackedBus.query()
    tempData = []
    for bus in buses:        
        results = routeCoordinates.query(routeCoordinates.route == bus.route_id).order(routeCoordinates.pos_index)    
        
        coor = "" 
        for result in results:
            coor += result.coorList
            
        temp = coor.split(",");
        
        previous_index = int(bus.index)
        current_index = previous_index + 1
        
        if current_index >= (len(temp) - 1):
            current_index = 0;
        
        latlong1 = (temp[current_index]).split("/")
        lat1 = float(latlong1[0])
        lon1 = float(latlong1[1])
        
        latlong2 = (temp[previous_index]).split("/")
        lat2 = float(latlong2[0])
        lon2 = float(latlong2[1])
        
        bus.velocity = str(calculateVelocity(lon1, lat1, lon2,lat2, 20000))
        bus.index = str(current_index)
        bus.lat = str(lat1)
        bus.long = str(lon1)
        
        bus.put()
        
    return "200 OK"
        
        
        
    





    
@app.route('/live')
def getLive():
    results = trackedBus.query()
    tempData = []
    for result in results:
        datadict = {"bus_id": result.bus_id,"route_id": result.route_id,"via": result.via,"lat": result.lat,"long": result.long,"velocity": result.velocity, "direction": result.direction,"origin": result.origin,"destination": result.destination}
        tempData.append(datadict)
    d={}
    d["trackedBus"] = tempData;
    out = json.dumps(d)
    resp = Response(response=out,status=200,mimetype="application/json")
    return resp   




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
            
            routes = jutcRoute.query(jutcRoute.route == data[1])
            tempData = []
            
            r =  model.trackedBus(
                    bus_id  = data[0],
                    route_id = data[1],
                    index = "0",
                    origin = "",
                    destination = "",
                    via = "",
                    direction = "",
                    lat = "",
                    long = "",
                    velocity = ""
                )
                
            for route in routes:
                r.origin = route.origin
                r.destination = route.destination
                r.via = route.via
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
    
def calculateVelocity(lon1, lat1, lon2,lat2,time):
    displacement = calculateDistanceInMeters(lon1, lat1, lon2,lat2)
    velocity = (displacement/1000)/((time/1000)*0.000277778)
    return velocity
    
    
def calculateDistanceInMeters(lon1, lat1, lon2,lat2):
    x = math.radians(lon1 - lon2) * math.cos( math.radians( lat1 ) )
    y = math.radians(lat1 - lat2)
    return  6371000.0 * math.sqrt( x*x + y*y )


@app.route('/tasks/test_simulation')
def test_simulation():
    results = number.query()
    for result in results:
        temp = float(result.number ) + 1
        result.number = str(temp)
        result.put()
        
    return "200 OK"

                
@app.route('/test_live')
def test_getLive():
    results = number.query()
    for result in results:
       return result.number

       
@app.route('/start')
def start():
    results = number.query()
    for result in results:
        result.key.delete()
    r =  model.number(number  = "0")
    k = r.put()
    
    return "Started"
    