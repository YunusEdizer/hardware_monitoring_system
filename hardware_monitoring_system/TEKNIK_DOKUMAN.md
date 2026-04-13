# Teknik Doküman — Donanım İzleme Sistemi

**Ders Kodu / Adı:** Sunucu Taraflı Web Programlama  
**Proje Adı:** Hardware Monitoring System (Donanım İzleme Sistemi)  
**Akademik Dönem:** 2024–2025 Bahar Yarıyılı

---

## A. Model Sınıf Diyagramı

```
┌─────────────────────────────────┐
│             Device              │
├─────────────────────────────────┤
│ + mac_address: CharField (PK)   │
│ + os_info: CharField            │
│ + is_active: BooleanField       │
│ + created_at: DateTimeField     │
└────────────┬────────────────────┘
             │
     ┌───────┼──────────────────────────┐
     │       │                          │
     │ (OneToOne)                 (ForeignKey)
     │       │                          │
     ▼       ▼                          ▼
┌──────────────────┐    ┌──────────────────────────┐
│    Location      │    │      HeartbeatLog         │
├──────────────────┤    ├──────────────────────────┤
│ + device (FK)    │    │ + device (FK)             │
│ + building: Char │    │ + timestamp: DateTimeField│
│ + floor: Char    │    └──────────────────────────┘
│ + room: Char     │
└──────────────────┘    ┌──────────────────────────┐
                        │          Alert            │
┌──────────────────┐    ├──────────────────────────┤
│  HardwareSpec    │    │ + device (FK)             │
├──────────────────┤    │ + alert_type: CharField   │
│ + device (FK)    │    │ + message: TextField      │
│ + cpu_info: Char │    │ + is_resolved: BooleanFld │
│ + ram_total: Char│    │ + created_at: DateTimeFld │
│ + vga_info: Char │    └──────────────────────────┘
│ + last_updated   │
└──────────────────┘
```

**İlişki Özeti:**
- `Device` ←→ `Location`: OneToOne (her cihazın en fazla 1 konumu olur)
- `Device` ←→ `HardwareSpec`: OneToOne (her cihazın 1 donanım kaydı olur)
- `Device` ←→ `HeartbeatLog`: ForeignKey/One-to-Many (bir cihazın çok sayıda heartbeat kaydı olabilir)
- `Device` ←→ `Alert`: ForeignKey/One-to-Many (bir cihazın çok sayıda uyarısı olabilir)

---

## B. UI Sayfa Ekran Görüntüleri

> **Not:** Ekran görüntüleri, uygulama çalıştırılarak alınmalıdır.  
> Sunucu başlatma: `python manage.py runserver`  
> Tarayıcı adresi: `http://127.0.0.1:8000/`

### Sayfa 1 — Cihaz Listesi (`/api/monitoring/ui/devices/`)

- Kayıtlı tüm cihazları tablo halinde listeler
- Her satırda: MAC Adresi, İşletim Sistemi, Aktiflik Durumu (Active/Inactive badge), Detay butonu
- Boş durumda "No devices registered yet." mesajı gösterilir

### Sayfa 2 — Uyarı Listesi (`/api/monitoring/ui/alerts/`)

- Tüm uyarıları tarih sıralamasıyla listeler
- Her satırda: Tarih, Cihaz MAC, Uyarı Türü, Mesaj, Durum (Resolved/Pending badge)

### Form 1 — Konum Ekleme (`/api/monitoring/ui/add-location/`)

- Cihaz seçimi (dropdown)
- Bina adı, Kat, Oda numarası giriş alanları
- "Save Location" butonu

### Form 2 — Uyarı Ekleme (`/api/monitoring/ui/add-alert/`)

- Cihaz seçimi (dropdown)
- Uyarı türü text girişi (örn: CPU_HIGH, DISK_FULL)
- Mesaj textarea alanı
- "Uyarıyı Kaydet" butonu

---

## C. Model ve API Python Kodları

### C.1 — Modeller (`monitoring/models.py`)

```python
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
```

---

### C.2 — Serializer'lar (`monitoring/serializers.py`)

```python
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
```

---

### C.3 — API View'ları (`monitoring/views.py`)

