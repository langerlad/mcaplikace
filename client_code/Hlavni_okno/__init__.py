from ._anvil_designer import Hlavni_oknoTemplate
from anvil import *
from ..import Navigace


class Hlavni_okno(Hlavni_oknoTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    Navigace.komponenta_hl_okna = self

  # linky z levého panelu a navbaru - řeší modul Navigace
  def link_domu_click(self, **event_args):
    Navigace.go_domu()
  def link_pridat_analyzu_click(self, **event_args):
    Navigace.go_pridat_analyzu()
  def link_nastaveni_click(self, **event_args):
    Navigace.go_nastaveni()
  def link_info_click(self, **event_args):
    Navigace.go_info()
  def link_administrace_click(self, **event_args):
    Navigace.go_administrace()
  def link_ucet_click(self, **event_args):
   Navigace.go_ucet()

  def nahraj_komponentu(self, komp):
    """"funkce nahraje komponent pomocí add_component na konec panelu"""
    self.pravy_panel.clear()
    self.pravy_panel.add_component(komp)

  def set_active_nav(self, stav):
    self.link_domu.role = 'selected' if stav == 'domu' else None
    self.link_pridat_analyzu.role = 'selected' if stav == 'pridat' else None
    self.link_nastaveni.role = 'selected' if stav == 'nastaveni' else None
    self.link_info.role = 'selected' if stav == 'info' else None
    self.link_administrace.role = 'selected' if stav == 'administrace' else None