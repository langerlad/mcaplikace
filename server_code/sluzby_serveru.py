# -------------------------------------------------------
# Modul: Sluzby_serveru
# Serverové funkce pro práci s analýzami
# -------------------------------------------------------
import datetime
import logging
from typing import Dict, List, Optional, Any
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import Konstanty

# =============== Validační funkce ===============


def validuj_nazev_analyzy(nazev: str) -> None:
    """
    Validuje název analýzy.
    
    Args:
        nazev: Název analýzy k validaci
        
    Raises:
        ValueError: Pokud název není validní
    """
    if not nazev:
        raise ValueError(Konstanty.ZPRAVY_CHYB['NAZEV_PRAZDNY'])
    if len(nazev) > Konstanty.VALIDACE['MAX_DELKA_NAZEV']:
        raise ValueError(Konstanty.ZPRAVY_CHYB['NAZEV_DLOUHY'])

def validuj_kriteria(kriteria: List[Dict]) -> None:
    """
    Validuje seznam kritérií včetně kontroly součtu vah.
    
    Args:
        kriteria: Seznam kritérií k validaci
        
    Raises:
        ValueError: Pokud kritéria nejsou validní
    """
    if not kriteria:
        raise ValueError(Konstanty.ZPRAVY_CHYB['MIN_KRITERIA'])
    
    try:
        vahy_suma = sum(float(k['vaha']) for k in kriteria)
        if abs(vahy_suma - 1.0) > Konstanty.VALIDACE['TOLERANCE_SOUCTU_VAH']:
            raise ValueError(Konstanty.ZPRAVY_CHYB['SUMA_VAH'].format(vahy_suma))
    except (ValueError, TypeError):
        raise ValueError(Konstanty.ZPRAVY_CHYB['NEPLATNA_VAHA'])

# =============== Pomocné funkce pro práci s daty ===============

def _uloz_kriteria(analyza: Any, kriteria: List[Dict]) -> None:
    """
    Uloží kritéria k dané analýze.
    
    Args:
        analyza: Instance analýzy
        kriteria: Seznam kritérií k uložení
    """
    for krit in kriteria:
        try:
            vaha = float(krit['vaha'])
            app_tables.kriterium.add_row(
                analyza=analyza,
                nazev_kriteria=krit['nazev_kriteria'],
                typ=krit['typ'],
                vaha=vaha
            )
        except (ValueError, TypeError):
            raise ValueError(
                Konstanty.ZPRAVY_CHYB['NEPLATNA_VAHA_KRITERIA'].format(krit['nazev_kriteria'])
            )

def _uloz_varianty(analyza: Any, varianty: List[Dict]) -> None:
    """
    Uloží varianty k dané analýze.
    
    Args:
        analyza: Instance analýzy
        varianty: Seznam variant k uložení
    """
    for var in varianty:
        app_tables.varianta.add_row(
            analyza=analyza,
            nazev_varianty=var['nazev_varianty'],
            popis_varianty=var['popis_varianty']
        )

def _uloz_hodnoty(analyza: Any, hodnoty: Dict) -> None:
    """
    Uloží hodnoty pro kombinace variant a kritérií.
    
    Args:
        analyza: Instance analýzy
        hodnoty: Dictionary obsahující matici hodnot
    """
    if not isinstance(hodnoty, dict) or 'matice_hodnoty' not in hodnoty:
        raise ValueError("Neplatný formát dat pro hodnoty")
        
    for klic, hodnota in hodnoty['matice_hodnoty'].items():
        try:
            id_varianty, id_kriteria = klic.split('_')
            
            varianta = app_tables.varianta.get(
                analyza=analyza,
                nazev_varianty=id_varianty
            )
            kriterium = app_tables.kriterium.get(
                analyza=analyza,
                nazev_kriteria=id_kriteria
            )
            
            if varianta and kriterium:
                try:
                    if isinstance(hodnota, str):
                        hodnota = hodnota.replace(',', '.')
                    hodnota_float = float(hodnota)
                    app_tables.hodnota.add_row(
                        analyza=analyza,
                        varianta=varianta,
                        kriterium=kriterium,
                        hodnota=hodnota_float
                    )
                except (ValueError, TypeError):
                    raise ValueError(
                        Konstanty.ZPRAVY_CHYB['NEPLATNA_HODNOTA'].format(id_varianty, id_kriteria)
                    )
        except Exception as e:
            raise ValueError(f"Chyba při ukládání hodnoty: {str(e)}")

