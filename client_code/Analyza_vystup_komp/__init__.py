from ._anvil_designer import Analyza_vystup_kompTemplate
from anvil import *


class Analyza_vystup_komp(Analyza_vystup_kompTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
