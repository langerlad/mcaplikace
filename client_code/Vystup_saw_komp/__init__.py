from ._anvil_designer import Vystup_saw_kompTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users


class Vystup_saw_komp(Vystup_saw_kompTemplate):
    """
    Formulář pro zobrazení výsledků SAW analýzy.
    Zobrazuje kompletní přehled včetně:
    - vstupních dat (kritéria, varianty, hodnotící matice)
    - normalizované matice
    - vážených hodnot
    - finálních výsledků
    """
    def __init__(self, analyza_id=None, **properties):
        self.init_components(**properties)
        self.analyza_id = analyza_id
        
    def form_show(self, **event_args):
        """Načte a zobrazí data analýzy při zobrazení formuláře."""
        if not self.analyza_id:
            self._zobraz_prazdny_formular()
            return
            
        try:
            # Jediné volání serveru - získání dat analýzy
            analyza_data = anvil.server.call('nacti_kompletni_analyzu', self.analyza_id)
            self._zobraz_kompletni_analyzu(analyza_data)
        except Exception as e:
            alert(f"Chyba při načítání analýzy: {str(e)}")

    def _zobraz_prazdny_formular(self):
        """Zobrazí prázdný formulář s informací o chybějících datech."""
        self.rich_text_vstupni_data.text = "Nepřišlo žádné ID analýzy."
        self.rich_text_normalizace.text = "Není co počítat."
        self.rich_text_vysledek.text = "Není co počítat."

    def _zobraz_kompletni_analyzu(self, analyza_data):
        """
        Zobrazí kompletní analýzu včetně všech výpočtů.
        
        Args:
            analyza_data: Slovník s kompletními daty analýzy
        """
        self._zobraz_vstupni_data(analyza_data)
        
        # Provedení výpočtů
        norm_vysledky = self._normalizuj_matici(analyza_data)
        vazene_hodnoty = self._vypocitej_vazene_hodnoty(analyza_data, norm_vysledky)
        saw_vysledky = self._vypocitej_saw_vysledky(analyza_data, vazene_hodnoty)
        
        # Zobrazení výsledků
        self._zobraz_normalizaci(norm_vysledky, vazene_hodnoty)
        self._zobraz_vysledky(saw_vysledky)

    def _zobraz_vstupni_data(self, analyza_data):
        """Zobrazí vstupní data analýzy v přehledné formě."""
        md = f"""
### {analyza_data['analyza']['nazev']}

#### Základní informace
- Metoda: {analyza_data['analyza']['zvolena_metoda']}
- Popis: {analyza_data['analyza']['popis'] or 'Bez popisu'}

#### Kritéria
| Název kritéria | Typ | Váha |
|----------------|-----|------|
"""
        # Přidání kritérií
        for k in analyza_data['kriteria']:
            vaha = float(k['vaha'])
            md += f"| {k['nazev_kriteria']} | {k['typ'].upper()} | {vaha:.3f} |\n"

        # Varianty
        md += "\n#### Varianty\n"
        for v in analyza_data['varianty']:
            popis = f" - {v['popis_varianty']}" if v['popis_varianty'] else ""
            md += f"- {v['nazev_varianty']}{popis}\n"

        # Hodnotící matice
        varianty = [v['nazev_varianty'] for v in analyza_data['varianty']]
        kriteria = [k['nazev_kriteria'] for k in analyza_data['kriteria']]
        
        md += "\n#### Hodnotící matice\n"
        md += f"| Kritérium | {' | '.join(varianty)} |\n"
        md += f"|{'-' * 10}|{('|'.join('-' * 12 for _ in varianty))}|\n"
        
        matice = analyza_data['hodnoty']['matice_hodnoty']
        for krit in kriteria:
            radek = f"| {krit} |"
            for var in varianty:
                klic = f"{var}_{krit}"
                hodnota = matice.get(klic, "N/A")
                hodnota = f" {hodnota:.2f} |" if isinstance(hodnota, (int, float)) else f" {hodnota} |"
                radek += hodnota
            md += radek + "\n"

        self.rich_text_vstupni_data.content = md

    def _zobraz_normalizaci(self, norm_vysledky, vazene_hodnoty):
        """
        Zobrazí normalizovanou matici a vážené hodnoty.
        
        Args:
            norm_vysledky: Výsledky normalizace
            vazene_hodnoty: Vypočtené vážené hodnoty
        """
        md = "### Normalizace hodnot\n\n"
        
        # Normalizační tabulka
        md += "| Varianta / Krit. | " + " | ".join(norm_vysledky['nazvy_kriterii']) + " |\n"
        md += "|" + "-|"*(len(norm_vysledky['nazvy_kriterii'])+1) + "\n"
        
        for i, var_name in enumerate(norm_vysledky['nazvy_variant']):
            md += f"| {var_name} |"
            for j in range(len(norm_vysledky['nazvy_kriterii'])):
                md += f" {norm_vysledky['normalizovana_matice'][i][j]:.3f} |"
            md += "\n"

        # Vysvětlení normalizace
        md += self._vytvor_vysvetleni_normalizace()
        
        # Tabulka vážených hodnot
        md += self._vytvor_tabulku_vazenych_hodnot(vazene_hodnoty)
        
        # Vysvětlení vážených hodnot
        md += self._vytvor_vysvetleni_vazenych_hodnot()
        
        self.rich_text_normalizace.content = md

    def _zobraz_vysledky(self, saw_vysledky):
        """
        Zobrazí finální výsledky SAW analýzy.
        
        Args:
            saw_vysledky: Výsledky SAW analýzy
        """
        md = "### Výsledky SAW analýzy\n\n"
        
        # Tabulka výsledků
        md += "| Pořadí | Varianta | Skóre |\n"
        md += "|---------|----------|--------|\n"
        
        for varianta, poradi, skore in saw_vysledky['results']:
            md += f"| {poradi}. | {varianta} | {skore:.3f} |\n"

        # Shrnutí výsledků
        md += f"""
#### Shrnutí výsledků
- Nejlepší varianta: {saw_vysledky['nejlepsi_varianta']} (skóre: {saw_vysledky['nejlepsi_skore']:.3f})
- Nejhorší varianta: {saw_vysledky['nejhorsi_varianta']} (skóre: {saw_vysledky['nejhorsi_skore']:.3f})
- Rozdíl nejlepší-nejhorší: {saw_vysledky['rozdil_skore']:.3f}

#### Metoda SAW (Simple Additive Weighting)
1. Princip metody
   - Normalizace hodnot do intervalu [0,1]
   - Vynásobení normalizovaných hodnot vahami
   - Sečtení vážených hodnot pro každou variantu

2. Interpretace výsledků
   - Vyšší skóre znamená lepší variantu
   - Výsledek zohledňuje všechna kritéria dle jejich vah
   - Rozdíly ve skóre ukazují relativní kvalitu variant
"""
        self.rich_text_vysledek.content = md

    def _normalizuj_matici(self, analyza_data):
        """
        Provede min-max normalizaci hodnot.
        
        Args:
            analyza_data: Slovník obsahující data analýzy
        
        Returns:
            dict: Slovník obsahující normalizovanou matici a metadata
        """
        varianty = [v['nazev_varianty'] for v in analyza_data['varianty']]
        kriteria = [k['nazev_kriteria'] for k in analyza_data['kriteria']]
        
        # Vytvoření původní matice
        matice = []
        for var in analyza_data['varianty']:
            radek = []
            for krit in analyza_data['kriteria']:
                klic = f"{var['nazev_varianty']}_{krit['nazev_kriteria']}"
                hodnota = float(analyza_data['hodnoty']['matice_hodnoty'].get(klic, 0))
                radek.append(hodnota)
            matice.append(radek)
        
        # Normalizace pomocí min-max pro každý sloupec (kritérium)
        norm_matice = []
        for i in range(len(matice)):
            norm_radek = []
            for j in range(len(matice[0])):
                sloupec = [row[j] for row in matice]
                min_val = min(sloupec)
                max_val = max(sloupec)
                
                if max_val == min_val:
                    norm_hodnota = 1.0  # Všechny hodnoty jsou stejné
                else:
                    # Pro MIN kritéria obrátíme normalizaci
                    if analyza_data['kriteria'][j]['typ'].lower() in ("min", "cost"):
                        norm_hodnota = (max_val - matice[i][j]) / (max_val - min_val)
                    else:
                        norm_hodnota = (matice[i][j] - min_val) / (max_val - min_val)
                
                norm_radek.append(norm_hodnota)
            norm_matice.append(norm_radek)
        
        return {
            'nazvy_variant': varianty,
            'nazvy_kriterii': kriteria,
            'normalizovana_matice': norm_matice
        }

    def _vypocitej_vazene_hodnoty(self, analyza_data, norm_vysledky):
        """
        Vypočítá vážené hodnoty pro všechny varianty a kritéria.
        
        Args:
            analyza_data: Slovník s daty analýzy
            norm_vysledky: Výsledky normalizace
            
        Returns:
            dict: Slovník vážených hodnot pro každou variantu a kritérium
        """
        vazene_hodnoty = {}
        
        for i, varianta in enumerate(norm_vysledky['nazvy_variant']):
            vazene_hodnoty[varianta] = {}
            for j, kriterium in enumerate(norm_vysledky['nazvy_kriterii']):
                norm_hodnota = norm_vysledky['normalizovana_matice'][i][j]
                vaha = float(analyza_data['kriteria'][j]['vaha'])
                vazene_hodnoty[varianta][kriterium] = norm_hodnota * vaha
        
        return vazene_hodnoty

    def _vypocitej_saw_vysledky(self, analyza_data, vazene_hodnoty):
        """
        Vypočítá finální výsledky SAW analýzy.
        
        Args:
            analyza_data: Slovník s daty analýzy
            vazene_hodnoty: Slovník vážených hodnot
            
        Returns:
            dict: Slovník obsahující seřazené výsledky a statistiky
        """
        # Výpočet celkového skóre pro každou variantu
        skore = {}
        for varianta, hodnoty in vazene_hodnoty.items():
            skore[varianta] = sum(hodnoty.values())
        
        # Seřazení variant podle skóre (sestupně)
        serazene = sorted(skore.items(), key=lambda x: x[1], reverse=True)
        
        # Vytvoření seznamu výsledků s pořadím
        results = []
        for poradi, (varianta, hodnota) in enumerate(serazene, 1):
            results.append((varianta, poradi, hodnota))
        
        return {
            'results': results,
            'nejlepsi_varianta': results[0][0],
            'nejlepsi_skore': results[0][2],
            'nejhorsi_varianta': results[-1][0],
            'nejhorsi_skore': results[-1][2],
            'rozdil_skore': results[0][2] - results[-1][2]
        }

    def _vytvor_vysvetleni_normalizace(self):
        """Vytvoří text s vysvětlením normalizace."""
        return """

Normalizační matice představuje úpravu původních hodnot na jednotné měřítko pro spravedlivé porovnání. 
V původních datech mohou být různá kritéria v odlišných jednotkách (např. cena v Kč a kvalita v bodech 1-10). 
Normalizací převedeme všechny hodnoty do intervalu [0,1].

#### Postup normalizace:
1. Pro každé kritérium je určen směr optimalizace (MAX/MIN)
2. Aplikuje se Min-Max normalizace:
   - Pro každý sloupec se najde minimum a maximum
   - Hodnoty jsou transformovány podle vzorce: (x - min) / (max - min)
   - Pro MIN kritéria je výsledek odečten od 1
3. Výsledná normalizovaná matice obsahuje hodnoty v intervalu [0,1]
   - 1 reprezentuje nejlepší hodnotu
   - 0 reprezentuje nejhorší hodnotu

"""

    def _vytvor_tabulku_vazenych_hodnot(self, vazene_hodnoty):
        """
        Vytvoří markdown tabulku vážených hodnot.
        
        Args:
            vazene_hodnoty: Slovník vážených hodnot
            
        Returns:
            str: Markdown formátovaná tabulka
        """
        varianty = list(vazene_hodnoty.keys())
        if not varianty:
            return ""
            
        kriteria = list(vazene_hodnoty[varianty[0]].keys())
        
        md = "\n#### Vážené hodnoty\n\n"
        md += "| Varianta | " + " | ".join(kriteria) + " | Součet |\n"
        md += "|" + "----|"*(len(kriteria)+2) + "\n"
        
        for var in varianty:
            md += f"| {var} |"
            soucet = 0.0
            for krit in kriteria:
                hodnota = vazene_hodnoty[var].get(krit, 0)
                soucet += hodnota
                md += f" {hodnota:.3f} |"
            md += f" {soucet:.3f} |\n"
        return md

    def _vytvor_vysvetleni_vazenych_hodnot(self):
        """Vytvoří text s vysvětlením vážených hodnot."""
        return """

#### Vysvětlení vážených hodnot:

1. Význam výpočtu
   - Vážené hodnoty vznikají násobením normalizovaných hodnot váhami kritérií
   - Zohledňují jak výkonnost varianty, tak důležitost kritéria

2. Váhy kritérií
   - Každému kritériu je přiřazena váha podle jeho důležitosti
   - Součet všech vah je 1
   - Vyšší váha znamená větší vliv na celkový výsledek

3. Interpretace hodnot
   - Vyšší hodnoty znamenají lepší hodnocení v daném kritériu
   - Součet představuje celkové hodnocení varianty
   - Slouží jako základ pro určení pořadí variant

"""

    def _vytvor_vysvetleni_metody(self):
        """Vytvoří text s vysvětlením metody SAW."""
        return """

#### Metoda SAW (Simple Additive Weighting)
1. Princip metody
   - Normalizace hodnot do intervalu [0,1]
   - Vynásobení normalizovaných hodnot vahami
   - Sečtení vážených hodnot pro každou variantu

2. Interpretace výsledků
   - Vyšší skóre znamená lepší variantu
   - Výsledek zohledňuje všechna kritéria dle jejich vah
   - Rozdíly ve skóre ukazují relativní kvalitu variant
"""

  
# class Vystup_saw_komp(Vystup_saw_kompTemplate):
#   """
#   Stránka pro zobrazení vstupních dat a výsledků SAW analýzy.
#   Zobrazuje kompletní přehled analýzy včetně kritérií, variant a jejich hodnocení.
#   """
#   def __init__(self, analyza_id=None, **properties):
   
