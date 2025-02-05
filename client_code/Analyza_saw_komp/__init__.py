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
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

    # Skrytí karet na začátku wizardu
    self.card_krok_2.visible = False
    self.card_krok_3.visible = False
    self.card_krok_4.visible = False
    
    # Inicializace vstupů krok 1, krok 2 a krok 3
    self.nazev = None
    self.popis = None
    self.zvolena_metoda = "SAW"
    self.nazev_kriteria = None
    self.typ = None
    self.vaha = None
    self.nazev_varianty = None
    self.popis_varinaty = None

    # Načtení uložených kritérií při inicializaci formuláře
    # self.nacti_kriteria()

    # Nastavení event handleru pro aktualizaci seznamu kritérií / variant
    self.repeating_panel_kriteria.set_event_handler('x-refresh', self.nacti_kriteria)
    self.repeating_panel_varianty.set_event_handler('x-refresh', self.nacti_varianty)
       

  def button_dalsi_click(self, **event_args):
    """Přepne na druhý krok formuláře a uloží název, popis a metodu do db"""
    self.label_chyba.visible = False
    chyba = self.validace_vstupu()
    if chyba:
      self.label_chyba.text = chyba
      self.label_chyba.visible = True
      return

    # Uložení analýzy a získání jejího ID
    self.analyza_id = anvil.server.call("pridej_analyzu", self.nazev, self.popis, self.zvolena_metoda)
    # print(f"Analýza vytvořena s ID: {self.analyza_id}")
    # print("uložené údaje: {} {} {}".format(self.nazev, self.popis, self.zvolena_metoda))

    # Přepnutí na druhou kartu
    self.card_krok_1.visible = False
    self.card_krok_2.visible = True

    self.nacti_kriteria()

  def validace_vstupu(self):
    if not self.text_box_nazev.text:
      return "Zadejte název analýzy."
    self.nazev = self.text_box_nazev.text
    self.popis = self.text_area_popis.text
    return None

  def button_pridej_kriterium_click(self, **event_args):
    """Uloží kritérium do db"""
    self.label_chyba_2.visible = False
    chyba_2 = self.validace_pridej_kryterium()
    
    if chyba_2:
      self.label_chyba_2.text = chyba_2
      self.label_chyba_2.visible = True
      return

    # Kontrola, zda existuje analýza
    if not hasattr(self, 'analyza_id') or not self.analyza_id:
        alert("Nejdříve musíte vytvořit analýzu.")
        return

    try:
        self.vaha = float(self.text_box_vaha.text)
    except ValueError:
        alert("Zadejte platné číslo pro váhu kritéria.")
        return

    # Odeslání dat na server  
    anvil.server.call('pridej_kriterium', self.analyza_id, self.nazev_kriteria, self.typ, self.vaha)

    # Resetování vstupních polí
    self.text_box_nazev_kriteria.text = ""
    self.drop_down_typ.selected_value = None
    self.text_box_vaha.text = ""

    # Znovu načtení pouze druhé karty (ponechání uživatele na stejném kroku)
    self.card_krok_2.visible = False
    self.card_krok_2.visible = True

    # Znovu načtení seznamu kritérií
    self.nacti_kriteria()

  def validace_pridej_kryterium(self):
    if not self.text_box_nazev_kriteria.text:
      return "Zadejte název kritéria."    
    self.nazev_kriteria = self.text_box_nazev_kriteria.text
    
    if not self.drop_down_typ.selected_value:
      return "Vyberte typ kritéria - max, nebo min."    
    self.typ = self.drop_down_typ.selected_value

    if not self.text_box_vaha.text:
      return "Zadejte hodnotu váhy kritéria."

    try:
      vaha = float(self.text_box_vaha.text)
      if not (0 <= vaha <= 1):
        return "Váha musí být číslo mezi 0 a 1."
    except ValueError:
        return "Váha musí být platné číslo."
    self.vaha = self.text_box_vaha.text

  def nacti_kriteria(self, **event_args):
    """Načte uložená kritéria a zobrazí je v repeating panelu"""
    kriteria = anvil.server.call('nacti_kriteria', self.analyza_id)

    # Přidání správného `row_id` pro každé kritérium
    seznam_kriterii = [
        {
            "id": kriterium.get_id(),  # Použití `row_id` jako `id`
            "nazev_kriteria": kriterium["nazev_kriteria"],
            "typ": kriterium["typ"],
            "vaha": kriterium["vaha"]
        }
        for kriterium in kriteria
    ]

    self.repeating_panel_kriteria.items = seznam_kriterii

  def kontrola_souctu_vah(self):
    """Kontroluje, zda součet všech vah kritérií je roven 1"""
    # Načtení všech kritérií pro tuto analýzu
    kriteria = anvil.server.call('nacti_kriteria', self.analyza_id)
    
    # Výpočet součtu vah
    soucet_vah = sum(float(kriterium['vaha']) for kriterium in kriteria)
    
    # Zaokrouhlení na 3 desetinná místa pro přesnější porovnání
    soucet_vah = round(soucet_vah, 3)
    
    if soucet_vah != 1:
      return False, f"Součet vah musí být přesně 1. Aktuální součet je {soucet_vah}"
    return True, None

  def button_dalsi_2_click(self, **event_args):
    """Přepne na třetí krok formuláře pro přidání variant a provede kontrolu součtu vah"""
    
    # Kontrola, zda existují nějaká kritéria
    kriteria = anvil.server.call('nacti_kriteria', self.analyza_id)
    if not kriteria:
      self.label_chyba_2.text = "Přidejte alespoň jedno kritérium před pokračováním."
      self.label_chyba_2.visible = True
      return
    
    # Kontrola součtu vah
    je_validni, chybova_zprava = self.kontrola_souctu_vah()
    
    if not je_validni:
      self.label_chyba_2.text = chybova_zprava
      self.label_chyba_2.visible = True
      return
        
    # Pokud jsou všechny kontroly v pořádku, skryjeme chybovou hlášku a přejdeme na další krok
    self.label_chyba_2.visible = False
    self.card_krok_2.visible = False
    self.card_krok_3.visible = True



  def button_pridej_variantu_click(self, **event_args):
    """Uloží variantu do db"""
    self.label_chyba_3.visible = False
    chyba_3 = self.validace_pridej_variantu()
    
    if chyba_3:
        self.label_chyba_3.text = chyba_3
        self.label_chyba_3.visible = True
        return

    # Kontrola, zda existuje analýza
    if not hasattr(self, 'analyza_id') or not self.analyza_id:
        alert("Nejdříve musíte vytvořit analýzu.")
        return

    # Odeslání dat na server  
    anvil.server.call('pridej_variantu', self.analyza_id, self.nazev_varianty, self.popis_varianty)

    # Resetování vstupních polí
    self.text_box_nazev_varianty.text = ""
    self.text_box_popis_varianty.text = ""

    # Znovu načtení pouze třetí karty
    self.card_krok_3.visible = False
    self.card_krok_3.visible = True

    # Znovu načtení seznamu variant
    self.nacti_varianty()

  def validace_pridej_variantu(self):
    """Validace vstupů pro přidání varianty"""
    if not self.text_box_nazev_varianty.text:
      return "Zadejte název varianty."    
    self.nazev_varianty = self.text_box_nazev_varianty.text
    
    self.popis_varianty = self.text_box_popis_varianty.text
    return None
  
  def nacti_varianty(self, **event_args):
      """Načte uložené varianty a zobrazí je v repeating panelu"""
      varianty = anvil.server.call('nacti_varianty', self.analyza_id)
  
      # Přidání správného `row_id` pro každou variantu
      seznam_variant = [
          {
              "id": varianta.get_id(),
              "nazev_varianty": varianta["nazev_varianty"],
              "popis_varianty": varianta["popis_varianty"]
          }
          for varianta in varianty
      ]
  
      self.repeating_panel_varianty.items = seznam_variant

  def button_dalsi_3_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.card_krok_3.visible = False
    self.card_krok_4.visible = True

    self.card_krok_4_show()

  def card_krok_4_show(self, **event_args):
    data = anvil.server.call('nacti_matice_data', self.analyza_id)
    self.Matice_var.items = data  

  def button_ulozit_4_click(self, **event_args):
    print("Starting save process...")
    ulozene_hodnoty = []
    chyby = []
    
    for varianta_row in self.Matice_var.get_components():
        id_varianty = varianta_row.item['id_varianty']
        
        for kriterium_row in varianta_row.Matice_krit.get_components():
            id_kriteria = kriterium_row.item['id_kriteria']
            hodnota_text = kriterium_row.text_box_matice_hodnota.text
            
          # Validace vstupu hodnota (TODO: zaměnitelnost pro float "." a "," ", ")
            if isinstance(hodnota_text, (int, float)):
                hodnota = float(hodnota_text)
            elif not hodnota_text or (isinstance(hodnota_text, str) and not hodnota_text.strip()):
                chyby.append(f"Chybí hodnota pro variantu {varianta_row.item['nazev_varianty']}")
                continue
            else:
                try:
                    hodnota = float(hodnota_text)
                except ValueError:
                    chyby.append(f"Neplatná hodnota pro variantu {varianta_row.item['nazev_varianty']}")
                    continue
            
            try:
                hodnota = float(hodnota_text) if isinstance(hodnota_text, str) else hodnota_text
                ulozene_hodnoty.append({
                    'id_varianty': id_varianty,
                    'id_kriteria': id_kriteria,
                    'hodnota': hodnota
                })
            except ValueError:
                chyby.append(f"Neplatná hodnota pro variantu {varianta_row.item['nazev_varianty']}")
    
    if chyby:
        self.label_chyba_4.text = "\n".join(chyby)
        self.label_chyba_4.visible = True
        return
      
    try:
        anvil.server.call('uloz_hodnoty_matice', self.analyza_id, ulozene_hodnoty)
        self.label_chyba_4.visible = False
        alert("Hodnoty byly úspěšně uloženy.")
        Navigace.go_domu()
    except Exception as e:
        self.label_chyba_4.text = f"Chyba při ukládání: {str(e)}"
        self.label_chyba_4.visible = True

  def nacti_existujici_hodnotu(self, id_varianty, id_kriteria):
    """Načte existující hodnotu pro danou variantu a kritérium"""
    hodnota = anvil.server.call('nacti_existujici_hodnotu', self.analyza_id, id_varianty, id_kriteria)
    return hodnota if hodnota is not None else ''

  def button_zrusit_click(self, **event_args):
   if confirm("Opravdu chcete zrušit tuto analýzu? Všechna data budou smazána."):
    try:
      anvil.server.call('smaz_analyzu', self.analyza_id)
      from .. import Navigace
      Navigace.go_domu()
    except Exception as e:
      alert(f"Chyba při mazání analýzy: {str(e)}")
