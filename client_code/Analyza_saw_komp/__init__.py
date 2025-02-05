from ._anvil_designer import Analyza_saw_kompTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
from .. import Navigace

class Analyza_saw_komp(Analyza_saw_kompTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    
    # Hide cards initially
    self.card_krok_2.visible = False
    self.card_krok_3.visible = False
    self.card_krok_4.visible = False
    
    # Local cache
    self.analyza_id = None
    self.cached_analyza = None
    self.cached_kriteria = []
    self.cached_varianty = []
    self.cached_hodnoty = {}
    
    # Event handlers
    self.repeating_panel_kriteria.set_event_handler('x-refresh', self.nacti_kriteria)
    self.repeating_panel_varianty.set_event_handler('x-refresh', self.nacti_varianty)

  def button_dalsi_click(self, **event_args):
    self.label_chyba.visible = False
    chyba = self.validace_vstupu()
    if chyba:
      self.label_chyba.text = chyba
      self.label_chyba.visible = True
      return

    # Cache analyza data locally
    self.cached_analyza = {
      'nazev': self.text_box_nazev.text,
      'popis': self.text_area_popis.text,
      'zvolena_metoda': "SAW"
    }

    # Create analysis to get ID
    self.analyza_id = anvil.server.call("pridej_analyzu", 
                                       self.cached_analyza['nazev'],
                                       self.cached_analyza['popis'], 
                                       self.cached_analyza['zvolena_metoda'])

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
      
      # Add to local cache
      self.cached_kriteria.append({
        'nazev_kriteria': self.text_box_nazev_kriteria.text,
        'typ': self.drop_down_typ.selected_value,
        'vaha': vaha
      })

      # Reset inputs
      self.text_box_nazev_kriteria.text = ""
      self.drop_down_typ.selected_value = None
      self.text_box_vaha.text = ""

      self.nacti_kriteria()
      
    except ValueError:
      alert("Zadejte platné číslo pro váhu kritéria.")

  def nacti_kriteria(self, **event_args):
    self.repeating_panel_kriteria.items = [
      {
        "nazev_kriteria": k["nazev_kriteria"],
        "typ": k["typ"],
        "vaha": k["vaha"]
      } for k in self.cached_kriteria
    ]

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

  def button_dalsi_3_click(self, **event_args):
      if not self.cached_varianty:
          self.label_chyba_3.text = "Přidejte alespoň jednu variantu."
          self.label_chyba_3.visible = True
          return
          
      self.card_krok_3.visible = False
      self.card_krok_4.visible = True
      self.card_krok_4_show()

  
  def button_pridej_variantu_click(self, **event_args):
    self.label_chyba_3.visible = False
    chyba_3 = self.validace_pridej_variantu()
    if chyba_3:
      self.label_chyba_3.text = chyba_3
      self.label_chyba_3.visible = True
      return

    # Add to local cache
    self.cached_varianty.append({
      'nazev_varianty': self.text_box_nazev_varianty.text,
      'popis_varianty': self.text_box_popis_varianty.text
    })

    # Reset inputs
    self.text_box_nazev_varianty.text = ""
    self.text_box_popis_varianty.text = ""

    self.nacti_varianty()

  def nacti_varianty(self, **event_args):
    self.repeating_panel_varianty.items = [
      {
        "nazev_varianty": v["nazev_varianty"],
        "popis_varianty": v["popis_varianty"]
      } for v in self.cached_varianty
    ]

  def button_ulozit_4_click(self, **event_args):
    if not self.validate_matrix():
      return
        
    try:
      # Save everything to DB in batch
      anvil.server.call('uloz_kompletni_analyzu', 
                       self.analyza_id,
                       self.cached_kriteria,
                       self.cached_varianty,
                       self.cached_hodnoty)
      alert("Analýza byla úspěšně uložena.")
      Navigace.go_domu()
    except Exception as e:
      self.label_chyba_4.text = f"Chyba při ukládání: {str(e)}"
      self.label_chyba_4.visible = True

  def validate_matrix(self):
    matrix_values = []
    errors = []
    
    for var_row in self.Matice_var.get_components():
      for krit_row in var_row.Matice_krit.get_components():
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

  # Navigation methods remain unchanged
  def button_zpet_2_click(self, **event_args):
    self.card_krok_1.visible = True
    self.card_krok_2.visible = False

  def button_zpet_3_click(self, **event_args):
    self.card_krok_2.visible = True
    self.card_krok_3.visible = False

  def button_zpet_4_click(self, **event_args):
    self.card_krok_3.visible = True
    self.card_krok_4.visible = False

  def button_zrusit_click(self, **event_args):
    if confirm("Opravdu chcete odstranit tuto analýzu?"):
      try:
        if self.analyza_id:
          anvil.server.call('smaz_analyzu', self.analyza_id)
        Navigace.go_domu()
      except Exception as e:
        alert(f"Chyba při mazání analýzy: {str(e)}")