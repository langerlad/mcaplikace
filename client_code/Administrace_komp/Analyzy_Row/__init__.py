from ._anvil_designer import Analyzy_RowTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Analyzy_Row(Analyzy_RowTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    # Zoom link zobrazíme pouze pro SAW analýzy
    self.link_zoom.visible = (self.item['zvolena_metoda'] == 'SAW')

  def link_zoom_click(self, **event_args):
    """Otevře výstup analýzy po kliknutí na zoom."""
    # Zkontrolujeme, zda máme k dispozici ID analýzy
    if 'id' not in self.item:
        print("CHYBA: Chybí ID analýzy")
        return
        
    # Získáme ID analýzy a vyvoláme událost
    analyza_id = self.item['id']
    print(f"Kliknutí na zoom pro analýzu: {analyza_id}")
    self.parent.raise_event('x-zobraz-vystup', analyza_id=analyza_id)
