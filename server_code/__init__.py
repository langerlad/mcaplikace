import anvil.server
from anvil.tables import app_tables
import datetime
from . import sluzby_serveru  # Import modulu s našimi službami

@anvil.server.background_task
def _inicializace_aplikace_pri_startu():
    """
    Funkce spuštěná automaticky při startu aplikace.
    Zajišťuje inicializaci potřebných dat a nastavení.
    """
    try:
        # Vytvoření prvního admin účtu
        vysledek = sluzby_serveru.nastavit_vychozi_admin()
        
        # Kontrola výsledku
        if vysledek["stav"] == "vytvoreno":
            print(f"DŮLEŽITÉ: {vysledek['zprava']}")
            print(f"Email pro přihlášení: {vysledek['email']}")
            print("Heslo je uloženo v App Secrets")
            
    except Exception as e:
        print(f"Chyba při inicializaci aplikace: {str(e)}")

# Spuštění inicializace na pozadí při startu serveru
anvil.server.launch_background_task("_inicializace_aplikace_pri_startu")
