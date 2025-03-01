# client_code/Dashboard_uziv_komp/Analyza_Row/__init__.py
from ._anvil_designer import Analyza_RowTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ... import Navigace, Spravce_stavu, Utils


class Analyza_Row(Analyza_RowTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.spravce = Spravce_stavu.Spravce_stavu()

    def button_smazat_click(self, **event_args):
        """
        Zpracuje požadavek na smazání analýzy.
        """
        if Utils.zobraz_potvrzovaci_dialog("Opravdu chcete odstranit tuto analýzu?"):
            try:
                # Smazání analýzy na serveru
                anvil.server.call('smaz_analyzu', self.item['id'])
                
                # Pokud se smazala aktivní analýza, vyčistíme stav
                if self.spravce.ziskej_aktivni_analyzu() == self.item['id']:
                    self.spravce.vycisti_data_analyzy()
                
                # Aktualizace seznamu analýz
                self.parent.raise_event('x-refresh')
                
            except Exception as e:
                Utils.zapsat_chybu(f"Chyba při mazání analýzy: {str(e)}")
                alert(f"Chyba při mazání analýzy: {str(e)}")

    def button_upravit_click(self, **event_args):
        """
        Zpracuje požadavek na úpravu analýzy.
        """
        try:
            Utils.zapsat_info(f"Úprava analýzy s ID: {self.item['id']}")
            
            # Vyčistíme předchozí stav před načtením nové analýzy
            self.spravce.vycisti_data_analyzy()
            
            # Nastavíme ID upravované analýzy
            self.spravce.nastav_aktivni_analyzu(self.item['id'], True)
            
            # Zavoláme serverovou metodu pro nastavení ID v session (zpětná kompatibilita)
            anvil.server.call('set_edit_analyza_id', self.item['id'])
            
            # Přejdeme na stránku úpravy analýzy
            Navigace.go('uprava_analyzy')
            
        except Exception as e:
            Utils.zapsat_chybu(f"Chyba při přípravě úpravy analýzy: {str(e)}")
            alert(f"Chyba při přípravě úpravy analýzy: {str(e)}")

    def button_vypocet_click(self, **event_args):
        """
        Zpracuje požadavek na zobrazení výstupu analýzy.
        """
        try:
            # Nastavíme ID aktivní analýzy (pouze pro zobrazení)
            self.spravce.nastav_aktivni_analyzu(self.item['id'], False)
            
            # Přejdeme na stránku s výstupem
            Navigace.go('saw_vystup', analyza_id=self.item['id'])
            
        except Exception as e:
            Utils.zapsat_chybu(f"Chyba při přechodu na výstup analýzy: {str(e)}")
            alert(f"Chyba při zobrazení výstupu analýzy: {str(e)}")
            
    # def button_klonovat_click(self, **event_args):
    #     """
    #     Zpracuje požadavek na klonování analýzy.
    #     """
    #     if not hasattr(self, 'button_klonovat') or not self.button_klonovat:
    #         return
            
    #     if Utils.zobraz_potvrzovaci_dialog(f"Opravdu chcete vytvořit kopii analýzy '{self.item['nazev']}'?"):
    #         try:
    #             # Tuto funkci byste museli implementovat na serveru
    #             nova_analyza_id = anvil.server.call('klonuj_analyzu', self.item['id'])
                
    #             if nova_analyza_id:
    #                 alert(f"Analýza byla úspěšně naklonována.")
    #                 self.parent.raise_event('x-refresh')
                    
    #         except Exception as e:
    #             Utils.zapsat_chybu(f"Chyba při klonování analýzy: {str(e)}")
    #             alert(f"Chyba při klonování analýzy: {str(e)}")