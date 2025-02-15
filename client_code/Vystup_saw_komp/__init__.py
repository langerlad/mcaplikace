from ._anvil_designer import Vystup_saw_kompTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users


class Vystup_saw_komp(Vystup_saw_kompTemplate):
  def __init__(self, analyza_data, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    
    # Instanční proměnné
    self.analyza_data = analyza_data

  def form_show(self, **event_args):
      # Zobrazíme názvy a další vstupní údaje v richtext
      # Můžeme použít markdown formát nebo jen prostý text
      txt = f"""
      **Název analýzy**: {self.analyza_data['analyza']['nazev']}

      **Popis**: {self.analyza_data['analyza']['popis']}

      **Metoda**: {self.analyza_data['analyza']['zvolena_metoda']}
      """
      
      # Kritéria
      txt += "\n\n**Kritéria**:\n"
      for k in self.analyza_data['kriteria']:
          txt += f"- {k['nazev_kriteria']} (typ: {k['typ']}, váha: {k['vaha']})\n"

      # Varianty
      txt += "\n**Varianty**:\n"
      for v in self.analyza_data['varianty']:
          txt += f"- {v['nazev_varianty']}: {v['popis_varianty']}\n"

      # Hodnoty (matice)
      txt += "\n**Matice hodnot**:\n"
      matice = self.analyza_data['hodnoty']['matice_hodnoty']
      for klic, val in matice.items():
          txt += f"- {klic} = {val}\n"

      self.rich_text_vstupni_data.text = txt

      # Do rich_text_vystupni_data zatím nic nedáváme,
      # vyplní se až při dalším kroku (např. s rozhodovací metodou).