#     self.init_components(**properties)
#     self.analyza_id = analyza_id

#   def form_show(self, **event_args):
#     """
#     Event handler vyvolaný při zobrazení formuláře.
#     Načte data analýzy a zobrazí je v připravených komponentách.
#     """
#     if self.analyza_id:
#         try:
#             analyza_data = anvil.server.call('nacti_kompletni_analyzu', self.analyza_id)
#             self.zobraz_vstup(analyza_data)
#             self.zobraz_normalizaci(analyza_data)
#             #self.rich_text_vysledek.content
#         except Exception as e:
#             alert(f"Chyba při načítání analýzy: {str(e)}")
#     else:
#         self.rich_text_vstupni_data.text = "Nepřišlo žádné ID analýzy."
#         self.rich_text_normalizace.text = "Není co počítat."
#         self.rich_text_vystupni_data.text = "Není co počítat."

#   def zobraz_vstup(self, analyza_data):
#     """
#     Formátuje a zobrazuje vstupní data analýzy.
    
#     Args:
#         analyza_data: Slovník obsahující kompletní data analýzy
#     """
#     # Základní informace o analýze
#     zakladni_info = f"""
# # {analyza_data['analyza']['nazev']}

# ### Základní informace
# - **Metoda**: {analyza_data['analyza']['zvolena_metoda']}
# - **Popis**: {analyza_data['analyza']['popis'] or 'Bez popisu'}

