import os
import json
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import DisasterAlert, SafetyGuideline
from django.conf import settings

try:
    from g4f.client import Client
    client = Client()
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    client = None

def index(request):
    alerts = DisasterAlert.objects.filter(is_active=True).order_by('-date_posted')
    guidelines = SafetyGuideline.objects.all()
    context = {
        'alerts': alerts,
        'guidelines': guidelines,
    }
    return render(request, 'core/index.html', context)

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'core/signup.html', {'form': form})

@csrf_exempt
def chat_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            location = data.get('location', None)
            
            if not user_message:
                return JsonResponse({'error': 'Message is required'}, status=400)

            if location or user_message.upper() == 'SOS':
                if location:
                    lat = location.get('latitude')
                    lon = location.get('longitude')
                    sos_msg = f"User has triggered an EMERGENCY SOS. Their exact coordinates are Latitude {lat}, Longitude {lon}. Dispatch immediate rescue and provide reassuring instructions."
                    fallback_text = f"EMERGENCY DISPATCH TRIGGERED: Rescue team has been sent to coordinates {lat}, {lon}. Please stay calm, remain where you are if safety permits, and conserve your phone battery."
                else:
                    sos_msg = "User has triggered an EMERGENCY SOS but their location is unknown. Dispatch rescue assistance protocols and ask them to describe their surroundings visually immediately."
                    fallback_text = "EMERGENCY DISPATCH TRIGGERED: Rescue team mobilized, but your location is unknown! PLEASE REPLY TO THIS CHAT WITH YOUR EXACT ADDRESS OR LOCATION IMMEDIATELY!"
                try:
                    if client:
                        response = client.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": sos_msg}])
                        return JsonResponse({'response': response.choices[0].message.content})
                except Exception:
                    pass
                return JsonResponse({'response': fallback_text})

            ai_text = None
            try:
                if client:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "system", "content": "You are a helpful disaster management AI assistant. Provide concise, helpful, and safety-focused responses."}, {"role": "user", "content": user_message}]
                    )
                    ai_text = response.choices[0].message.content
            except Exception:
                pass
            
            if not ai_text:
                msg_lower = user_message.lower()
                if 'earthquake' in msg_lower:
                    ai_text = "Drop, Cover, and Hold On! Stay away from glass, windows, and anything that could fall. If you are outdoors, stay in the open away from buildings and power lines."
                elif 'fire' in msg_lower:
                    ai_text = "If you are indoors, stay low to the floor, check doors for heat before opening, and evacuate immediately. Call emergency services once safe."
                elif 'flood' in msg_lower:
                    ai_text = "Move to higher ground immediately. Do not walk, swim, or drive through flood waters. Turn Around, Don't Drown!"
                elif 'hurricane' in msg_lower or 'tornado' in msg_lower:
                    ai_text = "Seek shelter in a small, windowless interior room or hallway on the lowest floor of a sturdy building. Protect your head and neck."
                else:
                    ai_text = "I am currently operating in offline fallback mode as the free AI proxy network is temporarily busy. For emergencies regarding earthquakes, fires, floods, or hurricanes/tornadoes, please mention the specific disaster type."
            
            return JsonResponse({'response': ai_text})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid method'}, status=405)
