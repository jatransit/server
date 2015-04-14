import os
import sys
import json
import model

from flask import Flask ,Response, jsonify
from flask import render_template

from model import route
from model import stop
import urllib

# sys.path includes 'server/lib' due to appengine_config.py

app = Flask(__name__.split('.')[0])

@app.route('/')
@app.route('/<name>')
def home(name=None):
    """ Return template at application root URL."""
    name = "JaTransit"
    return render_template('index.html', name=name)

@app.route('/test_routes')
def getTestRoutes():
    results = model.route.query()
    tempData = []
    for result in results:
        datadict = {"route_id": result.route_id,"agency_id": result.agency_id,"route_short_name": result.route_short_name,"route_long_name": result.route_long_name,"route_desc": result.route_desc,"route_type":result.route_type,"route_url": result.route_url,"route_color": result.route_color,"route_text_color": result.route_text_color,"route_sort_order": result.route_sort_order}
        tempData.append(datadict)
    d={}
    d["routes"] = tempData;
    out = json.dumps(d)
    resp = Response(response=out,status=200,mimetype="application/json")
    return resp

@app.route('/test_stops')
def getTestStops():
    results = model.stop.query()
    tempData = []
    for result in results:
        datadict = {"stop_id": result.stop_id,"stop_code": result.stop_code,"stop_name": result.stop_name,"stop_desc": result.stop_desc,"stop_lat": result.stop_lat,"stop_lon": result.stop_lon,"zone_id": result.zone_id,"stop_url": result.stop_url,"location_type": result.location_type,"parent_station": result.parent_station,"wheelchair_boarding": result.wheelchair_boarding}
        tempData.append(datadict)
    d={}
    d["stops"] = tempData;
    out = json.dumps(d)
    resp = Response(response=out,status=200,mimetype="application/json")
    return resp
    
    
@app.route('/load_test_routes')
def load_routes():
    results = model.route.query()
    for result in results:
        result.key.delete()
            
    f= open('routes.txt','r')
    for x in range(0, 200):
        line = f.readline()
        nline = line.replace("\n", "")
        rline = nline.replace("\r", "")
        qline = rline.replace('\"','')
        dline = repr(qline.strip())
        data = rline.split(",")
        r =  model.route(
            route_id  = data[0],
            agency_id = data[1],
            route_short_name = data[2],
            route_long_name = data[3],
            route_desc = data[4],
            route_type = data[5],
            route_url = data[6],
            route_color = data[7],
            route_text_color = data[8],
            route_sort_order = data[9]
        )
        k = r.put()
    return "Complete"

@app.route('/load_test_stops')
def load_stops():
    results = model.stop.query()
    for result in results:
        result.key.delete()
    
    f= open('stops.txt','r')
    for x in range(0, 200):
        line = f.readline()
        nline = line.replace("\n", "")
        rline = nline.replace("\r", "")
        qline = rline.replace('\"','')
        dline = repr(qline.strip())
        data = rline.split(",")
        s =  model.stop(
            stop_id  = data[0],
            stop_code  = data[1],
            stop_name  = data[2],
            stop_desc  = data[3],
            stop_lat  = data[4],
            stop_lon  = data[5],
            zone_id = data[6],
            stop_url = data[7],
            location_type = data[8],
            parent_station = data[9],
            wheelchair_boarding = data[10]
        )
        k = s.put()
    return "Complete"
    

@app.route('/live_test_positions')
def get_positions():
    return "Work in Progress!!"
    
@app.route('/load_jutc_routes')
def loadJutcRoutes():
    results = model.jutcRoute.query()
    for result in results:
        result.key.delete()
            
    f= open('jutc_routes.txt','r')
    for line in f.readlines():
        line = f.readline()
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
    results = model.jutcRoute.query()
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
    return

@app.route('/query/<query>')
def searchRoute(query=None):
    return
