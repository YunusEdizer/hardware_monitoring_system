from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Device, Location, HardwareSpec, HeartbeatLog, Alert
from .serializers import (
    DeviceSerializer, LocationSerializer, HardwareSpecSerializer,
    HeartbeatLogSerializer, AlertSerializer
)

# 1. Yeni cihaz kaydı (POST)
@api_view(['POST'])
def register_device(request):
    serializer = DeviceSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 2. Sinyal (Heartbeat) alma (POST)
@api_view(['POST'])
def receive_heartbeat(request):
    serializer = HeartbeatLogSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 3. Tüm cihazları listeleme (GET)
@api_view(['GET'])
def list_devices(request):
    devices = Device.objects.all()
    serializer = DeviceSerializer(devices, many=True)
    return Response(serializer.data)

# 4. Tek bir cihazın detayını getirme (GET)
@api_view(['GET'])
def device_detail(request, pk):
    try:
        device = Device.objects.get(pk=pk)
    except Device.DoesNotExist:
        return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = DeviceSerializer(device)
    return Response(serializer.data)

# 5. Konum (Location) ekleme (POST)
@api_view(['POST'])
def add_location(request):
    serializer = LocationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 6. Tüm konumları listeleme (GET)
@api_view(['GET'])
def list_locations(request):
    locations = Location.objects.all()
    serializer = LocationSerializer(locations, many=True)
    return Response(serializer.data)

# 7. Donanım (HardwareSpec) güncelleme (POST)
@api_view(['POST'])
def update_hardware(request):
    device_id = request.data.get('device')
    existing = HardwareSpec.objects.filter(device_id=device_id).first()
    if existing:
        serializer = HardwareSpecSerializer(existing, data=request.data, partial=True)
        response_status = status.HTTP_200_OK
    else:
        serializer = HardwareSpecSerializer(data=request.data)
        response_status = status.HTTP_201_CREATED

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=response_status)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 8. Tek cihazın donanım bilgisini getirme (GET)
@api_view(['GET'])
def get_hardware(request, device_id):
    try:
        hardware = HardwareSpec.objects.get(device_id=device_id)
    except HardwareSpec.DoesNotExist:
        return Response({'error': 'Hardware not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = HardwareSpecSerializer(hardware)
    return Response(serializer.data)

# 9. Tüm uyarıları (Alerts) listeleme (GET)
@api_view(['GET'])
def list_alerts(request):
    alerts = Alert.objects.all()
    serializer = AlertSerializer(alerts, many=True)
    return Response(serializer.data)

# 10. Bir uyarıyı "çözüldü" olarak işaretleme (POST/PATCH)
@api_view(['POST', 'PATCH'])
def resolve_alert(request, pk):
    try:
        alert = Alert.objects.get(pk=pk)
    except Alert.DoesNotExist:
        return Response({'error': 'Alert not found'}, status=status.HTTP_404_NOT_FOUND)
    
    alert.is_resolved = True
    alert.save()
    serializer = AlertSerializer(alert)
    return Response(serializer.data)

# --- UI VIEWS ---

def device_list_view(request):
    devices = Device.objects.all()
    return render(request, 'monitoring/device_list.html', {'devices': devices})

def alert_list_view(request):
    alerts = Alert.objects.all().order_by('-created_at')
    return render(request, 'monitoring/alert_list.html', {'alerts': alerts})

def add_alert_view(request):
    error = None
    if request.method == 'POST':
        device_mac = request.POST.get('device')
        alert_type = request.POST.get('alert_type')
        message = request.POST.get('message')
        try:
            device = Device.objects.get(mac_address=device_mac)
            Alert.objects.create(device=device, alert_type=alert_type, message=message)
            return redirect('ui_alert_list')
        except Device.DoesNotExist:
            error = 'Secilen cihaz bulunamadi.'

    devices = Device.objects.all()
    return render(request, 'monitoring/add_alert.html', {'devices': devices, 'error': error})

def add_location_view(request):
    error = None
    if request.method == 'POST':
        device_mac = request.POST.get('device')
        building = request.POST.get('building')
        floor = request.POST.get('floor')
        room = request.POST.get('room')
        try:
            device = Device.objects.get(mac_address=device_mac)
            Location.objects.update_or_create(
                device=device,
                defaults={'building': building, 'floor': floor, 'room': room}
            )
            return redirect('ui_device_list')
        except Device.DoesNotExist:
            error = 'Secilen cihaz bulunamadi.'

    devices = Device.objects.all()
    return render(request, 'monitoring/add_location.html', {'devices': devices, 'error': error})
