#!/usr/bin/env python3
"""
MLflow Monitoring Script for 52Pi Fan HAT (Clean Design)
- OLED Display: MLflow status + system stats (borderless)
- LED Indicators: System, MLflow health, network, temperature
- Fan Control: Simple on/off based on temperature

Hardware: 52Pi Fan HAT EP-0152 with 0.91" OLED (128x32)
GPIO Mapping: Fan=14, LEDs=[19,13,6,5], OLED=I2C@0x3C

Architecture: nginx (port 5000) → MLflow (127.0.0.1:5001)
"""

import time
import requests
import psutil
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from gpiozero import LED, OutputDevice
import subprocess
import socket

# Hardware Configuration
OLED_ADDRESS = 0x3C
FAN_GPIO = 14
LED_GPIOS = [19, 13, 6, 5]  # [Status, Service, Network, Temp]

# Temperature thresholds (Celsius)
TEMP_FAN_ON = 40
TEMP_WARNING = 45

class MLflowMonitor:
    def __init__(self):
        # Initialize OLED
        try:
            serial = i2c(port=1, address=OLED_ADDRESS)
            self.oled = ssd1306(serial, width=128, height=32)
            self.oled_available = True
            print("OLED initialized successfully")
        except Exception as e:
            print(f"OLED initialization failed: {e}")
            self.oled_available = False
        
        # Initialize LEDs
        try:
            self.leds = [LED(gpio) for gpio in LED_GPIOS]
            print("LEDs initialized successfully")
        except Exception as e:
            print(f"LED initialization failed: {e}")
            self.leds = []
        
        # Initialize Fan
        try:
            self.fan = OutputDevice(FAN_GPIO)
            print("Fan initialized successfully")
        except Exception as e:
            print(f"Fan initialization failed: {e}")
            self.fan = None
        
    def get_cpu_temperature(self):
        """Get CPU temperature in Celsius"""
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = int(f.read().strip()) / 1000
            return temp
        except:
            return 0
    
    def control_fan(self, temp):
        """Control fan - simple on/off"""
        if self.fan is None:
            return "disabled"
            
        if temp > TEMP_FAN_ON:
            self.fan.on()
            return "on"
        else:
            self.fan.off()
            return "off"
    
    def check_mlflow_health(self):
        """Check if MLflow is healthy"""
        try:
            # Check if nginx is running (our security layer)
            result = subprocess.run(['systemctl', 'is-active', 'nginx'], 
                                  capture_output=True, text=True)
            nginx_running = result.stdout.strip() == 'active'
            
            # Check if MLflow service is running
            result = subprocess.run(['systemctl', 'is-active', 'mlflow'], 
                                  capture_output=True, text=True)
            mlflow_running = result.stdout.strip() == 'active'
            
            # Test local MLflow connection (internal port)
            response = requests.get('http://127.0.0.1:5001', timeout=5)
            mlflow_responding = response.status_code == 200
            
            return nginx_running and mlflow_running and mlflow_responding
        except:
            return False
    
    def check_network(self):
        """Check network connectivity"""
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except:
            return False
    
    def get_system_stats(self):
        """Get system statistics"""
        cpu_temp = self.get_cpu_temperature()
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        return {
            'cpu_temp': cpu_temp,
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent
        }
    
    def update_oled(self, stats, mlflow_healthy, network_ok):
        """Update OLED display - Clean borderless design"""
        if not self.oled_available:
            return
            
        with canvas(self.oled) as draw:
            # Header
            status = "RUNNING" if mlflow_healthy else "ERROR"
            draw.text((0, 0), f"MLFLOW {status}", fill="white")
            
            # System stats
            draw.text((0, 12), f"CPU: {stats['cpu_percent']:.0f}% {stats['cpu_temp']:.1f}C", fill="white")
            draw.text((0, 22), f"RAM: {stats['memory_percent']:.0f}% Net: {'OK' if network_ok else 'ERR'}", fill="white")
    
    def control_leds(self, stats, mlflow_healthy, network_ok):
        """Control LED indicators"""
        if not self.leds:
            return
            
        temp_warning = stats['cpu_temp'] > TEMP_WARNING
        current_time = int(time.time() * 2)  # 2Hz blink
        
        # LED 0: System Status (always on)
        self.leds[0].on()
        
        # LED 1: MLflow Health
        if mlflow_healthy:
            self.leds[1].on()
        else:
            if current_time % 2:
                self.leds[1].on()
            else:
                self.leds[1].off()
        
        # LED 2: Network Status
        if network_ok:
            self.leds[2].on()
        else:
            if current_time % 2:
                self.leds[2].on()
            else:
                self.leds[2].off()
        
        # LED 3: Temperature Warning
        if temp_warning:
            if current_time % 2:
                self.leds[3].on()
            else:
                self.leds[3].off()
        else:
            self.leds[3].off()
    
    def run_monitoring_loop(self):
        """Main monitoring loop"""
        print("MLflow monitoring started...")
        
        while True:
            try:
                stats = self.get_system_stats()
                mlflow_healthy = self.check_mlflow_health()
                network_ok = self.check_network()
                fan_status = self.control_fan(stats['cpu_temp'])
                
                self.update_oled(stats, mlflow_healthy, network_ok)
                self.control_leds(stats, mlflow_healthy, network_ok)
                
                # Log every 30 seconds
                if int(time.time()) % 30 == 0:
                    print(f"MLflow: {'OK' if mlflow_healthy else 'ERROR'} | "
                          f"Temp: {stats['cpu_temp']:.1f}C | "
                          f"Fan: {fan_status} | "
                          f"CPU: {stats['cpu_percent']:.0f}% | "
                          f"RAM: {stats['memory_percent']:.0f}%")
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                print("\nMonitoring stopped")
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(5)
        
        self.cleanup()
    
    def cleanup(self):
        """Clean up"""
        try:
            for led in self.leds:
                led.off()
            if self.fan:
                self.fan.off()
            if self.oled_available:
                self.oled.clear()
        except:
            pass

if __name__ == "__main__":
    monitor = MLflowMonitor()
    monitor.run_monitoring_loop()
