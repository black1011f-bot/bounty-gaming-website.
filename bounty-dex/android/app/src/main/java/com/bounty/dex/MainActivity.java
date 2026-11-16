package com.bounty.dex;

import android.app.Activity;
import android.os.Bundle;
import android.graphics.Color;
import android.graphics.Typeface;
import android.view.Gravity;
import android.view.View;
import android.widget.LinearLayout;
import android.widget.TextView;

public class MainActivity extends Activity {
    private int dp(float value) {
        return (int) (value * getResources().getDisplayMetrics().density + 0.5f);
    }

    private TextView text(String value, int size, int color, boolean bold) {
        TextView view = new TextView(this);
        view.setText(value);
        view.setTextSize(size);
        view.setTextColor(color);
        view.setGravity(Gravity.CENTER_VERTICAL);
        if (bold) view.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        return view;
    }

    private LinearLayout card(String heading, String body) {
        LinearLayout box = new LinearLayout(this);
        box.setOrientation(LinearLayout.VERTICAL);
        box.setPadding(dp(18), dp(16), dp(18), dp(16));
        box.setBackgroundColor(Color.rgb(27, 31, 43));
        TextView title = text(heading, 17, Color.WHITE, true);
        TextView detail = text(body, 14, Color.rgb(190, 198, 214), false);
        detail.setPadding(0, dp(8), 0, 0);
        box.addView(title);
        box.addView(detail);
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(-1, -2);
        params.bottomMargin = dp(12);
        box.setLayoutParams(params);
        return box;
    }

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().setStatusBarColor(Color.rgb(12, 15, 23));
        getWindow().setNavigationBarColor(Color.rgb(12, 15, 23));

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(22), dp(28), dp(22), dp(20));
        root.setBackgroundColor(Color.rgb(12, 15, 23));

        TextView brand = text("BOUNTY", 14, Color.rgb(88, 166, 255), true);
        root.addView(brand);
        TextView heading = text("Dex", 34, Color.WHITE, true);
        root.addView(heading);
        TextView subtitle = text("Ваш телефон. Большой экран.", 15, Color.rgb(175, 185, 204), false);
        subtitle.setPadding(0, dp(4), 0, dp(24));
        root.addView(subtitle);

        root.addView(card("1. Подключение по USB",
                "Включите «Для разработчиков» и «Отладку по USB» на телефоне. Подключите кабель и подтвердите запрос доступа. На ПК откройте BOUNTY Dex и нажмите «Подключить USB»."));
        root.addView(card("2. Подключение по Wi‑Fi",
                "Подключите телефон и компьютер к одной сети Wi‑Fi. Включите «Беспроводную отладку» в настройках разработчика Android. Для первого сопряжения используйте код и порт из меню «Беспроводная отладка» в приложении BOUNTY Dex на ПК."));
        root.addView(card("Что делает приложение",
                "Это мобильный помощник: он показывает инструкции и помогает подготовить телефон. Передача экрана и управление выполняются приложением BOUNTY Dex на Windows через ADB и scrcpy."));
        TextView footer = text("BOUNTY Dex • Preview 0.1.0", 12, Color.rgb(115, 127, 148), false);
        footer.setGravity(Gravity.CENTER);
        footer.setPadding(0, dp(12), 0, 0);
        root.addView(footer);

        android.widget.ScrollView scroll = new android.widget.ScrollView(this);
        scroll.setFillViewport(true);
        scroll.addView(root);
        setContentView(scroll);
    }
}
