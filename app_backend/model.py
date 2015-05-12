from google.appengine.ext import ndb
 
class jutcRoute(ndb.Model):
    route = ndb.StringProperty()
    origin = ndb.StringProperty()
    via = ndb.StringProperty()
    destination = ndb.StringProperty()
    route_type = ndb.StringProperty()
    
class routeCoordinates(ndb.Model):
    route = ndb.StringProperty()
    pos_index = ndb.IntegerProperty()
    coorList = ndb.StringProperty()
    
class trackedBus(ndb.Model):
    bus_id = ndb.StringProperty() 
    route_id = ndb.StringProperty()
    origin = ndb.StringProperty()
    destination = ndb.StringProperty()
    via = ndb.StringProperty()
    index = ndb.StringProperty()
    lat = ndb.StringProperty() 
    long = ndb.StringProperty()
    velocity = ndb.StringProperty()
    direction = ndb.StringProperty()
    
    
    
class stop(ndb.Model):
    stop_id = ndb.StringProperty() 
    lat = ndb.StringProperty() 
    long = ndb.StringProperty()

class number(ndb.Model):
    number = ndb.StringProperty()     
