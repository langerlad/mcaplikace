from ._anvil_designer import Vyber_analyzy_kompTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
from .. import Navigace


class Vyber_analyzy_komp(Vyber_analyzy_kompTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def link_ahp_click(self, **event_args):
    Navigace.go_ahp()

  def link_SAW_click(self, **event_args):
    Navigace.go_saw()

