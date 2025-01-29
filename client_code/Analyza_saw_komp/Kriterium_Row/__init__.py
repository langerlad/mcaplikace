from ._anvil_designer import Kriterium_RowTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Kriterium_Row(Kriterium_RowTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def text_box_kriterium_change(self, **event_args):
    """Uloží změnu názvu kritéria do seznamu"""
    self.item["nazev_kriteria"] = self.text_box_nazev_kriteria.text

  def drop_down_typ_change(self, **event_args):
    """Uloží změnu typ min/max do seznamu"""
    self.item["typ"] = self.drop_down_typ.selected_value

  def text_box_vaha_change(self, **event_args):
    """Uloží změnu váhy kritéria do seznamu"""
    try:
      self.item["vaha"] = float(self.text_box_vaha.text)
    except ValueError:
      self.item["vaha"] = 1.0  # Výchozí váha, pokud uživatel zadá nesprávnou hodnotu