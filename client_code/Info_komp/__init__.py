from ._anvil_designer import Info_kompTemplate
from anvil import *


class Info_komp(Info_kompTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
