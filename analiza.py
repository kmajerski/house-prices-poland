import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# ================================
# WCZYTANIE I CZYSZCZENIE DANYCH
# ================================

df = pd.read_csv('Houses.csv', encoding='cp1250')
df = df.drop(columns=['Unnamed: 0', 'id'])

df.loc[(df['year'] == 70) & (df['city'] == 'Poznań'), 'year'] = 1970
df.loc[(df['year'] == 80) & (df['city'] == 'Poznań'), 'year'] = 1980
df = df[df['year'].between(1800, 2024)]
df.loc[(df['sq'] == 8.8) & (df['address'].str.contains('Targówek')), 'sq'] = 88.0
df = df[df['sq'].between(15, 300)]
df = df[df['price'] >= 50000]
df = df[df['longitude'].between(14, 24)]
df = df.drop_duplicates(subset=['address', 'city', 'sq', 'price', 'rooms', 'year', 'floor'])
df['price_per_sqm'] = df['price'] / df['sq']
limity = {'Warszawa': 4500, 'Kraków': 3500, 'Poznań': 3000}
for miasto, limit in limity.items():
    df = df[~((df['city'] == miasto) & (df['price_per_sqm'] < limit))]
df = df[~df['address'].str.lower().str.contains('wielkopolskie|małopolskie|mazowieckie')]
df = df[~((df['address'] == 'Grunwald Łazarz') & (df['year'] == 1899))]

print(f"✅ Dane gotowe! Rekordów: {len(df)}")

# ================================
# WYKRES 1: Metraż vs cena wg liczby pokoi — 3 miasta
# ================================

fig, axes = plt.subplots(3, 1, figsize=(11, 18))

pokoje_kolory = {1: '#E91E63', 2: '#9C27B0', 3: '#2196F3', 4: '#4CAF50', 5: '#FF9800'}
df_pokoje = df[df['rooms'].between(1, 5)].copy()
df_pokoje['rooms'] = df_pokoje['rooms'].astype(int)
miasta = ['Warszawa', 'Kraków', 'Poznań']

# Jednakowe zakresy osi dla wszystkich miast
X_TICKS = [15, 30, 50, 75, 100, 150, 200, 300]
Y_TICKS = [100, 300, 500, 750, 1000, 1500, 2000, 3000, 5000, 10000]
X_LIM = (14, 310)
Y_LIM = (80, 11000)

for ax, miasto in zip(axes, miasta):
    subset_miasto = df_pokoje[df_pokoje['city'] == miasto]

    for pokoje, kolor in pokoje_kolory.items():
        subset = subset_miasto[subset_miasto['rooms'] == pokoje]
        if len(subset) == 0:
            continue

        # Punkty
        ax.scatter(subset['sq'], subset['price'] / 1000,
                   alpha=0.2, s=12, color=kolor, label=f'{pokoje} pokój/e')

        # Średni punkt
        sr_sq = subset['sq'].mean()
        sr_cena = subset['price'].mean() / 1000
        ax.scatter(sr_sq, sr_cena, color=kolor, s=140,
                   zorder=5, edgecolors='black', linewidths=1.2)

        # Opis zawsze NAD punktem
        ax.annotate(f'{sr_sq:.0f} m²\n{sr_cena:.0f} tys. zł',
                    xy=(sr_sq, sr_cena),
                    xytext=(0, 14),
                    textcoords='offset points',
                    ha='center', va='bottom',
                    fontsize=7.5,
                    color='black',
                    fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.7, ec='none'))

    ax.set_xscale('symlog', linthresh=100)
    ax.set_yscale('symlog', linthresh=1000)

    ax.set_xticks(X_TICKS)
    ax.set_xticklabels([str(x) for x in X_TICKS])
    ax.set_xlim(X_LIM)

    ax.set_yticks(Y_TICKS)
    ax.set_yticklabels([str(y) for y in Y_TICKS])
    ax.set_ylim(Y_LIM)

    ax.set_xlabel('Powierzchnia (m²)', fontsize=10)
    ax.set_ylabel('Cena (tys. zł)', fontsize=10)

    ax.axvline(x=100, color='gray', linestyle='--', alpha=0.4, linewidth=0.8)
    ax.axhline(y=1000, color='gray', linestyle='--', alpha=0.4, linewidth=0.8)

    ax.set_title(f'{miasto} — cena vs metraż według liczby pokoi', fontsize=12, fontweight='bold')
    ax.legend(title='Liczba pokoi', fontsize=8, loc='upper left')
    ax.grid(alpha=0.3, which='both')

