# client_code/Nastaveni_komp/__init__.py
from ._anvil_designer import Nastaveni_kompTemplate
from anvil import *
import anvil.server
import anvil.users
from .. import Spravce_stavu, Utils, Konstanty

class Nastaveni_komp(Nastaveni_kompTemplate):
  def __init__(self, **properties):
    # Inicializace komponenty
    self.init_components(**properties)
    self.spravce = Spravce_stavu.Spravce_stavu()
    
    # Nacti aktuální nastavení při inicializaci
    self.nacti_nastaveni()
    
  def nacti_nastaveni(self):
    """Načte aktuální nastavení z databáze"""
    try:
      # Přidáme debug výpis
      Utils.zapsat_info("Začínám načítat nastavení v Nastaveni_komp")
      
      # Získání aktuálních hodnot z načteného uživatele
      nastaveni = anvil.server.call('nacti_uzivatelske_nastaveni')
      
      Utils.zapsat_info(f"Načtené nastavení ze serveru: {nastaveni}")
      
      if nastaveni:
        # Načtení hodnot do formuláře
        self.text_box_index_souhlasu.text = str(nastaveni.get('electre_index_souhlasu', '0.7'))
        self.text_box_index_nesouhlasu.text = str(nastaveni.get('electre_index_nesouhlasu', '0.3'))
        
        # Načtení metody stanovení vah
        stanoveni_vah = nastaveni.get('stanoveni_vah', 'manual')
        
        # Nastavení správného radio buttonu
        if stanoveni_vah == 'manual':
          self.radio_button_manual.selected = True
        elif stanoveni_vah == 'rank':
          self.radio_button_rank.selected = True
        elif stanoveni_vah == 'ahp':
          self.radio_button_ahp.selected = True
        elif stanoveni_vah == 'entropie':
          self.radio_button_entropie.selected = True
        else:
          # Výchozí - manuální
          self.radio_button_manual.selected = True
        
          # Debug výpis aktuálně nastavených hodnot
          Utils.zapsat_info(f"Nastavené hodnoty ve formuláři: souhlasu={self.text_box_index_souhlasu.text}, nesouhlasu={self.text_box_index_nesouhlasu.text}, stanoveni_vah={stanoveni_vah}")
          self.radio_button_manual.selected = True        
      else:
        # Nastavení výchozích hodnot
        self.text_box_index_souhlasu.text = '0.7'
        self.text_box_index_nesouhlasu.text = '0.3'
        self.radio_button_manual.selected = True
        Utils.zapsat_info("Nastaveny výchozí hodnoty, protože nastavení ze serveru je None")
        
      self.label_chyba.visible = False
    except Exception as e:
      Utils.zapsat_chybu(f"Chyba při načítání nastavení: {str(e)}")
      self.label_chyba.text = f"Chyba při načítání nastavení: {str(e)}"
      self.label_chyba.visible = True

  def button_ulozit_nastaveni_click(self, **event_args):
    """Zpracování kliknutí na tlačítko uložení nastavení"""
    try:
        # Validace hodnot
        try:
            # Použití existující funkce z Utils
            index_souhlasu = Utils.normalizuj_desetinne_cislo(self.text_box_index_souhlasu.text)
            index_nesouhlasu = Utils.normalizuj_desetinne_cislo(self.text_box_index_nesouhlasu.text)
            
            # Kontrola rozsahu hodnot
            if not (0 <= index_souhlasu <= 1):
                raise ValueError("Index souhlasu musí být číslo mezi 0 a 1")
            if not (0 <= index_nesouhlasu <= 1):
                raise ValueError("Index nesouhlasu musí být číslo mezi 0 a 1")
        except ValueError as e:
            self.label_chyba.text = str(e)
            self.label_chyba.visible = True
            return
        
        # Zjištění zvolené metody stanovení vah
        stanoveni_vah = 'manual'  # Výchozí hodnota
        
        if self.radio_button_manual.selected:
            stanoveni_vah = 'manual'
        elif self.radio_button_rank.selected:
            stanoveni_vah = 'rank'
        elif self.radio_button_ahp.selected:
            stanoveni_vah = 'ahp'
        elif self.radio_button_entropie.selected:
            stanoveni_vah = 'entropie'
        
        # Uložení nastavení
        nastaveni = {     
          'electre_index_souhlasu': index_souhlasu,
          'electre_index_nesouhlasu': index_nesouhlasu,
          'stanoveni_vah': stanoveni_vah
          }
        # Debug výpis
        Utils.zapsat_info(f"Ukládám nastavení: {nastaveni}") 
        # Serverové volání pro uložení
        uspech = anvil.server.call('uloz_uzivatelske_nastaveni', nastaveni)
        
        if not uspech:
            raise ValueError("Nepodařilo se uložit nastavení na server")
        
        # Aktualizace správce stavu - vynutíme nové načtení
        # Důležité: musíme explicitně znovu načíst nastavení z DB
        aktualni = self.spravce.nacti_nastaveni_uzivatele()
        
        # Debug výpis pro kontrolu
        Utils.zapsat_info(f"Aktualizované hodnoty ve správci stavu po opětovném načtení: {aktualni}")
        
        # Informování uživatele o úspěchu
        alert("Nastavení bylo úspěšně uloženo")
        
        # Znovu načteme formulář pro kontrolu
        self.nacti_nastaveni()
        
    except Exception as e:
        Utils.zapsat_chybu(f"Chyba při ukládání nastavení: {str(e)}")
        self.label_chyba.text = f"Chyba při ukládání nastavení: {str(e)}"
        self.label_chyba.visible = True
