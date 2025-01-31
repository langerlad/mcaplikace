kriteriufrom ._anvil_designer import Kriterium_RowTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Kriterium_Row(Kriterium_RowTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def link_smazat_kriterium_click(self, **event_args):
        """Smaže vybrané kritérium z databáze a obnoví seznam"""
        kriterium = self.item
        anvil.server.call('smazat_kriterium', kriterium['id'])
        self.parent.raise_event('x-refresh')
