from ._anvil_designer import Analyza_RowTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ... import Navigace


class Analyza_Row(Analyza_RowTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def button_smazat_click(self, **event_args):
        if confirm("Opravdu chcete odstranit tuto analýzu?", dismissible=True,
        buttons=[("Ano", True), ("Ne", False)]):
            anvil.server.call('smaz_analyzu', self.item['id'])
            self.parent.raise_event('x-refresh')

  def button_upravit_click(self, **event_args):
    print(f"Editing analysis with ID: {self.item['id']}")
    anvil.server.call('set_edit_analyza_id', self.item['id'])
    Navigace.go('uprava_analyzy')

  def button_vypocet_click(self, **event_args):
    Navigace.go('saw_vystup', analyza_id=self.item['id'])
           
