from ._anvil_designer import Matice_kritTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Matice_krit(Matice_kritTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    self.label_matice_nazev_kriteria.text = self.item['nazev_kriteria']
    self.text_box_matice_hodnota.text = str(self.item['hodnota'])