# ### Kritéria
# | Název kritéria | Typ | Váha |
# |----------------|-----|------|
# """
    
#     # Přidání kritérií do tabulky
#     for k in analyza_data['kriteria']:
#         vaha = float(k['vaha'])  # Převod na číslo pro formátování
#         zakladni_info += f"| {k['nazev_kriteria']} | {k['typ'].upper()} | {vaha:.3f} |\n"

#     # Seznam variant
#     zakladni_info += "\n### Varianty\n"
#     for v in analyza_data['varianty']:
#         if v['popis_varianty']:
#             zakladni_info += f"- **{v['nazev_varianty']}** - {v['popis_varianty']}\n"
#         else:
#             zakladni_info += f"- **{v['nazev_varianty']}**\n"

#     # Vytvoření hodnotící matice
#     zakladni_info += "\n### Hodnotící matice\n"
    
#     # Získání unikátních názvů variant a kritérií
#     varianty = [v['nazev_varianty'] for v in analyza_data['varianty']]
#     kriteria = [k['nazev_kriteria'] for k in analyza_data['kriteria']]
    
#     # Hlavička tabulky
#     zakladni_info += f"| Kritérium | {' | '.join(varianty)} |\n"
#     zakladni_info += f"|{'-' * 10}|{('|'.join('-' * 12 for _ in varianty))}|\n"
    
