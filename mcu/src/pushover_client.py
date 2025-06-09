import network
import urequests
import time

class PushoverClient:
    def __init__(self, ssid, password, pushover_user_key, pushover_api_token):
        """Initialize the Pushover client with Wi-Fi and Pushover credentials."""
        self.ssid = ssid
        self.password = password
        self.pushover_user_key = pushover_user_key
        self.pushover_api_token = pushover_api_token
        self.pushover_api_url = "https://api.pushover.net/1/messages.json"
        self.wlan = network.WLAN(network.STA_IF)
    
    def connect_wifi(self):
        """Connect to the Wi-Fi network."""
        self.wlan.active(True)
        self.wlan.connect(self.ssid, self.password)
        
        max_attempts = 10
        for _ in range(max_attempts):
            if self.wlan.isconnected():
                print("Connected to Wi-Fi:", self.wlan.ifconfig())
                return True
            time.sleep(1)
        print("Failed to connect to Wi-Fi")
        return False
    
    def send_notification(self, message, title="Pico W Notification"):
        """Send a notification to the smartphone via Pushover."""
        if not self.wlan.isconnected():
            print("Wi-Fi not connected. Attempting to reconnect...")
            self.connect_wifi()
        
        if self.wlan.isconnected():
            payload = {
                "token": self.pushover_api_token,
                "user": self.pushover_user_key,
                "message": message,
                "title": title
            }
            try:
                response = urequests.post(self.pushover_api_url, json=payload)
                if response.status_code == 200:
                    print("Notification sent successfully")
                    return True
                else:
                    print("Failed to send notification:", response.text)
                    return False
                response.close()
            except Exception as e:
                print("Error sending notification:", e)
                return False
        else:
            print("Cannot send notification: No Wi-Fi connection")
            return False
