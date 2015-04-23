from google.appengine.ext import ndb
    
class route(ndb.Model):
    route_id  = ndb.StringProperty()
    agency_id = ndb.StringProperty()
    route_short_name = ndb.StringProperty()
    route_long_name = ndb.StringProperty()
    route_desc = ndb.StringProperty()
    route_type = ndb.StringProperty()
    route_url = ndb.StringProperty()
    route_color = ndb.StringProperty()
    route_text_color = ndb.StringProperty()
    route_sort_order = ndb.StringProperty()
  
class stop(ndb.Model):
    stop_id  = ndb.StringProperty()
    stop_code  = ndb.StringProperty()
    stop_name  = ndb.StringProperty()
    stop_desc  = ndb.StringProperty()
    stop_lat  = ndb.StringProperty()
    stop_lon  = ndb.StringProperty()
    zone_id = ndb.StringProperty()
    stop_url = ndb.StringProperty()
    location_type = ndb.StringProperty()
    parent_station = ndb.StringProperty()
    wheelchair_boarding = ndb.StringProperty()
    
class jutcRoute(ndb.Model):
    route = ndb.StringProperty()
    origin = ndb.StringProperty()
    via = ndb.StringProperty()
    destination = ndb.StringProperty()
    route_type = ndb.StringProperty()
    
class routeCoordinates(ndb.Model):
    route = ndb.StringProperty()
    coorList = ndb.StringProperty()
    
class trackedBus(ndb.Model):
    bus_id = ndb.StringProperty() 
    route_id = ndb.StringProperty()
    lat = ndb.StringProperty() 
    long = ndb.StringProperty()
    velocity = ndb.StringProperty()
    