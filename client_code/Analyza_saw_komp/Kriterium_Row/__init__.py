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
    kriterium_kopie = {
      'id': self.item['id'],
      'nazev_kriteria': self.item['nazev_kriteria'],
      'typ': self.item['typ'],
      'vaha': self.item['vaha']
    }
    
    # Vytvoření formuláře pro úpravu
    edit_form = Uprava_kriteria_form(item=kriterium_kopie)
    
    while True:  # Loop until we get valid data or user cancels
      # Otevření modálního okna s editací
      save_clicked = alert(
        content=edit_form,
        title="Upravit kritérium",
        large=True,
        dismissible=True,
        buttons=[("Uložit", True), ("Zrušit", False)]
      )
      
      if not save_clicked:
        break  # User clicked Cancel
        
      # Získání aktualizovaných dat z formuláře
      updated_data = edit_form.get_updated_data()
      if updated_data:  # If validation passed
        # Volání serverové metody pro aktualizaci
        anvil.server.call('uprav_kriterium', self.item['id'], updated_data)
        # Obnovení dat v parent formuláři
        self.parent.raise_event('x-refresh')
        break
      # If validation failed, the form will show the error and stay open

