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
    
    # Initialize form with the existing criterion data
    self.text_box_nazev_kriteria.text = item['nazev_kriteria']
    self.drop_down_typ.selected_value = item['typ']
    self.text_box_vaha.text = str(item['vaha'])
    
    # Store the original item for reference
    self._item = item
  
  def get_updated_data(self):
    """Returns the updated criterion data"""
    return {
      'id': self._item['id'],
      'nazev_kriteria': self.text_box_nazev_kriteria.text,
      'typ': self.drop_down_typ.selected_value,
      'vaha': float(self.text_box_vaha.text)
    }