plt.tight_layout(pad=3.0)
plt.savefig('wykres1_metraz_pokoje.png', dpi=150)
plt.close()
print("✅ Wykres 1 gotowy")

# ================================
# WYKRES 2: Cena za m² vs odległość od centrum
# ================================
centra = {
    'Warszawa': (52.2317, 21.0062),  # Pałac Kultury i Nauki
    'Kraków':   (50.0617, 19.9372),  # Sukiennice
    'Poznań':   (52.4082, 16.9335),  # Stary Rynek
}

def odleglosc_km(lat, lon, lat_c, lon_c):
    dlat = (lat - lat_c) * 111
    dlon = (lon - lon_c) * 73
    return np.sqrt(dlat**2 + dlon**2)

df_dist = df.copy()
df_dist['dist'] = df_dist.apply(
    lambda r: odleglosc_km(r['latitude'], r['longitude'],
                           centra[r['city']][0], centra[r['city']][1]), axis=1)
df_dist = df_dist[df_dist['dist'] <= 20]

bins   = [0, 1, 2, 3, 5, 10, 20]
labels = ['0-1 km', '1-2 km', '2-3 km', '3-5 km', '5-10 km', '10+ km']
df_dist['strefa'] = pd.cut(df_dist['dist'], bins=bins, labels=labels)

fig, axes = plt.subplots(3, 1, figsize=(11, 18))
miasta = ['Warszawa', 'Kraków', 'Poznań']
kolory_stref = ['#1a237e', '#283593', '#1565C0', '#1976D2', '#42A5F5', '#90CAF9']

for ax, miasto in zip(axes, miasta):
    sub = df_dist[df_dist['city'] == miasto].copy()

    stats = sub.groupby('strefa', observed=True)['price_per_sqm'].agg(
        srednia='mean',
        q25=lambda x: x.quantile(0.25),
        q75=lambda x: x.quantile(0.75),
        n='count'
    ).reset_index()

    x = range(len(stats))
    x_list = list(x)

    y_max = stats['q75'].max() * 1.55
    ax.set_ylim(0, y_max)

    # Słupki średniej
    ax.bar(x, stats['srednia'], color=kolory_stref[:len(stats)],
           width=0.6, zorder=3)

    # Przedział 25-75 percentyl
    ax.errorbar(x, stats['srednia'],
                yerr=[stats['srednia'] - stats['q25'],
                      stats['q75'] - stats['srednia']],
                fmt='none', color='black', capsize=5, linewidth=1.5, zorder=4)

    # Ceny tuż nad górnym error barem
    for i, row in stats.iterrows():
        ax.text(x_list[i], row['q75'] + y_max * 0.02,
                f"{row['srednia']:,.0f} zł/m²",
                ha='center', va='bottom', fontsize=8.5,
                fontweight='bold', color='black', zorder=6,
                bbox=dict(boxstyle='round,pad=0.15', fc='white', alpha=0.95, ec='none'))

    ax.set_xticks(x)
    ax.set_xticklabels(stats['strefa'], fontsize=10)
    ax.set_ylabel('Średnia cena za m² (zł)', fontsize=10)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:,.0f} zł'))
    ax.grid(axis='y', alpha=0.3, zorder=0)

    # Druga oś Y — liczba ogłoszeń
    ax2 = ax.twinx()
    n_max = stats['n'].max() * 1.55
    ax2.set_ylim(0, n_max)

    # Poświata pod linią
    ax2.fill_between(x_list, stats['n'], alpha=0.12, color='#FF6F00', zorder=1)

    # Linia
    ax2.plot(x_list, stats['n'], color='#FF6F00', linewidth=2,
             marker='o', markersize=7, zorder=5)

    ax2.set_ylabel('Liczba ogłoszeń', fontsize=10, color='#FF6F00')
    ax2.tick_params(axis='y', labelcolor='#FF6F00')

    # n= w lewym górnym skosie od punktu
    for i, row in stats.iterrows():
        ax2.annotate(f"n={row['n']}",
                     xy=(x_list[i], row['n']),
                     xytext=(-12, 6),
                     textcoords='offset points',
                     ha='right', va='bottom', fontsize=8,
                     color='#FF6F00', fontweight='bold', zorder=6,
                     bbox=dict(boxstyle='round,pad=0.15', fc='white', alpha=0.95, ec='none'))

    # Legenda zawsze w prawym dolnym rogu gdzie jest najmniej danych
    ax.set_title(f'{miasto} — średnia cena za m² według odległości od centrum\n'
                 f'(słupki błędów = przedział 25-75 percentyl)',
                 fontsize=12, fontweight='bold')