#     # Naplnění tabulky hodnotami
#     matice = analyza_data['hodnoty']['matice_hodnoty']
#     for krit in kriteria:
#         radek = f"| {krit} |"
#         for var in varianty:
#             klic = f"{var}_{krit}"
#             hodnota = matice.get(klic, "N/A")
#             if isinstance(hodnota, (int, float)):
#                 radek += f" {hodnota:.2f} |"
#             else:
#                 radek += f" {hodnota} |"
#         zakladni_info += radek + "\n"

#     self.rich_text_vstupni_data.content = zakladni_info

#   def zobraz_normalizaci(self, analyza_data):
#     """
#     Zobrazí normalizovanou matici a vážené hodnoty v UI komponentě.
#     """
#     vysledky = anvil.server.call('vypocet_normalizace', analyza_data)
    
#     nazvy_var = vysledky['nazvy_variant']
#     nazvy_krit = vysledky['nazvy_kriterii']
#     nmtx = vysledky['normalizovana_matice']

#     # 1. Zobrazení normalizované matice
#     md_text = "## Normalizace hodnot\n\n"
#     md_text += "| Varianta / Krit. | " + " | ".join(nazvy_krit) + " |\n"
#     md_text += "|" + "-|"*(len(nazvy_krit)+1) + "\n"

