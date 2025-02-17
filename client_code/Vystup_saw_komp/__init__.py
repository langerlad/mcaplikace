from ._anvil_designer import Vystup_saw_kompTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users


class Vystup_saw_komp(Vystup_saw_kompTemplate):
  """
  Stránka pro zobrazení vstupních dat a výsledků SAW analýzy.
  Zobrazuje kompletní přehled analýzy včetně kritérií, variant a jejich hodnocení.
  """
  def __init__(self, analyza_id=None, **properties):
   
    self.init_components(**properties)
    self.analyza_id = analyza_id

  def form_show(self, **event_args):
    """
    Event handler vyvolaný při zobrazení formuláře.
    Načte data analýzy a zobrazí je v připravených komponentách.
    """
    if self.analyza_id:
        try:
            analyza_data = anvil.server.call('nacti_kompletni_analyzu', self.analyza_id)
            self.zobraz_vstup(analyza_data)
            self.zobraz_normalizaci(analyza_data)
            #self.rich_text_vysledek.content
        except Exception as e:
            alert(f"Chyba při načítání analýzy: {str(e)}")
    else:
        self.rich_text_vstupni_data.text = "Nepřišlo žádné ID analýzy."
        self.rich_text_normalizace.text = "Není co počítat."
        self.rich_text_vystupni_data.text = "Není co počítat."

  def zobraz_vstup(self, analyza_data):
    """
    Formátuje a zobrazuje vstupní data analýzy.
    
    Args:
        analyza_data: Slovník obsahující kompletní data analýzy
    """
    # Základní informace o analýze
    zakladni_info = f"""
# {analyza_data['analyza']['nazev']}

### Základní informace
- **Metoda**: {analyza_data['analyza']['zvolena_metoda']}
- **Popis**: {analyza_data['analyza']['popis'] or 'Bez popisu'}

### Kritéria
| Název kritéria | Typ | Váha |
|----------------|-----|------|
"""
    
    # Přidání kritérií do tabulky
    for k in analyza_data['kriteria']:
        vaha = float(k['vaha'])  # Převod na číslo pro formátování
        zakladni_info += f"| {k['nazev_kriteria']} | {k['typ'].upper()} | {vaha:.3f} |\n"

    # Seznam variant
    zakladni_info += "\n### Varianty\n"
    for v in analyza_data['varianty']:
        if v['popis_varianty']:
            zakladni_info += f"- **{v['nazev_varianty']}** - {v['popis_varianty']}\n"
        else:
            zakladni_info += f"- **{v['nazev_varianty']}**\n"

    # Vytvoření hodnotící matice
    zakladni_info += "\n### Hodnotící matice\n"
    
    # Získání unikátních názvů variant a kritérií
    varianty = [v['nazev_varianty'] for v in analyza_data['varianty']]
    kriteria = [k['nazev_kriteria'] for k in analyza_data['kriteria']]
    
    # Hlavička tabulky
    zakladni_info += f"| Kritérium | {' | '.join(varianty)} |\n"
    zakladni_info += f"|{'-' * 10}|{('|'.join('-' * 12 for _ in varianty))}|\n"
    
    # Naplnění tabulky hodnotami
    matice = analyza_data['hodnoty']['matice_hodnoty']
    for krit in kriteria:
        radek = f"| {krit} |"
        for var in varianty:
            klic = f"{var}_{krit}"
            hodnota = matice.get(klic, "N/A")
            if isinstance(hodnota, (int, float)):
                radek += f" {hodnota:.2f} |"
            else:
                radek += f" {hodnota} |"
        zakladni_info += radek + "\n"

    self.rich_text_vstupni_data.content = zakladni_info

  def zobraz_normalizaci(self, analyza_data):
    """
    Zobrazí normalizovanou matici a vážené hodnoty v UI komponentě.
    """
    vysledky = anvil.server.call('vypocet_normalizace', analyza_data)
    
    nazvy_var = vysledky['nazvy_variant']
    nazvy_krit = vysledky['nazvy_kriterii']
    nmtx = vysledky['normalizovana_matice']

    # 1. Zobrazení normalizované matice
    md_text = "## Normalizace hodnot\n\n"
    md_text += "| Varianta / Krit. | " + " | ".join(nazvy_krit) + " |\n"
    md_text += "|" + "-|"*(len(nazvy_krit)+1) + "\n"

    for i, var_name in enumerate(nazvy_var):
        radek = f"| {var_name} |"
        for j in range(len(nazvy_krit)):
            val = nmtx[i][j]
            radek += f" {round(val,3)} |"
        md_text += radek + "\n"

    # Přidání vysvětlujícího textu
    md_text += """

Normalizační matice (někdy též znormalizovaná matice) je výsledek úpravy původních hodnot (např. z různých kritérií) na jednotné měřítko tak, aby se spravedlivě porovnávaly. Jinými slovy, v původních datech může být jedno kritérium „cena v Kč" (velká čísla, kde menší hodnota je lepší – cost) a druhé „kvalita v bodech 1–10" (menší čísla, kde větší hodnota je lepší – benefit). Normalizací převedeme všechny sloupce do podobného intervalu (často [0,1]), abychom je mohli sčítat, násobit nebo jinak kombinovat.

#### Vysvětlení procesu:
1. Pro každé kritérium je určen směr optimalizace (MAX/MIN)
2. Aplikuje se Min-Max normalizace:
   - Pro každý sloupec (kritérium) se najde minimum a maximum
   - Hodnoty jsou transformovány podle vzorce: (x - min) / (max - min)
   - Pro MIN kritéria je výsledek odečten od 1
3. Výsledná normalizovaná matice obsahuje hodnoty v intervalu [0,1]
   - 1 reprezentuje nejlepší hodnotu
   - 0 reprezentuje nejhorší hodnotu

"""

    # 2. Vytvoření slovníku pro vážené hodnoty
    vysledky_soucinu = {}
    for i, varianta in enumerate(nazvy_var):
        vysledky_soucinu[varianta] = {}
        for j, kriterium in enumerate(nazvy_krit):
            norm_hodnota = nmtx[i][j]
            vaha = float(analyza_data['kriteria'][j]['vaha'])
            vysledky_soucinu[varianta][kriterium] = norm_hodnota * vaha

    # 3. Přidání tabulky vážených hodnot
    md_text += "## Vážené hodnoty\n\n"
    
    # Získat seznam všech variant a kritérií
    varianty = list(vysledky_soucinu.keys())
    prvni_variant = varianty[0] if varianty else None
    kriteria = list(vysledky_soucinu[prvni_variant].keys()) if prvni_variant else []
    
    # Vytvoření tabulky
    md_text += "| Varianta | " + " | ".join(kriteria) + " | **Součet** |\n"
    md_text += "|" + "----|"*(len(kriteria)+2) + "\n"
    
    # Naplnění řádků
    for var in varianty:
        radek = f"| **{var}** |"
        soucet = 0.0
        for krit in kriteria:
            hodnota = vysledky_soucinu[var].get(krit, 0)
            soucet += hodnota
            radek += f" {round(hodnota, 3)} |"
        radek += f" **{round(soucet, 3)}** |"
        md_text += radek + "\n"

    # After the weighted values table, add:
    md_text += """

**Tabulka vážených hodnot (normalizovaná hodnota × váha)**

Podobně jako u normalizační matice je i tabulka vážených hodnot klíčovým krokem v procesu **vícekriteriální analýzy** (např. metodou SAW).

Zatímco normalizační matice zachycuje převedené hodnoty na interval [0,1], v **tabulce vážených hodnot** každou tuto normalizovanou hodnotu ještě **násobíme** váhou daného kritéria.

### Postup výpočtu:

1. **Normalizace hodnot**
   - Po určení, zda je kritérium typu „max" (benefit) či „min" (cost), se aplikuje např. **min-max** normalizace (viz předchozí text)
   - Výsledkem je tzv. **normalizovaná matice**: každé kritérium se převede do intervalu [0,1]

2. **Váhy kritérií**
   - Každému kritériu je přiřazena **váha** odrážející jeho důležitost vůči ostatním (součet vah bývá 1)
   - Vyšší váha znamená, že se dané kritérium podílí na výsledku **významněji**

3. **Výpočet vážených hodnot**
   - Pro každou buňku normalizované matice (tj. pro každou variantu a kritérium) se spočítá **součin**:
     (normalizovaná hodnota) × (váha kritéria)
   - Tím vznikne **tabulka vážených hodnot**, kde se už zároveň zohledňuje důležitost kritéria

4. **Interpretace**
   - Výsledek v každé buňce vyjadřuje, **jak dobře** daná varianta splňuje kritérium, **s přihlédnutím** k jeho významnosti
   - Nulové či velmi nízké hodnoty znamenají, že varianta v daném kritériu **silně zaostává**, i po zohlednění váhy
   - Hodnoty blížící se 1 (resp. vyššího součtu přes všechna kritéria) znamenají, že varianta je **výhodná** z pohledu tohoto kritéria či celého souboru kritérií

> **Tabulka vážených hodnot** tak představuje **mezikrok** před finálním vyčíslením *celkového skóre* každé varianty (např. v metodě SAW se tyto vážené hodnoty ještě **sečtou** do jednoho čísla).
"""

    self.rich_text_normalizace.content = md_text
    self.zobraz_vysledek(analyza_data, vysledky_soucinu)

  def zobraz_vysledek(self, analyza_data, vysledky_soucinu):
    """
    Zobrazí finální výsledky SAW analýzy včetně seřazení variant a komentáře.
    """
    try:
        # 1) Vypočítat celkové skóre pro každou variantu (suma vážených hodnot)
        final_scores = {}
        for varianta, hodnoty in vysledky_soucinu.items():
            final_scores[varianta] = sum(hodnoty.values())

        # 2) Seřadit varianty podle skóre
        setridene = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)

        # 3) Vytvořit markdown text s výsledky
        md = "# Finální výsledky SAW analýzy\n\n"
        
        # Tabulka výsledků
        md += "| Pořadí | Varianta | Celkové skóre |\n"
        md += "|---------|-----------|---------------|\n"
        
        for i, (var, score) in enumerate(setridene, start=1):
            md += f"| {i}. | **{var}** | {round(score, 3)} |\n"

        # Přidat interpretaci výsledků
        best_variant = setridene[0][0]
        best_score = setridene[0][1]
        worst_variant = setridene[-1][0]
        worst_score = setridene[-1][1]
        score_diff = best_score - worst_score

        md += f"""

### Interpretace výsledků

- **Nejlepší varianta**: **{best_variant}** (skóre: {round(best_score, 3)})
- **Nejhorší varianta**: {worst_variant} (skóre: {round(worst_score, 3)})
- **Rozdíl nejlepší-nejhorší**: {round(score_diff, 3)}

### Vysvětlení hodnocení

1. **Celkové skóre** každé varianty je součtem všech jejích vážených hodnot
2. **Vyšší skóre** znamená lepší variantu v kontextu:
   - zadaných vah kritérií
   - směrů optimalizace (MIN/MAX)
   - původních hodnot kritérií

> Toto hodnocení zohledňuje všechna kritéria současně a bere v úvahu jejich relativní důležitost definovanou vahami.

"""

        self.rich_text_vysledek.content = md

    except Exception as e:
        alert(f"Chyba při zobrazení výsledků: {str(e)}")