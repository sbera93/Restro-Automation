package com.dmce.androidpothole;

import android.os.Bundle;
import android.os.Handler;

import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import com.dmce.androidpothole.directionhelpers.DataParser;
import com.dmce.androidpothole.directionhelpers.FetchURL;
import com.dmce.androidpothole.directionhelpers.TaskLoadedCallback;
import com.google.android.gms.maps.CameraUpdateFactory;
import com.google.android.gms.maps.GoogleMap;
import com.google.android.gms.maps.MapFragment;
import com.google.android.gms.maps.OnMapReadyCallback;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.MarkerOptions;
import com.google.android.gms.maps.model.Polyline;
import com.google.android.gms.maps.model.PolylineOptions;


import java.util.ArrayList;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

/**
 * Created by Vishal on 10/20/2018.
 */

public class MapActivity extends AppCompatActivity implements OnMapReadyCallback, TaskLoadedCallback {
    private GoogleMap mMap;
    private MarkerOptions place1, place2,place11;
    Button getDirection;
    private Polyline currentPolyline;
    TextView tvduration,distance;
    Handler handler = new Handler();
    Runnable runnable;
    int delay = 10*1000;
    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.map_display_activity);
        tvduration=(TextView)findViewById(R.id.textView4);
        distance=(TextView)findViewById(R.id.textView2);
        getDirection = findViewById(R.id.btnGetDirection);
        getDirection.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
//                new FetchURL(MapActivity.this).execute(getUrl(place1.getPosition(), place2.getPosition(), "driving"), "driving");
//                tvduration.setText(DataParser.timerequired+" minutes ");
//                distance.setText("distance is "+DataParser.totaldistance+" meters ");

            }
        });
        //27.658143,85.3199503
        //27.667491,85.3208583
        String srcsplit[]=SelectingLcoation.latilongisrc.split(",");


        place1 = new MarkerOptions().position(new LatLng(Double.parseDouble(srcsplit[0]), Double.parseDouble(srcsplit[1]))).title("Location 1");

        Toast.makeText(getApplicationContext(),""+SelectingLcoation.longitude1+SelectingLcoation.latitude1,Toast.LENGTH_LONG).show();

        SelectingLcoation.getLattitudeAndLongitudebyplate(SelectingLcoation.latitude1,SelectingLcoation.longitude1);

//        ArrayList<String> latilongidata=SelectingLcoation.latilongidata;
//        for(int k=0;k<latilongidata.size();k++)
//        {
//            String dstsplit[]=latilongidata.get(k).split("_");
//            place2 = new MarkerOptions().position(new LatLng(Double.parseDouble(dstsplit[0]), Double.parseDouble(dstsplit[1]))).title("Location 2");
//            mMap.addMarker(place2);
//
//        }
        MapFragment mapFragment = (MapFragment) getFragmentManager()
                .findFragmentById(R.id.mapNearBy);
        mapFragment.getMapAsync(this);
       }
    @Override
    protected void onResume() {
//        ArrayList<String> latilongidata=SelectingLcoation.latilongidata;
//        for(int k=0;k<latilongidata.size();k++)
//        {
//            String dstsplit[]=latilongidata.get(k).split("_");
//            place2 = new MarkerOptions().position(new LatLng(Double.parseDouble(dstsplit[0]), Double.parseDouble(dstsplit[1]))).title("Location 2");
//            mMap.addMarker(place2);
//
//        }
//        handler.postDelayed( runnable = new Runnable() {
//            public void run() {
                //do something
//                SelectingLcoation.getLattitudeAndLongitudebyplate(SelectingLcoation.busnumber);
//                ArrayList<String> latilongidata=SelectingLcoation.latilongidata;
//                for(int k=0;k<latilongidata.size();k++)
//                {
//                    String dstsplit[]=latilongidata.get(k).split("_");
//                    place2 = new MarkerOptions().position(new LatLng(Double.parseDouble(dstsplit[0]), Double.parseDouble(dstsplit[1]))).title("Location 2");
//                    mMap.addMarker(place2);
//
//                }
//                new FetchURL(MapActivity.this).execute(getUrl(place1.getPosition(), place2.getPosition(), "driving"), "driving");
//
//                handler.postDelayed(runnable, delay);
//            }
//        }, delay);

        super.onResume();

    }
    @Override
    protected void onPause() {
        handler.removeCallbacks(runnable); //stop handler when activity not visible
        super.onPause();
    }

    @Override
    public void onMapReady(GoogleMap googleMap) {
        mMap = googleMap;
        Log.d("mylog", "Added Markers");
        mMap.addMarker(place1);
        String srcsplit[]=SelectingLcoation.latilongisrc.split(",");
        LatLng latLng = new LatLng(Double.parseDouble(srcsplit[0]), Double.parseDouble(srcsplit[1]));
        mMap.moveCamera(CameraUpdateFactory.newLatLng(latLng));
        mMap.animateCamera(CameraUpdateFactory.zoomTo(12));
//        mMap.addMarker(place2);
        ArrayList<String> latilongidata=SelectingLcoation.latilongidata;
        for(int k=0;k<latilongidata.size();k++)
        {
            String dstsplit[]=latilongidata.get(k).split("_");
            place11 = new MarkerOptions().position(new LatLng(Double.parseDouble(dstsplit[0]), Double.parseDouble(dstsplit[1]))).title(dstsplit[2]);
            mMap.addMarker(place11);

        }
        //place11 = new MarkerOptions().position(new LatLng(0, 0)).title("Location next");


    }

    private String getUrl(LatLng origin, LatLng dest, String directionMode) {
        // Origin of route
        String str_origin = "origin=" + origin.latitude + "," + origin.longitude;
        // Destination of route
        String str_dest = "destination=" + dest.latitude + "," + dest.longitude;
        // Mode
        String mode = "mode=" + directionMode;
        // Building the parameters to the web service
        String parameters = str_origin + "&" + str_dest + "&" + mode;
        // Output format
        String output = "json";
        // Building the url to the web service
        String url = "https://maps.googleapis.com/maps/api/directions/" + output + "?" + parameters + "&key=" + getString(R.string.google_maps_key);

        mMap.moveCamera(CameraUpdateFactory.newLatLngZoom(origin,15));

        return url;
    }

    @Override
    public void onTaskDone(Object... values) {
        if (currentPolyline != null)
            currentPolyline.remove();
        currentPolyline = mMap.addPolyline((PolylineOptions) values[0]);
    }
}
