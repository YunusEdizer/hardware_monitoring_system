# Hardware Monitoring System

Django ve REST Framework ile geliştirilen sistem donanımı izleme ve yönetim platformu.

## 📋 Açıklama

Hardware Monitoring System, ağ üzerindeki bilgisayarların donanım bilgilerini merkezi olarak izleyen bir web uygulamasıdır. CPU, RAM, disk ve diğer bileşenleri gerçek zamanlı takip eder. RESTful API ile entegrasyona olanak tanır.

## 🛠️ Teknolojiler

- **Python 3.12**
- **Django 5.x**
- **Django REST Framework**
- **PostgreSQL** (Supabase)
- **psutil** - Sistem izleme
- **Bootstrap 5** - Frontend

## 🚀 Kurulum

```bash
# Repository'yi klonlayın
git clone https://github.com/YunusEdizer/hardware_monitoring_system.git

# Proje klasörüne gidin
cd hardware_monitoring_system

# Gerekli paketleri yükleyin
pip install -r requirements.txt

# Veritabanı ayarlarını yapılandırın
# core/settings.py dosyasını güncelleyin

# Tabloları oluşturun
python manage.py migrate

# Sunucuyu başlatın
python manage.py runserver
```

## 📊 Özellikler

- **Cihaz Yönetimi**: Bilgisayarları kayıt etme ve izleme
- **Donanım Bilgisi**: CPU, RAM, VGA, Disk bilgisi
- **Canlilik Takibi**: Heartbeat sinyalleri
- **Uyarı Sistemi**: Eşik değerlerini aşan uyarılar
- **REST API**: Tam teşekküllü API endpoints
- **Web Arayüzü**: Django Templates + Bootstrap

## 📡 API Endpoints

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| GET | `/api/monitoring/devices/` | Tüm cihazlar |
| POST | `/api/monitoring/devices/register/` | Cihaz kaydet |
| GET | `/api/monitoring/devices/<mac>/` | Cihaz detayı |
| POST | `/api/monitoring/heartbeats/` | Canlilik sinyali |
| GET | `/api/monitoring/alerts/` | Tüm uyarılar |
| PATCH | `/api/monitoring/alerts/<id>/resolve/` | Uyarıyı çöz |

## 🔧 Ajan Uygulaması

`agent.py` dosyası izlenecek bilgisayarlarda çalıştırılır:

```bash
python agent.py
```

**Toplanan Veriler:**
- MAC Adresi
- İşletim Sistemi
- İşlemci Bilgisi
- RAM Miktarı

## 👨‍💻 Geliştirici

[Yunus Edizer](https://github.com/YunusEdizer)
