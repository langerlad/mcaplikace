# -------------------------------------------------------
# Form: Wizard_komp
# Formulář pro vytváření a úpravu analýz.
# Ukládá data do lokální cache a na server až v posledním kroku.
# -------------------------------------------------------
from ._anvil_designer import Wizard_kompTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
from .. import Navigace, Konstanty, Spravce_stavu, Utils, Wizard


class Wizard_komp(Wizard_kompTemplate):
  def __init__(self, mode=Konstanty.STAV_ANALYZY['NOVY'], **properties):
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
    self.repeating_panel_kriteria.set_event_handler('x-refresh', self.nacti_kriteria)
    self.repeating_panel_varianty.set_event_handler('x-refresh', self.nacti_varianty)

    if self.mode == Konstanty.STAV_ANALYZY['UPRAVA']: 
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
    vaha = self.vaha
    
    self.spravce.pridej_kriterium(nazev, typ, vaha)

    # Reset vstupních polí
    self.text_box_nazev_kriteria.text = ""
    self.drop_down_typ.selected_value = None
    self.text_box_vaha.text = ""

    # Aktualizace seznamu kritérií
    self.nacti_kriteria()

  def validace_pridej_kriterium(self):
    """Validuje data pro přidání kritéria."""
    zakladni_chyba = Wizard.validace_pridej_kriterium(self)
    if zakladni_chyba:
      return zakladni_chyba
    
    # Specifická validace pro Wizard_komp (váhy)
    if not self.text_box_vaha.text:
      return Konstanty.ZPRAVY_CHYB['NEPLATNA_VAHA']
      
    try:    
      vaha_text = self.text_box_vaha.text.strip()
      
      # Pokud text obsahuje lomítko, zpracujeme ho jako zlomek
      if '/' in vaha_text:
        try:
          citatel, jmenovatel = vaha_text.split('/')
          citatel = float(citatel.strip())
          jmenovatel = float(jmenovatel.strip())
          
          # Ošetření dělení nulou
          if jmenovatel == 0:
            return Konstanty.ZPRAVY_CHYB['NEPLATNA_VAHA'] + " (dělení nulou)"
            
          self.vaha = citatel / jmenovatel
        except ValueError:
          return Konstanty.ZPRAVY_CHYB['NEPLATNA_VAHA'] + " (neplatný formát zlomku)"
      else:
        # Jinak zpracujeme jako desetinné číslo
        vaha_text = vaha_text.replace(',', '.')
        self.vaha = float(vaha_text)
        
      # Ověření rozsahu váhy (0 až 1)
      if not (0 <= self.vaha <= 1):
        return Konstanty.ZPRAVY_CHYB['NEPLATNA_VAHA'] + f" (hodnota {self.vaha:.4f} není v rozsahu 0-1)"
        
    except ValueError:
      return Konstanty.ZPRAVY_CHYB['NEPLATNA_VAHA'] + " (nelze převést na číslo)"
      
    return None

  def nacti_kriteria(self, **event_args):
    """Načte kritéria ze správce stavu a zobrazí je v repeating panelu."""
    Wizard.nacti_kriteria(self, **event_args)

  def button_dalsi_2_click(self, **event_args):
    """Zpracuje přechod z kroku 2 (kritéria) do kroku 3 (varianty)."""
    kriteria = self.spravce.ziskej_kriteria()
    if not kriteria:
      self.label_chyba_2.text = Konstanty.ZPRAVY_CHYB['MIN_KRITERIA']
      self.label_chyba_2.visible = True
      return

    je_validni, zprava = self.kontrola_souctu_vah()
    if not je_validni:
      self.label_chyba_2.text = zprava
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

  def button_ulozit_4_click(self, **event_args):
    """Uloží kompletní analýzu na server, pokud je matice validní."""
    if not self.validuj_matici():
        return
        
    try:
        # Uložení analýzy na server přes správce stavu
        if self.spravce.uloz_analyzu_na_server():
            self.mode = Konstanty.STAV_ANALYZY['ULOZENY']
            alert(Konstanty.ZPRAVY_CHYB['ANALYZA_ULOZENA'])
            
            # Vyčistíme data ve správci stavu
            self.spravce.vycisti_data_analyzy()
            
            Navigace.go('domu')
        else:
            raise ValueError("Nepodařilo se uložit analýzu.")
    except Exception as e:
        error_msg = f"Chyba při ukládání: {str(e)}"
        Utils.zapsat_chybu(error_msg)
        self.label_chyba_4.text = error_msg
        self.label_chyba_4.visible = True

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