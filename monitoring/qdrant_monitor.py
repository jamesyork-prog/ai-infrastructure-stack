#!/usr/bin/env python3
"""
Qdrant Monitoring Script for 52Pi Fan HAT (Clean Design)
- OLED Display: Qdrant status + system stats (borderless)
- LED Indicators: System, Qdrant health, network, temperature
- Fan Control: Simple on/off based on temperature

Hardware: 52Pi Fan HAT EP-0152 with 0.91" OLED (128x32)
GPIO Mapping: Fan=14, LEDs=[19,13,6,5], OLED=I2C@0x3C
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

class QdrantMonitor:
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
    
    def check_qdrant_health(self):
        """Check if Qdrant is healthy"""
        try:
            # Check container status
            result = subprocess.run(['docker', 'ps', '--filter', 'name=qdrant', '--format', '{{.Status}}'], 
                                  capture_output=True, text=True)
            container_running = 'Up' in result.stdout
            
            # Test Qdrant API
            response = requests.get('http://localhost:6333', timeout=5)
            qdrant_responding = response.status_code == 200
            
            return container_running and qdrant_responding
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
    
    def update_oled(self, stats, qdrant_healthy, network_ok):
        """Update OLED display - Clean borderless design"""
        if not self.oled_available:
            return
            
        with canvas(self.oled) as draw:
            # Header
            status = "RUNNING" if qdrant_healthy else "ERROR"
            draw.text((0, 0), f"QDRANT {status}", fill="white")
            
            # System stats
            draw.text((0, 12), f"CPU: {stats['cpu_percent']:.0f}% {stats['cpu_temp']:.1f}C", fill="white")
            draw.text((0, 22), f"RAM: {stats['memory_percent']:.0f}% Net: {'OK' if network_ok else 'ERR'}", fill="white")
    
    def control_leds(self, stats, qdrant_healthy, network_ok):
        """Control LED indicators"""
        if not self.leds:
            return
            
        temp_warning = stats['cpu_temp'] > TEMP_WARNING
        current_time = int(time.time() * 2)  # 2Hz blink
        
        # LED 0: System Status (always on)
        self.leds[0].on()
        
        # LED 1: Qdrant Health
        if qdrant_healthy:
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
        print("Qdrant monitoring started...")
        
        while True:
            try:
                stats = self.get_system_stats()
                qdrant_healthy = self.check_qdrant_health()
                network_ok = self.check_network()
                fan_status = self.control_fan(stats['cpu_temp'])
                
                self.update_oled(stats, qdrant_healthy, network_ok)
                self.control_leds(stats, qdrant_healthy, network_ok)
                
                # Log every 30 seconds
                if int(time.time()) % 30 == 0:
                    print(f"Qdrant: {'OK' if qdrant_healthy else 'ERROR'} | "
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
    monitor = QdrantMonitor()
    monitor.run_monitoring_loop()
