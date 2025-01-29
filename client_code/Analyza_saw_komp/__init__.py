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

    # Skrytí druhé karty na začátku
    self.card_kork_2.visible = False
    
    self.nazev = None
    self.popis = None
    self.zvolena_metoda = "SAW"

    # Inicializace seznamu kritérií
    self.kriteria = []
    self.repeating_panel_kriteria.items = self.kriteria
   

  def button_dalsi_click(self, **event_args):
    """Přepne na druhý krok formuláře a uloží název, popis a metodu do db"""
    self.label_chyba.visible = False
    chyba = self.validace_vstupu()
    if chyba:
      self.label_chyba.text = chyba
      self.label_chyba.visible = True
      return

    print("uložené údaje: {} {} {}".format(self.nazev, self.popis, self.zvolena_metoda))
    anvil.server.call("pridej_analyzu", self.nazev, self.popis, self.zvolena_metoda)

    # Přepnutí na druhou kartu
    self.card_krok_1.visible = False
    self.card_kork_2.visible = True

  def validace_vstupu(self):

    if not self.text_box_nazev.text:
      return "Zadejte název analýzy"

    self.nazev = self.text_box_nazev.text
    self.popis = self.text_area_popis.text

    return None

  def link_pridej_kriterium_click(self, **event_args):
    """Přidá nový řádek pro kritérium"""
    self.kriteria.append({"nazev_kriteria": "", "typ": "max", "vaha": 1.0})
    self.repeating_panel_kriteria.items = self.kriteria
