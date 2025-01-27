from ._anvil_designer import Hlavni_oknoTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
from ..import Navigace
from .. import Sprava_dat


class Hlavni_okno(Hlavni_oknoTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    Navigace.komponenta_hl_okna = self # obsah pravého panelu
    uzivatel = Sprava_dat.je_prihlasen() 
    self.nastav_ucet(uzivatel)
    Navigace.go_domu()

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

  # nahraje komponentu pomocí add_component na konec pravého panelu
  def nahraj_komponentu(self, komp):
    self.pravy_panel.clear()
    self.pravy_panel.add_component(komp)

  # označení aktuálního odkazu v levém menu
  def set_active_nav(self, stav):
    self.link_domu.role = 'selected' if stav == 'domu' else None
    self.link_pridat_analyzu.role = 'selected' if stav == 'pridat' else None
    self.link_nastaveni.role = 'selected' if stav == 'nastaveni' else None
    self.link_info.role = 'selected' if stav == 'info' else None
    self.link_administrace.role = 'selected' if stav == 'administrace' else None
  
  # viditelnost linků na navbaru,
  def nastav_ucet(self, uzivatel):
    self.link_ucet.visible = uzivatel is not None
    self.link_odhlasit.visible = uzivatel is not None
    self.link_prihlasit.visible = uzivatel is None
    self.link_registrace.visible = uzivatel is None
  
  # vytvoření účtu / přihlášení    
  def link_registrace_click(self, **event_args):
    uzivatel = anvil.users.signup_with_form(allow_cancel=True)
    self.nastav_ucet(uzivatel)
    Navigace.go_domu()

  def link_odhlasit_click(self, **event_args):
    anvil.users.logout() # odhlášení na serveru
    self.nastav_ucet(None)
    Sprava_dat.logout() # smaže cache z klienta
    Navigace.go_domu()

  def link_prihlasit_click(self, **event_args):
    uzivatel = anvil.users.login_with_form(allow_cancel=True)
    self.nastav_ucet(uzivatel)
    Navigace.go_domu()
