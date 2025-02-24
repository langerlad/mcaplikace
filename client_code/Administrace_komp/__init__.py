from ._anvil_designer import Administrace_kompTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
from .. import Konstanty


class Administrace_komp(Administrace_kompTemplate):
    def __init__(self, **properties):
        """Inicializace komponenty pro správu uživatelů."""
        self.init_components(**properties)
        self.zvoleny_uzivatel = None
        # Nastavení handleru pro události z x_Row
        self.repeating_panel_uzvatele.set_event_handler('x-uzivatel-zvolen', self.nacti_analyzy_uzivatele)
        self.repeating_panel_uzvatele.set_event_handler('x-refresh', self.nacti_uzivatele)
        self.repeating_panel_analyzy.set_event_handler('x-zobraz-vystup', self.zobraz_vystup_analyzy)
        
        # Inicializace stavu analýz - na začátku není vybrán žádný uživatel
        self.data_grid_analyzy.visible = False
        self.label_vyberte_ucet.visible = True
        
        self.nacti_uzivatele()
  
    def nacti_uzivatele(self, sender=None, **event_args):
      """Načte seznam uživatelů a aktualizuje UI."""
      try:
          uzivatele = anvil.server.call('nacti_vsechny_uzivatele')
          
          if not uzivatele:
              self.label_zadni_uzivatele.visible = True
              self.data_grid_uzivatele.visible = False
              return
          
          self.label_zadni_uzivatele.visible = False
          self.data_grid_uzivatele.visible = True
          
          self.repeating_panel_uzvatele.items = [
              {
                  'id': u.get_id(),
                  'email': u['email'],
                  'vytvoreni': u['signed_up'].strftime("%d.%m.%Y") if u['signed_up'] else '',
                  'prihlaseni': u['last_login'].strftime("%d.%m.%Y") if u['last_login'] else '',
                  'role': 'admin' if u['role'] == 'admin' else 'uživatel',
                  'pocet_analyz': anvil.server.call('vrat_pocet_analyz_pro_uzivatele', u)
              } 
              for u in uzivatele
          ]
              
      except Exception as e:
          alert(Konstanty.ZPRAVY_CHYB['CHYBA_NACTENI_UZIVATELU'].format(str(e)))

    def nacti_analyzy_uzivatele(self, sender, uzivatel, **event_args):
      """Načte a zobrazí analýzy zvoleného uživatele."""
      try:
          print(f"Načítám analýzy pro uživatele: {uzivatel['email']}")
          # Předáváme pouze email místo celého objektu uživatele
          analyzy = anvil.server.call('nacti_analyzy_uzivatele_admin', uzivatel['email'])

          # Aktualizace UI - skrytí zprávy o nutnosti výběru uživatele
          self.label_vyberte_ucet.visible = False
          
          # Aktualizace UI
          self.label_uzivatel.text = f"Zvolený uživatel: {uzivatel['email']}"
        
          # Zobrazení/skrytí datagridu podle toho, jestli jsou nalezeny analýzy
          self.data_grid_analyzy.visible = bool(analyzy)
          
          if not analyzy:
              print("Žádné analýzy nenalezeny")
              return
          
          print(f"Zpracovávám {len(analyzy)} analýz")

          # Nastavení handleru pro události z řádků
          self.repeating_panel_analyzy.set_event_handler('x-zobraz-vystup', self.zobraz_vystup_analyzy)
        
          self.repeating_panel_analyzy.items = [
              {
                  'id': a.get_id(),
                  'nazev': a['nazev'],
                  'popis': a['popis'],
                  'datum_vytvoreni': a['datum_vytvoreni'].strftime("%d.%m.%Y") if a['datum_vytvoreni'] else '',
                  'datum_upravy': a['datum_upravy'].strftime("%d.%m.%Y") if a['datum_upravy'] else '',
                  'zvolena_metoda': a['zvolena_metoda']
              }
              for a in analyzy
          ]
          print("Analýzy načteny do UI")
          
      except Exception as e:
          print(f"Klient chyba: {str(e)}")
          alert(f"Chyba při načítání analýz: {str(e)}")

    def zobraz_vystup_analyzy(self, sender, analyza_id, **event_args):
      """
      Zobrazí výstup zvolené analýzy.
      
      Args:
          sender: Komponenta, která událost vyvolala
          analyza_id: ID zvolené analýzy
          event_args: Další argumenty události
      """
      try:
          print(f"Zobrazuji výstup analýzy: {analyza_id}")
          
          # Přesměrování na stránku s výstupem analýzy
          from .. import Navigace
          Navigace.go('saw_vystup', analyza_id=analyza_id)
          
      except Exception as e:
          alert(f"Chyba při zobrazování výstupu analýzy: {str(e)}")

