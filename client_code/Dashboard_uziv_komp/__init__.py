# client_code/Dashboard_uziv_komp/__init__.py
from ._anvil_designer import Dashboard_uziv_kompTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
from .. import Navigace, Spravce_stavu, Utils


class Dashboard_uziv_komp(Dashboard_uziv_kompTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        # Inicializace správce stavu
        self.spravce = Spravce_stavu.Spravce_stavu()
        
        # Nastavení handlerů pro aktualizaci seznamu analýz
        self.repeating_panel_dashboard.set_event_handler('x-refresh', self.nahraj_analyzy)
        self.data_grid_dash.set_event_handler('x-refresh', self.nahraj_analyzy)
        
        # Načtení analýz při startu
        self.nahraj_analyzy()
    
    def form_show(self, **event_args):
        """
        Aktualizuje seznam analýz při zobrazení formuláře.
        """
        # Ujistíme se, že máme aktuálního uživatele
        self.spravce.nacti_uzivatele()
        self.nahraj_analyzy()
    
    def nahraj_analyzy(self, **event_args):
        """
        Načte seznam analýz ze serveru a zobrazí je v UI.
        """
        Utils.zapsat_info("Načítám seznam analýz")
        try:
            # Načtení analýz z nového serverového modulu
            analyzy = anvil.server.call('nacti_analyzy_uzivatele')
            
            if not analyzy:
                # Žádné analýzy k zobrazení
                self.label_no_analyzy.visible = True
                self.repeating_panel_dashboard.visible = False
                self.data_grid_dash.visible = False
                Utils.zapsat_info("Žádné analýzy nenalezeny")
                return
            
            # Máme analýzy k zobrazení
            self.label_no_analyzy.visible = False
            
            # Formátování dat pro repeating panel (původní implementace)
            self.repeating_panel_dashboard.items = [
                {
                    'id': a['id'],
                    'nazev': a['nazev'],
                    'popis': a.get('popis', ''),
                    'datum_vytvoreni': a['datum_vytvoreni'].strftime("%d.%m.%Y") if a['datum_vytvoreni'] else "",
                    'datum_upravy': a['datum_upravy'].strftime("%d.%m.%Y") if a['datum_upravy'] else ""
                } for a in analyzy
            ]
            
            # Formátování dat pro data grid - klíčové je, že předáváme všechny potřebné informace
            # podle toho, jak to vidíme v Administrace_komp
            self.repeating_panel_dash.items = [
                {
                    # ID musí být vždy přítomno pro fungování akcí
                    'id': a['id'],
                    # Mapování pro zobrazení v UI podle data_key v data_grid_dash
                    'nazev': a['nazev'],  # Sloupec Název
                    'datum_upravy': a['datum_upravy'].strftime("%d.%m.%Y") if a['datum_upravy'] else "",  # Sloupec Upraveno
                    'datum_vytvoreni': a['datum_vytvoreni'].strftime("%d.%m.%Y") if a['datum_vytvoreni'] else ""  # Sloupec Vytvořeno
                } for a in analyzy
            ]
            
            # Zobrazíme datagrid a skryjeme repeating panel pro testování
            self.repeating_panel_dashboard.visible = True
            self.data_grid_dash.visible = True
            
            Utils.zapsat_info(f"Načteno {len(analyzy)} analýz")
            
        except Exception as e:
            Utils.zapsat_chybu(f"Chyba při načítání analýz: {str(e)}")
            alert(f"Chyba při načítání analýz: {str(e)}")

    def button_pridat_analyzu_click(self, **event_args):
        """
        Přechod na stránku pro přidání nové analýzy.
        """
        # Vyčistíme předchozí stav analýzy před vytvořením nové
        self.spravce.vycisti_data_analyzy()
        
        # Přejdeme na stránku pro zadání dat analýzy
        Navigace.go('pridat_analyzu')