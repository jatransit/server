package com.jamrockmedz.jatransittest;

import android.app.Activity;
import android.content.Context;
import android.graphics.Color;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.AsyncTask;
import android.os.Bundle;
import android.util.Log;

import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import com.google.android.gms.maps.CameraUpdateFactory;
import com.google.android.gms.maps.GoogleMap;
import com.google.android.gms.maps.MapFragment;
import com.google.android.gms.maps.OnMapReadyCallback;
import com.google.android.gms.maps.model.BitmapDescriptorFactory;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.Marker;
import com.google.android.gms.maps.model.MarkerOptions;
import com.google.android.gms.maps.model.PolylineOptions;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.URL;
import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.Timer;
import java.util.TimerTask;
import java.util.Random;

public class MapActivity extends Activity implements OnMapReadyCallback {

    private MapFragment mapFragment;
    final String TAG = "JaTransit";
    final String mapType = "JA";
    protected LatLng currentLocation;
    DecimalFormat df = new DecimalFormat("#.##");
    LocationManager locationManager;

    MarkerOptions mOption;
    Random rand = new Random();

    ArrayList<ArrayList> routeList = new ArrayList<>();
    ArrayList<TrackedBus> buses = new ArrayList<>();
    Timer timer;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        locationManager = (LocationManager)
        getSystemService(Context.LOCATION_SERVICE);

        LocationListener locationListener = new AppLocationListener();
        locationManager.requestLocationUpdates(
                LocationManager.GPS_PROVIDER, 5000, 10, locationListener);

