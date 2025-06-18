#!/usr/bin/env python

import socket
import time
from machine import Pin

class ESPCAMInterface:
    def __init__(self, espcam_ip, espcam_port=80, timeout=5):
        """
        Initialize ESPCAM Interface
        
        Args:
            espcam_ip (str): IP address of the ESPCAM
            espcam_port (int): Port of the ESPCAM web server (default: 80)
            timeout (int): Connection timeout in seconds (default: 5)
        """
        self.espcam_ip = espcam_ip
        self.espcam_port = espcam_port
        self.timeout = timeout
        self.base_url = f"http://{espcam_ip}:{espcam_port}"
        
    def get_camera_url(self):
        """
        Get the camera streaming URL
        
        Returns:
            str: Full URL to access the camera stream
        """
        return f"{self.base_url}/stream"
    
    def get_capture_url(self):
        """
        Get the camera capture URL for single image
        
        Returns:
            str: Full URL to capture a single image
        """
        return f"{self.base_url}/capture"
    
    def get_web_interface_url(self):
        """
        Get the main web interface URL
        
        Returns:
            str: Full URL to access the camera web interface
        """
        return self.base_url
    
    def is_camera_available(self):
        """
        Check if the ESPCAM is available and responding
        
        Returns:
            bool: True if camera is available, False otherwise
        """
        try:
            # Create a socket connection to test availability
            addr = socket.getaddrinfo(self.espcam_ip, self.espcam_port)[0][-1]
            s = socket.socket()
            s.settimeout(self.timeout)
            s.connect(addr)
            s.close()
            return True
        except Exception as e:
            print(f"ESPCAM not available: {e}")
            return False
    
    def ping_camera(self):
        """
        Ping the camera to ensure it's responsive
        
        Returns:
            bool: True if ping successful, False otherwise
        """
        return self.is_camera_available()
    
    def get_camera_status(self):
        """
        Get camera status information
        
        Returns:
            dict: Status information including availability and URLs
        """
        is_available = self.is_camera_available()
        
        return {
            'available': is_available,
            'ip': self.espcam_ip,
            'port': self.espcam_port,
            'web_url': self.get_web_interface_url(),
            'stream_url': self.get_camera_url(),
            'capture_url': self.get_capture_url(),
            'last_check': time.time()
        }
    
    def format_notification_message(self, base_message="Choro detectado!"):
        """
        Format notification message with camera link
        
        Args:
            base_message (str): Base notification message
            
        Returns:
            str: Formatted message with camera link
        """
        if self.is_camera_available():
            return f"{base_message}\n\nVer câmera: {self.get_web_interface_url()}"
        else:
            return f"{base_message}\n\nCâmera indisponível no momento."
