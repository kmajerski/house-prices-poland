import pandas as pd
import urllib.request
import json
import time

df = pd.read_csv('Houses.csv', encoding='cp1250')
df = df.drop(columns=['id'])
podejrzane = df[df['year'] < 1800].copy().reset_index(drop=True)

wyniki = []
for i, row in podejrzane.iterrows():
    url = f'https://nominatim.openstreetmap.org/reverse?lat={row["latitude"]}&lon={row["longitude"]}&format=json&accept-language=pl'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'house-prices-pl/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            adres_gps = data.get('display_name', 'brak')
    except Exception as e:
        adres_gps = f'błąd: {e}'

    wyniki.append({
        'adres_w_danych': row['address'],
        'miasto': row['city'],
        'rok': int(row['year']),
        'lat': row['latitude'],
        'lon': row['longitude'],
        'adres_z_gps': adres_gps
    })
    print(f'[{i+1}/18] {row["address"][:40]}')
    time.sleep(1.1)  # Nominatim wymaga przerwy między zapytaniami!

df_wyniki = pd.DataFrame(wyniki)
df_wyniki.to_html('weryfikacja_gps.html', index=False)
print('\n✅ Gotowe! Otwórz plik weryfikacja_gps.html w przeglądarce.')