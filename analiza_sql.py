import pandas as pd
import sqlite3

# Wczytujemy i czyścimy dane (tak jak wcześniej)
df = pd.read_csv('Houses.csv', encoding='cp1250')
df = df.drop(columns=['Unnamed: 0', 'id'])
df.loc[(df['year'] == 70) & (df['city'] == 'Poznań'), 'year'] = 1970
df.loc[(df['year'] == 80) & (df['city'] == 'Poznań'), 'year'] = 1980
df = df[df['year'].between(1800, 2024)]
df.loc[(df['sq'] == 8.8) & (df['address'].str.contains('Targówek')), 'sq'] = 88.0
df = df[df['sq'].between(15, 300)]
df = df[df['price'] >= 50000]
df = df[df['longitude'].between(14, 24)]
df['price_per_sqm'] = df['price'] / df['sq']

# Ładujemy dane do SQLite
conn = sqlite3.connect(':memory:')
df.to_sql('mieszkania', conn, index=False)

# ================================
# ZAPYTANIE: podejrzanie niskie ceny za m²
# ================================

query = """
SELECT
    city                            AS miasto,
    address                         AS adres,
    ROUND(sq, 1)                    AS metraz,
    rooms                           AS pokoje,
    CAST(price AS INT)              AS cena,
    ROUND(price_per_sqm, 0)         AS cena_za_m2,
    CAST(year AS INT)               AS rok
FROM mieszkania
WHERE price_per_sqm < 3000
ORDER BY price_per_sqm ASC
"""

wyniki = pd.read_sql(query, conn)
print(f"Mieszkania z ceną poniżej 3000 zł/m²: {len(wyniki)}")
print()
print(wyniki.to_string(index=False))