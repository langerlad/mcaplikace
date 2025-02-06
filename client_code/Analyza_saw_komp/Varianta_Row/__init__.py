from ._anvil_designer import Varianta_RowTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. import Analyza_saw_komp


class Varianta_Row(Varianta_RowTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def link_smazat_variantu_click(self, **event_args):
    if confirm("Opravdu chcete smazat tuto variantu?"):
        main_form = self.get_main_form()
        main_form.cached_varianty = [v for v in main_form.cached_varianty 
                                   if v['nazev_varianty'] != self.item['nazev_varianty']]
        self.parent.raise_event('x-refresh')

  def get_main_form(self):
      current = self
      while current and not isinstance(current, Analyza_saw_komp):
          current = current.parent
      return current


   
