package com.bounty.dex;
import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebView;
import android.webkit.WebSettings;
public class MainActivity extends Activity {
 @Override public void onCreate(Bundle state) {
  super.onCreate(state);
  getWindow().setStatusBarColor(0xfff5f5f7); getWindow().setNavigationBarColor(0xfff5f5f7);
  getWindow().getDecorView().setSystemUiVisibility(0x00002000 | 0x00000010);
  WebView view = new WebView(this); view.setBackgroundColor(0xfff5f5f7);
  WebSettings settings=view.getSettings(); settings.setJavaScriptEnabled(false); settings.setDomStorageEnabled(false);
  view.loadUrl("file:///android_asset/index.html"); setContentView(view);
 }
}
