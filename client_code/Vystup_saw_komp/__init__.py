from ._anvil_designer import Vystup_saw_kompTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users

# scikit-criteria import
from skcriteria import Data, MAX, MIN
from skcriteria.madm import simple


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

  def zobraz_normalizaci_scikit(self, analyza_data):
    """
    Vytvoří scikit-criteria Data objekt a provede WeightedSum pro zjištění normalizované matice.
    Výsledek (n-matrix) zobrazí v self.rich_text_normalizace.
    """
    varianty = analyza_data['varianty']   # [{'nazev_varianty':..., 'popis_varianty':...}, ...]
    kriteria = analyza_data['kriteria']   # [{'nazev_kriteria':..., 'typ':..., 'vaha':...}, ...]
    matice_hodnot = analyza_data['hodnoty']['matice_hodnoty']  # dict { "Dodavatel A_Cena": 100.0, ... }

    # 1) Připravit "mtx" (list of lists) pro scikit-criteria:
    #    - Každý řádek = 1 varianta, sloupce = kritéria
    #    - objectives = [MAX nebo MIN podle 'typ' (benefit/cost)]
    #    - weights = [vaha1, vaha2, ...]
    #    - anames = ['Dodavatel A', ...], cnames = ['Kvalita', 'Cena', ...]

    anames = [v['nazev_varianty'] for v in varianty]
    cnames = [k['nazev_kriteria'] for k in kriteria]

    # objectives
    objectives = []
    for k in kriteria:
        if k['typ'] == 'max':
            objectives.append(MAX)
        else:
            objectives.append(MIN)

    # weights
    weights = [k['vaha'] for k in kriteria]

    # Vytvoříme matici (mtx)
    mtx = []
    for var in varianty:
        row = []
        for krit in kriteria:
            klic = f"{var['nazev_varianty']}_{krit['nazev_kriteria']}"
            hod = matice_hodnot.get(klic, 0)
            row.append(hod)
        mtx.append(row)

    # 2) Vytvořit Data objekt scikit-criteria
    data_obj = Data(
        mtx=mtx,
        objectives=objectives,
        weights=weights,
        anames=anames,
        cnames=cnames
    )

    # 3) WeightedSum rozhodovač
    decisor = simple.WeightedSum(mnorm="sum") 
    # mnorm="sum" → normalizace je L1 – tj. sečítá sloupce? 
    # Můžete zkusit i mnorm=None a nastavit si transformaci jinde,
    # ale to je detail scikit-criteria.

    # 4) Zavolat decide
    result = decisor.decide(data_obj)

    # 5) Získat normalizovanou matici
    nmatrix = result.e_.nmatrix   # 2D array (rows=varianty, cols=kriteria)
    # anames = result.e_.alternatives
    # cnames = result.e_.criteria  # to by mělo odpovídat anames, cnames výše

    # 6) Vygenerovat Markdown tabulku do rich_text_normalizace

    txt = "# Normalizovaná matice (scikit-criteria)\n\n"
    # Hlavička
    txt += "| Varianta / Kritérium | " + " | ".join(cnames) + " |\n"
    txt += "|" + "-|"*(len(cnames)+1) + "\n"

    for i, var_name in enumerate(result.e_.alternatives):
        radek = f"| {var_name} |"
        for j, c_name in enumerate(result.e_.criteria):
            val = nmatrix[i][j]
            radek += f" {round(val, 3)} |"
        txt += radek + "\n"

    self.rich_text_normalizace.content = txt
