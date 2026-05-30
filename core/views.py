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
    # Optional: Clear buffer after reading or keep it circular
    return JsonResponse({'logs': logs})

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
