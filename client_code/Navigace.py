import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
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

#funkce ověřuje vložení komponenty do hlavního okna
def get_komp():
  if komponenta_hl_okna is None:
    raise Exception("Není zvolena žádná komponenta hlavního okna")

  return komponenta_hl_okna

def go_domu():
  set_active_nav("domu")
  #set_title("")
  komp = get_komp()
  uzivatel = Sprava_dat.je_prihlasen() # ptáme se anvilu jestli máme přihlášeného uživatele
  if uzivatel:
    komp.nahraj_komponentu(Prihlas_uziv_komp()) # Dashboard
  else:
    komp.nahraj_komponentu(Neznam_uziv_komp()) # Landing page

def go_pridat_analyzu():
  set_active_nav("pridat")
  #set_title("")

  uzivatel = kontrola_prihlaseni()
  if not uzivatel:
    go_domu()
    return
  
  komp = get_komp()
  komp.nahraj_komponentu(Vyber_analyzy_komp())

def go_nastaveni():
  set_active_nav("nastaveni")
  #set_title("")

  uzivatel = kontrola_prihlaseni()
  if not uzivatel:
    go_domu()
    return
  
  komp = get_komp()
  komp.nahraj_komponentu(Nastaveni_komp())

def go_info():
  set_active_nav("info")
  #set_title("")
  komp = get_komp()
  komp.nahraj_komponentu(Info_komp())

def go_administrace():
  set_active_nav("administrace")
  #set_title("")

  uzivatel = kontrola_prihlaseni()
  if not uzivatel:
    go_domu()
    return
  
  komp = get_komp()
  komp.nahraj_komponentu(Administrace_komp())

def go_ucet():
  #set_title("")

  uzivatel = kontrola_prihlaseni()
  if not uzivatel:
    go_domu()
    return
  
  komp = get_komp()
  komp.nahraj_komponentu(Ucet_komp())

# link je na komponentě Výběr analýzy
def go_ahp():

  uzivatel = kontrola_prihlaseni()
  if not uzivatel:
    go_domu()
    return
  
  komp = get_komp()
  komp.nahraj_komponentu(Analyza_ahp_komp())

def go_saw():

  uzivatel = kontrola_prihlaseni()
  if not uzivatel:
    go_domu()
    return
  
  komp = get_komp()
  komp.nahraj_komponentu(Analyza_saw_komp())

# řízení přístupu uživatelů
def kontrola_prihlaseni():
  uzivatel = Sprava_dat.je_prihlasen()
  if uzivatel:
    return uzivatel

  uzivatel = anvil.users.login_with_form(allow_cancel=True)
  komp = get_komp()
  komp.nastav_ucet(uzivatel)
  return uzivatel

# aktivní položka v levém menu
def set_active_nav(stav):
  komp = get_komp()
  komp.set_active_nav(stav)

def check_and_delete_unfinished(next_page):
    komp = get_komp()
    if hasattr(komp, 'pravy_panel'):
        current_form = komp.pravy_panel.get_components()[0]
        if isinstance(current_form, Analyza_saw_komp) and current_form.analyza_id:
            if confirm("Opustíte rozpracovanou analýzu. Pokračovat?"):
                anvil.server.call('smaz_analyzu', current_form.analyza_id)
                return True
            return False
    return True

