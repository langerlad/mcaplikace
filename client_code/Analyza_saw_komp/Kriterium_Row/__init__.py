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
    self.init_components(**properties)

  def link_smazat_kriterium_click(self, **event_args):
    if confirm("Opravdu chcete smazat toto kritérium?"):
      self.parent.parent.cached_kriteria = [k for k in self.parent.parent.cached_kriteria 
                                          if k['nazev_kriteria'] != self.item['nazev_kriteria']]
      self.parent.raise_event('x-refresh')

  def link_upravit_kriterium_click(self, **event_args):
    kriterium_kopie = dict(self.item)
    edit_form = Uprava_kriteria_form(item=kriterium_kopie)
    
    while True:
      save_clicked = alert(
        content=edit_form,
        title="Upravit kritérium",
        large=True,
        dismissible=True,
        buttons=[("Uložit", True), ("Zrušit", False)]
      )
      
      if not save_clicked:
        break
        
      updated_data = edit_form.get_updated_data()
      if updated_data:
        # Update cache instead of DB
        for k in self.parent.parent.cached_kriteria:
          if k['nazev_kriteria'] == self.item['nazev_kriteria']:
            k.update(updated_data)
            break
        self.parent.raise_event('x-refresh')
        break

