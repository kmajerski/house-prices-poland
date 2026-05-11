import pandas as pd
import sqlite3

# ================================
# WCZYTANIE I CZYSZCZENIE DANYCH
# ================================

df = pd.read_csv('Houses.csv', encoding='cp1250')
df = df.drop(columns=['Unnamed: 0', 'id'])

# ROK BUDOWY
df.loc[(df['year'] == 70) & (df['city'] == 'Poznań'), 'year'] = 1970
df.loc[(df['year'] == 80) & (df['city'] == 'Poznań'), 'year'] = 1980
df = df[df['year'].between(1800, 2024)]

# METRAŻ
df.loc[(df['sq'] == 8.8) & (df['address'].str.contains('Targówek')), 'sq'] = 88.0
df = df[df['sq'].between(15, 300)]

# CENA
df = df[df['price'] >= 50000]

# GPS
df = df[df['longitude'].between(14, 24)]

# DUPLIKATY
df = df.drop_duplicates(subset=['address', 'city', 'sq', 'price', 'rooms', 'year', 'floor'])

# CENA ZA M² — osobne limity dla każdego miasta
df['price_per_sqm'] = df['price'] / df['sq']
limity = {'Warszawa': 4500, 'Kraków': 3500, 'Poznań': 3000}
for miasto, limit in limity.items():
    df = df[~((df['city'] == miasto) & (df['price_per_sqm'] < limit))]

# BŁĘDNE ADRESY
bledy_adres = ['wielkopolskie', 'małopolskie', 'mazowieckie']
wzorzec = '|'.join(bledy_adres)
df = df[~df['address'].str.lower().str.contains(wzorzec)]
df = df[~((df['address'] == 'Grunwald Łazarz') & (df['year'] == 1899))]

print(f"✅ Dane wyczyszczone! Rekordów: {len(df)}")

# ================================
# ZAPIS DO SQLITE
# ================================

conn = sqlite3.connect('mieszkania.db')
df.to_sql('mieszkania', conn, if_exists='replace', index=False)
conn.close()

print("✅ Plik mieszkania.db zapisany — możesz otworzyć go w DBeaver!")