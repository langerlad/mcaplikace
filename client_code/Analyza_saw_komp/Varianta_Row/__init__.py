from ._anvil_designer import Varianta_RowTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Varianta_Row(Varianta_RowTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def link_smazat_variantu_click(self, **event_args):
    """Smaže vybranou variantu z databáze a obnoví seznam"""
    varianta = self.item
    anvil.server.call('smazat_variantu', varianta["id"])
    self.parent.raise_event('x-refresh')

   
