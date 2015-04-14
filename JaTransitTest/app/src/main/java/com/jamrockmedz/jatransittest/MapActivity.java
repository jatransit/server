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
import com.google.transit.realtime.GtfsRealtime;

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
import java.util.concurrent.ScheduledThreadPoolExecutor;
import java.util.concurrent.TimeUnit;

public class MapActivity extends Activity implements OnMapReadyCallback {

    private MapFragment mapFragment;
    protected int interval  = 20000;
    final String TAG = "JaTransit";
    final String mapType = "JA";
    DecimalFormat df = new DecimalFormat("#.##");
    ScheduledThreadPoolExecutor updater;

    MarkerOptions mOption;
    Random rand = new Random();

    ArrayList<ArrayList> routeList = new ArrayList<>();
    ArrayList<TrackedBus> buses = new ArrayList<>();
    Timer timer;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        LocationManager locationManager = (LocationManager)
        getSystemService(Context.LOCATION_SERVICE);

        LocationListener locationListener = new AppLocationListener();
        locationManager.requestLocationUpdates(
                LocationManager.GPS_PROVIDER, 5000, 10, locationListener);

        final Button button = (Button) findViewById(R.id.find_closest);
        button.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                // Perform action on click
                displayToast("Hello World!");
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

    public void simulateTracking()
    {

        for(TrackedBus bus: buses)
        {
            int locationIndex = bus.getCurrentLocationIndex();
            locationIndex++;
            int routeIndex = bus.getRouteIndex();

            if(locationIndex < routeList.get(routeIndex).size())
            {
                LatLng loc = (LatLng)routeList.get(routeIndex).get(locationIndex);
                bus.updateLocation(locationIndex, loc, interval);
                bus.getMarker().setPosition(loc);
                bus.getMarker().setTitle("Speed: " + df.format(bus.getVelocity()) + "km/h");

            }
            else
            {
                LatLng loc = (LatLng)routeList.get(routeIndex).get(0);
                bus.updateLocation(0, loc, interval);
                bus.getMarker().setPosition(loc);
            }

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

        LatLng location = route.get(0);

        int routeIndex = routeList.size();

        Marker m = mapFragment.getMap().addMarker( mOption.position(location).icon(BitmapDescriptorFactory.fromResource(R.drawable.bus_marker)).anchor((float)0.5,(float)0.5));
        TrackedBus b = new TrackedBus(m,routeIndex,0,location);
        buses.add(b);

        pO.width(5).color(color);
        mapFragment.getMap().addPolyline(pO);

        routeList.add(route);

    }

    public void setupMap(GoogleMap map)
    {
        LatLng homeLoc = new LatLng(42.350, -71.146);
        LatLng jamhome = new LatLng(18.012,-76.797);

        map.setMyLocationEnabled(true);

        /*mOption = new MarkerOptions()
                .icon(BitmapDescriptorFactory.fromResource(R.drawable.bus_marker));*/
        mOption = new MarkerOptions();
        map.getUiSettings().setZoomControlsEnabled(true);

        timer = new Timer();

        if(mapType.compareTo("JA") == 0 )
        {
            map.moveCamera(CameraUpdateFactory.newLatLngZoom(jamhome, 13));
            new JaTransitFeedData().execute("http://server.jatransit.appspot.com/coordinates2");
        }
        else
        {
            map.moveCamera(CameraUpdateFactory.newLatLngZoom(homeLoc, 10));

            timer.scheduleAtFixedRate( new TimerTask() {
                public void run() {
                    try
                    {
                        new MBTAFeedData().execute("http://developer.mbta.com/lib/GTRTFS/Alerts/VehiclePositions.pb");
                    }
                    catch (Exception e)
                    {
                        Log.d(TAG, "MBTAFeedData scheduleAtFixedRate Error: " + e.toString());
                    }
                }
            }, 0, 20000);
        }
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

            setUpMapUpdater();

        }
    }


    private void setUpMapUpdater() {
        updater = new ScheduledThreadPoolExecutor(1);
        updater.scheduleAtFixedRate(new Runnable() {
            private Runnable update = new Runnable() {
                @Override
                public void run() {
                    simulateTracking();
                }
            };

            @Override
            public void run() {
                runOnUiThread(update);
            }
        }, 10, 10, TimeUnit.SECONDS);
    }

    private class AppLocationListener implements LocationListener {

        @Override
        public void onLocationChanged(Location loc) {

            displayToast("Lat: " + loc.getLatitude() + " Log: " + loc.getLongitude() );
        }

        @Override
        public void onProviderDisabled(String provider) {}

        @Override
        public void onProviderEnabled(String provider) {}

        @Override
        public void onStatusChanged(String provider, int status, Bundle extras) {}
    }

    protected class MBTAFeedData extends AsyncTask<String, Void, ArrayList<LatLng>> {

        protected ArrayList<LatLng> doInBackground(String... urls) {
            URL url;
            GtfsRealtime.FeedMessage feed;

            ArrayList<LatLng>  buses = new ArrayList<>();
            try
            {
                url = new URL(urls[0]);
                feed = GtfsRealtime.FeedMessage.parseFrom(url.openStream());
                int i = 0;
                for (GtfsRealtime.FeedEntity entity : feed.getEntityList()) {
                    //Log.d(TAG, "Loop");
                    if (entity.hasVehicle()) {
                        buses.add(new LatLng(entity.getVehicle().getPosition().getLatitude(),entity.getVehicle().getPosition().getLongitude()));
                    }
                }
            }
            catch (Exception e) {
                Log.d(TAG, "Error: " + e.toString());
            }

            return buses;
        }

        /** The system calls this to perform work in the UI thread and delivers
         * the result from doInBackground() */
        protected void onPostExecute(ArrayList<LatLng> locations) {

            clearMap();
            for(LatLng loc: locations)
            {
                try
                {
                    mapFragment.getMap().addMarker(mOption.position(loc));
                }
                catch(Exception e)
                {
                    Log.d(TAG, "Error: " + e.toString());
                }
            }


        }
    }


}