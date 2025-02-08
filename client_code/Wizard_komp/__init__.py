# -------------------------------------------------------
# Form: Wizard_komp
# -------------------------------------------------------
from ._anvil_designer import Wizard_kompTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
from .. import Navigace


class Wizard_komp(Wizard_kompTemplate):
  def __init__(self, mode='new', **properties):
    self.init_components(**properties)
    
    # Mode 'new' pro novou analýzu, 'edit' pro úpravu existující
    self.mode = mode
    
    # Skrýváme karty (kroky) na začátku
    self.card_krok_2.visible = False
    self.card_krok_3.visible = False
    self.card_krok_4.visible = False
    
    # Lokální cache
    self.analyza_id = None
    self.cached_analyza = None
    self.cached_kriteria = []
    self.cached_varianty = []
    self.cached_hodnoty = {'matice_hodnoty': {}}

    # Event handlery pro repeating panely
    self.repeating_panel_kriteria.set_event_handler('x-refresh', self.nacti_kriteria)
    self.repeating_panel_varianty.set_event_handler('x-refresh', self.nacti_varianty)

    if self.mode == 'edit': 
        self.load_existing_analyza()

  def load_existing_analyza(self):
    try:
        self.analyza_id = anvil.server.call('get_edit_analyza_id')
        print("Step 1 - analyza_id:", self.analyza_id)
        
        analyza_data = anvil.server.call('nacti_analyzu', self.analyza_id)
        print("Step 2 - analyza_data:", analyza_data)
        
        self.text_box_nazev.text = analyza_data.get('nazev', '')
        print("Step 3 - set nazev:", self.text_box_nazev.text)
        self.text_area_popis.text = analyza_data.get('popis', '')
        print("Step 4 - set popis:", self.text_area_popis.text)
        
        self.cached_analyza = analyza_data
        print("Step 5 - cached analyza:", self.cached_analyza)
        
        self.cached_kriteria = anvil.server.call('nacti_kriteria', self.analyza_id)
        print("Step 6 - cached kriteria:", self.cached_kriteria)
        
        self.cached_varianty = anvil.server.call('nacti_varianty', self.analyza_id)
        print("Step 7 - cached varianty:", self.cached_varianty)
        
        try:
            self.cached_hodnoty = anvil.server.call('nacti_hodnoty', self.analyza_id)
            print("Step 8 - cached hodnoty:", self.cached_hodnoty)
        except Exception as e:
            print("Warning: Failed to load hodnoty:", str(e))
            self.cached_hodnoty = {'matice_hodnoty': {}}

        # Update displays
        self.nacti_kriteria()
        print("Step 9 - nacti_kriteria done")
        self.nacti_varianty()
        print("Step 10 - nacti_varianty done")
        
    except Exception as e:
        print("Error occurred:", str(e))
        alert("Chyba při načítání analýzy: " + str(e))
        Navigace.go_domu()
      
  def button_dalsi_click(self, **event_args):
    self.label_chyba.visible = False
    chyba = self.validace_vstupu()
    if chyba:
      self.label_chyba.text = chyba
      self.label_chyba.visible = True
      return

    # Cache analytických dat
    self.cached_analyza = {
      'nazev': self.text_box_nazev.text,
      'popis': self.text_area_popis.text,
      'zvolena_metoda': "SAW"
    }

    # Uložíme analýzu na server, získáme ID
    self.analyza_id = anvil.server.call(
      "pridej_analyzu", 
      self.cached_analyza['nazev'],
      self.cached_analyza['popis'], 
      self.cached_analyza['zvolena_metoda']
    )

    self.card_krok_1.visible = False
    self.card_krok_2.visible = True

  def validace_vstupu(self):
    if not self.text_box_nazev.text:
      return "Zadejte název analýzy."
    return None

  def button_pridej_kriterium_click(self, **event_args):
    self.label_chyba_2.visible = False
    chyba_2 = self.validace_pridej_kriterium()
    if chyba_2:
      self.label_chyba_2.text = chyba_2
      self.label_chyba_2.visible = True
      return

    try:
      vaha = float(self.text_box_vaha.text)
      # Přidání do lokální cache
      self.cached_kriteria.append({
        'nazev_kriteria': self.text_box_nazev_kriteria.text,
        'typ': self.drop_down_typ.selected_value,
        'vaha': vaha
      })

      # Reset vstupních polí
      self.text_box_nazev_kriteria.text = ""
      self.drop_down_typ.selected_value = None
      self.text_box_vaha.text = ""

      self.nacti_kriteria()
      
    except ValueError:
      alert("Zadejte platné číslo pro váhu kritéria.")

  def validace_pridej_kriterium(self):
    if not self.text_box_nazev_kriteria.text:
      return "Zadejte název kritéria."
    if not self.drop_down_typ.selected_value:
      return "Vyberte typ kritéria."
    if not self.text_box_vaha.text:
      return "Zadejte hodnotu váhy kritéria."
    try:
      vaha = float(self.text_box_vaha.text)
      if not (0 <= vaha <= 1):
        return "Váha musí být číslo mezi 0 a 1."
    except ValueError:
      return "Váha musí být platné číslo."
    return None

  def nacti_kriteria(self, **event_args):
    self.repeating_panel_kriteria.items = [
      {
        "nazev_kriteria": k["nazev_kriteria"],
        "typ": k["typ"],
        "vaha": k["vaha"]
      } for k in self.cached_kriteria
    ]

  def button_dalsi_2_click(self, **event_args):
    kriteria = self.cached_kriteria
    if not kriteria:
      self.label_chyba_2.text = "Přidejte alespoň jedno kritérium."
      self.label_chyba_2.visible = True
      return

    je_validni, zprava = self.kontrola_souctu_vah()
    if not je_validni:
      self.label_chyba_2.text = zprava
      self.label_chyba_2.visible = True
      return
    
    self.label_chyba_2.visible = False
    self.card_krok_2.visible = False
    self.card_krok_3.visible = True

  def kontrola_souctu_vah(self):
    """
    Kontroluje, zda součet všech vah kritérií je roven 1
    """
    soucet_vah = sum(float(k['vaha']) for k in self.cached_kriteria)
    soucet_vah = round(soucet_vah, 3)  # Pro jistotu zaokrouhlení
    
    if soucet_vah != 1:
      return False, f"Součet vah musí být přesně 1. Aktuální součet je {soucet_vah}"
    return True, None

  def button_pridej_variantu_click(self, **event_args):
    self.label_chyba_3.visible = False
    chyba_3 = self.validace_pridej_variantu()
    if chyba_3:
      self.label_chyba_3.text = chyba_3
      self.label_chyba_3.visible = True
      return

    # Přidání do lokální cache
    self.cached_varianty.append({
      'nazev_varianty': self.text_box_nazev_varianty.text,
      'popis_varianty': self.text_box_popis_varianty.text
    })

    # Reset vstupů
    self.text_box_nazev_varianty.text = ""
    self.text_box_popis_varianty.text = ""

    self.nacti_varianty()

  def validace_pridej_variantu(self):
    if not self.text_box_nazev_varianty.text:
      return "Zadejte název varianty."
    return None

  def nacti_varianty(self, **event_args):
    self.repeating_panel_varianty.items = [
      {
        "nazev_varianty": v["nazev_varianty"],
        "popis_varianty": v["popis_varianty"]
      } for v in self.cached_varianty
    ]

  def button_dalsi_3_click(self, **event_args):
    if not self.cached_varianty:
      self.label_chyba_3.text = "Přidejte alespoň jednu variantu."
      self.label_chyba_3.visible = True
      return

    self.card_krok_3.visible = False
    self.card_krok_4.visible = True
    self.zobraz_krok_4()

  def zobraz_krok_4(self, **event_args):
    """
    Naplní RepeatingPanel (Matice_var) daty pro zadání matice hodnot.
    """
    matice_data = []
    for varianta in self.cached_varianty:
        kriteria_pro_variantu = []
        for k in self.cached_kriteria:
            # Create key in same format as when saving
            key = f"{varianta['nazev_varianty']}_{k['nazev_kriteria']}"
            hodnota = self.cached_hodnoty['matice_hodnoty'].get(key, '')
            
            kriteria_pro_variantu.append({
                'nazev_kriteria': k['nazev_kriteria'],
                'id_kriteria': k['nazev_kriteria'],
                'hodnota': hodnota
            })

        matice_data.append({
            'nazev_varianty': varianta['nazev_varianty'],
            'id_varianty': varianta['nazev_varianty'],
            'kriteria': kriteria_pro_variantu
        })

    self.Matice_var.items = matice_data

  def button_ulozit_4_click(self, **event_args):
    """
    Uloží kompletní analýzu na server, pokud je matice validní.
    """
    if not self.validuj_matici():
      return

    try:
      anvil.server.call(
        'uloz_kompletni_analyzu', 
        self.analyza_id,
        self.cached_kriteria,
        self.cached_varianty,
        self.cached_hodnoty
      )
      self.analyza_id = None  # odstraňení ID zabrání zobrazení konfirmace opuštění stránky
      alert("Analýza byla úspěšně uložena.")
      Navigace.go_domu()
    except Exception as e:
      self.label_chyba_4.text = f"Chyba při ukládání: {str(e)}"
      self.label_chyba_4.visible = True

  def validuj_matici(self):
    """
    Prochází zadané hodnoty v text boxech matice
    a ukládá je do self.cached_hodnoty, pokud jsou validní.
    """
    matrix_values = []
    errors = []

    for var_row in self.Matice_var.get_components():
        print(f"Validating varianta: {var_row.item}")  # Debug
        for krit_row in var_row.Matice_krit.get_components():
            print(f"Validating kriterium: {krit_row.item}")  # Debug
            val = krit_row.text_box_matice_hodnota.text
            if not val:
                errors.append("Všechny hodnoty musí být vyplněny")
                continue
            try:
                val = float(val)
                matrix_values.append({
                    'varianta_id': var_row.item['id_varianty'],
                    'kriterium_id': krit_row.item['id_kriteria'],
                    'hodnota': val
                })
            except ValueError:
                errors.append(f"Neplatná hodnota pro {var_row.item['nazev_varianty']}")

    if errors:
        self.label_chyba_4.text = "\n".join(errors)
        self.label_chyba_4.visible = True
        return False

    self.cached_hodnoty = matrix_values
    return True

  # ----------------------------
  # Tlačítka Zpět a Zrušit
  # ----------------------------
  def button_zpet_2_click(self, **event_args):
    # Pokud vracíme uživatele na Krok 1, a existuje analyza_id, můžeme ji smazat ze serveru
    if hasattr(self, 'analyza_id') and self.analyza_id:
      anvil.server.call('smaz_analyzu', self.analyza_id)
      self.analyza_id = None
    self.cached_analyza = None
    self.card_krok_1.visible = True
    self.card_krok_2.visible = False

  def button_zpet_3_click(self, **event_args):
    self.card_krok_2.visible = True
    self.card_krok_3.visible = False

  def button_zpet_4_click(self, **event_args):
    self.card_krok_3.visible = True
    self.card_krok_4.visible = False

  def button_zrusit_click(self, **event_args):
    if confirm("Opravdu chcete odstranit tuto analýzu?", dismissible=True,
        buttons=[("Ano", True), ("Ne", False)]):
      try:
        if self.analyza_id:
          anvil.server.call('smaz_analyzu', self.analyza_id)
        self.analyza_id = None  # odstraňení ID zabrání zobrazení konfirmace opuštění stránky
        Navigace.go_domu()
      except Exception as e:
        alert(f"Chyba při mazání analýzy: {str(e)}")