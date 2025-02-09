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

# Komponenta hlavního okna
komponenta_hl_okna = None

# =============== Pomocné funkce ===============

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

def set_active_nav(stav):
    """
    Označí aktivní položku v navigaci.
    
    Args:
        stav: Identifikátor aktivní položky
    """
    komp = ziskej_komponentu()
    komp.set_active_nav(stav)

def over_a_smaz_rozpracovanou(cilova_stranka):
    """
    Zkontroluje, zda v pravém panelu není rozdělaná analýza.
    
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
                    
                # Kontrola upravované analýzy
                elif wizard.mode == Konstanty.STAV_ANALYZY['UPRAVA'] and wizard.mode != Konstanty.STAV_ANALYZY['ULOZENY']:
                    return confirm(Konstanty.ZPRAVY_CHYB['POTVRZENI_ZRUSENI_UPRAVY'],
                                 dismissible=True,
                                 buttons=[("Ano", True), ("Ne", False)])
        return True
        
    except Exception as e:
        logging.error(f"Chyba při kontrole rozpracované analýzy: {str(e)}")
        return True

# =============== Navigační funkce ===============

def go_domu():
    """Přejde na hlavní stránku."""
    if over_a_smaz_rozpracovanou("domu"):
        set_active_nav("domu")
        komp = ziskej_komponentu()
        uzivatel = Sprava_dat.je_prihlasen()
        if uzivatel:
            komp.nahraj_komponentu(Dashboard_uziv_komp())
        else:
            komp.nahraj_komponentu(HERO_komp())

def go_pridat_analyzu():
    """Přejde na stránku pro přidání nové analýzy."""
    if over_a_smaz_rozpracovanou("pridat"):
        set_active_nav("pridat")
        uzivatel = kontrola_prihlaseni()
        if not uzivatel:
            go_domu()
            return
        
        komp = ziskej_komponentu()
        komp.nahraj_komponentu(Vyber_analyzy_komp())

def go_upravit_analyzu():
    """Přejde na stránku pro úpravu existující analýzy."""
    set_active_nav("pridat")
    uzivatel = kontrola_prihlaseni()
    if not uzivatel:
        go_domu()
        return
        
    komp = ziskej_komponentu()
    komp.nahraj_komponentu(Wizard_komp(mode=Konstanty.STAV_ANALYZY['UPRAVA']))

def go_nastaveni():
    """Přejde na stránku nastavení."""
    if over_a_smaz_rozpracovanou("nastaveni"):
        set_active_nav("nastaveni")
        uzivatel = kontrola_prihlaseni()
        if not uzivatel:
            go_domu()
            return
        
        komp = ziskej_komponentu()
        komp.nahraj_komponentu(Nastaveni_komp())

def go_info():
    """Přejde na informační stránku."""
    if over_a_smaz_rozpracovanou("info"):
        set_active_nav("info")
        komp = ziskej_komponentu()
        komp.nahraj_komponentu(Info_komp())

def go_administrace():
    """Přejde na stránku administrace."""
    if over_a_smaz_rozpracovanou("administrace"):
        set_active_nav("administrace")
        uzivatel = kontrola_prihlaseni()
        if not uzivatel:
            go_domu()
            return
        
        komp = ziskej_komponentu()
        komp.nahraj_komponentu(Administrace_komp())

def go_ucet():
    """Přejde na stránku uživatelského účtu."""
    if over_a_smaz_rozpracovanou("ucet"):
        uzivatel = kontrola_prihlaseni()
        if not uzivatel:
            go_domu()
            return
        
        komp = ziskej_komponentu()
        komp.nahraj_komponentu(Ucet_komp())

def go_ahp():
    """Přejde na stránku AHP analýzy."""
    uzivatel = kontrola_prihlaseni()
    if not uzivatel:
        go_domu()
        return
    komp = ziskej_komponentu()
    komp.nahraj_komponentu(Analyza_ahp_komp())

def go_saw():
    """Přejde na stránku SAW analýzy."""
    uzivatel = kontrola_prihlaseni()
    if not uzivatel:
        go_domu()
        return
    komp = ziskej_komponentu()
    komp.nahraj_komponentu(Wizard_komp())