from ._anvil_designer import Vystup_saw_kompTemplate
from anvil import *
import plotly.graph_objects as go
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
from .. import Spravce_stavu, Utils


class Vystup_saw_komp(Vystup_saw_kompTemplate):
    """
    Formulář pro zobrazení výsledků SAW analýzy.
    Zobrazuje kompletní přehled včetně:
    - vstupních dat (kritéria, varianty, hodnotící matice)
    - normalizované matice
    - vážených hodnot
    - finálních výsledků
    """
    def __init__(self, analyza_id=None, **properties):
        self.init_components(**properties)
        # Inicializace správce stavu
        self.spravce = Spravce_stavu.Spravce_stavu()
        
        # Použijeme ID z parametrů nebo z aktivní analýzy ve správci
        self.analyza_id = analyza_id or self.spravce.ziskej_aktivni_analyzu()
        
    def form_show(self, **event_args):
        """Načte a zobrazí data analýzy při zobrazení formuláře."""
        if not self.analyza_id:
            self._zobraz_prazdny_formular()
            return
            
        try:
            Utils.zapsat_info(f"Načítám výsledky analýzy ID: {self.analyza_id}")
            
            # Jediné volání serveru - získání dat analýzy
            analyza_data = anvil.server.call('nacti_kompletni_analyzu', self.analyza_id)
            
            # Uložení dat do správce stavu pro případné další použití
            self.spravce.uloz_data_analyzy(analyza_data['analyza'])
            self.spravce.uloz_kriteria(analyza_data['kriteria'])
            self.spravce.uloz_varianty(analyza_data['varianty'])
            self.spravce.uloz_hodnoty(analyza_data['hodnoty'])
            
            # Zobrazení výsledků
            self._zobraz_kompletni_analyzu(analyza_data)
            
            Utils.zapsat_info(f"Výsledky analýzy úspěšně zobrazeny")
            
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
            analyza_data: Slovník s kompletními daty analýzy
        """
        # Zobrazení vstupních dat
        self._zobraz_vstupni_data(analyza_data)
        
        # Provedení výpočtů
        try:
            norm_vysledky = self._normalizuj_matici(analyza_data)
            vazene_hodnoty = self._vypocitej_vazene_hodnoty(analyza_data, norm_vysledky)
            saw_vysledky = self._vypocitej_saw_vysledky(analyza_data, vazene_hodnoty)
            
            # Zobrazení výsledků
            self._zobraz_normalizaci(norm_vysledky, vazene_hodnoty)
            self._zobraz_vysledky(saw_vysledky)
        except Exception as e:
            Utils.zapsat_chybu(f"Chyba při výpočtu výsledků: {str(e)}")
            self.rich_text_normalizace.content = f"Chyba při výpočtu: {str(e)}"
            self.rich_text_vysledek.content = f"Chyba při výpočtu: {str(e)}"
            self.plot_saw_vysledek.visible = False

#-----------------------------------------------------
# Výpočty
#-----------------------------------------------------

    def _normalizuj_matici(self, analyza_data):
            """
            Provede min-max normalizaci hodnot.
            
            Args:
                analyza_data: Slovník obsahující data analýzy
            
            Returns:
                dict: Slovník obsahující normalizovanou matici a metadata
            """
            try:
                varianty = [v['nazev_varianty'] for v in analyza_data['varianty']]
                kriteria = [k['nazev_kriteria'] for k in analyza_data['kriteria']]
                
                # Vytvoření původní matice
                matice = []
                for var in analyza_data['varianty']:
                    radek = []
                    for krit in analyza_data['kriteria']:
                        klic = f"{var['nazev_varianty']}_{krit['nazev_kriteria']}"
                        hodnota = float(analyza_data['hodnoty']['matice_hodnoty'].get(klic, 0))
                        radek.append(hodnota)
                    matice.append(radek)
                
                # Normalizace pomocí min-max pro každý sloupec (kritérium)
                norm_matice = []
                for i in range(len(matice)):
                    norm_radek = []
                    for j in range(len(matice[0])):
                        sloupec = [row[j] for row in matice]
                        min_val = min(sloupec)
                        max_val = max(sloupec)
                        
                        if max_val == min_val:
                            norm_hodnota = 1.0  # Všechny hodnoty jsou stejné
                        else:
                            # Pro MIN kritéria obrátíme normalizaci
                            if analyza_data['kriteria'][j]['typ'].lower() in ("min", "cost"):
                                norm_hodnota = (max_val - matice[i][j]) / (max_val - min_val)
                            else:
                                norm_hodnota = (matice[i][j] - min_val) / (max_val - min_val)
                        
                        norm_radek.append(norm_hodnota)
                    norm_matice.append(norm_radek)
                
                return {
                    'nazvy_variant': varianty,
                    'nazvy_kriterii': kriteria,
                    'normalizovana_matice': norm_matice
                }
            except Exception as e:
                Utils.zapsat_chybu(f"Chyba při normalizaci matice: {str(e)}")
                raise

    def _vypocitej_vazene_hodnoty(self, analyza_data, norm_vysledky):
        """
        Vypočítá vážené hodnoty pro všechny varianty a kritéria.
        
        Args:
            analyza_data: Slovník s daty analýzy
            norm_vysledky: Výsledky normalizace
            
        Returns:
            dict: Slovník vážených hodnot pro každou variantu a kritérium
        """
        try:
            vazene_hodnoty = {}
            
            for i, varianta in enumerate(norm_vysledky['nazvy_variant']):
                vazene_hodnoty[varianta] = {}
                for j, kriterium in enumerate(norm_vysledky['nazvy_kriterii']):
                    norm_hodnota = norm_vysledky['normalizovana_matice'][i][j]
                    vaha = float(analyza_data['kriteria'][j]['vaha'])
                    vazene_hodnoty[varianta][kriterium] = norm_hodnota * vaha
            
            return vazene_hodnoty
        except Exception as e:
            Utils.zapsat_chybu(f"Chyba při výpočtu vážených hodnot: {str(e)}")
            raise

    def _vypocitej_saw_vysledky(self, analyza_data, vazene_hodnoty):
        """
        Vypočítá finální výsledky SAW analýzy.
        
        Args:
            analyza_data: Slovník s daty analýzy
            vazene_hodnoty: Slovník vážených hodnot
            
        Returns:
            dict: Slovník obsahující seřazené výsledky a statistiky
        """
        try:
            # Výpočet celkového skóre pro každou variantu
            skore = {}
            for varianta, hodnoty in vazene_hodnoty.items():
                skore[varianta] = sum(hodnoty.values())
            
            # Seřazení variant podle skóre (sestupně)
            serazene = sorted(skore.items(), key=lambda x: x[1], reverse=True)
            
            # Vytvoření seznamu výsledků s pořadím
            results = []
            for poradi, (varianta, hodnota) in enumerate(serazene, 1):
                results.append((varianta, poradi, hodnota))
            
            return {
                'results': results,
                'nejlepsi_varianta': results[0][0],
                'nejlepsi_skore': results[0][2],
                'nejhorsi_varianta': results[-1][0],
                'nejhorsi_skore': results[-1][2],
                'rozdil_skore': results[0][2] - results[-1][2]
            }
        except Exception as e:
            Utils.zapsat_chybu(f"Chyba při výpočtu SAW výsledků: {str(e)}")
            raise

#-----------------------------------------------------
# Display
#-----------------------------------------------------



#-----------------------------------------------------
# Komentáře + gra
#-----------------------------------------------------



#-----------------------------------------------------
# Display
#-----------------------------------------------------