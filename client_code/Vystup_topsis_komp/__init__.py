from ._anvil_designer import Vystup_topsis_kompTemplate
from anvil import *
import plotly.graph_objects as go
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. import Spravce_stavu, Utils,Generator_html, Vypocty, Vizualizace, mcapp_styly


class Vystup_topsis_komp(Vystup_topsis_kompTemplate):
  """
  Formulář pro zobrazení výsledků TOPSIS analýzy (Technique for Order of Preference by Similarity to Ideal Solution) s využitím HTML.
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

      # Výpočet TOPSIS analýzy pomocí centralizované funkce z modulu Vypocty
      self.vysledky_vypoctu = Vypocty.vypocitej_topsis_analyzu(self.analyza_data)

      # Zobrazení výsledků
      self._zobraz_kompletni_analyzu()

      Utils.zapsat_info("Výsledky TOPSIS analýzy úspěšně zobrazeny")

    except Exception as e:
      Utils.zapsat_chybu(f"Chyba při načítání analýzy: {str(e)}")
      self._zobraz_chybovou_zpravu(str(e))
      alert(f"Chyba při načítání analýzy: {str(e)}")

  def _zobraz_prazdny_formular(self):
    """Zobrazí prázdný formulář s informací o chybějících datech."""
    Utils.zapsat_info("Zobrazuji prázdný formulář TOPSIS HTML - chybí ID analýzy")
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
        self.analyza_data, self.vysledky_vypoctu, "TOPSIS"
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
            self.vysledky_vypoctu["topsis_vysledky"]["results"], 
            key=lambda x: x[1]  # Seřazení podle pořadí
        )]
        
        # Graf výsledků - relativní blízkost k ideálnímu řešení
        self.plot_topsis_vysledek.figure = Vizualizace.vytvor_sloupovy_graf_vysledku(
            self.vysledky_vypoctu["topsis_vysledky"]["results"],
            self.vysledky_vypoctu["topsis_vysledky"]["nejlepsi_varianta"],
            self.vysledky_vypoctu["topsis_vysledky"]["nejhorsi_varianta"],
            "TOPSIS - relativní blízkost k ideálnímu řešení",
        )
        self.plot_topsis_vysledek.visible = True

        # Úpravy dat pro grafy v seřazeném pořadí
        topsis_vysledky_upravene = self._preusporadat_data_topsis(
            self.vysledky_vypoctu["topsis_vysledky"],
            self.vysledky_vypoctu["norm_vysledky"]["nazvy_variant"],
            serazene_varianty
        )
        
        # Graf vzdáleností od ideálního a anti-ideálního řešení
        self.plot_topsis_vzdalenosti.figure = Vizualizace.vytvor_graf_vzdalenosti_topsis(
            topsis_vysledky_upravene,
            serazene_varianty
        )
        self.plot_topsis_vzdalenosti.visible = True

        # Radarový graf porovnání s ideálním řešením
        self.plot_topsis_radar.figure = Vizualizace.vytvor_radar_graf_topsis(
            topsis_vysledky_upravene,
            serazene_varianty,
            self.vysledky_vypoctu["norm_vysledky"]["nazvy_kriterii"]
        )
        self.plot_topsis_radar.visible = True

        # 2D rozptylový graf vzdáleností
        self.plot_topsis_2d.figure = Vizualizace.vytvor_2d_graf_vzdalenosti_topsis(
            topsis_vysledky_upravene,
            serazene_varianty
        )
        self.plot_topsis_2d.visible = True

        # Analýza citlivosti - povolená pouze pokud máme více než jedno kritérium
        kriteria = self.vysledky_vypoctu["norm_vysledky"]["nazvy_kriterii"]
        if len(kriteria) > 1:
            # Připravíme analýzy citlivosti pro všechna kritéria
            vsechny_analyzy = {}
            
            # Pro každé kritérium
            for i, kriterium in enumerate(kriteria):
                # Výpočet analýzy citlivosti pro toto kritérium
                analyza = Vypocty.vypocitej_analyzu_citlivosti(
                    self.vysledky_vypoctu["norm_vysledky"]["normalizovana_matice"],
                    self.vysledky_vypoctu["vahy"],
                    self.vysledky_vypoctu["norm_vysledky"]["nazvy_variant"],
                    kriteria,
                    metoda="topsis",
                    typy_kriterii=self.vysledky_vypoctu["typy_kriterii"],
                    vyber_kriteria=i  # Index aktuálního kritéria
                )
                
                vsechny_analyzy[kriterium] = analyza
            
            # Výchozí analýza pro první kritérium pro zpětnou kompatibilitu
            analyza_citlivosti = vsechny_analyzy[kriteria[0]]
            
            # Grafy citlivosti s dropdown menu
            self.plot_citlivost_skore.figure = Vizualizace.vytvor_graf_citlivosti_skore(
                analyza_citlivosti, 
                self.vysledky_vypoctu["norm_vysledky"]["nazvy_variant"],
                kriteria,  # Seznam všech kritérií
                vsechny_analyzy  # Výsledky analýzy pro všechna kritéria
            )
            self.plot_citlivost_skore.visible = True
            
            self.plot_citlivost_poradi.figure = Vizualizace.vytvor_graf_citlivosti_poradi(
                analyza_citlivosti, 
                self.vysledky_vypoctu["norm_vysledky"]["nazvy_variant"],
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

  def _preusporadat_data_topsis(self, topsis_vysledky, puvodni_poradi, nove_poradi):
      """
      Přeuspořádá data TOPSIS výsledků podle nového pořadí variant.
      
      Args:
          topsis_vysledky: Slovník s výsledky TOPSIS analýzy
          puvodni_poradi: Seznam názvů variant v původním pořadí
          nove_poradi: Seznam názvů variant v novém pořadí
          
      Returns:
          dict: Upravený slovník s výsledky TOPSIS
      """
      try:
          # Vytvoření mapování jméno varianty -> index
          var_to_idx = {var: idx for idx, var in enumerate(puvodni_poradi)}
          
          # Vytvoření kopie topsis_vysledky
          import copy
          upravene_vysledky = copy.deepcopy(topsis_vysledky)
          
          # Seznamy, které je potřeba přeuspořádat - jednodimenzionální
          jednodim_seznamy = ["dist_ideal", "dist_anti_ideal", "relativni_blizkost"]
          
          for nazev_seznamu in jednodim_seznamy:
              if nazev_seznamu in upravene_vysledky:
                  puvodni_seznam = upravene_vysledky[nazev_seznamu]
                  if len(puvodni_seznam) == len(puvodni_poradi):
                      novy_seznam = []
                      for var in nove_poradi:
                          idx = var_to_idx.get(var)
                          if idx is not None and idx < len(puvodni_seznam):
                              novy_seznam.append(puvodni_seznam[idx])
                          else:
                              # Pokud varianta není v původním pořadí, přidáme nulu
                              novy_seznam.append(0)
                      
                      upravene_vysledky[nazev_seznamu] = novy_seznam
          
          # Seznamy, které je potřeba přeuspořádat - dvoudimenzionální
          dvoudim_seznamy = ["vazena_matice", "norm_matice"]
          
          for nazev_seznamu in dvoudim_seznamy:
              if nazev_seznamu in upravene_vysledky:
                  puvodni_matice = upravene_vysledky[nazev_seznamu]
                  if len(puvodni_matice) == len(puvodni_poradi):
                      nova_matice = []
                      for var in nove_poradi:
                          idx = var_to_idx.get(var)
                          if idx is not None and idx < len(puvodni_matice):
                              nova_matice.append(puvodni_matice[idx])
                          else:
                              # Pokud varianta není v původním pořadí, přidáme prázdný řádek
                              if puvodni_matice and len(puvodni_matice[0]) > 0:
                                  nova_matice.append([0] * len(puvodni_matice[0]))
                              else:
                                  nova_matice.append([])
                      
                      upravene_vysledky[nazev_seznamu] = nova_matice
          
          return upravene_vysledky
      except Exception as e:
          Utils.zapsat_chybu(f"Chyba při přeuspořádání dat TOPSIS: {str(e)}")
          return topsis_vysledky  # V případě chyby vrátíme původní výsledky

  def _skryj_grafy(self):
    """Skryje všechny grafy ve formuláři."""
    self.plot_topsis_vysledek.visible = False
    self.plot_topsis_vzdalenosti.visible = False
    self.plot_topsis_radar.visible = False
    self.plot_topsis_2d.visible = False
    self.plot_citlivost_skore.visible = False
    self.plot_citlivost_poradi.visible = False

  def export_link_click(self, **event_args):
        """Obsluha kliknutí na tlačítko pro export PDF."""
        try:
            # Kontrola, zda máme ID analýzy
            if not self.analyza_id:
                alert("Není k dispozici žádná analýza pro export.")
                return
            
            # Změna textu tlačítka během generování
            self.export_link.text = "Generuji PDF..."
            self.export_link.enabled = False
            
            # Volání serverové funkce pro vytvoření PDF
            pdf = anvil.server.call('vytvor_analyzu_pdf', self.analyza_id, "TOPSIS")
            
            # Stažení PDF
            download(pdf)
            
        except Exception as e:
            alert(f"Chyba při generování PDF: {str(e)}")
        finally:
            # Obnovení tlačítka
            self.export_link.text = "Export do PDF"
            self.export_link.enabled = True