        final Button button = (Button) findViewById(R.id.find_closest);
        button.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                // Perform action on click
                displayClosestBus();
            }
        });

        mapFragment = (MapFragment) getFragmentManager()
                .findFragmentById(R.id.map);
        mapFragment.getMapAsync(this);
    }

    @Override
    public void onMapReady(GoogleMap map) {
        setupMap(map);
    }


    public void simulateTracking(JSONArray livebuses)
    {
        try
        {
            for (int i = 0; i < livebuses.length(); i++) {
                JSONObject jo = (JSONObject) livebuses.get(i);

                String lat = jo.getString("lat");
                String lon = jo.getString("long");
                String origin = jo.getString("origin");
                String via = jo.getString("via");
                String destination = jo.getString("destination");
                String velocity = jo.getString("velocity");
                String bus_id = jo.getString("bus_id");
                String route_id = jo.getString("route_id");
                String direction = jo.getString("direction");

                LatLng location = new LatLng(Double.parseDouble(lat), Double.parseDouble(lon));

                boolean found = false;
                for(TrackedBus bus: buses)
                {
                    if(bus.getBusId().equals(bus_id))
                    {
                        found = true;
                        bus.setVelocity(Double.parseDouble(velocity));
                        bus.getMarker().setTitle("Speed: " + df.format(bus.getVelocity()) + "km/h");
                        bus.setCurrentLocation(location);
                        bus.getMarker().setPosition(location);
                    }
                }

                if(!found)
                {
                    Marker m = mapFragment.getMap().addMarker( mOption.position(location).icon(BitmapDescriptorFactory.fromResource(R.drawable.bus_marker)).anchor((float)0.5,(float)0.5));
                    TrackedBus b = new TrackedBus(bus_id,m,0,location);
                    b.setVelocity(Double.parseDouble(velocity));
                    b.getMarker().setTitle("Speed: " + df.format(b.getVelocity()) + "km/h");
                    buses.add(b);
                }
            }
        }
        catch (Exception e)
        {
            Log.d(TAG, "onPostExecute Error: " + e.toString());
        }
    }

    public void clearMap()
    {
        try
        {
            mapFragment.getMap().clear();
        }
        catch(Exception e)
        {
            Log.d(TAG, "Error: " + e.toString());
        }

    }

    public void drawRoute(ArrayList<LatLng> route)
    {
        PolylineOptions pO = new PolylineOptions();

        for(LatLng loc: route)
        {
            try
            {
                pO.add(loc);
            }
            catch(Exception e)
            {
                Log.d(TAG, "drawRoute Error: " + e.toString());
            }
        }
        int color = Color.argb(255, rand.nextInt(256) + 128, rand.nextInt(256) + 128, rand.nextInt(256) + 128);

        pO.width(5).color(color);
        mapFragment.getMap().addPolyline(pO);
        routeList.add(route);

    }

    public void setupMap(GoogleMap map)
    {
        //LatLng homeLoc = new LatLng(42.350, -71.146);
        LatLng jamhome = new LatLng(18.012,-76.797);

        map.setMyLocationEnabled(true);

        /*mOption = new MarkerOptions()
                .icon(BitmapDescriptorFactory.fromResource(R.drawable.bus_marker));*/
        mOption = new MarkerOptions();
        map.getUiSettings().setZoomControlsEnabled(true);

        clearMap();

        timer = new Timer();

        if(mapType.compareTo("JA") == 0 )
        {
            map.moveCamera(CameraUpdateFactory.newLatLngZoom(jamhome, 13));
            new JaTransitFeedData().execute("http://server.jatransit.appspot.com/coordinates2");

            timer.scheduleAtFixedRate( new TimerTask() {
                public void run() {
                    try
                    {
                        //new JATransitLiveFeed().execute("http://developer.mbta.com/lib/GTRTFS/Alerts/VehiclePositions.pb");
                        new JATransitLiveFeed().execute("http://jatransit.appspot.com/live");
                    }
                    catch (Exception e)
                    {
                        Log.d(TAG, "JATransitLiveFeed scheduleAtFixedRate Error: " + e.toString());
                    }
                }
            }, 0, 20000);
        }
    }


    public void displayClosestBus()
    {
        TrackedBus bus = findNearestBus();

        if(bus != null)
        {

            bus.getMarker().setTitle("Closest Bus!!");
            bus.getMarker().showInfoWindow();
            displayToast("Closest bus found and displayed on map!");
        }
    }
    public TrackedBus findNearestBus()
    {
        TrackedBus closest = null;
        double shortestDistance = 999999999;
        double distance = 0;

        if(getCurrentLocation() == null)
        {
            String locationProvider = LocationManager.NETWORK_PROVIDER; // Or use LocationManager.GPS_PROVIDER
            Location lastKnownLocation = locationManager.getLastKnownLocation(locationProvider);
            setCurrentLocation(lastKnownLocation);

            if(getCurrentLocation() == null)
            {
                displayToast("Please enable GPS!!");
                return null;
            }
        }


        for(TrackedBus bus: buses)
        {
            distance = calculateDistanceInMeters(getCurrentLocation(),bus.getLocation());

            if( distance < shortestDistance )
            {
                closest = bus;
                shortestDistance = distance;
            }
        }

        return  closest;
    }

    public LatLng getCurrentLocation() {
        return currentLocation;
    }

    public void setCurrentLocation(Location currentLocation)
    {
        this.currentLocation = new LatLng(currentLocation.getLatitude(),currentLocation.getLongitude());
    }

    public void displayToast(String message)
    {
        LayoutInflater inflater = getLayoutInflater();
        View layout = inflater.inflate(R.layout.toast_layout,
                (ViewGroup) findViewById(R.id.toast_layout_root));

        TextView text = (TextView) layout.findViewById(R.id.text);
        text.setText(message);

        Toast toast = new Toast(getApplicationContext());
        toast.setGravity(Gravity.CENTER_VERTICAL, 0, 0);
        toast.setDuration(Toast.LENGTH_LONG);
        toast.setView(layout);
        toast.show();
    }

    protected class JaTransitFeedData extends AsyncTask<String, Void, JSONArray> {

        protected JSONArray doInBackground(String... urls) {
            URL url;
            JSONArray routes = new JSONArray();
            try
            {
                url = new URL(urls[0]);

                BufferedReader bufferedReader =
                        new BufferedReader(new InputStreamReader(
                                url.openStream()));
                String next;
                while ((next = bufferedReader.readLine()) != null){
                    JSONObject ja = new JSONObject(next);

                    routes = ja.getJSONArray("routes");
                }
            }
            catch (Exception e) {
                Log.d(TAG, "doInBackground Error: " + e.toString());
            }
            return routes;
        }

        /** The system calls this to perform work in the UI thread and delivers
         * the result from doInBackground() */
        protected void onPostExecute(JSONArray routes) {

            try
            {
                for (int i = 0; i < routes.length(); i++) {
                    JSONObject jo = (JSONObject) routes.get(i);

                    String routeNum = jo.getString("route");
                    ArrayList<LatLng>  coordinates = new ArrayList<>();

                    String[] coordinateList = jo.getString("coordinates").split(",");

                    for (String coordinate : coordinateList) {

                        String[] coordinateArray = coordinate.split("/");
                        Log.d(TAG, "Lat: " + coordinateArray[0] + " Lon: " + coordinateArray[1]);
                        coordinates.add(new LatLng(Double.parseDouble(coordinateArray[0]), Double.parseDouble(coordinateArray[1])));
                    }

                    drawRoute(coordinates);
                }
            }
            catch (Exception e)
            {
                Log.d(TAG, "onPostExecute Error: " + e.toString());
            }

        }
    }


    private class AppLocationListener implements LocationListener {

        @Override
        public void onLocationChanged(Location loc) {

            displayToast("Lat: " + loc.getLatitude() + " Log: " + loc.getLongitude() );
            setCurrentLocation(loc);
        }

        @Override
        public void onProviderDisabled(String provider) {}

        @Override
        public void onProviderEnabled(String provider) {}

        @Override
        public void onStatusChanged(String provider, int status, Bundle extras) {}
    }

    protected class JATransitLiveFeed extends AsyncTask<String, Void, JSONArray> {

        protected JSONArray doInBackground(String... urls) {
            URL url;
            JSONArray buses = new JSONArray();
            try
            {
                url = new URL(urls[0]);

                BufferedReader bufferedReader =
                        new BufferedReader(new InputStreamReader(
                                url.openStream()));
                String next;
                while ((next = bufferedReader.readLine()) != null){
                    JSONObject ja = new JSONObject(next);

                    buses = ja.getJSONArray("trackedBus");
                }
            }
            catch (Exception e) {
                Log.d(TAG, "doInBackground Error: " + e.toString());
            }
            return buses;
        }


        /** The system calls this to perform work in the UI thread and delivers
         * the result from doInBackground() */
        protected void onPostExecute(JSONArray buses) {

            simulateTracking(buses);
        }
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

}