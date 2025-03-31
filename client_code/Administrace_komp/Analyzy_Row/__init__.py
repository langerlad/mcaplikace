# client_code/Administrace_komp/Analyzy_Row/__init__.py
from ._anvil_designer import Analyzy_RowTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ... import Spravce_stavu, Utils



class Analyzy_Row(Analyzy_RowTemplate):
    def __init__(self, **properties):
        """Inicializace řádku analýzy."""
        self.init_components(**properties)
        self.spravce = Spravce_stavu.Spravce_stavu()

    def link_zoom_click(self, **event_args):
        """Zobrazí JSON data analýzy po kliknutí na zoom."""
        # Zkontrolujeme, zda máme k dispozici ID analýzy
        if 'id' not in self.item:
            Utils.zapsat_chybu("CHYBA: Chybí ID analýzy")
            return
            
        # Získáme ID analýzy
        analyza_id = self.item['id']
        Utils.zapsat_info(f"Zobrazuji JSON data pro analýzu: {analyza_id}")
        
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
            
            # Zobrazení dat v dialogu
            text_area = TextArea(font="monospace", height=400, text=formatted_text)
            
            alert(title=f"JSON data analýzy: {analyza_data.get('nazev', 'Bez názvu')}", 
                  content=text_area,
                  large=True)
                  
        except Exception as e:
            Utils.zapsat_chybu(f"Chyba při načítání dat analýzy: {str(e)}")
            alert(f"Chyba při načítání dat analýzy: {str(e)}")