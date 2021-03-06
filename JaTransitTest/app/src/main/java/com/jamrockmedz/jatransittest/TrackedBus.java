package com.jamrockmedz.jatransittest;

import android.util.Log;

import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.Marker;

/**
 * Created by Jamrockmedz on 07/04/2015.
 */
public class TrackedBus {
    Marker marker;
    int currentLocationIndex;
    LatLng currentLocation;
    double velocity;
    String origin;
    String via;
    String destination;
    String busId;

    TrackedBus(String busId, Marker marker, int locationIndex, LatLng location)
    {
        this.marker = marker;
        this.currentLocationIndex = locationIndex;
        this.currentLocation = location;
        this.velocity = 0;
        this.busId = busId;
    }


    public LatLng getCurrentLocation() {
        return currentLocation;
    }

    public void setCurrentLocation(LatLng currentLocation) {
        this.currentLocation = currentLocation;
    }

    public void updateLocation(int locationIndex, LatLng location, int interval)
    {
        this.currentLocationIndex = locationIndex;
        calculateVelocity(this.currentLocation, location, (double)interval);
        this.currentLocation = location;
    }

    public void calculateVelocity(LatLng current, LatLng previous, double time)
    {

        double displacement = calculateDistanceInMeters(current, previous);
        double velocity = (displacement/1000)/((time/1000)*0.000277778);
        setVelocity(velocity);
    }


    public double getVelocity() {
        return this.velocity;
    }

    public void setVelocity(double velocity) {
        this.velocity = velocity;
    }

    public int getCurrentLocationIndex()
    {
        return this.currentLocationIndex;
    }
    public Marker getMarker()
    {
        return this.marker;
    }

    public LatLng getLocation()
    {
        return this.currentLocation;
    }

    public double calculateDistanceInMeters(LatLng loc1, LatLng loc2)
    {
        double lon1 = loc1.longitude;
        double lat1 = loc1.latitude;
        double lon2 = loc2.longitude;
        double lat2 = loc2.latitude;

        double x = Math.toRadians(lon1 - lon2) * Math.cos( Math.toRadians( lat1 ) );
        double y = Math.toRadians(lat1 - lat2);

        return  6371000.0 * Math.sqrt( x*x + y*y );

    }


    public String getBusId() {
        return busId;
    }

    public void setBusId(String busId) {
        this.busId = busId;
    }
}
