from .Administrace_komp import Administrace_komp
from .Analyza_ahp_komp import Analyza_ahp_komp
from .Analyza_vystup_komp import Analyza_vystup_komp
from .Info_komp import Info_komp
from .Nastaveni_komp import Nastaveni_komp
from .Neznam_uziv_komp import Neznam_uziv_komp
from .Prihlas_uziv_komp import Prihlas_uziv_komp
from .Ucet_komp import Ucet_komp
from .Vyber_analyzy_komp import Vyber_analyzy_komp


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
  komp.nahraj_komponentu(Neznam_uziv_komp())

def go_pridat_analyzu():
  set_active_nav("pridat")
  #set_title("")
  komp = get_komp()
  komp.nahraj_komponentu(Vyber_analyzy_komp())

def go_nastaveni():
  set_active_nav("nastaveni")
  #set_title("")
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
  komp = get_komp()
  komp.nahraj_komponentu(Administrace_komp())

def go_ucet():
  #set_title("")
  komp = get_komp()
  komp.nahraj_komponentu(Ucet_komp())

# link je na komponentě Výběr analýzy
def go_ahp():
  komp = get_komp()
  komp.nahraj_komponentu(Analyza_ahp_komp())

# aktivní polozka v levém menu
def set_active_nav(stav):
  komp = get_komp()
  komp.set_active_nav(stav)