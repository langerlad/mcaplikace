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
            self.zobraz_normalizaci_scikit(analyza_data)
            self.rich_text_vystupni_data.content = "Výpočet SAW bude doplněn."
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

## Základní informace
- **Metoda**: {analyza_data['analyza']['zvolena_metoda']}
- **Popis**: {analyza_data['analyza']['popis'] or 'Bez popisu'}

## Kritéria
| Název kritéria | Typ | Váha |
|----------------|-----|------|
"""
    
    # Přidání kritérií do tabulky
    for k in analyza_data['kriteria']:
        zakladni_info += f"| {k['nazev_kriteria']} | {k['typ']} | {k['vaha']} |\n"

    # Seznam variant
    zakladni_info += "\n## Varianty\n"
    for v in analyza_data['varianty']:
        zakladni_info += f"- **{v['nazev_varianty']}**"
        if v['popis_varianty']:
            zakladni_info += f": {v['popis_varianty']}"
        zakladni_info += "\n"

    # Vytvoření hodnotící matice
    zakladni_info += "\n## Hodnotící matice\n"
    
    # Získání unikátních názvů variant a kritérií
    varianty = [v['nazev_varianty'] for v in analyza_data['varianty']]
    kriteria = [k['nazev_kriteria'] for k in analyza_data['kriteria']]
    
    # Hlavička tabulky
    zakladni_info += "| Kritérium | " + " | ".join(varianty) + " |\n"
    zakladni_info += "|" + "-|"*(len(varianty) + 1) + "\n"
    
    # Naplnění tabulky hodnotami
    matice = analyza_data['hodnoty']['matice_hodnoty']
    for krit in kriteria:
        radek = f"| {krit} |"
        for var in varianty:
            klic = f"{var}_{krit}"
            hodnota = matice.get(klic, "N/A")
            radek += f" {hodnota} |"
        zakladni_info += radek + "\n"

    self.rich_text_vstupni_data.content = zakladni_info

  def zobraz_normalizaci(self, analyza_data):
    """
    Zavolá serverový modul 'vypocet_normalizace' a zobrazí normalizovanou matici v nějaké UI komponentě.
    """
    vysledky = anvil.server.call('vypocet_normalizace', analyza_data)
    # vysledky by měl obsahovat klíče: 'nazvy_variant', 'nazvy_kriterii', 'normalizovana_matice', 'zprava'

    nazvy_var = vysledky['nazvy_variant']
    nazvy_krit = vysledky['nazvy_kriterii']
    nmtx = vysledky['normalizovana_matice']

    # Tady si v UI vygenerujte např. tabulku v RichText
    md_text = "# Výsledek normalizace\n\n"
    md_text += "| Varianta / Krit. | " + " | ".join(nazvy_krit) + " |\n"
    md_text += "|" + "-|"*(len(nazvy_krit)+1) + "\n"

    for i, var_name in enumerate(nazvy_var):
        radek = f"| {var_name} |"
        for j in range(len(nazvy_krit)):
            val = nmtx[i][j]
            radek += f" {round(val,3)} |"
        md_text += radek + "\n"

    # Nyní třeba:
    print(md_text)  # pro ladění v konzoli
    # Nebo to zobrazit v RichText komponentě:
    # self.rich_text_normalizace.content = md_text

#   def zobraz_normalizaci_scikit(self, analyza_data):
#     """
#     Zobrazí postup normalizace pomocí scikit-criteria včetně mezivýpočtů.
#     Výsledek zobrazí v self.rich_text_normalizace.
#     """
#     try:
#         print("Starting zobraz_normalizaci_scikit")  # Debug print
        
#         # Získání výsledků ze serveru
#         vysledky = anvil.server.call('vypocet_normalizace', analyza_data)
#         print("Got results from server:", vysledky)  # Debug print

#         # Vytvoření výstupu s vysvětlením
#         txt = """# Postup normalizace metodou SAW

# ## 1. Vstupní matice hodnot
# Původní hodnoty před normalizací:
        
# | Varianta / Kritérium | """ + " | ".join(vysledky['nazvy_kriterii']) + " |\n"
#         txt += "|" + "-|"*(len(vysledky['nazvy_kriterii'])+1) + "\n"
        
#         for i, var_name in enumerate(vysledky['nazvy_variant']):
#             radek = f"| {var_name} |"
#             for val in vysledky['puvodni_matice'][i]:
#                 radek += f" {val} |"
#             txt += radek + "\n"

#         txt += "\n## 2. Parametry normalizace\n"
#         txt += "### Váhy kritérií:\n"
#         for krit, vaha in zip(vysledky['nazvy_kriterii'], vysledky['vahy']):
#             txt += f"- {krit}: {vaha}\n"
        
#         txt += "\n### Směry optimalizace:\n"
#         for krit, smer in zip(vysledky['nazvy_kriterii'], vysledky['smery']):
#             txt += f"- {krit}: {smer}\n"

#         txt += """
# ## 3. Normalizovaná matice
# Normalizace metodou sum - hodnoty jsou vyděleny součtem sloupce:
        
# | Varianta / Kritérium | """ + " | ".join(vysledky['nazvy_kriterii']) + " |\n"
#         txt += "|" + "-|"*(len(vysledky['nazvy_kriterii'])+1) + "\n"
        
#         for i, var_name in enumerate(vysledky['nazvy_variant']):
#             radek = f"| {var_name} |"
#             for val in vysledky['normalizovana_matice'][i]:
#                 radek += f" {val:.3f} |"
#             txt += radek + "\n"

#         txt += """
# ## Vysvětlení procesu
# 1. Nejprve se určí směr optimalizace pro každé kritérium (MAX/MIN)
# 2. Aplikuje se normalizace sum:
#    - Pro MAX kritéria: hodnota / součet všech hodnot ve sloupci
#    - Pro MIN kritéria: (1/hodnota) / součet (1/hodnota) všech variant
# 3. Výsledná normalizovaná matice obsahuje hodnoty v intervalu [0,1]
# """
#         print("Generated text:", txt)  # Debug print
#         self.rich_text_normalizace.content = txt
#         print("Text set to rich_text_normalizace")  # Debug print

#     except Exception as e:
#         print(f"Error in zobraz_normalizaci_scikit: {str(e)}")  # Debug print
#         alert(f"Chyba při zobrazení normalizace: {str(e)}")
