from ._anvil_designer import Neznam_uziv_kompTemplate
from anvil import *


class Neznam_uziv_komp(Neznam_uziv_kompTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
