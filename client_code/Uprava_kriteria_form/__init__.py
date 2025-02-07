# -------------------------------------------------------
# Form: Uprava_kriteria_form
# -------------------------------------------------------
from ._anvil_designer import Uprava_kriteria_formTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Uprava_kriteria_form(Uprava_kriteria_formTemplate):
  def __init__(self, item, **properties):
    self.init_components(**properties)
    self.text_box_nazev_kriteria.text = item['nazev_kriteria']
    self.drop_down_typ.selected_value = item['typ']
    self.text_box_vaha.text = str(item['vaha'])
    self._item = item
    self.label_chyba.visible = False

  def validuj_vahu(self):
    try:
      vaha = float(self.text_box_vaha.text)
      if not (0 <= vaha <= 1):
        self.label_chyba.text = "Váha musí být číslo mezi 0 a 1"
        self.label_chyba.visible = True
        return False
      return True
    except ValueError:
      self.label_chyba.text = "Váha musí být platné číslo"
      self.label_chyba.visible = True
      return False

  def ziskej_upravena_data(self):
    """
    Z validovaných polí vrátí dict s aktualizovanými daty kritéria
    """
    if not self.validuj_vahu():
      return None
    return {
      'nazev_kriteria': self.text_box_nazev_kriteria.text,
      'typ': self.drop_down_typ.selected_value,
      'vaha': float(self.text_box_vaha.text)
    }

  def text_box_vaha_lost_focus(self, **event_args):
    self.validuj_vahu()