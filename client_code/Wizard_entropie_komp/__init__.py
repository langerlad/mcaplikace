# -------------------------------------------------------
# Form: Wizard_entropie_komp
# Formulář pro vytváření a úpravu analýz metodou entropie.
# Ukládá data do lokální cache a na server až v posledním kroku.
# -------------------------------------------------------
from ._anvil_designer import Wizard_entropie_kompTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
from .. import Navigace, Konstanty, Spravce_stavu, Utils, Wizard


class Wizard_entropie_komp(Wizard_entropie_kompTemplate):
  def __init__(self, mode=Konstanty.STAV_ANALYZY["NOVY"], **properties):
    self.init_components(**properties)

    # Inicializace správce stavu
    self.spravce = Spravce_stavu.Spravce_stavu()

    self.mode = mode

    # Skrýváme karty (kroky) na začátku
    self.card_krok_2.visible = False
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

  def nacti_kriteria(self, **event_args):
    """Načte kritéria ze správce stavu a zobrazí je v repeating panelu."""
    Wizard.nacti_kriteria(self, **event_args)

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
    self.card_krok_3.visible = True

  def kontrola_souctu_vah(self):
    """Kontroluje, zda součet všech vah kritérií je roven 1"""
    return Wizard.kontrola_souctu_vah(self)

  def button_pridej_variantu_click(self, **event_args):
    """Zpracuje přidání nové varianty."""
    Wizard.button_pridej_variantu_click(self, **event_args)

  def validace_pridej_variantu(self):
    """Validuje data pro přidání varianty."""
    return Wizard.validace_pridej_variantu(self)

  def nacti_varianty(self, **event_args):
    """Načte varianty ze správce stavu a zobrazí je v repeating panelu."""
    Wizard.nacti_varianty(self, **event_args)

  def button_dalsi_3_click(self, **event_args):
    """Zpracuje přechod z kroku 3 (varianty) do kroku 4 (matice hodnot)."""
    Wizard.button_dalsi_3_click(self, **event_args)

  def zobraz_krok_4(self, **event_args):
    """Naplní RepeatingPanel (Matice_var) daty pro zadání matice hodnot."""
    Wizard.zobraz_krok_4(self, **event_args)

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

  # Entropie - specifické funkce

  def vypocitej_vahy_entropii(self):
    """
    Vypočítá váhy kritérií metodou entropie na základě zadaných hodnot v matici.
    
    Metoda entropie stanoví váhy kritérií na základě míry variability hodnot v kritériích:
    1. Normalizujeme hodnoty v matici pro každé kritérium
    2. Vypočítáme entropii pro každé kritérium
    3. Vypočítáme míru diverzity (1 - entropie)
    4. Normalizujeme výsledné hodnoty diverzity, abychom získali váhy
    
    Returns:
        dict: Slovník s vypočtenými váhami pro každé kritérium
    """
    import math

    try:
      # Nejprve získáme všechny hodnoty z matice
      varianty = self.spravce.ziskej_varianty()
      kriteria = self.spravce.ziskej_kriteria()
      
      # Kontrola, zda máme dostatečný počet variant a kritérií
      if len(varianty) < 2:
        raise ValueError("Pro výpočet vah metodou entropie jsou potřeba alespoň 2 varianty.")
      if len(kriteria) < 2:
        raise ValueError("Pro výpočet vah metodou entropie jsou potřeba alespoň 2 kritéria.")
      
      # Vytvoření matice hodnot
      matice = []
      for var_nazev, var_data in varianty.items():
        radek = []
        for krit_nazev in kriteria.keys():
          hodnota = var_data.get(krit_nazev, 0)
          if hodnota <= 0:
            hodnota = 0.001  # Zabránění nulám nebo záporným hodnotám
          radek.append(float(hodnota))
        matice.append(radek)
      
      # 1. Normalizace matice pro každé kritérium (sloupec)
      norm_matice = []
      for radek in matice:
        norm_radek = []
        for j in range(len(kriteria)):
          sloupec = [matice[i][j] for i in range(len(varianty))]
          soucet_sloupec = sum(sloupec)
          if soucet_sloupec <= 0:
            norm_hodnota = 1.0 / len(varianty)  # Rovnoměrné rozdělení při nulách
          else:
            norm_hodnota = radek[j] / soucet_sloupec
          norm_radek.append(norm_hodnota)
        norm_matice.append(norm_radek)
      
      # 2. Výpočet entropie pro každé kritérium
      entropie = []
      k = 1 / math.log(len(varianty))  # Konstanta pro normalizaci entropie
      
      for j in range(len(kriteria)):
        e_j = 0
        for i in range(len(varianty)):
          # Vynecháme nulové hodnoty při výpočtu entropie (log(0) je nedefinováno)
          if norm_matice[i][j] > 0:
            e_j -= norm_matice[i][j] * math.log(norm_matice[i][j])
        e_j *= k
        entropie.append(e_j)
      
      # 3. Výpočet míry diverzity (1 - entropie)
      diverzita = [1 - e for e in entropie]
      
      # 4. Normalizace diverzity na váhy (suma vah = 1)
      suma_diverzity = sum(diverzita)
      
      # Kontrola, zda suma diverzity není nulová
      if suma_diverzity <= 0:
        # Pokud je suma nulová, použijeme rovnoměrné váhy
        vahy = {krit: 1.0 / len(kriteria) for krit in kriteria.keys()}
      else:
        vahy = {}
        for i, krit in enumerate(kriteria.keys()):
          vahy[krit] = diverzita[i] / suma_diverzity
      
      # Debug výpis
      Utils.zapsat_info(f"Vypočtené váhy metodou entropie: {vahy}")
      
      return vahy
      
    except Exception as e:
      Utils.zapsat_chybu(f"Chyba při výpočtu vah metodou entropie: {str(e)}")
      self.label_chyba_4.text = f"Chyba při výpočtu vah: {str(e)}"
      self.label_chyba_4.visible = True
      return None

  def button_ulozit_4_click(self, **event_args):
    """
    Uloží kompletní analýzu na server, pokud je matice validní.
    Pro metodu entropie nejprve provede výpočet vah na základě zadaných hodnot.
    """
    if not self.validuj_matici():
      return

    try:
      # Nejprve vypočítáme váhy metodou entropie
      vahy = self.vypocitej_vahy_entropii()
      if vahy is None:
        raise ValueError("Nepodařilo se vypočítat váhy metodou entropie")
      
      # Aktualizujeme váhy kritérií ve správci stavu
      kriteria = self.spravce.ziskej_kriteria()
      for nazev_krit, vaha in vahy.items():
        self.spravce.uprav_kriterium(
          nazev_krit,
          nazev_krit,
          kriteria[nazev_krit]['typ'],
          vaha
        )
      
      # Kontrola součtu vah - pro jistotu
      je_validni, zprava = self.kontrola_souctu_vah()
      if not je_validni:
        raise ValueError(zprava)
      
      # Zobrazíme uživateli informaci o vypočtených váhách
      vahy_text = "\n".join([f"{krit}: {vaha:.4f}" for krit, vaha in vahy.items()])
      confirm_message = f"Byly vypočteny následující váhy kritérií metodou entropie:\n\n{vahy_text}\n\nPokračovat s uložením analýzy?"
      if not Utils.zobraz_potvrzovaci_dialog(confirm_message):
        return
      
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