from ._anvil_designer import Vystup_electre_kompTemplate
from anvil import *
import plotly.graph_objects as go
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. import Spravce_stavu, Utils, Vypocty, Vizualizace, mcapp_styly

class Vystup_electre_komp(Vystup_electre_kompTemplate):
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
        
        # Ujistíme se, že máme aktuální nastavení uživatele
        self.spravce.nacti_nastaveni_uzivatele()
        electre_params = self.spravce.ziskej_nastaveni_electre()
        Utils.zapsat_info(f"Aktuální parametry ELECTRE: souhlas={electre_params['index_souhlasu']}, nesouhlas={electre_params['index_nesouhlasu']}")

        # Načtení dat analýzy z JSON struktury
        self.analyza_data = anvil.server.call("nacti_analyzu", self.analyza_id)

        # Výpočet ELECTRE analýzy
        self.vysledky_vypoctu = Vypocty.vypocitej_analyzu(self.analyza_data, metoda="electre")

        # Zobrazení výsledků
        self._zobraz_kompletni_analyzu()

        Utils.zapsat_info("Výsledky ELECTRE analýzy úspěšně zobrazeny")

    except Exception as e:
        Utils.zapsat_chybu(f"Chyba při načítání analýzy: {str(e)}")
        self._zobraz_chybovou_zpravu(str(e))
        alert(f"Chyba při načítání analýzy: {str(e)}")

  def _zobraz_prazdny_formular(self):
    """Zobrazí prázdný formulář s informací o chybějících datech."""
    Utils.zapsat_info("Zobrazuji prázdný formulář ELECTRE HTML - chybí ID analýzy")
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
      html_obsah = Vizualizace.vytvor_kompletni_html_analyzy(
        self.analyza_data, self.vysledky_vypoctu, "ELECTRE"
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
        # Graf výsledků - pořadí variant
        self.plot_sablona_vysledek.figure = Vizualizace.vytvor_graf_electre_vysledky(
            self.vysledky_vypoctu["electre_vysledky"]["results"],
            self.vysledky_vypoctu["norm_vysledky"]["nazvy_variant"]
        )
        self.plot_sablona_vysledek.visible = True

        # Graf matice souhlasu (concordance)
        self.plot_sablona_skladba.figure = Vizualizace.vytvor_graf_concordance_electre(
            self.vysledky_vypoctu["electre_vysledky"]["concordance_matrix"], 
            self.vysledky_vypoctu["norm_vysledky"]["nazvy_variant"]
        )
        self.plot_sablona_skladba.visible = True

        # Graf matice nesouhlasu (discordance)
        self.plot_discordance.figure = Vizualizace.vytvor_graf_discordance_electre(
            self.vysledky_vypoctu["electre_vysledky"]["discordance_matrix"], 
            self.vysledky_vypoctu["norm_vysledky"]["nazvy_variant"]
        )
        self.plot_discordance.visible = True

        # Graf převahy (outranking)
        self.plot_outranking.figure = Vizualizace.vytvor_graf_outranking_electre(
            self.vysledky_vypoctu["electre_vysledky"]["outranking_matrix"], 
            self.vysledky_vypoctu["norm_vysledky"]["nazvy_variant"]
        )
        self.plot_outranking.visible = True

    except Exception as e:
        Utils.zapsat_chybu(f"Chyba při vytváření grafů: {str(e)}")
        self._skryj_grafy()

  def _skryj_grafy(self):
    """Skryje všechny grafy ve formuláři."""
    self.plot_sablona_vysledek.visible = False
    self.plot_sablona_skladba.visible = False
    self.plot_discordance.visible = False
    self.plot_outranking.visible = False
