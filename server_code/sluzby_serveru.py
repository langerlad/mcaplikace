# -------------------------------------------------------
# Modul: Sluzby_serveru
# -------------------------------------------------------
import datetime
import logging
from typing import Dict, List, Optional, Any
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

# Custom exceptions
class AnalyzaError(Exception):
    """Základní výjimka pro operace s analýzou."""
    pass

class AnalyzaNotFoundError(AnalyzaError):
    """Výjimka při nenalezení analýzy."""
    pass

class NeplatnyUzivatelError(AnalyzaError):
    """Výjimka při neplatném uživateli."""
    pass

def validuj_nazev_analyzy(nazev: str) -> None:
    """Validuje název analýzy."""
    if not nazev:
        raise ValueError("Název analýzy nesmí být prázdný.")
    if len(nazev) > 100:
        raise ValueError("Název analýzy je příliš dlouhý (max 100 znaků).")

def validuj_kriteria(kriteria: List[Dict]) -> None:
    """Validuje seznam kritérií."""
    if not kriteria:
        raise ValueError("Je vyžadováno alespoň jedno kritérium.")
    
    vahy_suma = sum(float(k['vaha']) for k in kriteria)
    if abs(vahy_suma - 1.0) > 0.001:  # Tolerance pro desetinná čísla
        raise ValueError(f"Součet vah musí být 1.0 (aktuálně: {vahy_suma})")

@anvil.server.callable
def pridej_analyzu(nazev: str, popis: str, zvolena_metoda: str) -> str:
    """
    Vytvoří novou analýzu.
    
    Args:
        nazev: Název analýzy
        popis: Popis analýzy
        zvolena_metoda: Zvolená metoda analýzy
        
    Returns:
        str: ID nově vytvořené analýzy
        
    Raises:
        NeplatnyUzivatelError: Pokud uživatel není přihlášen
        ValueError: Pokud jsou vstupní data neplatná
    """
    try:
        uzivatel = anvil.users.get_user()
        if not uzivatel:
            raise NeplatnyUzivatelError("Pro vytvoření analýzy musíte být přihlášen.")

        validuj_nazev_analyzy(nazev)
        
        analyza = app_tables.analyza.add_row(
            nazev=nazev,
            popis=popis,
            datum_vytvoreni=datetime.datetime.now(),
            zvolena_metoda=zvolena_metoda,
            uzivatel=uzivatel,
            datum_upravy=None,
            stav=None
        )
        return analyza.get_id()
        
    except Exception as e:
        logging.error(f"Chyba při vytváření analýzy: {str(e)}")
        raise

@anvil.server.callable
def uloz_kompletni_analyzu(analyza_id: str, kriteria: List[Dict], 
                          varianty: List[Dict], hodnoty: List[Dict]) -> None:
    """
    Uloží kompletní analýzu včetně kritérií, variant a hodnot.
    
    Args:
        analyza_id: ID analýzy
        kriteria: Seznam kritérií
        varianty: Seznam variant
        hodnoty: Seznam hodnot pro kombinace variant a kritérií
        
    Raises:
        AnalyzaNotFoundError: Pokud analýza neexistuje
        ValueError: Pokud jsou vstupní data neplatná
    """
    try:
        analyza = app_tables.analyza.get_by_id(analyza_id)
        if not analyza:
            raise AnalyzaNotFoundError(f"Analýza s ID {analyza_id} neexistuje")

        validuj_kriteria(kriteria)
        
        with tables.batch_update():
            # Smazání starých dat
            _smaz_stara_data(analyza)
            
            # Uložení nových dat
            _uloz_kriteria(analyza, kriteria)
            _uloz_varianty(analyza, varianty)
            _uloz_hodnoty(analyza, hodnoty)
            
    except Exception as e:
        logging.error(f"Chyba při ukládání analýzy {analyza_id}: {str(e)}")
        raise

def _smaz_stara_data(analyza: Any) -> None:
    """Smaže stará data analýzy."""
    for hodnota in app_tables.hodnota.search(analyza=analyza):
        hodnota.delete()
    for varianta in app_tables.varianta.search(analyza=analyza):
        varianta.delete()
    for kriterium in app_tables.kriterium.search(analyza=analyza):
        kriterium.delete()

