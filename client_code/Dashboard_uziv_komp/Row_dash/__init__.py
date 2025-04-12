# client_code/Dashboard_uziv_komp/Row_dash/__init__.py
from ._anvil_designer import Row_dashTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ... import Konstanty, Navigace, Spravce_stavu, Utils


class Row_dash(Row_dashTemplate):
    """
    Třída reprezentující řádek v datovém gridu analýz.
    Poskytuje funkcionalitu pro manipulaci s konkrétní analýzou.
    """
    
    def __init__(self, **properties):
        """
        Inicializace komponenty řádku analýzy v data gridu.
        """
        # Inicializace komponent a správce stavu
        self.init_components(**properties)
        self.spravce = Spravce_stavu.Spravce_stavu()

    def link_vizualizace_click(self, **event_args):
        """
        Zpracuje požadavek na zobrazení výstupu analýzy.
        Zobrazí dialog pro výběr metody analýzy.
        """
        try:
            Utils.zapsat_info(f"Požadavek na vizualizaci analýzy s ID: {self.item['id']}")
            
            # Nastavíme ID aktivní analýzy
            self.spravce.nastav_aktivni_analyzu(self.item['id'], False)
            
            # Zobrazí dialog pro výběr metody analýzy
            self.zobraz_dialog_vyberu_metody()
            
        except Exception as e:
            Utils.zapsat_chybu(f"Chyba při přípravě analýzy: {str(e)}")
            alert(f"Chyba při přípravě analýzy: {str(e)}")

    def link_upravit_click(self, **event_args):
        """
        Zpracuje požadavek na úpravu analýzy.
        """
        try:
            Utils.zapsat_info(f"Úprava analýzy s ID: {self.item['id']}")
            
            # Vyčistíme předchozí stav před načtením nové analýzy
            self.spravce.vycisti_data_analyzy()
            
            # Nastavíme ID upravované analýzy - toto je vše co potřebujeme
            self.spravce.nastav_aktivni_analyzu(self.item['id'], True)
            
            # Přejdeme na stránku úpravy analýzy
            Navigace.go('uprava_analyzy')
            
        except Exception as e:
            Utils.zapsat_chybu(f"Chyba při přípravě úpravy analýzy: {str(e)}")
            alert(f"Chyba při přípravě úpravy analýzy: {str(e)}")

    def link_klonovat_click(self, **event_args):
        """
        Zpracuje požadavek na klonování analýzy.
        Vytvoří kopii vybrané analýzy.
        """
        try:
            Utils.zapsat_info(f"Klonování analýzy s ID: {self.item['id']}")
            
            # Zobrazení dialogu s potvrzením
            if Utils.zobraz_potvrzovaci_dialog("Opravdu chcete vytvořit kopii této analýzy?"):
                # Volání serverové funkce pro klonování
                nova_analyza_id = anvil.server.call('klonuj_analyzu', self.item['id'])
                
                if nova_analyza_id:
                    # Informování uživatele
                    alert("Analýza byla úspěšně naklonována.")
                    
                    # Aktualizace seznamu analýz - akce na data_grid_dash
                    self.parent.parent.raise_event('x-refresh')
                else:
                    raise ValueError("Klonování analýzy se nezdařilo")
                    
        except Exception as e:
            Utils.zapsat_chybu(f"Chyba při klonování analýzy: {str(e)}")
            alert(f"Chyba při klonování analýzy: {str(e)}")

    def link_json_click(self, **event_args):
        """
        Zobrazí a umožní editaci JSON dat analýzy.
        """
        # Zkontrolujeme, zda máme k dispozici ID analýzy
        if 'id' not in self.item:
            Utils.zapsat_chybu("CHYBA: Chybí ID analýzy")
            return
            
        # Získáme ID analýzy
        analyza_id = self.item['id']
        Utils.zapsat_info(f"Editace JSON dat pro analýzu: {analyza_id}")
        
        try:
            # Načtení dat analýzy ze serveru
            analyza_data = anvil.server.call('nacti_analyzu', analyza_id)
            
            # Vytvoření bezpečného slovníku pro JSON serializaci
            import datetime
            def safe_serialize(obj):
                if isinstance(obj, dict):
                    return {k: safe_serialize(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [safe_serialize(i) for i in obj]
                elif isinstance(obj, datetime.datetime):
                    return obj.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(obj, datetime.date):
                    return obj.strftime('%Y-%m-%d')
                else:
                    return obj
                    
            # Konverze dat
            safe_data = safe_serialize(analyza_data)
            
            # Použití standardního JSON
            import json
            formatted_text = json.dumps(safe_data, indent=2, ensure_ascii=False)
            
            # Vytvoření TextArea pro editaci
            text_area = TextArea(font="monospace", height=400, text=formatted_text)
            
            # Zobrazení dialogu s editorem
            result = alert(
                title=f"Editace JSON dat analýzy: {analyza_data.get('nazev', 'Bez názvu')}", 
                content=text_area,
                large=True,
                buttons=[("Uložit změny", True), ("Zrušit", False)]
            )
            
            # Pokud uživatel klikl na Uložit, pokusíme se uložit změny
            if result:
                try:
                    # Parsování upraveného JSON
                    updated_json = json.loads(text_area.text)
                    
                    # Ověření struktury JSON
                    if not isinstance(updated_json, dict):
                        raise ValueError("JSON data musí být objekt (slovník)")
                    
                    # Získáme původní název analýzy
                    nazev = analyza_data.get('nazev', '')
                    
                    # Pro zachování kompatibility s původní strukturou extrahujeme pouze data_json část
                    data_json = {
                        'popis_analyzy': updated_json.get('popis_analyzy', ''),
                        'kriteria': updated_json.get('kriteria', {}),
                        'varianty': updated_json.get('varianty', {})
                    }
                    
                    # Validace dat pomocí funkce z Utils
                    Utils.validuj_data_analyzy(data_json)
                    
                    # Uložení změn na server
                    anvil.server.call('uprav_analyzu', analyza_id, nazev, data_json)
                    
                    # Informujeme uživatele o úspěchu
                    alert("Změny byly úspěšně uloženy.")
                    
                    # Obnovení seznamu analýz pro aktualizaci UI
                    self.parent.parent.raise_event('x-refresh')
                    
                except json.JSONDecodeError as e:
                    alert(f"Neplatný JSON formát: {str(e)}")
                except ValueError as e:
                    alert(f"Chyba validace dat: {str(e)}")
                except Exception as e:
                    Utils.zapsat_chybu(f"Chyba při ukládání JSON dat: {str(e)}")
                    alert(f"Chyba při ukládání změn: {str(e)}")
                  
        except Exception as e:
            Utils.zapsat_chybu(f"Chyba při načítání dat analýzy: {str(e)}")
            alert(f"Chyba při načítání dat analýzy: {str(e)}")

    def link_smazat_click(self, **event_args):
        """
        Zpracuje požadavek na smazání analýzy.
        """
        if Utils.zobraz_potvrzovaci_dialog("Opravdu chcete odstranit tuto analýzu?"):
            try:
                # Smazání analýzy na serveru
                anvil.server.call('smaz_analyzu', self.item['id'])
                
                # Pokud se smazala aktivní analýza, vyčistíme stav
                if self.spravce.ziskej_aktivni_analyzu() == self.item['id']:
                    self.spravce.vycisti_data_analyzy()
                
                # Aktualizace seznamu analýz
                self.parent.parent.raise_event('x-refresh')
                
            except Exception as e:
                Utils.zapsat_chybu(f"Chyba při mazání analýzy: {str(e)}")
                alert(f"Chyba při mazání analýzy: {str(e)}")

    def link_export_click(self, **event_args):
        """
        Zpracuje požadavek na export analýzy do Excelu.
        """
        try:
            Utils.zapsat_info(f"Požadavek na export analýzy s ID: {self.item['id']}")
            
            if not self.item and not hasattr(self.item, 'id'):
                alert("Není k dispozici žádná analýza pro export.")
                return
        
            # Zobrazení indikátoru průběhu
            self.link_export.icon = "fa:spinner"
            self.link_export.tooltip = "Generuji Excel..."
            self.link_export.enabled = False
            
            # Volání serverové funkce pro komplexní export
            excel = anvil.server.call('vytvor_komplexni_excel_report', self.item['id'])
            
            # Stažení Excel souboru
            download(excel)
            
        except Exception as e:
            Utils.zapsat_chybu(f"Chyba při exportu: {str(e)}")
            alert(f"Chyba při generování Excel reportu: {str(e)}")
        finally:
            # Obnovení ikony
            self.link_export.icon = "fa:file-excel-o"
            self.link_export.tooltip = "Stáhnout celý výpočet do Excelu"
            self.link_export.enabled = True

    def zobraz_dialog_vyberu_metody(self):
        """
        Zobrazí dialog pro výběr metody analýzy.
        """
        try:
            # Definice dostupných metod
            dostupne_metody = [
                ("Weighted Sum Model (WSM)", "wsm"),
                ("Weighted Product Model (WPM)", "wpm"),
                ("TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution)", "topsis"),
                ("ELECTRE (Elimination Et Choix Traduisant la Réalité)", "electre"),
                ("MABAC (Multi-Attributive Border Approximation area Comparison)", "mabac")
            ]
            
            # Vytvoření komponenty pro výběr
            dropdown = DropDown(items=[m[0] for m in dostupne_metody])
            dropdown.selected_value = dostupne_metody[0][0]  # Výchozí hodnota
            
            # Vytvoření panelu s komponenty
            panel = FlowPanel()
            panel.add_component(Label(text="Vyberte metodu analýzy:"))
            panel.add_component(dropdown)
            
            # Zobrazení dialogu
            result = alert(
                content=panel,
                title="Výběr metody analýzy",
                large=True,
                dismissible=True,
                buttons=[("Pokračovat", True), ("Zrušit", False)]
            )
            
            if result:  # Pokud uživatel klikl na "Pokračovat"
                # Získání vybrané metody
                vybrany_text = dropdown.selected_value
                vybrana_metoda = next((kod for nazev, kod in dostupne_metody if nazev == vybrany_text), None)
                
                if vybrana_metoda:
                    # Přesměrování na správnou výstupní stránku podle zvolené metody
                    self.presmeruj_na_vystup_metody(vybrana_metoda)
                else:
                    alert("Nebyla vybrána žádná metoda.")
            
        except Exception as e:
            Utils.zapsat_chybu(f"Chyba při zobrazení dialogu pro výběr metody: {str(e)}")
            alert(f"Chyba při výběru metody: {str(e)}")
            
    def presmeruj_na_vystup_metody(self, metoda_kod):
        """
        Přesměruje na stránku s výstupem podle zvolené metody.
        
        Args:
            metoda_kod: Kód zvolené metody (např. 'saw', 'wpm', atd.)
        """
        try:
            analyza_id = self.item['id']
            
            # Přesměrování podle metody
            if metoda_kod == "wsm":
                Navigace.go('vystup_wsm', analyza_id=analyza_id)
            elif metoda_kod == "wpm":
                Navigace.go('vystup_wpm', analyza_id=analyza_id)
            elif metoda_kod == "topsis":
                Navigace.go('vystup_topsis', analyza_id=analyza_id)
            elif metoda_kod == "electre":
                Navigace.go('vystup_electre', analyza_id=analyza_id)
            elif metoda_kod == "mabac":
                Navigace.go('vystup_mabac', analyza_id=analyza_id)
            else:
                alert(f"Metoda '{metoda_kod}' ještě není implementována")
                
        except Exception as e:
            Utils.zapsat_chybu(f"Chyba při přechodu na výstup metody {metoda_kod}: {str(e)}")
            alert(f"Chyba při zobrazení výstupu analýzy: {str(e)}")