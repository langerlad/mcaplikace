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
        self.nacti_uzivatele()
  
    def nacti_uzivatele(self):
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
            
    @staticmethod
    def _formatuj_datum(datum):
        """Formátuje datum do českého formátu."""
        return datum.strftime("%d.%m.%Y") if datum else ""