# =============== Veřejné serverové funkce ===============

@anvil.server.callable
def pridej_analyzu(nazev: str, popis: str, zvolena_metoda: str) -> str:
    """
    Vytvoří novou analýzu.
    
    Args:
        nazev: Název nové analýzy
        popis: Popis analýzy
        zvolena_metoda: Typ zvolené metody pro analýzu
        
    Returns:
        str: ID nově vytvořené analýzy
        
    Raises:
        ValueError: Pokud vytvoření selže nebo data nejsou validní
    """
    uzivatel = anvil.users.get_user()
    if not uzivatel:
        raise ValueError(Konstanty.ZPRAVY_CHYB['NEZNAMY_UZIVATEL'])

    validuj_nazev_analyzy(nazev)
    
    try:
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
def nacti_analyzu(analyza_id: str) -> Dict:
    """
    Načte detaily konkrétní analýzy.
    
    Args:
        analyza_id: ID požadované analýzy
        
    Returns:
        Dict: Základní údaje o analýze
    """
    try:
        analyza = app_tables.analyza.get_by_id(analyza_id)
        if not analyza:
            raise ValueError(Konstanty.ZPRAVY_CHYB['ANALYZA_NEEXISTUJE'].format(analyza_id))
            
        return {
            'nazev': analyza['nazev'],
            'popis': analyza['popis'],
            'zvolena_metoda': analyza['zvolena_metoda'],
            'datum_vytvoreni': analyza['datum_vytvoreni']
        }
    except Exception as e:
        logging.error(f"Chyba při načítání analýzy {analyza_id}: {str(e)}")
        raise

@anvil.server.callable
def nacti_analyzy_uzivatele() -> List[Any]:
    """
    Načte seznam analýz přihlášeného uživatele.
    
    Returns:
        List[Any]: Seznam analýz s jejich základními údaji
    """
    uzivatel = anvil.users.get_user()
    if not uzivatel:
        return []
        
    try:
        return list(app_tables.analyza.search(
            tables.order_by("datum_vytvoreni", ascending=False),
            uzivatel=uzivatel
        ))
    except Exception as e:
        logging.error(f"Chyba při načítání analýz uživatele: {str(e)}")
        return []


@anvil.server.callable
def nacti_kriteria(analyza_id: str) -> List[Dict]:
    """
    Načte kritéria pro danou analýzu.
    
    Args:
        analyza_id: ID analýzy
        
    Returns:
        List[Dict]: Seznam kritérií a jejich vlastností
    """
    try:
        analyza = app_tables.analyza.get_by_id(analyza_id)
        if analyza:
            kriteria = list(app_tables.kriterium.search(analyza=analyza))
            return [{
                'nazev_kriteria': k['nazev_kriteria'],
                'typ': k['typ'],
                'vaha': float(k['vaha'])
            } for k in kriteria]
        return []
    except Exception as e:
        logging.error(f"Chyba při načítání kritérií pro analýzu {analyza_id}: {str(e)}")
        raise

@anvil.server.callable
def nacti_varianty(analyza_id: str) -> List[Dict]:
    """
    Načte varianty pro danou analýzu.
    
    Args:
        analyza_id: ID analýzy
        
    Returns:
        List[Dict]: Seznam variant a jejich vlastností
    """
    try:
        analyza = app_tables.analyza.get_by_id(analyza_id)
        if analyza:
            varianty = list(app_tables.varianta.search(analyza=analyza))
            return [{
                'nazev_varianty': v['nazev_varianty'],
                'popis_varianty': v['popis_varianty']
            } for v in varianty]
        return []
    except Exception as e:
        logging.error(f"Chyba při načítání variant pro analýzu {analyza_id}: {str(e)}")
        raise