#     for i, var_name in enumerate(nazvy_var):
#         radek = f"| {var_name} |"
#         for j in range(len(nazvy_krit)):
#             val = nmtx[i][j]
#             radek += f" {round(val,3)} |"
#         md_text += radek + "\n"

#     # Přidání vysvětlujícího textu
#     md_text += """

# Normalizační matice (někdy též znormalizovaná matice) je výsledek úpravy původních hodnot (např. z různých kritérií) na jednotné měřítko tak, aby se spravedlivě porovnávaly. Jinými slovy, v původních datech může být jedno kritérium „cena v Kč" (velká čísla, kde menší hodnota je lepší – cost) a druhé „kvalita v bodech 1–10" (menší čísla, kde větší hodnota je lepší – benefit). Normalizací převedeme všechny sloupce do podobného intervalu (často [0,1]), abychom je mohli sčítat, násobit nebo jinak kombinovat.

# #### Vysvětlení procesu:
# 1. Pro každé kritérium je určen směr optimalizace (MAX/MIN)
# 2. Aplikuje se Min-Max normalizace:
#    - Pro každý sloupec (kritérium) se najde minimum a maximum
#    - Hodnoty jsou transformovány podle vzorce: (x - min) / (max - min)
#    - Pro MIN kritéria je výsledek odečten od 1
# 3. Výsledná normalizovaná matice obsahuje hodnoty v intervalu [0,1]
#    - 1 reprezentuje nejlepší hodnotu
#    - 0 reprezentuje nejhorší hodnotu

# """

#     # 2. Vytvoření slovníku pro vážené hodnoty
#     vysledky_soucinu = {}
#     for i, varianta in enumerate(nazvy_var):
#         vysledky_soucinu[varianta] = {}
#         for j, kriterium in enumerate(nazvy_krit):
#             norm_hodnota = nmtx[i][j]
#             vaha = float(analyza_data['kriteria'][j]['vaha'])
#             vysledky_soucinu[varianta][kriterium] = norm_hodnota * vaha

#     # 3. Přidání tabulky vážených hodnot
#     md_text += "## Vážené hodnoty\n\n"
    
#     # Získat seznam všech variant a kritérií
#     varianty = list(vysledky_soucinu.keys())
#     prvni_variant = varianty[0] if varianty else None
#     kriteria = list(vysledky_soucinu[prvni_variant].keys()) if prvni_variant else []
    
#     # Vytvoření tabulky
#     md_text += "| Varianta | " + " | ".join(kriteria) + " | **Součet** |\n"
#     md_text += "|" + "----|"*(len(kriteria)+2) + "\n"
    
#     # Naplnění řádků
#     for var in varianty:
#         radek = f"| **{var}** |"
#         soucet = 0.0
#         for krit in kriteria:
#             hodnota = vysledky_soucinu[var].get(krit, 0)
#             soucet += hodnota
#             radek += f" {round(hodnota, 3)} |"
#         radek += f" **{round(soucet, 3)}** |"
#         md_text += radek + "\n"

#     # After the weighted values table, add:
#     md_text += """

# **Tabulka vážených hodnot (normalizovaná hodnota × váha)**