plt.tight_layout(pad=3.0)
plt.savefig('wykres2_odleglosc_centrum.png', dpi=150)
plt.close()
print("✅ Wykres 2 gotowy — cena vs odleglosc od centrum")

# ================================
# WYKRES 3: Treemap — nowe inwestycje wg dzielnicy
# ================================

import squarify

# Wyciągamy pierwszą dzielnicę z adresu (pierwsze 1-2 słowa)
def wyciagnij_dzielnice(address):
    # Dzielnice wieloczłonowe które chcemy zachować razem
    wieloczlonowe = [
        'Praga-Południe', 'Praga-Północ', 'Prądnik Czerwony', 'Prądnik Biały',
        'Nowa Huta', 'Stare Miasto', 'Nowe Miasto', 'Bieżanów-Prokocim',
        'Podgórze Duchackie', 'Wzgórza Krzesławickie', 'Łagiewniki-Borek Fałęcki'
    ]
    for w in wieloczlonowe:
        if address.startswith(w):
            return w
    return address.split()[0] if address.split() else 'Inne'

nowe = df[df['year'] >= 2010].copy()
nowe['dzielnica'] = nowe['address'].apply(wyciagnij_dzielnice)

fig, axes = plt.subplots(1, 3, figsize=(18, 10))
miasta = ['Warszawa', 'Kraków', 'Poznań']

for ax, miasto in zip(axes, miasta):
    sub = nowe[nowe['city'] == miasto]
    counts = sub['dzielnica'].value_counts()

    # Zostawiamy top 12 dzielnic, resztę grupujemy jako "Inne"
    top = counts.head(12)
    inne = counts.iloc[12:].sum()
    if inne > 0:
        top['Inne'] = inne

    total = top.sum()
    procenty = (top / total * 100).round(1)

    # Kolory — gradient zielony, ciemniejszy = więcej inwestycji
    import matplotlib.cm as cm
    n = len(top)
    # Sortujemy od największego do najmniejszego — już są posortowane przez value_counts
    kolory = [cm.Greens(0.35 + 0.55 * (n - i) / n) for i in range(n)]

    squarify.plot(
        sizes=top.values,
        label=[f"{dz}\n{procenty[dz]:.1f}%\n(n={top[dz]})" for dz in top.index],
        color=kolory,
        alpha=0.9,
        ax=ax,
        text_kwargs={'fontsize': 7.5, 'fontweight': 'bold', 'color': 'white'}
    )
    ax.set_title(f'{miasto}\nnowe inwestycje 2010+ wg dzielnicy',
                 fontsize=12, fontweight='bold')
    ax.axis('off')

plt.suptitle('Udział nowych inwestycji (2010+) według dzielnicy',
             fontsize=14, fontweight='bold', y=1.01)
plt.tight_layout()
plt.savefig('wykres3_treemap_dzielnice.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ Wykres 3 gotowy — treemap nowe inwestycje")

nowe = df[df['year'] >= 2010]
print(nowe['city'].value_counts())