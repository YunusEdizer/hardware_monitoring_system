from django.db import models

class Device(models.Model):
    mac_address = models.CharField(max_length=17, primary_key=True, unique=True)
    os_info = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.mac_address

class Location(models.Model):
    device = models.OneToOneField(Device, on_delete=models.CASCADE, related_name='location')
    building = models.CharField(max_length=100)
    floor = models.CharField(max_length=50)
    room = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.building} - {self.floor} - {self.room} ({self.device_id})"

class HardwareSpec(models.Model):
    device = models.OneToOneField(Device, on_delete=models.CASCADE, related_name='hardware')
    cpu_info = models.CharField(max_length=255)
    ram_total = models.CharField(max_length=50)
    vga_info = models.CharField(max_length=255)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Hardware for {self.device_id}"

class HeartbeatLog(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='heartbeats')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device_id} - {self.timestamp}"

class Alert(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=50)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.alert_type} for {self.device_id} - Resolved: {self.is_resolved}"
