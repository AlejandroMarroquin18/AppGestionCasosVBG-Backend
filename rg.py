from django.db.models import Count
from agenda.models import Event  # ajusta el import al nombre real de tu app

# Buscar IDs duplicados
duplicates = (
    Event.objects.values('google_event_id')
    .annotate(total=Count('id'))
    .filter(total__gt=1)
)

print("Duplicados encontrados:", duplicates.count())
for dup in duplicates:
    print(dup)
