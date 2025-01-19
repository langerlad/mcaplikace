from ._anvil_designer import Prihlas_uziv_kompTemplate
from anvil import *


class Prihlas_uziv_komp(Prihlas_uziv_kompTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
