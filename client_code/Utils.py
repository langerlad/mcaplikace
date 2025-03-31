# -------------------------------------------------------
# Modul: Utils
# -------------------------------------------------------
from anvil import confirm

def zapsat_info(zprava):
    """
    Pomocná funkce pro konzolové výpisy info v klientském kódu.
    
    Args:
        zprava (str): Informační zpráva k vypsání
    """
    print(f"[INFO] {zprava}")

def zapsat_chybu(zprava):
    """
    Pomocná funkce pro konzolové výpisy chyb v klientském kódu.
    
    Args:
        zprava (str): Chybová zpráva k vypsání
    """
    print(f"[CHYBA] {zprava}")

def zobraz_potvrzovaci_dialog(zprava, ano_text="Ano", ne_text="Ne"):
    """
    Zobrazí potvrzovací dialog s vlastním textem tlačítek.
    
    Args:
        zprava (str): Text zprávy v dialogu
        ano_text (str): Text pro potvrzovací tlačítko
        ne_text (str): Text pro zamítací tlačítko
        
    Returns:
        bool: True pokud uživatel potvrdil, jinak False
    """
    return confirm(zprava, dismissible=True, 
                  buttons=[(ano_text, True), (ne_text, False)])

def normalizuj_desetinne_cislo(text):
    """
    Převede textový vstup na desetinné číslo.
    Nahradí čárku tečkou a ověří platnost formátu.
    
    Args:
        text (str): Textový vstup
        
    Returns:
        float: Normalizované číslo
        
    Raises:
        ValueError: Pokud vstup není platné číslo
    """
    if not text:
        raise ValueError("Hodnota je povinná")
        
    # Nahrazení čárky za tečku
    text = text.replace(',', '.')
    
    try:
        hodnota = float(text)
        return hodnota
    except ValueError:
        raise ValueError("Zadaná hodnota není platné číslo")

def validuj_data_analyzy(data):
    """Validuje strukturu a obsah dat analýzy"""
    # Kontrola požadovaných polí
    if not isinstance(data, dict):
        raise ValueError("Data musí být slovník")
    
    # Kontrola struktury kritérií
    kriteria = data.get('kriteria', {})
    if not kriteria:
        raise ValueError("Analýza musí obsahovat alespoň jedno kritérium")
    
    # Kontrola struktury variant
    varianty = data.get('varianty', {})
    if not varianty:
        raise ValueError("Analýza musí obsahovat alespoň jednu variantu")
    
    # Validace každého kritéria
    for nazev_krit, data_krit in kriteria.items():
        if not isinstance(data_krit, dict):
            raise ValueError(f"Data kritéria '{nazev_krit}' musí být slovník")
        
        # Kontrola požadovaných polí kritéria
        if 'typ' not in data_krit:
            raise ValueError(f"Kritérium '{nazev_krit}' musí mít pole 'typ'")
        
        if 'vaha' not in data_krit:
            raise ValueError(f"Kritérium '{nazev_krit}' musí mít pole 'vaha'")
        
        # Validace typu kritéria
        if data_krit['typ'] not in ['max', 'min']:
            raise ValueError(f"Typ kritéria '{nazev_krit}' musí být 'max' nebo 'min', zadáno '{data_krit['typ']}'")
        
        # Validace váhy kritéria
        try:
            vaha = float(data_krit['vaha'])
            if vaha < 0 or vaha > 1:
                raise ValueError(f"Váha kritéria '{nazev_krit}' musí být mezi 0 a 1")
        except (ValueError, TypeError):
            raise ValueError(f"Váha kritéria '{nazev_krit}' musí být číslo")
    
    # Kontrola součtu vah = 1
    soucet_vah = sum(float(k['vaha']) for k in kriteria.values())
    if abs(soucet_vah - 1.0) > 0.001:  # Povolíme malou chybu zaokrouhlení
        raise ValueError(f"Součet vah kritérií musí být 1.0, zadáno {soucet_vah:.3f}")
    
    # Validace každé varianty
    for nazev_var, data_var in varianty.items():
        if not isinstance(data_var, dict):
            raise ValueError(f"Data varianty '{nazev_var}' musí být slovník")
        
        # Kontrola, že každá varianta má hodnoty pro všechna kritéria
        for nazev_krit in kriteria.keys():
            if nazev_krit not in data_var and nazev_krit != "popis_varianty":
                raise ValueError(f"Varianta '{nazev_var}' nemá hodnotu pro kritérium '{nazev_krit}'")
            
            # Validace, že hodnota je číselná (pokud existuje)
            if nazev_krit in data_var and nazev_krit != "popis_varianty":
                try:
                    float(data_var[nazev_krit])
                except (ValueError, TypeError):
                    raise ValueError(f"Hodnota pro variantu '{nazev_var}', kritérium '{nazev_krit}' musí být číslo")