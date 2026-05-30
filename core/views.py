from django.shortcuts import render
from django.http import JsonResponse
from wifipumpkin3 import engine, log_buffer
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import FileResponse
import json
import os

@ensure_csrf_cookie
def dashboard(request):
    return render(request, 'core/dashboard.html', {
        'ssid': engine.ssid,
        'interface': engine.interface,
        'is_running': engine.is_running
    })

def start_attack(request):
    if engine.start_attack():
        return JsonResponse({'status': 'success', 'message': 'Attack started'})
    return JsonResponse({'status': 'error', 'message': 'Attack already running'}, status=400)

def stop_attack(request):
    engine.stop_attack()
    return JsonResponse({'status': 'success', 'message': 'Attack stopped'})

def get_logs(request):
    logs = list(log_buffer)
    return JsonResponse({'logs': logs})

def scan_networks(request):
    if request.method == 'POST':
        action = json.loads(request.body).get('action', 'start')
        if action == 'start':
            engine.start_continuous_scan()
        else:
            engine.stop_continuous_scan()
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'networks': engine.scanned_networks})

def get_clients(request):
    return JsonResponse({
        'clients': engine.get_clients(),
        'leases': engine.dhcp_leases,
        'credentials': engine.credentials
    })

def deauth_target(request):
    if request.method == 'POST':
        target = json.loads(request.body).get('target')
        if engine.deauth_attack(target):
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error'})
    return JsonResponse({'status': 'error'}, status=405)

def update_settings(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        if 'portal' in data:
            engine.portal_template = data['portal']
            engine.log(f"Active portal changed to: {data['portal']}", "INFO")
        if 'interface' in data:
            engine.set_interface(data['interface'])
        if 'monitor' in data:
            engine.toggle_monitor(data['monitor'])
        if 'mitm' in data:
            engine.set_mitm_method(data['mitm'])
        return JsonResponse({'status': 'success'})

def get_hardware_info(request):
    return JsonResponse({
        'interfaces': engine.list_interfaces(),
        'selected': engine.selected_interface,
        'monitor': engine.monitor_mode,
        'mitm': engine.mitm_method
    })

def get_stats(request):
    return JsonResponse(engine.get_stats())

def stealth_mode(request):
    if engine.randomize_mac():
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

def toggle_capture(request):
    if request.method == 'POST':
        action = json.loads(request.body).get('action', 'start')
        if action == 'start':
            engine.start_capture()
        else:
            engine.stop_capture()
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({
        'is_capturing': engine.is_capturing,
        'pcap_path': engine.pcap_path
    })

def download_pcap(request):
    if os.path.exists(engine.pcap_path):
        return FileResponse(open(engine.pcap_path, 'rb'), as_attachment=True, filename='traffic.pcap')
    return JsonResponse({'status': 'error', 'message': 'Capture file not found'}, status=404)

def settings_view(request):
    return render(request, 'core/settings.html', {
        'engine': engine
    })
