from django.shortcuts import render
from django.http import JsonResponse
from wifipumpkin3 import engine, log_buffer
from django.views.decorators.csrf import ensure_csrf_cookie
import json

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
        return JsonResponse({'status': 'success'})

def settings_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        engine.ssid = data.get('ssid', engine.ssid)
        engine.interface = data.get('interface', engine.interface)
        engine.monitor = data.get('monitor', engine.monitor)
        engine.channel = data.get('channel', engine.channel)
        return JsonResponse({'status': 'success'})
    
    return render(request, 'core/settings.html', {
        'engine': engine
    })
