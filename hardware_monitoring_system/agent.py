import platform
import uuid
import psutil
import requests

SERVER_URL = "http://127.0.0.1:8000/api/monitoring"


def get_mac_address():
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0, 8*6, 8)][::-1])
    return mac.upper()


def get_gpu_info():
    try:
        import subprocess
        if platform.system() == "Windows":
            result = subprocess.check_output(
                "wmic path win32_VideoController get name",
                shell=True, text=True, stderr=subprocess.DEVNULL
            )
            lines = [l.strip() for l in result.strip().splitlines() if l.strip() and l.strip() != "Name"]
            return lines[0] if lines else "Bilinmeyen GPU"
        else:
            return "Bilinmeyen GPU"
    except Exception:
        return "Bilinmeyen GPU"


def get_system_info():
    return {
        "mac_address": get_mac_address(),
        "os_info": f"{platform.system()} {platform.release()}",
        "cpu_info": platform.processor() or "Bilinmeyen CPU",
        "ram_total": str(round(psutil.virtual_memory().total / (1024 ** 3), 2)) + " GB",
        "vga_info": get_gpu_info(),
    }


def register_device(info):
    payload = {
        "mac_address": info["mac_address"],
        "os_info": info["os_info"],
        "is_active": True,
    }
    try:
        response = requests.post(f"{SERVER_URL}/devices/register/", json=payload, timeout=5)
        if response.status_code == 201:
            print("[OK] Cihaz basariyla kaydedildi.")
        elif response.status_code == 400 and "mac_address" in response.text:
            print("[INFO] Bu cihaz zaten sistemde kayitli.")
        else:
            print(f"[HATA] Kayit: {response.text}")
    except requests.exceptions.ConnectionError:
        print("[HATA] Sunucuya ulasilamiyor! Django runserver calisiyor mu?")
        raise SystemExit(1)


def send_hardware_spec(info):
    payload = {
        "device": info["mac_address"],
        "cpu_info": info["cpu_info"],
        "ram_total": info["ram_total"],
        "vga_info": info["vga_info"],
    }
    try:
        response = requests.post(f"{SERVER_URL}/hardware/", json=payload, timeout=5)
        if response.status_code in (200, 201):
            print("[OK] Donanim bilgisi guncellendi.")
        else:
            print(f"[HATA] Donanim: {response.text}")
    except requests.exceptions.ConnectionError:
        print("[HATA] Donanim bilgisi gonderilemedi.")


def send_heartbeat(mac_address):
    payload = {"device": mac_address}
    try:
        response = requests.post(f"{SERVER_URL}/heartbeats/", json=payload, timeout=5)
        if response.status_code == 201:
            print(f"[OK] Heartbeat gonderildi.")
        else:
            print(f"[HATA] Heartbeat: {response.text}")
    except requests.exceptions.ConnectionError:
        print("[HATA] Heartbeat gonderilemedi.")


if __name__ == "__main__":
    print("--- Donanim Izleme Ajani Baslatildi ---")
    info = get_system_info()
    print(f"[MAC] {info['mac_address']} | [OS] {info['os_info']}")

    register_device(info)
    send_hardware_spec(info)
    send_heartbeat(info["mac_address"])

    print("--- Tamamlandi ---")