# Podobně jako u normalizační matice je i tabulka vážených hodnot klíčovým krokem v procesu **vícekriteriální analýzy** (např. metodou SAW).

# Zatímco normalizační matice zachycuje převedené hodnoty na interval [0,1], v **tabulce vážených hodnot** každou tuto normalizovanou hodnotu ještě **násobíme** váhou daného kritéria.

# ### Postup výpočtu:

# 1. **Normalizace hodnot**
#    - Po určení, zda je kritérium typu „max" (benefit) či „min" (cost), se aplikuje např. **min-max** normalizace (viz předchozí text)
#    - Výsledkem je tzv. **normalizovaná matice**: každé kritérium se převede do intervalu [0,1]

# 2. **Váhy kritérií**
#    - Každému kritériu je přiřazena **váha** odrážející jeho důležitost vůči ostatním (součet vah bývá 1)
#    - Vyšší váha znamená, že se dané kritérium podílí na výsledku **významněji**

# 3. **Výpočet vážených hodnot**
#    - Pro každou buňku normalizované matice (tj. pro každou variantu a kritérium) se spočítá **součin**:
#      (normalizovaná hodnota) × (váha kritéria)
#    - Tím vznikne **tabulka vážených hodnot**, kde se už zároveň zohledňuje důležitost kritéria

# 4. **Interpretace**
#    - Výsledek v každé buňce vyjadřuje, **jak dobře** daná varianta splňuje kritérium, **s přihlédnutím** k jeho významnosti
#    - Nulové či velmi nízké hodnoty znamenají, že varianta v daném kritériu **silně zaostává**, i po zohlednění váhy
#    - Hodnoty blížící se 1 (resp. vyššího součtu přes všechna kritéria) znamenají, že varianta je **výhodná** z pohledu tohoto kritéria či celého souboru kritérií

# > **Tabulka vážených hodnot** tak představuje **mezikrok** před finálním vyčíslením *celkového skóre* každé varianty (např. v metodě SAW se tyto vážené hodnoty ještě **sečtou** do jednoho čísla).
# """

#     self.rich_text_normalizace.content = md_text
#     self.zobraz_vysledek(analyza_data, vysledky_soucinu)

#   def zobraz_vysledek(self, analyza_data, vysledky_soucinu):
#     """
#     Zobrazí finální výsledky SAW analýzy včetně seřazení variant a komentáře.
#     """
#     try:
#         # 1) Vypočítat celkové skóre pro každou variantu (suma vážených hodnot)
#         final_scores = {}
#         for varianta, hodnoty in vysledky_soucinu.items():
#             final_scores[varianta] = sum(hodnoty.values())

#         # 2) Seřadit varianty podle skóre
#         setridene = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)

#         # 3) Vytvořit markdown text s výsledky
#         md = "# Finální výsledky SAW analýzy\n\n"
        
#         # Tabulka výsledků
#         md += "| Pořadí | Varianta | Celkové skóre |\n"
#         md += "|---------|-----------|---------------|\n"
        
#         for i, (var, score) in enumerate(setridene, start=1):
#             md += f"| {i}. | **{var}** | {round(score, 3)} |\n"

#         # Přidat interpretaci výsledků
#         best_variant = setridene[0][0]
#         best_score = setridene[0][1]
#         worst_variant = setridene[-1][0]
#         worst_score = setridene[-1][1]
#         score_diff = best_score - worst_score

#         md += f"""

# ### Interpretace výsledků

# - **Nejlepší varianta**: **{best_variant}** (skóre: {round(best_score, 3)})
# - **Nejhorší varianta**: {worst_variant} (skóre: {round(worst_score, 3)})
# - **Rozdíl nejlepší-nejhorší**: {round(score_diff, 3)}

# ### Vysvětlení hodnocení

# 1. **Celkové skóre** každé varianty je součtem všech jejích vážených hodnot
# 2. **Vyšší skóre** znamená lepší variantu v kontextu:
#    - zadaných vah kritérií
#    - směrů optimalizace (MIN/MAX)
#    - původních hodnot kritérií

# > Toto hodnocení zohledňuje všechna kritéria současně a bere v úvahu jejich relativní důležitost definovanou vahami.

# """

#         self.rich_text_vysledek.content = md

#     except Exception as e:
#         alert(f"Chyba při zobrazení výsledků: {str(e)}")