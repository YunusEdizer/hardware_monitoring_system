from django.contrib import admin
from .models import Device, Location, HardwareSpec, HeartbeatLog, Alert


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('mac_address', 'os_info', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('mac_address', 'os_info')
    ordering = ('-created_at',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('device', 'building', 'floor', 'room')
    search_fields = ('device__mac_address', 'building', 'room')


@admin.register(HardwareSpec)
class HardwareSpecAdmin(admin.ModelAdmin):
    list_display = ('device', 'cpu_info', 'ram_total', 'vga_info', 'last_updated')
    search_fields = ('device__mac_address', 'cpu_info')
    ordering = ('-last_updated',)


@admin.register(HeartbeatLog)
class HeartbeatLogAdmin(admin.ModelAdmin):
    list_display = ('device', 'timestamp')
    list_filter = ('device',)
    ordering = ('-timestamp',)


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('device', 'alert_type', 'message', 'is_resolved', 'created_at')
    list_filter = ('is_resolved', 'alert_type')
    search_fields = ('device__mac_address', 'message')
    ordering = ('-created_at',)
    actions = ['mark_resolved']

    @admin.action(description='Secili uyarilari cozuldu olarak isaretle')
    def mark_resolved(self, request, queryset):
        queryset.update(is_resolved=True)
