# -------------------------------------------------------
# RowTemplate: Varianta_Row
# -------------------------------------------------------
from ._anvil_designer import Varianta_RowTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. import Wizard_komp


class Varianta_Row(Varianta_RowTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

  def link_smazat_variantu_click(self, **event_args):
    if confirm("Opravdu chcete smazat tuto variantu?", dismissible=True,
        buttons=[("Ano", True), ("Ne", False)]):
      main_form = self.get_main_form()
      main_form.cached_varianty = [
        v for v in main_form.cached_varianty
        if v['nazev_varianty'] != self.item['nazev_varianty']
      ]
      self.parent.raise_event('x-refresh')

  def get_main_form(self):
    current = self
    while current and not isinstance(current, Wizard_komp):
      current = current.parent
    return current