```python
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Device, Location, HardwareSpec, HeartbeatLog, Alert
from .serializers import (
    DeviceSerializer, LocationSerializer, HardwareSpecSerializer,
    HeartbeatLogSerializer, AlertSerializer
)

# API 1 — Yeni cihaz kaydı (POST)
@api_view(['POST'])
def register_device(request):
    serializer = DeviceSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# API 2 — Heartbeat (canlilik sinyali) alma (POST)
@api_view(['POST'])
def receive_heartbeat(request):
    serializer = HeartbeatLogSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# API 3 — Tüm cihazları listeleme (GET)
@api_view(['GET'])
def list_devices(request):
    devices = Device.objects.all()
    serializer = DeviceSerializer(devices, many=True)
    return Response(serializer.data)

# API 4 — Tek cihaz detayı (GET)
@api_view(['GET'])
def device_detail(request, pk):
    try:
        device = Device.objects.get(pk=pk)
    except Device.DoesNotExist:
        return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = DeviceSerializer(device)
    return Response(serializer.data)

# API 5 — Konum ekleme (POST)
@api_view(['POST'])
def add_location(request):
    serializer = LocationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# API 6 — Tüm konumları listeleme (GET)
@api_view(['GET'])
def list_locations(request):
    locations = Location.objects.all()
    serializer = LocationSerializer(locations, many=True)
    return Response(serializer.data)

# API 7 — Donanım bilgisi güncelleme/ekleme (POST)
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

# API 8 — Tek cihazın donanım bilgisi (GET)
@api_view(['GET'])
def get_hardware(request, device_id):
    try:
        hardware = HardwareSpec.objects.get(device_id=device_id)
    except HardwareSpec.DoesNotExist:
        return Response({'error': 'Hardware not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = HardwareSpecSerializer(hardware)
    return Response(serializer.data)

# API 9 — Tüm uyarıları listeleme (GET)
@api_view(['GET'])
def list_alerts(request):
    alerts = Alert.objects.all()
    serializer = AlertSerializer(alerts, many=True)
    return Response(serializer.data)

# API 10 — Uyarıyı "çözüldü" işaretleme (POST/PATCH)
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

# UI View 1 — Cihaz listesi
def device_list_view(request):
    devices = Device.objects.all()
    return render(request, 'monitoring/device_list.html', {'devices': devices})

# UI View 2 — Uyarı listesi
def alert_list_view(request):
    alerts = Alert.objects.all().order_by('-created_at')
    return render(request, 'monitoring/alert_list.html', {'alerts': alerts})

# UI View 3 — Uyarı ekleme formu
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
            error = 'Seçilen cihaz bulunamadı.'
    devices = Device.objects.all()
    return render(request, 'monitoring/add_alert.html', {'devices': devices, 'error': error})

# UI View 4 — Konum ekleme formu
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
            error = 'Seçilen cihaz bulunamadı.'
    devices = Device.objects.all()
    return render(request, 'monitoring/add_location.html', {'devices': devices, 'error': error})
```

---

### C.4 — URL Tanımları (`monitoring/urls.py`)

```python
from django.urls import path
from . import views

urlpatterns = [
    # API Endpoints
    path('devices/',                  views.list_devices,      name='list_devices'),
    path('devices/register/',         views.register_device,   name='register_device'),
    path('devices/<str:pk>/',         views.device_detail,     name='device_detail'),
    path('heartbeats/',               views.receive_heartbeat, name='receive_heartbeat'),
    path('locations/',                views.list_locations,    name='list_locations'),
    path('locations/add/',            views.add_location,      name='add_location'),
    path('hardware/',                 views.update_hardware,   name='update_hardware'),
    path('hardware/<str:device_id>/', views.get_hardware,      name='get_hardware'),
    path('alerts/',                   views.list_alerts,       name='list_alerts'),
    path('alerts/<int:pk>/resolve/',  views.resolve_alert,     name='resolve_alert'),

    # UI Sayfaları
    path('ui/devices/',              views.device_list_view,  name='ui_device_list'),
    path('ui/alerts/',               views.alert_list_view,   name='ui_alert_list'),
    path('ui/add-location/',         views.add_location_view, name='ui_add_location'),
    path('ui/add-alert/',            views.add_alert_view,    name='ui_add_alert'),
]
```

---

## Özet — Gereksinim Karşılama Tablosu

| Gereksinim                        | Durum | Detay                                          |
|-----------------------------------|-------|------------------------------------------------|
| En az 5 model                     | ✅    | Device, Location, HardwareSpec, HeartbeatLog, Alert |
| URL yönlendirmeleri               | ✅    | core/urls.py + monitoring/urls.py              |
| En az 10 API view                 | ✅    | 10 API endpoint (REST)                         |
| En az 2 giriş formu (UI)          | ✅    | Konum Ekle + Uyarı Ekle                        |
| En az 2 varlık listeleme sayfası  | ✅    | Cihaz Listesi + Uyarı Listesi                  |
