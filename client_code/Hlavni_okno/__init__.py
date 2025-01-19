from ._anvil_designer import Hlavni_oknoTemplate
from anvil import *


class Hlavni_okno(Hlavni_oknoTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
