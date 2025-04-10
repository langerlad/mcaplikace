from ._anvil_designer import Vystup_mabac_kompTemplate
from anvil import *
import plotly.graph_objects as go
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. import Spravce_stavu, Utils, Generator_html, Vypocty, Vizualizace, mcapp_styly

class Vystup_mabac_komp(Vystup_mabac_kompTemplate):
  """
  Formulář pro zobrazení výsledků MABAC analýzy (Multi-Attributive Border Approximation area Comparison) s využitím HTML.
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
      self.analyza_data = anvil.server.call("nacti_analyzu", self.analyza_id)

      # Výpočet MABAC analýzy pomocí centralizované funkce z modulu Vypocty
      self.vysledky_vypoctu = Vypocty.vypocitej_mabac_analyzu(self.analyza_data)

      # Zobrazení výsledků
      self._zobraz_kompletni_analyzu()

      Utils.zapsat_info("Výsledky MABAC analýzy úspěšně zobrazeny")

    except Exception as e:
      Utils.zapsat_chybu(f"Chyba při načítání analýzy: {str(e)}")
      self._zobraz_chybovou_zpravu(str(e))
      alert(f"Chyba při načítání analýzy: {str(e)}")

  def _zobraz_prazdny_formular(self):
    """Zobrazí prázdný formulář s informací o chybějících datech."""
    Utils.zapsat_info("Zobrazuji prázdný formulář MABAC HTML - chybí ID analýzy")
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
      # Vytvoření HTML obsahu pomocí funkcí z modulu Generator_html
      html_obsah = Generator_html.vytvor_kompletni_html_analyzy(
        self.analyza_data, self.vysledky_vypoctu, "MABAC"
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
        # Získání seřazených variant podle výsledků
        serazene_varianty = [var for var, _, _ in sorted(
            self.vysledky_vypoctu["mabac_vysledky"]["results"], 
            key=lambda x: x[1]  # Seřazení podle pořadí
        )]
      
        # Graf výsledků
        self.plot_mabac_vysledek.figure = Vizualizace.vytvor_sloupovy_graf_vysledku(
            self.vysledky_vypoctu["mabac_vysledky"]["results"],
            self.vysledky_vypoctu["mabac_vysledky"]["nejlepsi_varianta"],
            self.vysledky_vypoctu["mabac_vysledky"]["nejhorsi_varianta"],
            "MABAC",
        )
        self.plot_mabac_vysledek.visible = True

        # Přeuspořádání matice q_distance_matrix podle seřazených variant
        q_matrix_serazena = self._preusporadat_matici(
            self.vysledky_vypoctu["mabac_vysledky"]["q_distance_matrix"],
            self.vysledky_vypoctu["norm_vysledky"]["nazvy_variant"],
            serazene_varianty
        )

        # Graf pro vizualizaci vzdáleností od hraničních oblastí (G)
        self.plot_mabac_vzdalenosti.figure = Vizualizace.vytvor_skladany_sloupovy_graf(
            serazene_varianty,  # Použití seřazených variant
            self.vysledky_vypoctu["norm_vysledky"]["nazvy_kriterii"],
            q_matrix_serazena
        )
        self.plot_mabac_vzdalenosti.visible = True

        # Radarový graf 
        self.plot_mabac_radar.figure = Vizualizace.vytvor_radar_graf_mabac(
            self.vysledky_vypoctu["mabac_vysledky"],
            serazene_varianty,  # Použití seřazených variant
            self.vysledky_vypoctu["norm_vysledky"]["nazvy_kriterii"],
            self.vysledky_vypoctu["vazena_matice"]
        )
        self.plot_mabac_radar.visible = True

        # Analýza citlivosti - povolená pouze pokud máme více než jedno kritérium
        kriteria = self.vysledky_vypoctu["norm_vysledky"]["nazvy_kriterii"]
        if len(kriteria) > 1:
            # Výpočet analýzy citlivosti pro první kritérium
            analyza_citlivosti = Vypocty.vypocitej_analyzu_citlivosti(
                self.vysledky_vypoctu["vazena_matice"],
                self.vysledky_vypoctu["vahy"],
                self.vysledky_vypoctu["norm_vysledky"]["nazvy_variant"],
                kriteria,
                metoda="mabac",
                typy_kriterii=self.vysledky_vypoctu["typy_kriterii"]
            )

            # Grafy citlivosti
            self.plot_citlivost_skore.figure = Vizualizace.vytvor_graf_citlivosti_skore(
                analyza_citlivosti, 
                self.vysledky_vypoctu["norm_vysledky"]["nazvy_variant"]
            )
            self.plot_citlivost_skore.visible = True

            self.plot_citlivost_poradi.figure = Vizualizace.vytvor_graf_citlivosti_poradi(
                analyza_citlivosti, 
                self.vysledky_vypoctu["norm_vysledky"]["nazvy_variant"]
            )
            self.plot_citlivost_poradi.visible = True
        else:
            # Skryjeme grafy citlivosti, pokud máme jen jedno kritérium
            self.plot_citlivost_skore.visible = False
            self.plot_citlivost_poradi.visible = False

    except Exception as e:
        Utils.zapsat_chybu(f"Chyba při vytváření grafů: {str(e)}")
        self._skryj_grafy()

  def _preusporadat_matici(self, matice, puvodni_poradi, nove_poradi):
      """
      Přeuspořádá matici hodnot podle nového pořadí řádků.
      
      Args:
          matice: 2D seznam hodnot [varianty][kriteria]
          puvodni_poradi: Seznam názvů variant v původním pořadí
          nove_poradi: Seznam názvů variant v novém pořadí
          
      Returns:
          2D seznam: Přeuspořádaná matice hodnot
      """
      try:
          # Vytvoření mapování jméno varianty -> index
          var_to_idx = {var: idx for idx, var in enumerate(puvodni_poradi)}
          
          # Vytvoření nové matice s přeuspořádanými řádky
          nova_matice = []
          for var in nove_poradi:
              idx = var_to_idx.get(var)
              if idx is not None:
                  nova_matice.append(matice[idx])
              else:
                  # Pokud varianta není v původním pořadí, přidáme prázdný řádek
                  Utils.zapsat_chybu(f"Varianta '{var}' není v původním seznamu variant")
                  nova_matice.append([0] * len(matice[0]) if matice else [])
                  
          return nova_matice
      except Exception as e:
          Utils.zapsat_chybu(f"Chyba při přeuspořádání matice: {str(e)}")
          return matice  # V případě chyby vrátíme původní matici

  def _skryj_grafy(self):
    """Skryje všechny grafy ve formuláři."""
    self.plot_mabac_vysledek.visible = False
    self.plot_mabac_vzdalenosti.visible = False
    self.plot_mabac_radar.visible = False
    self.plot_citlivost_skore.visible = False
    self.plot_citlivost_poradi.visible = False