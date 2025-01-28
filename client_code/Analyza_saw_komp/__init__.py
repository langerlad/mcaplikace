from ._anvil_designer import Analyza_saw_kompTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
from .. import Navigace


class Analyza_saw_komp(Analyza_saw_kompTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    self.nazev = None
    self.popis = None
    self.zvolena_metoda = "SAW"
   

  def button_dalsi_click(self, **event_args):
    """This method is called when the button Další krok is clicked"""
    self.label_chyba.visible = False
    chyba = self.validace_vstupu()
    if chyba:
      self.label_chyba.text = chyba
      self.label_chyba.visible = True
      return

    print("uložené údaje: {} {} {}".format(self.nazev, self.popis, self.zvolena_metoda))
    anvil.server.call("pridej_analyzu", self.nazev, self.popis, self.zvolena_metoda)

  def validace_vstupu(self):

    if not self.text_box_nazev.text:
      return "Zadejte název analýzy"

    self.nazev = self.text_box_nazev.text
    self.popis = self.text_area_popis.text

    return None
