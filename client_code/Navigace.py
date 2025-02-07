# -------------------------------------------------------
# Modul: Navigace
# -------------------------------------------------------
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
from anvil import *
from .Administrace_komp import Administrace_komp
from .Analyza_ahp_komp import Analyza_ahp_komp
from .Analyza_vystup_komp import Analyza_vystup_komp
from .Analyza_saw_komp import Analyza_saw_komp
from .Info_komp import Info_komp
from .Nastaveni_komp import Nastaveni_komp
from .Neznam_uziv_komp import Neznam_uziv_komp
from .Prihlas_uziv_komp import Prihlas_uziv_komp
from .Ucet_komp import Ucet_komp
from .Vyber_analyzy_komp import Vyber_analyzy_komp
from . import Sprava_dat

komponenta_hl_okna = None

def ziskej_komponentu():
  if komponenta_hl_okna is None:
    raise Exception("Není zvolena žádná komponenta hlavního okna")
  return komponenta_hl_okna

def go_domu():
  if over_a_smaz_rozpracovanou("domu"):
    set_active_nav("domu")
    komp = ziskej_komponentu()
    uzivatel = Sprava_dat.je_prihlasen()
    if uzivatel:
      komp.nahraj_komponentu(Prihlas_uziv_komp())
    else:
      komp.nahraj_komponentu(Neznam_uziv_komp())

def go_pridat_analyzu():
  if over_a_smaz_rozpracovanou("pridat"):
    set_active_nav("pridat")
    uzivatel = kontrola_prihlaseni()
    if not uzivatel:
      go_domu()
      return
    
    komp = ziskej_komponentu()
    komp.nahraj_komponentu(Vyber_analyzy_komp())

def go_nastaveni():
  if over_a_smaz_rozpracovanou("nastaveni"):
    set_active_nav("nastaveni")
    uzivatel = kontrola_prihlaseni()
    if not uzivatel:
      go_domu()
      return
    
    komp = ziskej_komponentu()
    komp.nahraj_komponentu(Nastaveni_komp())

def go_info():
  if over_a_smaz_rozpracovanou("info"):
    set_active_nav("info")
    komp = ziskej_komponentu()
    komp.nahraj_komponentu(Info_komp())

def go_administrace():
  if over_a_smaz_rozpracovanou("administrace"):
    set_active_nav("administrace")
    uzivatel = kontrola_prihlaseni()
    if not uzivatel:
      go_domu()
      return
    
    komp = ziskej_komponentu()
    komp.nahraj_komponentu(Administrace_komp())

def go_ucet():
  if over_a_smaz_rozpracovanou("ucet"):
    uzivatel = kontrola_prihlaseni()
    if not uzivatel:
      go_domu()
      return
    
    komp = ziskej_komponentu()
    komp.nahraj_komponentu(Ucet_komp())

def go_ahp():
  uzivatel = kontrola_prihlaseni()
  if not uzivatel:
    go_domu()
    return
  komp = ziskej_komponentu()
  komp.nahraj_komponentu(Analyza_ahp_komp())

def go_saw():
  uzivatel = kontrola_prihlaseni()
  if not uzivatel:
    go_domu()
    return
  komp = ziskej_komponentu()
  komp.nahraj_komponentu(Analyza_saw_komp())

def kontrola_prihlaseni():
  uzivatel = Sprava_dat.je_prihlasen()
  if uzivatel:
    return uzivatel
  uzivatel = anvil.users.login_with_form(allow_cancel=True)
  komp = ziskej_komponentu()
  komp.nastav_ucet(uzivatel)
  return uzivatel

def set_active_nav(stav):
  komp = ziskej_komponentu()
  komp.set_active_nav(stav)

def over_a_smaz_rozpracovanou(cilova_stranka):
  """
  Zkontroluje, zda v pravém panelu není rozdělaná SAW analýza.
  Pokud je, a uživatel potvrdí, smaže ji ze serveru a vrátí True.
  Pokud uživatel odmítne, vrátí False a zůstane na stránce.
  """
  komp = ziskej_komponentu()
  if hasattr(komp, 'pravy_panel'):
    components = komp.pravy_panel.get_components()
    if (components
        and isinstance(components[0], Analyza_saw_komp)
        and components[0].analyza_id):
      if confirm("Opustíte rozpracovanou analýzu a data budou smazána. Pokračovat?", dismissible=True,
        buttons=[("Ano", True), ("Ne", False)]):
        anvil.server.call('smaz_analyzu', components[0].analyza_id)
        return True
      return False
  return True