@anvil.server.callable
def nacti_hodnoty(analyza_id: str) -> Dict:
    """
    Načte matici hodnot pro danou analýzu.
    
    Args:
        analyza_id: ID analýzy
        
    Returns:
        Dict: Dictionary obsahující matici hodnot
    """
    try:
        analyza = app_tables.analyza.get_by_id(analyza_id)
        hodnoty = {'matice_hodnoty': {}}
        
        if analyza:
            for h in app_tables.hodnota.search(analyza=analyza):
                if h['varianta'] and h['kriterium']:
                    klic = f"{h['varianta']['nazev_varianty']}_{h['kriterium']['nazev_kriteria']}"
                    hodnoty['matice_hodnoty'][klic] = float(h['hodnota'])
        
        return hodnoty
    except Exception as e:
        logging.error(f"Chyba při načítání hodnot pro analýzu {analyza_id}: {str(e)}")
        raise

@anvil.server.callable
def uprav_analyzu(analyza_id: str, nazev: str, popis: str, zvolena_metoda: str) -> None:
    """
    Upraví základní údaje analýzy.
    
    Args:
        analyza_id: ID analýzy
        nazev: Nový název
        popis: Nový popis
        zvolena_metoda: Nová zvolená metoda
    """
    try:
        analyza = app_tables.analyza.get_by_id(analyza_id)
        if not analyza:
            raise ValueError(Konstanty.ZPRAVY_CHYB['ANALYZA_NEEXISTUJE'].format(analyza_id))
            
        validuj_nazev_analyzy(nazev)
        
        analyza.update(
            nazev=nazev,
            popis=popis,
            zvolena_metoda=zvolena_metoda,
            datum_upravy=datetime.datetime.now()
        )
    except Exception as e:
        logging.error(f"Chyba při úpravě analýzy {analyza_id}: {str(e)}")
        raise

@anvil.server.callable
def uloz_kompletni_analyzu(analyza_id: str, kriteria: List[Dict], 
                          varianty: List[Dict], hodnoty: Dict) -> None:
    """
    Uloží kompletní analýzu včetně všech souvisejících dat.
    
    Args:
        analyza_id: ID analýzy
        kriteria: Seznam kritérií
        varianty: Seznam variant
        hodnoty: Matice hodnot pro varianty a kritéria
    """
    try:
        analyza = app_tables.analyza.get_by_id(analyza_id)
        if not analyza:
            raise ValueError(Konstanty.ZPRAVY_CHYB['ANALYZA_NEEXISTUJE'].format(analyza_id))

        validuj_kriteria(kriteria)
        
        # Smaže existující data
        #smaz_analyzu(analyza_id) <- Asi logický BUG
        # Smaže pouze související data, ne samotnou analýzu
        try:
            # Delete related data first
            for hodnota in app_tables.hodnota.search(analyza=analyza):
                hodnota.delete()
            for varianta in app_tables.varianta.search(analyza=analyza):
                varianta.delete()
            for kriterium in app_tables.kriterium.search(analyza=analyza):
                kriterium.delete()
        except Exception as e:
            logging.error(f"Chyba při mazání souvisejících dat: {str(e)}")
            raise
        
        # Uloží nová data
        _uloz_kriteria(analyza, kriteria)
        _uloz_varianty(analyza, varianty)
        _uloz_hodnoty(analyza, hodnoty)
            
    except Exception as e:
        logging.error(f"Chyba při ukládání analýzy {analyza_id}: {str(e)}")
        raise

