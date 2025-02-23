# -------------------------------------------------------
# Form: Hlavni_okno
# -------------------------------------------------------
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
    self.init_components(**properties)

    # Nastavení hlavní komponenty (obsah pravého panelu)
    Navigace.komponenta_hl_okna = self
    uzivatel = Sprava_dat.je_prihlasen() 
    self.nastav_ucet(uzivatel)
    Navigace.go('domu')

  # Odkazy z levého panelu a navbaru - řeší modul Navigace
  def link_domu_click(self, **event_args):
    Navigace.go('domu')

  def link_pridat_analyzu_click(self, **event_args):
    Navigace.go('pridat_analyzu')

  def link_nastaveni_click(self, **event_args):
    Navigace.go('nastaveni')

  def link_info_click(self, **event_args):
    Navigace.go('info')

  def link_administrace_click(self, **event_args):
    Navigace.go('administrace')

  def link_ucet_click(self, **event_args):
    Navigace.go('ucet')

  # Nahraje komponentu do pravého panelu
  def nahraj_komponentu(self, komp):
    self.pravy_panel.clear()
    self.pravy_panel.add_component(komp)

  # Označení aktuálního odkazu v levém menu
  def set_active_nav(self, stav):
    self.link_domu.role = 'selected' if stav == 'domu' else None
    self.link_pridat_analyzu.role = 'selected' if stav == 'pridat' else None
    self.link_nastaveni.role = 'selected' if stav == 'nastaveni' else None
    self.link_info.role = 'selected' if stav == 'info' else None
    self.link_administrace.role = 'selected' if stav == 'administrace' else None

  def nastav_ucet(self, uzivatel):
    """
    Nastaví viditelnost prvků pro přihlášeného/odhlášeného uživatele
    a zobrazí informace o přihlášeném uživateli.
    
    Args:
        uzivatel: Instance přihlášeného uživatele nebo None
    """
    prihlasen = (uzivatel is not None)
    self.link_ucet.visible = prihlasen
    self.link_odhlasit.visible = prihlasen
    self.link_prihlasit.visible = not prihlasen
    self.link_registrace.visible = not prihlasen
    
    if prihlasen:
        uzivatel_info = self.ziskej_info_uzivatele(uzivatel)
        if uzivatel_info:
            self.link_ucet.text = uzivatel_info['zobrazene_jmeno']
            self.link_ucet.tooltip = uzivatel_info['tooltip']

  def ziskej_info_uzivatele(self, uzivatel):
    """
    Získá informace o uživateli pro zobrazení v UI.
    
    Args:
        uzivatel: Instance přihlášeného uživatele
    
    Returns:
        dict: Slovník obsahující 'zobrazene_jmeno' a 'tooltip',
              nebo None v případě chyby
    """
    if not uzivatel:
        return None
    
    try:
        # Získání emailu z objektu uživatele
        email = uzivatel['email']
        zobrazeny_text = f"[{email}]"
            
        return {
            'zobrazene_jmeno': zobrazeny_text,
            'tooltip': zobrazeny_text
        }
    except Exception as e:
        print(f"Chyba při získávání informací o uživateli: {str(e)}")
        return None
  
  # Vytvoření účtu / přihlášení    
  def link_registrace_click(self, **event_args):
    uzivatel = anvil.users.signup_with_form(allow_cancel=True)
    self.nastav_ucet(uzivatel)
    Navigace.go('domu')

  def link_odhlasit_click(self, **event_args):
    anvil.users.logout()  # Odhlášení na serveru
    self.nastav_ucet(None)
    Sprava_dat.logout()   # Smaže cache z klienta
    Navigace.go('domu')

  def link_prihlasit_click(self, **event_args):
    uzivatel = anvil.users.login_with_form(allow_cancel=True)
    self.nastav_ucet(uzivatel)
    Navigace.go('domu')