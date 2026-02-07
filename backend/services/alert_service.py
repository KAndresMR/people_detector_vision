import time

class AlertService:
    def __init__(self, cooldown=10):
        self.last_alert = 0
        self.cooldown = cooldown

    def should_alert(self, detections):
        if not detections:
            return False

        now = time.time()
        if now - self.last_alert > self.cooldown:
            self.last_alert = now
            return True

        return False
