from ._anvil_designer import Vystup_saw_kompTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users


class Vystup_saw_komp(Vystup_saw_kompTemplate):
  def __init__(self, analyza_id=None, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    
    # Instanční proměnné
    self.analyza_id = analyza_id

  def form_show(self, **event_args):
        if self.analyza_id:
            analyza_data = anvil.server.call('nacti_kompletni_analyzu', self.analyza_id)

            self.zobraz_vstup(analyza_data)

            # spočítáme SAW scikit-criteria a výstup dáme do rich_text_vystupni_data
            # "Zatím nenaimplementováno"
            self.rich_text_vystupni_data.content = "Výpočet SAW bude doplněn."
        else:
            self.rich_text_vstupni_data.text = "Nepřišlo žádné ID analýzy."
            self.rich_text_vystupni_data.text = "Není co počítat."

  def zobraz_vstup(self, analyza_data):
      txt = f"""
      **Název analýzy**: {analyza_data['analyza']['nazev']}
      
      **Popis**: {analyza_data['analyza']['popis']}
      
      **Metoda**: {analyza_data['analyza']['zvolena_metoda']}
      """
    
      # Kritéria
      txt += "\n\n**Kritéria**:\n"
      for k in analyza_data['kriteria']:
          txt += f"- {k['nazev_kriteria']} (typ: {k['typ']}, váha: {k['vaha']})\n"

      # Varianty
      txt += "\n**Varianty**:\n"
      for v in analyza_data['varianty']:
          txt += f"- {v['nazev_varianty']}: {v['popis_varianty']}\n"

      # Hodnoty
      txt += "\n**Hodnoty (matice_hodnoty)**:\n"
      matice = analyza_data['hodnoty']['matice_hodnoty']
      for klic, val in matice.items():
          txt += f"- {klic} = {val}\n"

      self.rich_text_vstupni_data.content = txt

      # Do rich_text_vystupni_data zatím nic nedáváme,
      # vyplní se až při dalším kroku (např. s rozhodovací metodou).