@anvil.server.callable
def smaz_analyzu(analyza_id: str) -> None:
    """
    Smaže analýzu a všechna související data.
    
    Args:
        analyza_id: ID analýzy ke smazání
    """
    try:
        analyza = app_tables.analyza.get_by_id(analyza_id)
        if not analyza:
            return
            
        # Nejdřív smaže související data
        for hodnota in app_tables.hodnota.search(analyza=analyza):
            hodnota.delete()
        for varianta in app_tables.varianta.search(analyza=analyza):
            varianta.delete()
        for kriterium in app_tables.kriterium.search(analyza=analyza):
            kriterium.delete()
            
        # Nakonec smaže samotnou analýzu
        analyza.delete()
        
    except Exception as e:
        logging.error(f"Chyba při mazání analýzy {analyza_id}: {str(e)}")
        raise ValueError(Konstanty.ZPRAVY_CHYB['SMAZANI_SELHALO'])

@anvil.server.callable
def set_edit_analyza_id(analyza_id: str) -> None:
    """
    Nastaví ID editované analýzy do session.
    
    Args:
        analyza_id: ID analýzy k editaci
    """
    anvil.server.session['edit_analyza_id'] = analyza_id

@anvil.server.callable
def get_edit_analyza_id() -> Optional[str]:
    """
    Získá ID editované analýzy ze session.
    
    Returns:
        Optional[str]: ID analýzy nebo None
    """
    return anvil.server.session.get('edit_analyza_id')

@anvil.server.callable
def nacti_kompletni_analyzu(analyza_id: str) -> Dict:
    """
    Načte kompletní data analýzy podle zadaného ID.
    Vrací slovník obsahující údaje o samotné analýze a k ní patřící kritéria,
    varianty a hodnoty.

    Args:
        analyza_id: ID analýzy k načtení

    Returns:
        Dict obsahující klíče:
            'analyza': dict s klíči 'id', 'nazev', 'popis', 'zvolena_metoda', 'datum_vytvoreni', 'datum_upravy', 'stav'
            'kriteria': list slovníků s klíči 'nazev_kriteria', 'typ', 'vaha'
            'varianty': list slovníků s klíči 'nazev_varianty', 'popis_varianty'
            'hodnoty': dict, kde 'matice_hodnoty' je dict klíč = "{nazev_varianty}_{nazev_kriteria}", hodnota = float
    """
    analyza = app_tables.analyza.get_by_id(analyza_id)
    if not analyza:
        raise ValueError(Konstanty.ZPRAVY_CHYB['ANALYZA_NEEXISTUJE'].format(analyza_id))

    analyza_data = {
        'id': analyza.get_id(),
        'nazev': analyza['nazev'],
        'popis': analyza['popis'],
        'zvolena_metoda': analyza['zvolena_metoda'],
        'datum_vytvoreni': analyza['datum_vytvoreni'],
        'datum_upravy': analyza['datum_upravy'],
        'stav': analyza['stav']
    }

    # Načtení kritérií
    zaznamy_kriterii = app_tables.kriterium.search(analyza=analyza)
    kriteria = [
        {
            'nazev_kriteria': k['nazev_kriteria'],
            'typ': k['typ'],
            'vaha': float(k['vaha'])
        }
        for k in zaznamy_kriterii
    ]

    # Načtení variant
    zaznamy_variant = app_tables.varianta.search(analyza=analyza)
    varianty = [
        {
            'nazev_varianty': v['nazev_varianty'],
            'popis_varianty': v['popis_varianty']
        }
        for v in zaznamy_variant
    ]

    # Načtení hodnot
    zaznamy_hodnot = app_tables.hodnota.search(analyza=analyza)
    hodnoty = {'matice_hodnoty': {}}
    for h in zaznamy_hodnot:
        if h['varianta'] and h['kriterium']:
            klic = f"{h['varianta']['nazev_varianty']}_{h['kriterium']['nazev_kriteria']}"
            hodnoty['matice_hodnoty'][klic] = float(h['hodnota'])

    return {
        'analyza': analyza_data,
        'kriteria': kriteria,
        'varianty': varianty,
        'hodnoty': hodnoty
    }

