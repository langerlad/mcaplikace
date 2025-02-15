# -------------------------------------------------------
# Modul: Navigace
# Správa navigace v aplikaci a související funkce
# -------------------------------------------------------
import logging
import anvil.server
import anvil.users
from anvil import *
from . import Konstanty, Sprava_dat
from .Administrace_komp import Administrace_komp
from .Analyza_ahp_komp import Analyza_ahp_komp
from .Wizard_komp import Wizard_komp
from .Info_komp import Info_komp
from .Nastaveni_komp import Nastaveni_komp
from .HERO_komp import HERO_komp
from .Dashboard_uziv_komp import Dashboard_uziv_komp
from .Ucet_komp import Ucet_komp
from .Vyber_analyzy_komp import Vyber_analyzy_komp
from .Vystup_saw_komp import Vystup_saw_komp

# Komponenta hlavního okna
komponenta_hl_okna = None

# Konfigurace stránek a navigace
KONFIGURACE_NAVIGACE = {
    'domu': {
        'komponenta': HERO_komp,
        'dashboard_komponenta': Dashboard_uziv_komp,
        'vyzaduje_prihlaseni': False,
        'oznaceni_nav': 'domu',
        'kontrola_rozpracovane': True
    },
    'pridat_analyzu': {
        'komponenta': Vyber_analyzy_komp,
        'vyzaduje_prihlaseni': True,
        'oznaceni_nav': 'pridat',
        'kontrola_rozpracovane': True
    },
    'uprava_analyzy': {
        'komponenta': Wizard_komp,
        'vyzaduje_prihlaseni': True,
        'oznaceni_nav': 'pridat',
        'kontrola_rozpracovane': False,
        'parametry': {'mode': Konstanty.STAV_ANALYZY['UPRAVA']}
    },
    'nastaveni': {
        'komponenta': Nastaveni_komp,
        'vyzaduje_prihlaseni': True,
        'oznaceni_nav': 'nastaveni',
        'kontrola_rozpracovane': True
    },
    'info': {
        'komponenta': Info_komp,
        'vyzaduje_prihlaseni': False,
        'oznaceni_nav': 'info',
        'kontrola_rozpracovane': True
    },
    'administrace': {
        'komponenta': Administrace_komp,
        'vyzaduje_prihlaseni': True,
        'oznaceni_nav': 'administrace',
        'kontrola_rozpracovane': True
    },
    'ucet': {
        'komponenta': Ucet_komp,
        'vyzaduje_prihlaseni': True,
        'oznaceni_nav': 'ucet',
        'kontrola_rozpracovane': True
    },
    'ahp': {
        'komponenta': Analyza_ahp_komp,
        'vyzaduje_prihlaseni': True,
        'oznaceni_nav': None,
        'kontrola_rozpracovane': False
    },
    'saw_vstup': {
        'komponenta': Wizard_komp,
        'vyzaduje_prihlaseni': True,
        'oznaceni_nav': None,
        'kontrola_rozpracovane': False
    },
    'saw_vystup': {
        'komponenta': Vystup_saw_komp,
        'vyzaduje_prihlaseni': True,
        'oznaceni_nav': None,
        'kontrola_rozpracovane': False
    }
}

# Veřejné navigační funkce - nyní jen jednoduché wrappery
def go_domu():
    """Přejde na hlavní stránku."""
    naviguj('domu')

def go_pridat_analyzu():
    """Přejde na stránku pro přidání nové analýzy."""
    naviguj('pridat_analyzu')

def go_upravit_analyzu():
    """Přejde na stránku pro úpravu analýzy."""
    naviguj('uprava_analyzy')

def go_nastaveni():
    """Přejde na stránku nastavení."""
    naviguj('nastaveni')

def go_info():
    """Přejde na informační stránku."""
    naviguj('info')

def go_administrace():
    """Přejde na stránku administrace."""
    naviguj('administrace')

def go_ucet():
    """Přejde na stránku uživatelského účtu."""
    naviguj('ucet')

def go_ahp():
    """Přejde na wizard AHP analýzy."""
    naviguj('ahp')

def go_saw_vstup():
    """Přejde na wizard SAW analýzy."""
    naviguj('saw_vstup')

def go_saw_vystup():
    """Přejde na stránku zpracované SAW analýzy."""
    naviguj('saw_vystup')

