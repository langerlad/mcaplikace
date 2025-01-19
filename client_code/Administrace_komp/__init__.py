from ._anvil_designer import Administrace_kompTemplate
from anvil import *


class Administrace_komp(Administrace_kompTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