@anvil.server.callable
def nacti_vsechny_uzivatele():
    """
    Načte všechny uživatele z databáze.
    
    Returns:
        List[Row]: Seznam uživatelů nebo prázdný seznam při chybě
    """
    try:
        return list(app_tables.users.search())
    except Exception as e:
        logging.error(f"Chyba při načítání uživatelů: {str(e)}")
        raise Exception("Nepodařilo se načíst seznam uživatelů")

@anvil.server.callable
def vrat_pocet_analyz_pro_uzivatele(uzivatel):
  """
  Vrátí počet analýz přidružených k danému uživateli.
  
  Parametry:
      uzivatel: Řádek uživatele z tabulky 'users'
  
  Návratová hodnota:
      Celkový počet analýz, které se vážou k danému uživateli.
  """
  try:
    print(f"Hledám analýzy pro uživatele: {uzivatel['email']}")
    # Převedeme výsledek vyhledávání na list a spočítáme jeho délku
    analyzy = list(app_tables.analyza.search(uzivatel=uzivatel))
    pocet = len(analyzy)
    print(f"Nalezeno analýz: {pocet}")
    return pocet
  except Exception as e:
    print(f"Chyba při načítání počtu analýz: {str(e)}")
    logging.error(f"Chyba při načítání počtu analýz pro uživatele {uzivatel['email']}: {str(e)}")
    return 0

@anvil.server.callable
def nacti_analyzy_uzivatele_admin(email):
    """
    Načte všechny analýzy daného uživatele pro admin rozhraní.
    
    Args:
        email: Email uživatele
        
    Returns:
        List[Row]: Seznam analýz uživatele
    """
    try:
        print(f"Načítám analýzy pro uživatele: {email}")
        # Nejprve získáme správný Row objekt uživatele
        uzivatel = app_tables.users.get(email=email)
        if not uzivatel:
            raise Exception(f"Uživatel {email} nenalezen")
            
        analyzy = app_tables.analyza.search(uzivatel=uzivatel)
        analyzy_list = list(analyzy)
        print(f"Nalezeno {len(analyzy_list)} analýz")
        return analyzy_list
    except Exception as e:
        print(f"Server chyba: {str(e)}")
        logging.error(f"Chyba při načítání analýz uživatele {email}: {str(e)}")
        raise Exception("Nepodařilo se načíst analýzy uživatele")

@anvil.server.callable
def smaz_uzivatele(email):
    """
    Smaže uživatele a všechny jeho analýzy.
    
    Args:
        email: Email uživatele ke smazání
    
    Returns:
        bool: True pokud byl uživatel úspěšně smazán
    """
    try:
        print(f"Mažu uživatele: {email}")
        uzivatel = app_tables.users.get(email=email)

        # Kontrola, zda nejde o aktuálně přihlášeného uživatele
        aktualni_uzivatel = anvil.users.get_user()
        if aktualni_uzivatel and aktualni_uzivatel['email'] == email:
            raise ValueError("Nelze smazat vlastní účet, se kterým jste aktuálně přihlášeni.")
        
        if not uzivatel:
            raise ValueError(f"Uživatel {email} nebyl nalezen")
            
        # Nejprve získáme všechny analýzy uživatele
        analyzy = app_tables.analyza.search(uzivatel=uzivatel)
        
        # Postupně smažeme každou analýzu včetně souvisejících dat
        for analyza in analyzy:
            analyza_id = analyza.get_id()
            try:
                smaz_analyzu(analyza_id)
                print(f"Analýza {analyza_id} smazána")
            except Exception as e:
                print(f"Chyba při mazání analýzy {analyza_id}: {str(e)}")
                # Pokračujeme s dalšími analýzami
        
        # Nakonec smažeme samotného uživatele
        uzivatel.delete()
        print(f"Uživatel {email} úspěšně smazán")
        return True
        
    except Exception as e:
        print(f"Chyba při mazání uživatele: {str(e)}")
        logging.error(f"Chyba při mazání uživatele {email}: {str(e)}")
        raise ValueError(f"Nepodařilo se smazat uživatele: {str(e)}")