def naviguj(stranka, **parametry):
    """
    Centrální navigační funkce.
    
    Args:
        stranka: Identifikátor cílové stránky
        parametry: Volitelné parametry pro komponentu
    """
    try:
        # Získání konfigurace stránky
        konfig = KONFIGURACE_NAVIGACE.get(stranka)
        if not konfig:
            raise ValueError(f"Neznámá stránka: {stranka}")
            
        # Kontrola přihlášení
        if konfig['vyzaduje_prihlaseni']:
            uzivatel = kontrola_prihlaseni()
            if not uzivatel:
                naviguj('domu')
                return
                
        # Kontrola rozpracované analýzy
        if konfig['kontrola_rozpracovane']:
            if not over_a_smaz_rozpracovanou(stranka):
                return
                
        # Nastavení aktivní položky v navigaci
        if konfig['oznaceni_nav']:
            komp = ziskej_komponentu()
            komp.set_active_nav(konfig['oznaceni_nav'])
            
        # Speciální případy
        if stranka == 'domu':
            komp = ziskej_komponentu()
            uzivatel = Sprava_dat.je_prihlasen()
            komponenta = konfig['dashboard_komponenta'] if uzivatel else konfig['komponenta']
            komp.nahraj_komponentu(komponenta())
            return
            
        # Standardní navigace
        komp = ziskej_komponentu()
        # Sloučení výchozích parametrů z konfigurace s předanými parametry
        vsechny_parametry = {**(konfig.get('parametry', {})), **parametry}
        komp.nahraj_komponentu(konfig['komponenta'](**vsechny_parametry))
        
    except Exception as e:
        logging.error(f"Chyba při navigaci na stránku {stranka}: {str(e)}")
        alert("Došlo k chybě při navigaci")
        naviguj('domu')

def ziskej_komponentu():
    """
    Získá instanci hlavní komponenty.
    
    Returns:
        Instance hlavní komponenty
        
    Raises:
        Exception: Pokud není komponenta inicializována
    """
    if komponenta_hl_okna is None:
        raise Exception("Není zvolena žádná komponenta hlavního okna")
    return komponenta_hl_okna
  
def kontrola_prihlaseni():
    """
    Zkontroluje, zda je uživatel přihlášen, případně zobrazí přihlašovací dialog.
    
    Returns:
        Instance přihlášeného uživatele nebo None
    """
    uzivatel = Sprava_dat.je_prihlasen()
    if uzivatel:
        return uzivatel
        
    uzivatel = anvil.users.login_with_form(allow_cancel=True)
    komp = ziskej_komponentu()
    komp.nastav_ucet(uzivatel)
    return uzivatel

def over_a_smaz_rozpracovanou(cilova_stranka):
    """
    Zkontroluje, zda v hlavním panelu není rozdělaná analýza.
    
    Args:
        cilova_stranka: Identifikátor cílové stránky
        
    Returns:
        True pokud lze pokračovat v navigaci, False pokud byla zrušena
    """
    try:
        komp = ziskej_komponentu()
        if hasattr(komp, 'pravy_panel'):
            components = komp.pravy_panel.get_components()
            if components and isinstance(components[0], Wizard_komp):
                wizard = components[0]
                
                # Kontrola nové analýzy
                if wizard.mode == Konstanty.STAV_ANALYZY['NOVY'] and wizard.analyza_id:
                    if confirm(Konstanty.ZPRAVY_CHYB['POTVRZENI_ZRUSENI_NOVE'],
                             dismissible=True,
                             buttons=[("Ano", True), ("Ne", False)]):
                        try:
                            anvil.server.call('smaz_analyzu', wizard.analyza_id)
                        except Exception:
                            logging.error(f"Nepodařilo se smazat analýzu {wizard.analyza_id}")
                        return True
                    return False
                    
                elif wizard.mode == Konstanty.STAV_ANALYZY['UPRAVA'] and wizard.mode != Konstanty.STAV_ANALYZY['ULOZENY']:
                    return confirm(Konstanty.ZPRAVY_CHYB['POTVRZENI_ZRUSENI_UPRAVY'],
                                 dismissible=True,
                                 buttons=[("Ano", True), ("Ne", False)])
        return True
        
    except Exception as e:
        logging.error(f"Chyba při kontrole rozpracované analýzy: {str(e)}")
        return True