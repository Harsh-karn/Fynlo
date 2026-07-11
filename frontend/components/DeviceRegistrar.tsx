"use client";

import { useEffect } from "react";
import api from "@/lib/api";

interface AndroidInterface {
  setApiKey: (key: string) => void;
}

declare global {
  interface Window {
    Android?: AndroidInterface;
  }
}

export function DeviceRegistrar() {
  useEffect(() => {
    async function registerDevice() {
      // Check if we already registered this device
      if (localStorage.getItem("fynlo_device_registered")) return;

      // Ensure we are inside the Android WebView
      if (typeof window !== "undefined" && window.Android && window.Android.setApiKey) {
        try {
          const res = await api.post("/sms/devices/register", {
            device_name: "Fynlo Android App"
          });
          
          if (res.data && res.data.api_key) {
            // Pass the API key to Android Native
            window.Android.setApiKey(res.data.api_key);
            localStorage.setItem("fynlo_device_registered", "true");
            console.log("Device successfully registered and linked to Android App!");
          }
        } catch (error) {
          console.error("Failed to register device", error);
        }
      }
    }

    registerDevice();
  }, []);

  return null; // Hidden component
}
