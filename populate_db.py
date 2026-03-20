import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'disaster_project.settings')
django.setup()

from core.models import DisasterAlert, SafetyGuideline

DisasterAlert.objects.all().delete()
SafetyGuideline.objects.all().delete()

DisasterAlert.objects.create(title="Hurricane Warning: Coastal Region C", description="Evacuation ordered for all residents within 5 miles of the coast.", severity="CRITICAL")
DisasterAlert.objects.create(title="Flash Flood Watch", description="Heavy rainfall expected in the valley area over the next 24 hours.", severity="HIGH")
DisasterAlert.objects.create(title="Air Quality Alert", description="Smoke from distant wildfires is affecting air quality. Sensitive groups should stay indoors.", severity="MEDIUM")

SafetyGuideline.objects.create(category="Earthquake", content="Drop, Cover, and Hold On. Stay away from glass, windows, outside doors and walls, and anything that could fall.")
SafetyGuideline.objects.create(category="Fire", content="Have an evacuation plan. If you see smoke, stay low to the ground. Check doors for heat before opening.")
SafetyGuideline.objects.create(category="Flood", content="Move to higher ground immediately. Do not drive or walk through floodwaters. 'Turn Around, Don't Drown'.")

print("Database populated successfully.")
