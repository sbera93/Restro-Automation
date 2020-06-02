package com.dmce.androidpothole;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;

public class StartingActivity extends AppCompatActivity {
Button b1,b2,b3;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_starting);
        b1=(Button)findViewById(R.id.button5);
        b2=(Button)findViewById(R.id.button6);
        b3=(Button)findViewById(R.id.button7);

        b1.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
//                Intent I = new Intent(getApplicationContext(),MapActivity.class);
                Intent I = new Intent(getApplicationContext(),SelectingLcoation.class);
//                Intent I = new Intent(getApplicationContext(),SendingFIlefromandroid.class);
                startActivity(I);
            }
        });
        b2.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
//                Intent I = new Intent(getApplicationContext(),MapActivity.class);
                Intent I = new Intent(getApplicationContext(),ScanQRcode.class);
//                Intent I = new Intent(getApplicationContext(),SendingFIlefromandroid.class);
                startActivity(I);
            }
        });
        b3.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent I = new Intent(getApplicationContext(),WebViewActivity.class);
//                Intent I = new Intent(getApplicationContext(),ScanQRcode.class);
//                Intent I = new Intent(getApplicationContext(),SendingFIlefromandroid.class);
                startActivity(I);
            }
        });
    }
}
