# -------------------------------------------------------
# Form: Wizard_komp
# Formulář pro vytváření a úpravu analýz.
# Ukládá data do lokální cache a na server až v posledním kroku.
# -------------------------------------------------------
from ._anvil_designer import Wizard_ahp_kompTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
from .. import Navigace, Konstanty, Spravce_stavu, Utils


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

  def load_existing_analyza(self):
    """Načte existující analýzu pro editaci."""
    try:
      # Pokud nemáme ID analýzy ze správce stavu, zkusíme ho získat ze serveru
      if not self.analyza_id:
        self.analyza_id = anvil.server.call("get_edit_analyza_id")
        if self.analyza_id:
          self.spravce.nastav_aktivni_analyzu(self.analyza_id, True)

      if not self.analyza_id:
        raise Exception(Konstanty.ZPRAVY_CHYB["NEPLATNE_ID"])

      # Načtení dat přímo ze serveru pouze jednou - na začátku úpravy
      data = anvil.server.call("nacti_analyzu", self.analyza_id)

      if data:
        Utils.zapsat_info(f"Data načtena: {data}")

        # 1. Nastavení základních dat
        self.spravce.uloz_zakladni_data_analyzy(
          data.get("nazev", ""), data.get("popis_analyzy", "")
        )

        # 2. Zpracování kritérií v novém formátu
        kriteria = data.get("kriteria", {})
        for nazev_krit, krit_data in kriteria.items():
          self.spravce.pridej_kriterium(
            nazev_krit, krit_data.get("typ", "max"), krit_data.get("vaha", 0)
          )

        # 3. Zpracování variant a jejich hodnot v novém formátu
        varianty = data.get("varianty", {})
        for nazev_var, var_data in varianty.items():
          # Získáme kopii dat varianty, abychom mohli bezpečně odebrat popis_varianty
          var_data_copy = var_data.copy()
          # Extrahujeme popis varianty
          popis_var = var_data_copy.pop("popis_varianty", "")
          # Přidáme variantu
          self.spravce.pridej_variantu(nazev_var, popis_var)

          # Přidání hodnot pro kritéria
          for nazev_krit, hodnota in var_data.items():
            if nazev_krit != "popis_varianty" and nazev_krit in kriteria:
              self.spravce.uloz_hodnotu_varianty(nazev_var, nazev_krit, hodnota)

        # Nastavení polí formuláře z dat ve správci stavu
        self.text_box_nazev.text = self.spravce.ziskej_nazev()
        self.text_area_popis.text = self.spravce.ziskej_popis()

        # Zobrazení dat z kritérií a variant
        self.nacti_kriteria()
        self.nacti_varianty()

        Utils.zapsat_info(f"Analýza {self.analyza_id} úspěšně načtena pro úpravu")
      else:
        raise Exception("Nepodařilo se načíst data analýzy")

    except Exception as e:
      Utils.zapsat_chybu(f"Chyba při načítání analýzy: {str(e)}")
      alert(f"Chyba při načítání analýzy: {str(e)}")
      Navigace.go("domu")

  def button_dalsi_click(self, **event_args):
    """Zpracuje klik na tlačítko Další v prvním kroku."""
    self.label_chyba.visible = False
    chyba = self.validace_vstupu()
    if chyba:
      self.label_chyba.text = chyba
      self.label_chyba.visible = True
      return

    # Uložení základních dat pouze do správce stavu
    self.spravce.uloz_zakladni_data_analyzy(
      nazev=self.text_box_nazev.text, popis=self.text_area_popis.text
    )

    # Vytvoření ID pro novou analýzu (pouze při prvním průchodu)
    if self.mode == Konstanty.STAV_ANALYZY["NOVY"] and not self.analyza_id:
      # V tomto kroku jen vytvoříme ID ve správci stavu, ale neukládáme na server
      # ID analýzy bude vygenerováno až při finálním uložení
      self.analyza_id = "temp_id"  # Dočasné ID pro správce stavu
      self.spravce.nastav_aktivni_analyzu(self.analyza_id, False)
      Utils.zapsat_info(f"Vytvořeno dočasné ID analýzy: {self.analyza_id}")

    # Přechod na další krok
    self.card_krok_1.visible = False
    self.card_krok_2.visible = True

  def validace_vstupu(self):
    """Validuje vstupní data v prvním kroku."""
    if not self.text_box_nazev.text:
      return Konstanty.ZPRAVY_CHYB["NAZEV_PRAZDNY"]
    if len(self.text_box_nazev.text) > Konstanty.VALIDACE["MAX_DELKA_NAZEV"]:
      return Konstanty.ZPRAVY_CHYB["NAZEV_DLOUHY"]
    return None

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
    if not self.text_box_nazev_kriteria.text:
      return "Zadejte název kritéria."
    if not self.drop_down_typ.selected_value:
      return "Vyberte typ kritéria."
    return None

  def nacti_kriteria(self, **event_args):
    """Načte kritéria ze správce stavu a zobrazí je v repeating panelu."""
    # Získáme kritéria ve správném formátu pro UI
    kriteria = []
    for nazev, data in self.spravce.ziskej_kriteria().items():
      kriteria.append(
        {
          "nazev_kriteria": nazev,
          "typ": data.get("typ", "max"),
          "vaha": data.get("vaha", 0),
        }
      )

    self.repeating_panel_kriteria.items = kriteria

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

  def kontrola_souctu_vah(self):
    """Kontroluje, zda součet všech vah kritérií je roven 1"""
    kriteria = self.spravce.ziskej_kriteria()
    soucet_vah = sum(float(k_data["vaha"]) for k_data in kriteria.values())
    soucet_vah = round(soucet_vah, 3)  # Pro jistotu zaokrouhlení

    if abs(soucet_vah - 1.0) > Konstanty.VALIDACE["TOLERANCE_SOUCTU_VAH"]:
      return False, Konstanty.ZPRAVY_CHYB["SUMA_VAH"].format(soucet_vah)
    return True, None

  def button_pridej_variantu_click(self, **event_args):
    """Zpracuje přidání nové varianty."""
    self.label_chyba_3.visible = False
    chyba_3 = self.validace_pridej_variantu()
    if chyba_3:
      self.label_chyba_3.text = chyba_3
      self.label_chyba_3.visible = True
      return

    # Použijeme novou metodu správce stavu pro přidání varianty
    nazev = self.text_box_nazev_varianty.text
    popis = self.text_box_popis_varianty.text

    self.spravce.pridej_variantu(nazev, popis)

    # Reset vstupních polí
    self.text_box_nazev_varianty.text = ""
    self.text_box_popis_varianty.text = ""

    # Aktualizace seznamu variant
    self.nacti_varianty()

  def validace_pridej_variantu(self):
    """Validuje data pro přidání varianty."""
    if not self.text_box_nazev_varianty.text:
      return "Zadejte název varianty."
    return None

  def nacti_varianty(self, **event_args):
    """Načte varianty ze správce stavu a zobrazí je v repeating panelu."""
    # Získáme varianty ve správném formátu pro UI
    varianty = []
    for nazev, data in self.spravce.ziskej_varianty().items():
      varianty.append(
        {"nazev_varianty": nazev, "popis_varianty": data.get("popis_varianty", "")}
      )

    self.repeating_panel_varianty.items = varianty

  def button_dalsi_3_click(self, **event_args):
    """Zpracuje přechod z kroku 3 (varianty) do kroku 4 (matice hodnot)."""
    varianty = self.spravce.ziskej_varianty()
    if not varianty:
      self.label_chyba_3.text = Konstanty.ZPRAVY_CHYB["MIN_VARIANTY"]
      self.label_chyba_3.visible = True
      return

    # Přechod na další krok - data jsou už uložena ve správci stavu
    self.card_krok_3.visible = False
    self.card_krok_4.visible = True
    self.zobraz_krok_4()

  def zobraz_krok_4(self, **event_args):
    """Naplní RepeatingPanel (Matice_var) daty pro zadání matice hodnot."""
    varianty = self.spravce.ziskej_varianty()
    kriteria = self.spravce.ziskej_kriteria()

    matice_data = []
    for nazev_var, var_data in varianty.items():
      kriteria_pro_variantu = []

      for nazev_krit, krit_data in kriteria.items():
        # Získáme hodnotu pro toto kritérium a variantu
        hodnota = var_data.get(nazev_krit, "")

        kriteria_pro_variantu.append(
          {"nazev_kriteria": nazev_krit, "id_kriteria": nazev_krit, "hodnota": hodnota}
        )

      matice_data.append(
        {
          "nazev_varianty": nazev_var,
          "id_varianty": nazev_var,
          "kriteria": kriteria_pro_variantu,
        }
      )

    self.Matice_var.items = matice_data

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

  def validuj_matici(self):
    """Validuje a ukládá hodnoty matice do správce stavu."""
    errors = []

    for var_row in self.Matice_var.get_components():
      nazev_var = var_row.item["id_varianty"]

      for krit_row in var_row.Matice_krit.get_components():
        hodnota_text = krit_row.text_box_matice_hodnota.text
        nazev_krit = krit_row.item["id_kriteria"]

        if not hodnota_text:
          errors.append("Všechny hodnoty musí být vyplněny")
          continue

        try:
          hodnota_text = hodnota_text.replace(",", ".")
          hodnota = float(hodnota_text)
          krit_row.text_box_matice_hodnota.text = str(hodnota)

          # Ukládání v novém formátu
          self.spravce.uloz_hodnotu_varianty(nazev_var, nazev_krit, hodnota)

        except ValueError:
          errors.append(
            Konstanty.ZPRAVY_CHYB["NEPLATNA_HODNOTA"].format(
              var_row.item["nazev_varianty"], krit_row.item["nazev_kriteria"]
            )
          )

    if errors:
      self.label_chyba_4.text = "\n".join(list(set(errors)))
      self.label_chyba_4.visible = True
      return False

    self.label_chyba_4.visible = False
    return True

  def button_zpet_2_click(self, **event_args):
    # Při návratu z kritérií na první krok
    self.card_krok_1.visible = True
    self.card_krok_2.visible = False

  def button_zpet_3_click(self, **event_args):
    # Při návratu z variant na kritéria
    self.card_krok_2.visible = True
    self.card_krok_3.visible = False

  def button_zpet_4_click(self, **event_args):
    # Při návratu z matice na varianty
    self.card_krok_3.visible = True
    self.card_krok_4.visible = False

  def button_zrusit_click(self, **event_args):
    """Zruší vytváření/úpravu analýzy."""
    try:
      if self.mode == Konstanty.STAV_ANALYZY["NOVY"]:
        if Utils.zobraz_potvrzovaci_dialog(
          Konstanty.ZPRAVY_CHYB["POTVRZENI_ZRUSENI_NOVE"]
        ):
          # Pouze vyčistíme data ve správci stavu, nic nemusíme mazat z DB
          self.spravce.vycisti_data_analyzy()
          Navigace.go("domu")

      elif self.mode == Konstanty.STAV_ANALYZY["UPRAVA"]:
        if Utils.zobraz_potvrzovaci_dialog(
          Konstanty.ZPRAVY_CHYB["POTVRZENI_ZRUSENI_UPRAVY"]
        ):
          self.mode = Konstanty.STAV_ANALYZY["ULOZENY"]  # Prevent deletion prompt
          # Vyčistíme data ve správci stavu
          self.spravce.vycisti_data_analyzy()
          Navigace.go("domu")

    except Exception as e:
      Utils.zapsat_chybu(f"Chyba při rušení analýzy: {str(e)}")
      alert(f"Nastala chyba: {str(e)}")
      # I v případě chyby se pokusíme vyčistit stav a přejít na domovskou stránku
      self.spravce.vycisti_data_analyzy()
      Navigace.go("domu")


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
                      "Je stejně důležité jako",
                      "Je mírně důležitější než",
                      "Je středně důležitější než",
                      "Je silně důležitější než", 
                      "Je velmi silně důležitější než",
                      "Je extrémně důležitější než",
                      "Je mírně méně důležité než",
                      "Je středně méně důležité než",
                      "Je silně méně důležité než",
                      "Je velmi silně méně důležité než",
                      "Je extrémně méně důležité než"
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
              "Je stejně důležité jako": 1,
              "Je mírně důležitější než": 3,
              "Je středně důležitější než": 5,
              "Je silně důležitější než": 7, 
              "Je velmi silně důležitější než": 8,
              "Je extrémně důležitější než": 9,
              "Je mírně méně důležité než": 1/3,
              "Je středně méně důležité než": 1/5,
              "Je silně méně důležité než": 1/7,
              "Je velmi silně méně důležité než": 1/8,
              "Je extrémně méně důležité než": 1/9
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