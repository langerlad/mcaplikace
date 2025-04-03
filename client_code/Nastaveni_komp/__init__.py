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
    
    # Načtení hodnot při inicializaci
    self.nacti_nastaveni()
    
  def nacti_nastaveni(self):
    """Načte aktuální nastavení z databáze"""
    try:
      # Přidáme debug výpis
      Utils.zapsat_info("Začínám načítat nastavení v Nastaveni_komp")
      
      # Získání aktuálních hodnot
      nastaveni = anvil.server.call('nacti_uzivatelske_nastaveni')
      
      Utils.zapsat_info(f"Načtené nastavení ze serveru: {nastaveni}")
      
      if nastaveni:
        # Načtení hodnot do formuláře
        self.text_box_index_souhlasu.text = str(nastaveni.get('electre_index_souhlasu', '0.7'))
        self.text_box_index_nesouhlasu.text = str(nastaveni.get('electre_index_nesouhlasu', '0.3'))
        
        # Debug výpis aktuálně nastavených hodnot
        Utils.zapsat_info(f"Nastavené hodnoty ve formuláři: souhlasu={self.text_box_index_souhlasu.text}, nesouhlasu={self.text_box_index_nesouhlasu.text}")
      else:
        # Nastavení výchozích hodnot
        self.text_box_index_souhlasu.text = '0.7'
        self.text_box_index_nesouhlasu.text = '0.3'
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
      
        # Uložení nastavení
        nastaveni = {
          'electre_index_souhlasu': index_souhlasu,
          'electre_index_nesouhlasu': index_nesouhlasu
        }
        
        anvil.server.call('uloz_uzivatelske_nastaveni', nastaveni)
        
        # Informování uživatele o úspěchu
        alert("Nastavení bylo úspěšně uloženo")
        
        # Aktualizace správce stavu
        self.spravce.nacti_nastaveni_uzivatele()
        
    except Exception as e:
      Utils.zapsat_chybu(f"Chyba při ukládání nastavení: {str(e)}")
      self.label_chyba.text = f"Chyba při ukládání nastavení: {str(e)}"
      self.label_chyba.visible = True

  def button_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass


