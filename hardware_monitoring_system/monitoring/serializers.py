from rest_framework import serializers
from .models import Device, Location, HardwareSpec, HeartbeatLog, Alert

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = '__all__'

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class HardwareSpecSerializer(serializers.ModelSerializer):
    class Meta:
        model = HardwareSpec
        fields = '__all__'

class HeartbeatLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeartbeatLog
        fields = '__all__'

class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = '__all__'
