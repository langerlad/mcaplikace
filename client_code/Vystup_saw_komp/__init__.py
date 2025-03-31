from ._anvil_designer import Vystup_saw_kompTemplate
from anvil import *
import plotly.graph_objects as go
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
from .. import Spravce_stavu, Utils, Vypocty, Vizualizace


class Vystup_saw_komp(Vystup_saw_kompTemplate):
    """
    Formulář pro zobrazení výsledků SAW analýzy.
    Zobrazuje kompletní přehled včetně:
    - vstupních dat (kritéria, varianty, hodnotící matice)
    - normalizované matice
    - vážených hodnot
    - finálních výsledků
    Upraveno pro novou JSON strukturu a lepší zobrazení tabulek.
    """
    def __init__(self, analyza_id=None, metoda=None, **properties):
        self.init_components(**properties)
        # Inicializace správce stavu
        self.spravce = Spravce_stavu.Spravce_stavu()
      
        # Použijeme ID z parametrů nebo z aktivní analýzy ve správci
        self.analyza_id = analyza_id or self.spravce.ziskej_aktivni_analyzu()

        # Uložíme zvolenou metodu
        self.metoda = metoda or "SAW"  # Výchozí metoda je SAW
    
        # Aktualizujeme titulek podle zvolené metody
        self.headline_1.text = f"Analýza metodou {self.metoda}"
        
    def form_show(self, **event_args):
        """Načte a zobrazí data analýzy při zobrazení formuláře."""
        if not self.analyza_id:
            self._zobraz_prazdny_formular()
            return
            
        try:
            Utils.zapsat_info(f"Načítám výsledky analýzy ID: {self.analyza_id}")
            
            # Načtení dat analýzy z nové JSON struktury
            analyza_data = anvil.server.call('nacti_analyzu', self.analyza_id)
            
            # Zobrazení výsledků
            self._zobraz_kompletni_analyzu(analyza_data)
            
            Utils.zapsat_info("Výsledky analýzy úspěšně zobrazeny")
            
        except Exception as e:
            Utils.zapsat_chybu(f"Chyba při načítání analýzy: {str(e)}")
            alert(f"Chyba při načítání analýzy: {str(e)}")

    def _zobraz_prazdny_formular(self):
        """Zobrazí prázdný formulář s informací o chybějících datech."""
        Utils.zapsat_info("Zobrazuji prázdný formulář - chybí ID analýzy")
        self.rich_text_vstupni_data.content = "Nepřišlo žádné ID analýzy."
        self.rich_text_normalizace.content = "Není co počítat."
        self.rich_text_vysledek.content = "Není co počítat."
        self.plot_saw_vysledek.visible = False

    def _zobraz_kompletni_analyzu(self, analyza_data):
        """
        Zobrazí kompletní analýzu včetně všech výpočtů.
        
        Args:
            analyza_data: Slovník s kompletními daty analýzy v novém formátu
        """
        # Zobrazení vstupních dat
        self._zobraz_vstupni_data(analyza_data)
        
        # Provedení výpočtů
        try:
            # Použití sdílených modulů pro výpočty
            matice, typy_kriterii, varianty, kriteria, vahy = Vypocty.priprav_data_z_json(analyza_data)
            
            # Normalizace matice
            norm_vysledky = Vypocty.normalizuj_matici_minmax(matice, typy_kriterii, varianty, kriteria)
            
            # Výpočet vážených hodnot
            vazene_matice = Vypocty.vypocitej_vazene_hodnoty(
                norm_vysledky['normalizovana_matice'], 
                vahy
            )
            
            # Výpočet SAW výsledků
            saw_vysledky = Vypocty.wsm_vypocet(
                norm_vysledky['normalizovana_matice'], 
                vahy, 
                varianty
            )
            
            # Uložení dat pro další použití
            self._data_pro_grafy = {
                'norm_vysledky': norm_vysledky,
                'vazene_matice': vazene_matice,
                'vahy': vahy,
                'saw_vysledky': saw_vysledky
            }
            
            # Zobrazení výsledků
            self._zobraz_normalizaci(norm_vysledky, vazene_matice)
            self._zobraz_vysledky(saw_vysledky)
        except Exception as e:
            Utils.zapsat_chybu(f"Chyba při výpočtu výsledků: {str(e)}")
            self.rich_text_normalizace.content = f"Chyba při výpočtu: {str(e)}"
            self.rich_text_vysledek.content = f"Chyba při výpočtu: {str(e)}"
            self.plot_saw_vysledek.visible = False

    def _zobraz_vstupni_data(self, analyza_data):
        """Zobrazí vstupní data analýzy v přehledné formě."""
        try:
            md = f"""
### {analyza_data['nazev']}

#### Základní informace
- Metoda: SAW (Simple Additive Weighting)
- Popis: {analyza_data.get('popis_analyzy', 'Bez popisu')}

<div style='width:100%; overflow-x:auto; margin-bottom:20px;'>

#### Kritéria
| Název kritéria | Typ | Váha |
|----------------|-----|------|
"""
            # Přidání kritérií
            kriteria = analyza_data.get('kriteria', {})
            for nazev_krit, krit_data in kriteria.items():
                vaha = float(krit_data['vaha'])
                md += f"| {nazev_krit} | {krit_data['typ'].upper()} | {vaha:.3f} |\n"

            md += "</div>\n\n"
            
            # Varianty
            md += "#### Varianty\n"
            varianty = analyza_data.get('varianty', {})
            for nazev_var, var_data in varianty.items():
                popis = f" - {var_data.get('popis_varianty', '')}" if var_data.get('popis_varianty') else ""
                md += f"- {nazev_var}{popis}\n"

            # Hodnotící matice
            kriteria_nazvy = list(kriteria.keys())
            varianty_nazvy = list(varianty.keys())
            
            md += "\n<div style='width:100%; overflow-x:auto; margin-bottom:20px;'>\n\n"
            md += "#### Hodnotící matice\n"
            md += f"| Kritérium | {' | '.join(varianty_nazvy)} |\n"
            md += f"|{'-' * 10}|{('|'.join('-' * 12 for _ in varianty_nazvy))}|\n"
            
            for nazev_krit in kriteria_nazvy:
                radek = f"| {nazev_krit} |"
                for nazev_var in varianty_nazvy:
                    hodnota = varianty[nazev_var].get(nazev_krit, "N/A")
                    hodnota = f" {hodnota:.2f} |" if isinstance(hodnota, (int, float)) else f" {hodnota} |"
                    radek += hodnota
                md += radek + "\n"
            
            md += "</div>\n"

            self.rich_text_vstupni_data.content = md
        except Exception as e:
            Utils.zapsat_chybu(f"Chyba při zobrazování vstupních dat: {str(e)}")
            self.rich_text_vstupni_data.content = f"Chyba při zobrazování vstupních dat: {str(e)}"

    def _zobraz_normalizaci(self, norm_vysledky, vazene_matice):
        """
        Zobrazí normalizovanou matici a vážené hodnoty s horizontálním posuvníkem.
        
        Args:
            norm_vysledky: Výsledky normalizace
            vazene_matice: Vypočtené vážené hodnoty
        """
        try:
            md = "### Normalizace hodnot\n\n"
            
            # Normalizační tabulka s horizontálním posuvníkem
            md += "<div style='width:100%; overflow-x:auto; margin-bottom:20px;'>\n\n"
            md += "#### Normalizovaná matice\n"
            md += "| Varianta / Krit. | " + " | ".join(norm_vysledky['nazvy_kriterii']) + " |\n"
            md += "|" + "-|"*(len(norm_vysledky['nazvy_kriterii'])+1) + "\n"
            
            for i, var_name in enumerate(norm_vysledky['nazvy_variant']):
                md += f"| {var_name} |"
                for j in range(len(norm_vysledky['nazvy_kriterii'])):
                    md += f" {norm_vysledky['normalizovana_matice'][i][j]:.3f} |"
                md += "\n"
            
            md += "\n</div>\n"

            # Vysvětlení normalizace
            md += self._vytvor_vysvetleni_normalizace()
            
            # Tabulka vážených hodnot s horizontálním posuvníkem
            md += self._vytvor_tabulku_vazenych_hodnot(vazene_matice, norm_vysledky)
            
            # Vysvětlení vážených hodnot
            md += self._vytvor_vysvetleni_vazenych_hodnot()
            
            self.rich_text_normalizace.content = md
        except Exception as e:
            Utils.zapsat_chybu(f"Chyba při zobrazování normalizace: {str(e)}")
            self.rich_text_normalizace.content = f"Chyba při zobrazování normalizace: {str(e)}"

    def _zobraz_vysledky(self, saw_vysledky):
        """
        Zobrazí finální výsledky SAW analýzy s horizontálním posuvníkem pro tabulky.
        
        Args:
            saw_vysledky: Výsledky SAW analýzy
        """
        try:
            md = "### Výsledky SAW analýzy\n\n"
            
            # Tabulka výsledků s horizontálním posuvníkem
            md += "<div style='width:100%; overflow-x:auto; margin-bottom:20px;'>\n\n"
            md += "#### Pořadí variant\n"
            md += "| Pořadí | Varianta | Skóre | % z maxima |\n"
            md += "|:-------|:---------|------:|------------:|\n"
            
            max_skore = saw_vysledky['nejlepsi_skore']
            
            for varianta, poradi, skore in saw_vysledky['results']:
                procento = (skore / max_skore) * 100 if max_skore > 0 else 0
                md += f"| {poradi}. | {varianta} | {skore:.3f} | {procento:.1f}% |\n"
            
            md += "\n</div>\n"

            # Shrnutí výsledků
            md += f"""
#### Shrnutí výsledků

- **Nejlepší varianta:** {saw_vysledky['nejlepsi_varianta']} (skóre: {saw_vysledky['nejlepsi_skore']:.3f})
- **Nejhorší varianta:** {saw_vysledky['nejhorsi_varianta']} (skóre: {saw_vysledky['nejhorsi_skore']:.3f})
- **Rozdíl nejlepší-nejhorší:** {saw_vysledky['rozdil_skore']:.3f}
- **Poměr nejhorší/nejlepší:** {(saw_vysledky['nejhorsi_skore'] / saw_vysledky['nejlepsi_skore'] * 100):.1f}% z maxima

#### Metoda SAW (Simple Additive Weighting)

SAW, také známý jako Simple Additive Weighting, je jedna z nejjednodušších a nejpoužívanějších metod vícekriteriálního rozhodování.

**Princip metody:**
1. Normalizace hodnot do intervalu [0,1] pomocí metody Min-Max
2. Vynásobení normalizovaných hodnot vahami kritérií
3. Sečtení vážených hodnot pro každou variantu
4. Seřazení variant podle celkového skóre (vyšší je lepší)

**Výhody metody:**
- Jednoduchá a intuitivní
- Transparentní výpočty a výsledky
- Snadná interpretace

**Omezení metody:**
- Předpokládá lineární užitek
- Není vhodná pro silně konfliktní kritéria
- Méně robustní vůči extrémním hodnotám než některé pokročilejší metody
"""
            self.rich_text_vysledek.content = md

            # Přidání grafu s využitím sdíleného modulu Vizualizace
            self.plot_saw_vysledek.figure = Vizualizace.vytvor_sloupovy_graf_vysledku(
                saw_vysledky['results'], 
                saw_vysledky['nejlepsi_varianta'], 
                saw_vysledky['nejhorsi_varianta'], 
                "SAW"
            )
            self.plot_saw_vysledek.visible = True
        except Exception as e:
            Utils.zapsat_chybu(f"Chyba při zobrazování výsledků: {str(e)}")
            self.rich_text_vysledek.content = f"Chyba při zobrazování výsledků: {str(e)}"
            self.plot_saw_vysledek.visible = False

    def _vytvor_vysvetleni_normalizace(self):
        """Vytvoří text s vysvětlením normalizace."""
        return """
#### Princip metody Min-Max normalizace:

Pro **Maximalizační kritéria** (čím více, tím lépe):
- Normalizovaná hodnota = (hodnota - minimum) / (maximum - minimum)
- Nejlepší hodnota = 1 (maximum)
- Nejhorší hodnota = 0 (minimum)

Pro **Minimalizační kritéria** (čím méně, tím lépe):
- Normalizovaná hodnota = (maximum - hodnota) / (maximum - minimum)
- Nejlepší hodnota = 1 (minimum)
- Nejhorší hodnota = 0 (maximum)

Kde:
- minimum = nejmenší hodnota v daném kritériu
- maximum = největší hodnota v daném kritériu
"""

    def _vytvor_tabulku_vazenych_hodnot(self, vazene_matice, norm_vysledky):
        """
        Vytvoří markdown tabulku vážených hodnot s horizontálním posuvníkem.
        
        Args:
            vazene_matice: 2D list vážených hodnot
            norm_vysledky: Výsledky normalizace
            
        Returns:
            str: Markdown formátovaná tabulka s HTML wrapperem
        """
        try:
            md = "\n<div style='width:100%; overflow-x:auto; margin-bottom:20px;'>\n\n"
            md += "#### Vážené hodnoty (normalizované hodnoty × váhy)\n"
            md += "| Varianta / Krit. | " + " | ".join(norm_vysledky['nazvy_kriterii']) + " | Součet |\n"
            md += "|" + "-|"*(len(norm_vysledky['nazvy_kriterii'])+2) + "\n"
            
            for i, var_name in enumerate(norm_vysledky['nazvy_variant']):
                md += f"| {var_name} |"
                sum_val = 0
                for j in range(len(norm_vysledky['nazvy_kriterii'])):
                    val = vazene_matice[i][j]
                    sum_val += val
                    md += f" {val:.3f} |"
                md += f" {sum_val:.3f} |\n"
            
            md += "\n</div>\n"
            return md
        except Exception as e:
            Utils.zapsat_chybu(f"Chyba při vytváření tabulky vážených hodnot: {str(e)}")
            return "\n<p>Chyba při vytváření tabulky vážených hodnot</p>\n"

    def _vytvor_vysvetleni_vazenych_hodnot(self):
        """Vytvoří text s vysvětlením vážených hodnot."""
        return """
#### Interpretace vážených hodnot:

1. Pro každé kritérium je normalizovaná hodnota vynásobena příslušnou vahou.
2. Vážené hodnoty ukazují, jak jednotlivé kritérium přispívá ke konečnému hodnocení varianty.
3. **Součet vážených hodnot** představuje konečné skóre varianty a slouží pro určení pořadí variant.
4. Čím vyšší je skóre, tím lépe varianta splňuje požadavky definované kritérii a jejich vahami.
"""





