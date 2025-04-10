from ._anvil_designer import Vystup_wsm_kompTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. import Spravce_stavu, Utils, Generator_html, Vypocty, Vizualizace, mcapp_styly


class Vystup_wsm_komp(Vystup_wsm_kompTemplate):
    """
    Formulář pro zobrazení výsledků WSM analýzy (Weighted Sum Model) s využitím HTML.
    Využívá sdílené moduly pro výpočty a vizualizace a zobrazuje výstup s bohatým formátováním.
    """
    
    def __init__(self, analyza_id=None, **properties):
        """
        Inicializace formuláře s ID analýzy.
        
        Args:
            analyza_id: ID analýzy k zobrazení, pokud None, použije aktivní analýzu ze správce
        """
        self.init_components(**properties)
        # Inicializace správce stavu
        self.spravce = Spravce_stavu.Spravce_stavu()
        
        # Použijeme ID z parametrů nebo z aktivní analýzy ve správci
        self.analyza_id = analyza_id or self.spravce.ziskej_aktivni_analyzu()
        
        # Data, která budeme používat v celém formuláři
        self.analyza_data = None
        self.vysledky_vypoctu = None
        
    def form_show(self, **event_args):
        """Načte a zobrazí data analýzy při zobrazení formuláře."""
        if not self.analyza_id:
            self._zobraz_prazdny_formular()
            return
            
        try:
            Utils.zapsat_info(f"Načítám data analýzy ID: {self.analyza_id}")
            
            # Načtení dat analýzy z JSON struktury
            self.analyza_data = anvil.server.call('nacti_analyzu', self.analyza_id)
            
            # Výpočet WSM analýzy pomocí centralizované funkce z modulu Vypocty
            self.vysledky_vypoctu = Vypocty.vypocitej_wsm_analyzu(self.analyza_data)
            
            # Zobrazení výsledků
            self._zobraz_kompletni_analyzu()
            
            Utils.zapsat_info("Výsledky WSM analýzy úspěšně zobrazeny")
            
        except Exception as e:
            Utils.zapsat_chybu(f"Chyba při načítání analýzy: {str(e)}")
            self._zobraz_chybovou_zpravu(str(e))
            alert(f"Chyba při načítání analýzy: {str(e)}")

    def _zobraz_prazdny_formular(self):
        """Zobrazí prázdný formulář s informací o chybějících datech."""
        Utils.zapsat_info("Zobrazuji prázdný formulář WSM HTML - chybí ID analýzy")
        chyba_html = """
        <div class="mcapp-error-message">
            <div class="mcapp-error-icon"><i class="fa fa-exclamation-circle"></i></div>
            <div class="mcapp-error-text">Nepřišlo žádné ID analýzy.</div>
        </div>
        """
        self.html_1.html = mcapp_styly.vloz_styly_do_html(chyba_html)
        self._skryj_grafy()
    
    def _zobraz_chybovou_zpravu(self, zprava):
        """Zobrazí chybovou zprávu v HTML formátu."""
        chyba_html = f"""
        <div class="mcapp-error-message">
            <div class="mcapp-error-icon"><i class="fa fa-exclamation-circle"></i></div>
            <div class="mcapp-error-text">Chyba při zpracování: {zprava}</div>
        </div>
        """
        self.html_1.html = mcapp_styly.vloz_styly_do_html(chyba_html)
        self._skryj_grafy()
            
    def _zobraz_kompletni_analyzu(self):
        """Zobrazí kompletní analýzu včetně všech výpočtů a vizualizací."""
        try:
            # Vytvoření HTML obsahu pomocí funkcí z modulu Vizualizace
            html_obsah = Generator_html.vytvor_kompletni_html_analyzy(
                self.analyza_data,
                self.vysledky_vypoctu,
                "WSM"
            )
            
            # Vložení stylů do HTML
            self.html_1.html = mcapp_styly.vloz_styly_do_html(html_obsah)
            
            # Vytvoření a nastavení grafů
            self._vytvor_a_nastav_grafy()
            
        except Exception as e:
            Utils.zapsat_chybu(f"Chyba při zobrazování výsledků: {str(e)}")
            self._zobraz_chybovou_zpravu(str(e))
            self._skryj_grafy()
    
    def _vytvor_a_nastav_grafy(self):
        """Vytvoří a nastaví grafy pro vizualizaci výsledků."""
        try:
            # Graf výsledků
            self.plot_wsm_vysledek.figure = Vizualizace.vytvor_sloupovy_graf_vysledku(
                self.vysledky_vypoctu['wsm_vysledky']['results'], 
                self.vysledky_vypoctu['wsm_vysledky']['nejlepsi_varianta'], 
                self.vysledky_vypoctu['wsm_vysledky']['nejhorsi_varianta'], 
                "WSM"
            )
            self.plot_wsm_vysledek.visible = True
            
            # Získání seřazených variant podle výsledků (pro konzistentní zobrazení)
            serazene_varianty = [var for var, _, _ in sorted(
                self.vysledky_vypoctu['wsm_vysledky']['results'], 
                key=lambda x: x[1]  # Seřazení podle pořadí (druhý prvek v tuple)
            )]
            
            # Graf skladby skóre s předáním seřazených variant
            self.plot_wsm_skladba.figure = Vizualizace.vytvor_skladany_sloupovy_graf(
                self.vysledky_vypoctu['norm_vysledky']['nazvy_variant'],
                self.vysledky_vypoctu['norm_vysledky']['nazvy_kriterii'],
                self.vysledky_vypoctu['vazene_matice'],
                serazene_varianty  # Předání seřazených variant
            )
            self.plot_wsm_skladba.visible = True
            
            # Analýza citlivosti - povolená pouze pokud máme více než jedno kritérium
            kriteria = self.vysledky_vypoctu['norm_vysledky']['nazvy_kriterii']
            if len(kriteria) > 1:
                # Připravíme analýzy citlivosti pro všechna kritéria
                vsechny_analyzy = {}
                
                # Pro každé kritérium
                for i, kriterium in enumerate(kriteria):
                    # Výpočet analýzy citlivosti pro toto kritérium
                    analyza = Vypocty.vypocitej_analyzu_citlivosti(
                        self.vysledky_vypoctu['norm_vysledky']['normalizovana_matice'], 
                        self.vysledky_vypoctu['vahy'], 
                        self.vysledky_vypoctu['norm_vysledky']['nazvy_variant'], 
                        kriteria,
                        metoda="wsm",  # Upravit podle použité metody
                        vyber_kriteria=i  # Index aktuálního kritéria
                    )
                    
                    vsechny_analyzy[kriterium] = analyza
                
                # Výchozí analýza pro první kritérium pro zpětnou kompatibilitu
                analyza_citlivosti = vsechny_analyzy[kriteria[0]]
                
                # Grafy citlivosti s dropdown menu
                self.plot_citlivost_skore.figure = Vizualizace.vytvor_graf_citlivosti_skore(
                    analyza_citlivosti, 
                    self.vysledky_vypoctu['norm_vysledky']['nazvy_variant'],
                    kriteria,  # Seznam všech kritérií
                    vsechny_analyzy  # Výsledky analýzy pro všechna kritéria
                )
                self.plot_citlivost_skore.visible = True
                
                self.plot_citlivost_poradi.figure = Vizualizace.vytvor_graf_citlivosti_poradi(
                    analyza_citlivosti, 
                    self.vysledky_vypoctu['norm_vysledky']['nazvy_variant'],
                    kriteria,
                    vsechny_analyzy
                )
                self.plot_citlivost_poradi.visible = True
            else:
                # Skryjeme grafy citlivosti, pokud máme jen jedno kritérium
                self.plot_citlivost_skore.visible = False  
                self.plot_citlivost_poradi.visible = False
                
        except Exception as e:
            Utils.zapsat_chybu(f"Chyba při vytváření grafů: {str(e)}")
            self._skryj_grafy()
    
    def _skryj_grafy(self):
        """Skryje všechny grafy ve formuláři."""
        self.plot_wsm_vysledek.visible = False
        self.plot_wsm_skladba.visible = False
        self.plot_citlivost_skore.visible = False
        self.plot_citlivost_poradi.visible = False