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
    self.card_krok_2.visible = False
    
    # Inicializace vstupů krok 1, krok 2 a krok 3
    self.nazev = None
    self.popis = None
    self.zvolena_metoda = "SAW"
    self.nazev_kriteria = None
    self.typ = None
    self.vaha = None

    # Načtení uložených kritérií při inicializaci formuláře
    # self.nacti_kriteria()

    # Nastavení event handleru pro aktualizaci seznamu kritérií
    self.repeating_panel_kriteria.set_event_handler('x-refresh', self.nacti_kriteria)
       

  def button_dalsi_click(self, **event_args):
    """Přepne na druhý krok formuláře a uloží název, popis a metodu do db"""
    self.label_chyba.visible = False
    chyba = self.validace_vstupu()
    if chyba:
      self.label_chyba.text = chyba
      self.label_chyba.visible = True
      return

    # Uložení analýzy a získání jejího ID
    self.analyza_id = anvil.server.call("pridej_analyzu", self.nazev, self.popis, self.zvolena_metoda)
    print(f"Analýza vytvořena s ID: {self.analyza_id}")
    print("uložené údaje: {} {} {}".format(self.nazev, self.popis, self.zvolena_metoda))

    # Přepnutí na druhou kartu
    self.card_krok_1.visible = False
    self.card_krok_2.visible = True

    self.nacti_kriteria()

  def validace_vstupu(self):
    if not self.text_box_nazev.text:
      return "Zadejte název analýzy."
    self.nazev = self.text_box_nazev.text
    self.popis = self.text_area_popis.text
    return None

  def button_pridej_kriterium_click(self, **event_args):
    """Uloží kritérium do db"""
    self.label_chyba_2.visible = False
    chyba_2 = self.validace_pridej_kryterium()
    
    if chyba_2:
      self.label_chyba_2.text = chyba_2
      self.label_chyba_2.visible = True
      return

    # Kontrola, zda existuje analýza
    if not hasattr(self, 'analyza_id') or not self.analyza_id:
        alert("Nejdříve musíte vytvořit analýzu.")
        return

    try:
        self.vaha = float(self.text_box_vaha.text)
    except ValueError:
        alert("Zadejte platné číslo pro váhu kritéria.")
        return

    # Odeslání dat na server  
    anvil.server.call('pridej_kriterium', self.analyza_id, self.nazev_kriteria, self.typ, self.vaha)

    # Resetování vstupních polí
    self.text_box_nazev_kriteria.text = ""
    self.drop_down_typ.selected_value = None
    self.text_box_vaha.text = ""

    # Znovu načtení pouze druhé karty (ponechání uživatele na stejném kroku)
    self.card_krok_2.visible = False
    self.card_krok_2.visible = True

    # Znovu načtení seznamu kritérií
    self.nacti_kriteria()

  def validace_pridej_kryterium(self):
    if not self.text_box_nazev_kriteria.text:
      return "Zadejte název kritéria."    
    self.nazev_kriteria = self.text_box_nazev_kriteria.text
    
    if not self.drop_down_typ.selected_value:
      return "Vyberte typ kritéria - max, nebo min."    
    self.typ = self.drop_down_typ.selected_value

    if not self.text_box_vaha.text:
        return "Zadejte hodnotu váhy kritéria."

    try:
      vaha = float(self.text_box_vaha.text)
      if not (0 <= vaha <= 1):
        return "Váha musí být číslo mezi 0 a 1."
    except ValueError:
        return "Váha musí být platné číslo."
    self.vaha = self.text_box_vaha.text

  def nacti_kriteria(self):
    """Načte uložená kritéria a zobrazí je v repeating panelu""" 
    kriteria = anvil.server.call('nacti_kriteria', self.analyza_id)
    for kriterium in kriteria:
      kriterium['id'] = kriterium.get_id()  # Přidání row_id do slovníku
    self.repeating_panel_kriteria.items = kriteria