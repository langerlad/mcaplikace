# -------------------------------------------------------
# Form: Wizard_ahp_komp
# Formulář pro vytváření a úpravu analýz metodou AHP.
# Ukládá data do lokální cache a na server až v posledním kroku.
# -------------------------------------------------------
from ._anvil_designer import Wizard_ahp_kompTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
from .. import Navigace, Konstanty, Spravce_stavu, Utils, Wizard


class Wizard_ahp_komp(Wizard_ahp_kompTemplate):
  def __init__(self, mode=Konstanty.STAV_ANALYZY["NOVY"], **properties):
    self.init_components(**properties)

    # Inicializace správce stavu
    self.spravce = Spravce_stavu.Spravce_stavu()

    self.mode = mode

    # Skrýváme karty (kroky) na začátku
    self.card_krok_2.visible = False
    self.card_ahp.visible = False
    self.card_krok_3.visible = False
    self.card_krok_4.visible = False

    # Získáme ID analýzy ze správce stavu
    self.analyza_id = self.spravce.ziskej_aktivni_analyzu()

    # Event handlery pro repeating panely
    self.repeating_panel_kriteria.set_event_handler("x-refresh", self.nacti_kriteria)
    self.repeating_panel_varianty.set_event_handler("x-refresh", self.nacti_varianty)

    if self.mode == Konstanty.STAV_ANALYZY["UPRAVA"]:
      self.load_existing_analyza()

  # Delegování na sdílené metody
  def load_existing_analyza(self):
      """Načte existující analýzu pro editaci."""
      Wizard.load_existing_analyza(self)
  
  def button_dalsi_click(self, **event_args):
      """Zpracuje klik na tlačítko Další v prvním kroku."""
      Wizard.button_dalsi_click(self, **event_args)
  
  def validace_vstupu(self):
      """Validuje vstupní data v prvním kroku."""
      return Wizard.validace_vstupu(self)
  
  def nacti_kriteria(self, **event_args):
      """Načte kritéria ze správce stavu a zobrazí je v repeating panelu."""
      Wizard.nacti_kriteria(self, **event_args)
  
  def button_pridej_variantu_click(self, **event_args):
      """Zpracuje přidání nové varianty."""
      Wizard.button_pridej_variantu_click(self, **event_args)
  
  def nacti_varianty(self, **event_args):
      """Načte varianty ze správce stavu a zobrazí je v repeating panelu."""
      Wizard.nacti_varianty(self, **event_args)
  
  def button_dalsi_3_click(self, **event_args):
      """Zpracuje přechod z kroku 3 (varianty) do kroku 4 (matice hodnot)."""
      Wizard.button_dalsi_3_click(self, **event_args)
  
  def validuj_matici(self):
      """Validuje a ukládá hodnoty matice do správce stavu."""
      return Wizard.validuj_matici(self)
  
  def button_zpet_2_click(self, **event_args):
      """Při návratu z kritérií na první krok"""
      Wizard.button_zpet_2_click(self, **event_args)
  
  def button_zpet_3_click(self, **event_args):
      """Při návratu z variant na kritéria"""
      Wizard.button_zpet_3_click(self, **event_args)
  
  def button_zpet_4_click(self, **event_args):
      """Při návratu z matice na varianty"""
      Wizard.button_zpet_4_click(self, **event_args)
  
  def button_zrusit_click(self, **event_args):
      """Zruší vytváření/úpravu analýzy."""
      Wizard.button_zrusit_click(self, **event_args)
    
  # Metody specifické pro formulář AHP

  def button_pridej_kriterium_click(self, **event_args):
    """Zpracuje přidání nového kritéria."""
    self.label_chyba_2.visible = False
    chyba_2 = self.validace_pridej_kriterium()
    if chyba_2:
      self.label_chyba_2.text = chyba_2
      self.label_chyba_2.visible = True
      return

    # Použijeme novou metodu správce stavu pro přidání kritéria
    nazev = self.text_box_nazev_kriteria.text
    typ = self.drop_down_typ.selected_value

    self.spravce.pridej_kriterium(nazev, typ, 0)

    # Reset vstupních polí
    self.text_box_nazev_kriteria.text = ""
    self.drop_down_typ.selected_value = None
    self.text_box_vaha.text = ""

    # Aktualizace seznamu kritérií
    self.nacti_kriteria()

  def validace_pridej_kriterium(self):
    """Validuje data pro přidání kritéria."""
    return Wizard.validace_pridej_kriterium(self)

  def zobraz_krok_4(self, **event_args):
    """Naplní RepeatingPanel (Matice_var) daty pro zadání matice hodnot."""
    Wizard.zobraz_krok_4(self, **event_args)

  def kontrola_souctu_vah(self):
    """Kontroluje, zda součet všech vah kritérií je roven 1"""
    return Wizard.kontrola_souctu_vah(self)

  def button_dalsi_2_click(self, **event_args):
    """Zpracuje přechod z kroku 2 (kritéria) do kroku 3 (varianty)."""
    kriteria = self.spravce.ziskej_kriteria()
    if not kriteria:
      self.label_chyba_2.text = Konstanty.ZPRAVY_CHYB["MIN_KRITERIA"]
      self.label_chyba_2.visible = True
      return

    # Přechod na další krok - data jsou už uložena ve správci stavu
    self.label_chyba_2.visible = False
    self.card_krok_2.visible = False
    self.card_ahp.visible = True

    # Vytvoříme matici párového porovnání
    self.vytvor_ahp_matici()

  def button_zpet_ahp_click(self, **event_args):
    """Při návratu z AHP na kritéria"""
    self.card_ahp.visible = False
    self.card_krok_2.visible = True

  def button_ulozit_4_click(self, **event_args):
    """Uloží kompletní analýzu na server, pokud je matice validní."""
    if not self.validuj_matici():
      return

    try:
      # Uložení analýzy na server přes správce stavu
      if self.spravce.uloz_analyzu_na_server():
        self.mode = Konstanty.STAV_ANALYZY["ULOZENY"]
        alert(Konstanty.ZPRAVY_CHYB["ANALYZA_ULOZENA"])

        # Vyčistíme data ve správci stavu
        self.spravce.vycisti_data_analyzy()

        Navigace.go("domu")
      else:
        raise ValueError("Nepodařilo se uložit analýzu.")
    except Exception as e:
      error_msg = f"Chyba při ukládání: {str(e)}"
      Utils.zapsat_chybu(error_msg)
      self.label_chyba_4.text = error_msg
      self.label_chyba_4.visible = True

  # AHP porovnání
  
  def vytvor_ahp_matici(self):
      """Vytvoří dynamickou matici párového porovnání pro AHP metodu."""
      try:
          # Získáme seznam kritérií
          kriteria = self.spravce.ziskej_kriteria()
          nazvy_kriterii = list(kriteria.keys())
          
          # Kontrola, zda máme alespoň 2 kritéria
          if len(nazvy_kriterii) < 2:
              self.label_chyba_ahp.text = "Pro AHP metodu jsou potřeba alespoň 2 kritéria."
              self.label_chyba_ahp.visible = True
              return
              
          # Vyčistíme předchozí obsah panelu
          self.column_panel_ahp_matice.clear()
          
          # Inicializujeme pole pro ukládání hodnot
          self.ahp_hodnoty = {}
          
          # Pro každou dvojici kritérií vytvoříme řádek v matici
          for i in range(len(nazvy_kriterii)):
              for j in range(i+1, len(nazvy_kriterii)):
                  krit1 = nazvy_kriterii[i]
                  krit2 = nazvy_kriterii[j]
                  
                  # Vytvoříme řádek pro porovnání
                  radek_panel = FlowPanel()
                  radek_panel.spacing = "large"
                  
                  # Kritérium 1
                  label_krit1 = Label(text=krit1, bold=True)
                  radek_panel.add_component(label_krit1)
                  
                  # Dropdown s volbami
                  volby = [
                      "obě kritéria jsou rovnocenná (1)",
                      "je trochu důležitější (3) než",
                      "je středně důležitější (5) než",
                      "je mnohem důležitější (7) než", 
                      "je extrémně důležitější (9) než",
                      "Je je trochu méně důležité (1/3)",
                      "Je středně méně důležité než (1/5)",
                      "je mnohem méně důležité (1/7) než",
                      "je extrémně méně důležité (1/9) než"
                      ]
                  
                  dropdown = DropDown(items=volby)
                  dropdown.selected_value = volby[0]  # Výchozí hodnota (stejně důležité)
                  dropdown.tag = (krit1, krit2)  # Uložíme si ID porovnávaných kritérií
                  dropdown.set_event_handler('change', self.ahp_dropdown_change)
                  radek_panel.add_component(dropdown)
                  
                  # Kritérium 2
                  label_krit2 = Label(text=krit2, bold=True)
                  radek_panel.add_component(label_krit2)
                  
                  # Přidáme řádek do panelu
                  self.column_panel_ahp_matice.add_component(radek_panel)
                  
                  # Inicializujeme hodnotu v ahp_hodnoty (1 = stejně důležité)
                  self.ahp_hodnoty[(krit1, krit2)] = 1
                  
          # Přidáme tlačítko pro výpočet vah
          self.column_panel_ahp_matice.add_component(Spacer(height=32))
          
          Utils.zapsat_info(f"AHP matice vytvořena pro {len(nazvy_kriterii)} kritérií, celkem {len(self.ahp_hodnoty)} porovnání")
                  
      except Exception as e:
          Utils.zapsat_chybu(f"Chyba při vytváření AHP matice: {str(e)}")
          self.label_chyba_ahp.text = f"Chyba při vytváření AHP matice: {str(e)}"
          self.label_chyba_ahp.visible = True
  
  def ahp_dropdown_change(self, **event_args):
      """Handler pro změnu hodnoty v dropdown menu AHP matice."""
      try:
          dropdown = event_args['sender']
          krit1, krit2 = dropdown.tag  # Získáme ID kritérií
          
          # Mapování textových hodnot na číselné (pro AHP)
          hodnoty_mapa = {
              "obě kritéria jsou rovnocenná (1)": 1,
              "je trochu důležitější (3) než": 3,
              "je středně důležitější (5) než": 5,
              "je mnohem důležitější (7) než": 7, 
              "je extrémně důležitější (9) než": 9,
              "Je je trochu méně důležité (1/3)": 1/3,
              "Je středně méně důležité než (1/5)": 1/5,
              "je mnohem méně důležité (1/7) než": 1/7,
              "je extrémně méně důležité (1/9) než": 1/9
          }
          
          # Získáme číselnou hodnotu a uložíme do ahp_hodnoty
          hodnota = hodnoty_mapa.get(dropdown.selected_value, 1)
          self.ahp_hodnoty[(krit1, krit2)] = hodnota
          
          Utils.zapsat_info(f"AHP hodnota pro {krit1} vs {krit2} nastavena na {hodnota}")
          
      except Exception as e:
          Utils.zapsat_chybu(f"Chyba při změně AHP hodnoty: {str(e)}")
  
  def vypocitej_ahp_vahy(self):
      """Vypočítá váhy kritérií pomocí AHP metody."""
      try:
          # Získáme seznam kritérií
          kriteria = self.spravce.ziskej_kriteria()
          nazvy_kriterii = list(kriteria.keys())
          pocet_kriterii = len(nazvy_kriterii)
          
          # Vytvoříme matici porovnání
          matice = []
          for i in range(pocet_kriterii):
              radek = []
              for j in range(pocet_kriterii):
                  if i == j:
                      # Diagonála matice
                      radek.append(1)
                  elif i < j:
                      # Hodnota z párového porovnání
                      hodnota = self.ahp_hodnoty.get((nazvy_kriterii[i], nazvy_kriterii[j]), 1)
                      radek.append(hodnota)
                  else:  # i > j
                      # Reciproká hodnota
                      hodnota = self.ahp_hodnoty.get((nazvy_kriterii[j], nazvy_kriterii[i]), 1)
                      radek.append(1/hodnota)
              matice.append(radek)
              
          # Výpočet vah (metoda geometrického průměru)
          # 1. Výpočet geometrických průměrů řádků
          geom_prumery = []
          for radek in matice:
              soucin = 1
              for hodnota in radek:
                  soucin *= hodnota
              geom_prumer = soucin ** (1/pocet_kriterii)
              geom_prumery.append(geom_prumer)
              
          # 2. Normalizace na součet 1
          soucet_prumeru = sum(geom_prumery)
          normalizovane_vahy = [prumer/soucet_prumeru for prumer in geom_prumery]
          
          # Debug výpis
          Utils.zapsat_info(f"AHP váhy vypočítány: {dict(zip(nazvy_kriterii, normalizovane_vahy))}")
          
          # Uložení vah do kritérií
          for i, nazev in enumerate(nazvy_kriterii):
              vaha = normalizovane_vahy[i]
              self.spravce.uprav_kriterium(nazev, nazev, kriteria[nazev]['typ'], vaha)
              
          return True
          
      except Exception as e:
          Utils.zapsat_chybu(f"Chyba při výpočtu AHP vah: {str(e)}")
          self.label_chyba_ahp.text = f"Chyba při výpočtu AHP vah: {str(e)}"
          self.label_chyba_ahp.visible = True
          return False

  def button_dalsi_ahp_click(self, **event_args):
      """Zpracuje kliknutí na tlačítko Další u AHP matice."""
      # Kontrola, zda jsou vyplněna všechna porovnání
      if not self.ahp_hodnoty:
          self.label_chyba_ahp.text = "Nejsou vyplněna všechna párová porovnání."
          self.label_chyba_ahp.visible = True
          return
          
      # Výpočet vah z AHP matice
      if not self.vypocitej_ahp_vahy():
          return  # Chyba při výpočtu
          
      # Přechod na další krok - varianty
      self.card_ahp.visible = False
      self.card_krok_3.visible = True

  def button_spocitat_ahp_click(self, **event_args):
      """
      Spočítá váhy kritérií metodou AHP a zobrazí je v rich_text_ahp_vahy
      s podrobnějším vysvětlením mezikroků i interpretací CR.
      """
      try:
          # 1) Načteme a zvalidujeme seznam kritérií
          kriteria_dict = self.spravce.ziskej_kriteria()
          kriteria_list = list(kriteria_dict.keys())
          n = len(kriteria_list)
          
          if n < 2:
              alert("Pro výpočet AHP potřebujete alespoň 2 kritéria.")
              return
          
          # Vytvoření matice A (párového srovnání)
          A = []
          for i in range(n):
              radek = [1.0] * n
              A.append(radek)
          
          # Naplnění matice z ahp_hodnoty (které máte uložené)
          for i in range(n):
              for j in range(i+1, n):
                  krit1 = kriteria_list[i]
                  krit2 = kriteria_list[j]
                  hodnota = self.ahp_hodnoty.get((krit1, krit2), 1.0)
                  A[i][j] = hodnota
                  A[j][i] = 1.0 / hodnota
          
          # 2) Výpočet váhy každého řádku = geometrický průměr
          row_prod = []
          for i in range(n):
              soucin = 1.0
              for j in range(n):
                  soucin *= A[i][j]
              row_prod.append(soucin)
          
          geo_mean = [prod**(1.0/n) for prod in row_prod]
          
          # Normalizace tak, aby součet všech vah = 1
          suma_vah = sum(geo_mean)
          w = [vaha / suma_vah for vaha in geo_mean]
          
          # 3) Výpočet konzistence
          # A * w
          Aw = []
          for i in range(n):
              soucin = 0.0
              for j in range(n):
                  soucin += A[i][j] * w[j]
              Aw.append(soucin)
          
          # lambda_vec = (A w) / w
          lambda_vec = []
          for i in range(n):
              if w[i] != 0:
                  lambda_vec.append(Aw[i] / w[i])
              else:
                  lambda_vec.append(0)
          
          lambda_max = sum(lambda_vec) / n
          
          CI = (lambda_max - n) / (n - 1) if n > 1 else 0
          
          RI_values = {1: 0, 2: 0, 3: 0.58, 4: 0.9, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
          RI = RI_values.get(n, 1.49)
          
          CR = CI / RI if RI != 0 else 0
          
          # 4) Tvorba detailního Markdownu
          md_vystup = "## AHP – Výpočet vah kritérií\n\n"
          
          # (A) Ukázka matice A
          md_vystup += "### Matice párového srovnání (A)\n"
          md_vystup += "Hodnoty, kde je každá buňka > 1 znamená, že řádkové kritérium je tolikrát důležitější než sloupcové.\n\n"
          md_vystup += "| &nbsp; | " + " | ".join(kriteria_list) + " |\n"
          md_vystup += "|---" + "|---" * n + "|\n"
          for i in range(n):
              row_str = f"| **{kriteria_list[i]}** "
              for j in range(n):
                  row_str += f"| {A[i][j]:.3f} "
              row_str += "|\n"
              md_vystup += row_str
          md_vystup += "\n"
          
          # (B) Geometrické průměry (row_prod a geo_mean)
          md_vystup += "### Geometrický průměr řádků\n\n"
          md_vystup += "Zde vidíte součin hodnot v řádku (row_prod) a jejich n-tou odmocninu (geo_mean). \n\n"
          md_vystup += "| Kritérium | Součin řádku | GeoMean |\n"
          md_vystup += "|---|---|---|\n"
          for i, k in enumerate(kriteria_list):
              md_vystup += f"| **{k}** | {row_prod[i]:.4f} | {geo_mean[i]:.4f} |\n"
          md_vystup += "\n"
          
          # (C) Normalizované váhy
          md_vystup += "### Normalizované váhy (w)\n\n"
          md_vystup += "Po normalizaci mají váhy součet 1.\n\n"
          md_vystup += "| Kritérium | Váha |\n"
          md_vystup += "|---|---|\n"
          
          # Seřazené dle váhy
          vahy_serazene = sorted(zip(kriteria_list, w), key=lambda x: x[1], reverse=True)
          for (krit, vaha) in vahy_serazene:
              md_vystup += f"| **{krit}** | {vaha:.4f} |\n"
          md_vystup += "\n"
          
          md_vystup += "Součet vah = 1.0000\n\n"
          
          # (D) Konzistence
          md_vystup += "### Konzistence hodnocení\n"
          md_vystup += f"- **lambda_max** = {lambda_max:.3f}\n"
          md_vystup += f"- **CI (Consistency Index)** = {CI:.4f}\n"
          md_vystup += f"- **RI (Random Index)** pro n={n} je {RI:.2f}\n"
          md_vystup += f"- **CR (Consistency Ratio)** = {CR:.4f}\n\n"
          
          # Interpretace CR
          if CR <= 0.1:
              md_vystup += "> **Interpretace**: CR ≤ 0.1 značí, že hodnocení je **dostatečně konzistentní**.\n"
          elif CR <= 0.2:
              md_vystup += "> **Interpretace**: CR je mezi 0.1 a 0.2 – jedná se o **hraniční** konzistenci. Je možné zvážit úpravu.\n"
          else:
              md_vystup += "> **Interpretace**: CR > 0.2 značí, že hodnocení je **nekonzistentní**. Doporučuje se **znovu** projít párová srovnání.\n"
          
          # Pokud CR je až moc vysoké, upozorníme
          if CR > 0.1:
              md_vystup += "\n> **Upozornění**: Konzistence je nad doporučenou hranicí 0.1, zvažte úpravu párových srovnání.\n"
          
          # 5) Vypsat do RichText
          self.rich_text_ahp_vahy.content = md_vystup
          self.rich_text_ahp_vahy.visible = True
          
          # 6) Případně zobrazit tlačítko pro další krok
          self.button_dalsi_ahp.visible = True
          
      except Exception as e:
          Utils.zapsat_chybu(f"Chyba při výpočtu AHP vah: {str(e)}")
          alert(f"Chyba při výpočtu vah: {str(e)}")