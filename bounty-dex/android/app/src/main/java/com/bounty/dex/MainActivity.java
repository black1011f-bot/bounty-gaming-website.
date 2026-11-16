package com.bounty.dex;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;

public class MainActivity extends Activity {
    @Override
    public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().setStatusBarColor(0xff0d0f14);
        getWindow().setNavigationBarColor(0xff0d0f14);
        getWindow().getDecorView().setSystemUiVisibility(0);

        WebView view = new WebView(this);
        view.setBackgroundColor(0xff0d0f14);
        WebSettings settings = view.getSettings();
        settings.setJavaScriptEnabled(false);
        settings.setDomStorageEnabled(false);
        view.loadUrl("file:///android_asset/index.html");
        setContentView(view);
    }
}