def _uloz_kriteria(analyza: Any, kriteria: List[Dict]) -> None:
    """Uloží kritéria analýzy."""
    for k in kriteria:
        app_tables.kriterium.add_row(
            analyza=analyza,
            nazev_kriteria=k['nazev_kriteria'],
            typ=k['typ'],
            vaha=k['vaha']
        )

def _uloz_varianty(analyza: Any, varianty: List[Dict]) -> None:
    """Uloží varianty analýzy."""
    for v in varianty:
        app_tables.varianta.add_row(
            analyza=analyza,
            nazev_varianty=v['nazev_varianty'],
            popis_varianty=v['popis_varianty']
        )

def _uloz_hodnoty(analyza: Any, hodnoty: List[Dict]) -> None:
    """Uloží hodnoty pro kombinace variant a kritérií."""
    for h in hodnoty:
        varianta = app_tables.varianta.get(
            analyza=analyza,
            nazev_varianty=h['varianta_id']
        )
        kriterium = app_tables.kriterium.get(
            analyza=analyza,
            nazev_kriteria=h['kriterium_id']
        )
        
        if varianta and kriterium:
            app_tables.hodnota.add_row(
                analyza=analyza,
                varianta=varianta,
                kriterium=kriterium,
                hodnota=h['hodnota']
            )

@anvil.server.callable
def smaz_analyzu(analyza_id: str) -> None:
    """
    Smaže analýzu a všechna související data.
    
    Args:
        analyza_id: ID analýzy ke smazání
    """
    try:
        analyza = app_tables.analyza.get_by_id(analyza_id)
        if analyza:
            with tables.batch_update():
                _smaz_stara_data(analyza)
                analyza.delete()
    except Exception as e:
        logging.error(f"Chyba při mazání analýzy {analyza_id}: {str(e)}")
        raise

@anvil.server.callable
def nacti_analyzy_uzivatele() -> List[Dict]:
    """
    Načte seznam analýz přihlášeného uživatele.
    
    Returns:
        List[Dict]: Seznam analýz s jejich základními údaji
    """
    uzivatel = anvil.users.get_user()
    if not uzivatel:
        return []
        
    try:
        analyzy = list(app_tables.analyza.search(
            tables.order_by("datum_vytvoreni", ascending=False),
            uzivatel=uzivatel
        ))
        
        return [{
            'id': a.get_id(),
            'nazev': a['nazev'],
            'popis': a['popis'],
            'datum_vytvoreni': a['datum_vytvoreni'],
            'zvolena_metoda': a['zvolena_metoda']
        } for a in analyzy]
    except Exception as e:
        logging.error(f"Chyba při načítání analýz uživatele: {str(e)}")
        return []

@anvil.server.callable
def nacti_analyzu(analyza_id: str) -> Dict:
    """
    Načte detaily konkrétní analýzy.
    
    Args:
        analyza_id: ID požadované analýzy
        
    Returns:
        Dict: Detaily analýzy
        
    Raises:
        AnalyzaNotFoundError: Pokud analýza neexistuje
    """
    try:
        analyza = app_tables.analyza.get_by_id(analyza_id)
        if not analyza:
            raise AnalyzaNotFoundError(f"Analýza s ID {analyza_id} nebyla nalezena")
            
        return {
            'nazev': analyza['nazev'],
            'popis': analyza['popis'],
            'zvolena_metoda': analyza['zvolena_metoda'],
            'datum_vytvoreni': analyza['datum_vytvoreni']
        }
    except Exception as e:
        logging.error(f"Chyba při načítání analýzy {analyza_id}: {str(e)}")
        raise

# Session management methods can be simplified
@anvil.server.callable
def set_edit_analyza_id(analyza_id: str) -> None:
    """Nastaví ID editované analýzy do session."""
    anvil.server.session['edit_analyza_id'] = analyza_id

@anvil.server.callable
def get_edit_analyza_id() -> Optional[str]:
    """Získá ID editované analýzy ze session."""
    return anvil.server.session.get('edit_analyza_id')