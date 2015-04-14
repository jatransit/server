package com.jamrockmedz.jatransittest;

import android.app.Application;
import android.content.Context;


/**
 * Created by Jamrockmedz on 16/03/2015.
 */
public class ThisApplication extends Application {

    private static ThisApplication sInstance;

    public void onCreate()
    {
        super.onCreate();
        sInstance = this;

    }

    public static ThisApplication getsInstance()
    {
        return sInstance;
    }

    public static Context getAppContext()
    {
        return sInstance.getApplicationContext();
    }
}
