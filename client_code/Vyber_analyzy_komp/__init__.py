from ._anvil_designer import Vyber_analyzy_kompTemplate
from anvil import *


class Vyber_analyzy_komp(Vyber_analyzy_kompTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
