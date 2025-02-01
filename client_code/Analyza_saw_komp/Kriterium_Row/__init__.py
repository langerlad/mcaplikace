from ._anvil_designer import Kriterium_RowTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...Uprava_kriteria_form import Uprava_kriteria_form


class Kriterium_Row(Kriterium_RowTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def link_smazat_kriterium_click(self, **event_args):
        """Smaže vybrané kritérium z databáze a obnoví seznam"""
        kriterium = self.item
        anvil.server.call('smazat_kriterium', kriterium["id"])
        self.parent.raise_event('x-refresh')

  def link_upravit_kriterium_click(self, **event_args):
    """Otevře modální okno pro úpravu kritéria"""

    # Vytvoření kopie dat kritéria
    kriterium_kopie = dict(self.item)
    
    # Otevření modálního okna s editací
    edit_form = Uprava_kriteria_form(item=kriterium_kopie)

    save_clicked = alert(
        content=edit_form,
        title="Editace kritéria",
        large=True,
        buttons=[("Uložit", True), ("Zrušit", False)]
    )
    
    if save_clicked:
        
      upravene_hodnoty = edit_form.get_updated_values()

      print(f"🔹 Odesílám na server ID: {self.item['id']} s daty: {upravene_hodnoty}")  # Debugging
      anvil.server.call('update_kriterium', self.item["id"], upravene_hodnoty)

      # Obnovení dat v parent formuláři
      self.parent.raise_event('x-refresh')  # Správné obnovení dat
ě

