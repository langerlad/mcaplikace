from ._anvil_designer import Uprava_kriteria_formTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Uprava_kriteria_form(Uprava_kriteria_formTemplate):
  def __init__(self, item, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.


