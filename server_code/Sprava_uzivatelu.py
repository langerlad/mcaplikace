# -------------------------------------------------------
# Modul: Sprava_uzivatelu
#
# Modul obsahuje funkce pro správu uživatelů a jejich analýz:
# - Správa uživatelských účtů (vytvoření, úprava, mazání)
# - Načítání seznamů analýz pro uživatele
# - Administrativní funkce
# - Pomocné funkce
# -------------------------------------------------------
import datetime
import logging
import functools
from typing import Dict, List, Optional, Any
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

# ============= Konfigurace / konstanty =============

# Seznam emailů, které automaticky získají administrátorská práva při registraci
ADMIN_EMAILY = [
    # Sem přidejte emaily administrátorů
    'demo@ucet.utb',
    'servisni@ucet.utb',
    'langer_l@utb.cz',
    'saur@utb.cz'
]

def nastav_vychozi_nastaveni_uzivatele(uzivatel):
    """
    Nastaví výchozí konfigurační parametry pro nového uživatele.
    
    Args:
        uzivatel: Uživatelský objekt
    """
    # Nastavení výchozích parametrů pro ELECTRE
    uzivatel['electre_index_souhlasu'] = 0.7
    uzivatel['electre_index_nesouhlasu'] = 0.3
    uzivatel['stanoveni_vah'] = 'manual'

# ============= Pomocné funkce pro error handling =============

def zapsat_info(zprava):
    """Pomocná funkce pro serverové logování info zpráv"""
    logging.info(f"[INFO] {zprava}")
    
def zapsat_chybu(zprava):
    """Pomocná funkce pro serverové logování chyb"""
    logging.error(f"[CHYBA] {zprava}")

def handle_errors(func):
    """
    Dekorátor pro jednotné zpracování chyb v serverových funkcích.
    Zachytí výjimky, zaloguje je a přehodí klientovi.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            zprava = f"Chyba v {func.__name__}: {str(e)}"
            zapsat_chybu(zprava)
            raise ValueError(zprava) from e
    return wrapper

#=====================================================================
# FUNKCE PRO VEŘEJNOU REGISTRACI UŽIVATELŮ (z Prihlaseni formuláře)
#=====================================================================

@anvil.server.callable
@handle_errors
def registruj_noveho_uzivatele(email, heslo):
    """
    Registruje nového uživatele v systému.
    Tato funkce je určena pro veřejnou registraci z přihlašovacího formuláře.
    
    Args:
        email: Email nového uživatele
        heslo: Heslo nového uživatele
        
    Returns:
        bool: True pokud byl uživatel úspěšně registrován
    """
    try:
        # Validace emailu
        if not email or '@' not in email:
            raise ValueError("Zadejte platný email")
        
        # Validace hesla
        if not heslo or len(heslo) < 6:
            raise ValueError("Heslo musí mít alespoň 6 znaků")
        
        # Kontrola, zda uživatel s tímto emailem již existuje
        existujici_uzivatel = app_tables.users.get(email=email)
        if existujici_uzivatel:
            raise anvil.users.UserExists("Uživatel s tímto emailem již existuje")
            
        # Vytvoření uživatele
        uzivatel = anvil.users.signup_with_email(email, heslo)
        
        # Nastavení role
        if email.lower() in [e.lower() for e in ADMIN_EMAILY] or not app_tables.users.search():
            # Je v seznamu administrátorů nebo je prvním uživatelem
            uzivatel['role'] = 'admin'
            uzivatel['protected'] = email.lower() in [e.lower() for e in ADMIN_EMAILY]  # Ochrana pro admin účty
            zapsat_info(f"Registrován nový administrátor: {email}")
        else:
            # Běžný uživatel
            uzivatel['role'] = 'uživatel'
            zapsat_info(f"Registrován nový uživatel: {email}")
        
        # Nastavení výchozích parametrů
        nastav_vychozi_nastaveni_uzivatele(uzivatel)
        
        return True
        
    except Exception as e:
        zapsat_chybu(f"Chyba při registraci uživatele: {str(e)}")
        raise

#=====================================================================
# FUNKCE PRO ADMINISTRAČNÍ ROZHRANÍ (z Administrace_komp)
#=====================================================================

@anvil.server.callable
@handle_errors
def vytvor_noveho_uzivatele(email, heslo, je_admin=False):
    """
    Vytvoří nového uživatele z administračního rozhraní.
    Pouze pro administrátory.
    
    Args:
        email: Email uživatele
        heslo: Heslo uživatele
        je_admin: True pokud uživatel má být admin
        
    Returns:
        bool: True pokud byl uživatel úspěšně vytvořen
    """
    try:
        # Kontrola, zda je aktuální uživatel admin
        aktualni_uzivatel = anvil.users.get_user()
        if not aktualni_uzivatel or aktualni_uzivatel['role'] != 'admin':
            raise ValueError("Pouze administrátor může vytvářet nové uživatele")
        
        # Validace emailu
        if not email or '@' not in email:
            raise ValueError("Zadejte platný email")
        
        # Validace hesla
        if not heslo or len(heslo) < 6:
            raise ValueError("Heslo musí mít alespoň 6 znaků")
        
        # Kontrola, zda uživatel s tímto emailem již existuje
        existujici_uzivatel = app_tables.users.get(email=email)
        if existujici_uzivatel:
            raise ValueError("Uživatel s tímto emailem již existuje")

        # Důležité: Uložíme si ID a email aktuálního administrátora, abychom
        # mohli poté ověřit, že nedošlo k omylem k jeho odhlášení nebo změně role
        admin_id = aktualni_uzivatel.get_id()
      
        # Vytvoření uživatele
        uzivatel = anvil.users.signup_with_email(email, heslo)
        
        # Nastavení role
        uzivatel['role'] = 'admin' if je_admin else 'uživatel'
        
        # Nastavení výchozích parametrů
        nastav_vychozi_nastaveni_uzivatele(uzivatel)

        # Ověření, že jsme stále přihlášeni jako původní admin
        aktualni_uzivatel = anvil.users.get_user()
        if not aktualni_uzivatel or aktualni_uzivatel.get_id() != admin_id:
            # Uživatel byl odhlášen nebo změněn - došlo k autorizační chybě
            # Pokusíme se znovu přihlásit jako původní admin
            zapsat_chybu("Uživatel byl odhlášen při vytváření nového účtu. Pokus o obnovení přihlášení.")
            # Zde nemůžeme provést přihlášení, ale můžeme vrátit speciální zprávu
            return {
                "uspech": True,
                "varovani": "Během vytváření účtu došlo k odhlášení. Prosím, přihlaste se znovu."
            }
        
        zapsat_info(f"Administrátor vytvořil nového uživatele: {email}, role: {'admin' if je_admin else 'uživatel'}")
        return True
    except Exception as e:
        zapsat_chybu(f"Chyba při vytváření uživatele: {str(e)}")
        raise ValueError(f"Chyba při vytváření uživatele: {str(e)}")
        
@anvil.server.callable
@handle_errors
def nacti_vsechny_uzivatele():
    """
    Načte všechny uživatele z databáze.
    Pouze pro administrátory.
    
    Returns:
        list: Seznam uživatelů
    """
    try:
        # Kontrola, zda je aktuální uživatel admin
        aktualni_uzivatel = anvil.users.get_user()
        if not aktualni_uzivatel or aktualni_uzivatel['role'] != 'admin':
            raise ValueError("Pouze administrátor může zobrazit seznam uživatelů")
        
        # Načtení všech uživatelů
        uzivatele = list(app_tables.users.search())
        zapsat_info(f"Načteno {len(uzivatele)} uživatelů")
        return uzivatele
    except Exception as e:
        zapsat_chybu(f"Chyba při načítání uživatelů: {str(e)}")
        raise ValueError(f"Chyba při načítání uživatelů: {str(e)}")
        
@anvil.server.callable
@handle_errors
def vrat_pocet_analyz_pro_uzivatele(uzivatel):
    """
    Vrátí počet analýz pro daného uživatele.
    
    Args:
        uzivatel: Uživatelský objekt
        
    Returns:
        int: Počet analýz
    """
    try:
        # Počet analýz podle uživatele
        pocet = len(list(app_tables.analyzy.search(uzivatel=uzivatel)))
        return pocet
    except Exception as e:
        zapsat_chybu(f"Chyba při zjišťování počtu analýz: {str(e)}")
        return 0
        
@anvil.server.callable
@handle_errors
def nacti_analyzy_uzivatele_admin(email):
    """
    Načte analýzy konkrétního uživatele.
    Pouze pro administrátory.
    
    Args:
        email: Email uživatele, jehož analýzy chceme načíst
        
    Returns:
        list: Seznam analýz
    """
    try:
        # Kontrola, zda je aktuální uživatel admin
        aktualni_uzivatel = anvil.users.get_user()
        if not aktualni_uzivatel or aktualni_uzivatel['role'] != 'admin':
            raise ValueError("Pouze administrátor může zobrazit analýzy jiných uživatelů")
        
        # Načtení uživatele podle emailu
        uzivatel = app_tables.users.get(email=email)
        if not uzivatel:
            raise ValueError(f"Uživatel s emailem {email} neexistuje")
        
        # Načtení analýz
        analyzy = list(app_tables.analyzy.search(uzivatel=uzivatel))
        zapsat_info(f"Načteno {len(analyzy)} analýz pro uživatele {email}")
        return analyzy
    except Exception as e:
        zapsat_chybu(f"Chyba při načítání analýz uživatele: {str(e)}")
        raise ValueError(f"Chyba při načítání analýz uživatele: {str(e)}")
        
@anvil.server.callable
@handle_errors
def smaz_uzivatele(email):
    """
    Smaže uživatele a všechny jeho analýzy.
    Pouze pro administrátory.
    
    Args:
        email: Email uživatele, kterého chceme smazat
        
    Returns:
        bool: True pokud byl uživatel úspěšně smazán
    """
    try:
        # Kontrola, zda je aktuální uživatel admin
        aktualni_uzivatel = anvil.users.get_user()
        if not aktualni_uzivatel or aktualni_uzivatel['role'] != 'admin':
            raise ValueError("Pouze administrátor může mazat uživatele")
        
        # Načtení uživatele podle emailu
        uzivatel = app_tables.users.get(email=email)
        if not uzivatel:
            raise ValueError(f"Uživatel s emailem {email} neexistuje")
        
        # Kontrola, zda uživatel nemá speciální ochranu
        if uzivatel.get('protected', False):
            raise ValueError("Tohoto uživatele nelze smazat")
        
        # Smazání analýz uživatele
        analyzy = app_tables.analyzy.search(uzivatel=uzivatel)
        for a in analyzy:
            a.delete()
        zapsat_info(f"Smazány všechny analýzy uživatele {email}")
        
        # Smazání uživatele
        uzivatel.delete()
        zapsat_info(f"Smazán uživatel {email}")
        
        return True
    except Exception as e:
        zapsat_chybu(f"Chyba při mazání uživatele: {str(e)}")
        raise ValueError(f"Chyba při mazání uživatele: {str(e)}")
        
@anvil.server.callable
@handle_errors
def zmenit_roli_uzivatele(email, nova_role):
    """
    Změní roli uživatele.
    Pouze pro administrátory.
    
    Args:
        email: Email uživatele, jehož roli chceme změnit
        nova_role: Nová role (admin/uživatel)
        
    Returns:
        bool: True pokud byla role úspěšně změněna
    """
    try:
        # Kontrola, zda je aktuální uživatel admin
        aktualni_uzivatel = anvil.users.get_user()
        if not aktualni_uzivatel or aktualni_uzivatel['role'] != 'admin':
            raise ValueError("Pouze administrátor může měnit role uživatelů")
        
        # Načtení uživatele podle emailu
        uzivatel = app_tables.users.get(email=email)
        if not uzivatel:
            raise ValueError(f"Uživatel s emailem {email} neexistuje")
        
        # Validace nové role
        if nova_role not in ['admin', 'uživatel']:
            raise ValueError(f"Neplatná role: {nova_role}")
        
        # Kontrola, zda uživatel nemá speciální ochranu
        if uzivatel.get('protected', False) and nova_role != 'admin':
            raise ValueError("Tomuto uživateli nelze odebrat administrátorská práva")
        
        # Změna role
        uzivatel['role'] = nova_role
        zapsat_info(f"Změněna role uživatele {email} na {nova_role}")
        
        return True
    except Exception as e:
        zapsat_chybu(f"Chyba při změně role uživatele: {str(e)}")
        raise ValueError(f"Chyba při změně role uživatele: {str(e)}")

# =============== Správa uživatelských účtů ===============

# @anvil.server.callable
# @handle_errors
# def nacti_vsechny_uzivatele():
#     """
#     Načte všechny uživatele z databáze.
#     Určeno pro administrátory.
    
#     Returns:
#         List[Row]: Seznam uživatelů nebo prázdný seznam při chybě
#     """
#     # Ověření, že volající je admin
#     over_admin_prava()
    
#     try:
#         return list(app_tables.users.search())
#     except Exception as e:
#         zapsat_chybu(f"Chyba při načítání uživatelů: {str(e)}")
#         raise ValueError("Nepodařilo se načíst seznam uživatelů")

# @anvil.server.callable
# @handle_errors
# def vytvor_noveho_uzivatele(email: str, heslo: str):
#     """
#     Vytvoří nového uživatele z administrátorského rozhraní.
    
#     Args:
#         email: Email nového uživatele
#         heslo: Heslo pro nový účet
#         je_admin: True pokud má být uživatel administrátor
    
#     Returns:
#         dict: Informace o vytvořeném uživateli nebo None při chybě
#     """
#     # Ověření, že volající je admin
#     over_admin_prava()
    
#     try:
#         zapsat_info(f"Vytvářím nového uživatele: {email}")

#         # Uložení původního uživatele
#         puvodni_uzivatel = anvil.users.get_user()

#         # Kontrola, zda uživatel již neexistuje
#         existujici = app_tables.users.get(email=email)
#         if existujici:
#             raise ValueError(f"Uživatel s emailem {email} již existuje")
        
#         # Vytvoření uživatele pomocí signup_with_email
#         novy_uzivatel = anvil.users.signup_with_email(email, heslo, remember=False)
        
#         # Nastavení data vytvoření a aktivace účtu
#         novy_uzivatel['signed_up'] = datetime.datetime.now()
#         novy_uzivatel['enabled'] = True
        
#         # Nastavení výchozích hodnot parametrů ELECTRE
#         novy_uzivatel['electre_index_souhlasu'] = 0.7
#         novy_uzivatel['electre_index_nesouhlasu'] = 0.3
        
#         # Nastavení role pokud je výchozí admin
#         if email.lower() in ['servisni_ucet@505.kg', 'saur@utb.cz', 'langer_l@utb.cz', 'demo@ucet.utb', 'demo2@ucet.utb']:
#             novy_uzivatel['role'] = 'admin'
#             zapsat_info(f"Automaticky přidělena admin role uživateli: {email}")
     
#         # Přihlášení zpět jako původní admin
#         if puvodni_uzivatel:
#             anvil.users.force_login(puvodni_uzivatel)
      
#         zapsat_info(f"Uživatel {email} úspěšně vytvořen")
        
#         return {
#             'email': email,
#             'signed_up': novy_uzivatel['signed_up'],
#             'enabled': True,
#             'role': novy_uzivatel.get('role')
#         }
        
#     except Exception as e:
#         zapsat_chybu(f"Chyba při vytváření uživatele {email}: {str(e)}")
#         raise ValueError(f"Nepodařilo se vytvořit uživatele: {str(e)}")

# @anvil.server.callable
# @handle_errors
# def zmenit_roli_uzivatele(email: str, nova_role: str) -> bool:
#     """
#     Změní roli uživatele.
    
#     Args:
#         email: Email uživatele
#         nova_role: Nová role uživatele ('admin' nebo 'uživatel')
    
#     Returns:
#         bool: True pokud byla role úspěšně změněna
#     """
#     # Ověření, že volající je admin
#     over_admin_prava()
    
#     try:
#         zapsat_info(f"Měním roli uživatele {email} na: {nova_role}")
        
#         # Kontrola, zda nejde o aktuálně přihlášeného uživatele
#         aktualni_uzivatel = anvil.users.get_user()
#         if aktualni_uzivatel and aktualni_uzivatel['email'] == email:
#             raise ValueError("Nemůžete měnit roli vlastního účtu.")
        
#         uzivatel = app_tables.users.get(email=email)
        
#         if not uzivatel:
#             raise ValueError(f"Uživatel {email} nebyl nalezen")
            
#         # Kontrola platnosti role
#         if nova_role not in ('admin', 'uživatel'):
#             raise ValueError(f"Neplatná role: {nova_role}")
            
#         # Změna role
#         uzivatel['role'] = nova_role if nova_role == 'admin' else None
        
#         zapsat_info(f"Role uživatele {email} úspěšně změněna na {nova_role}")
#         return True
        
#     except Exception as e:
#         zapsat_chybu(f"Chyba při změně role uživatele {email}: {str(e)}")
#         raise ValueError(f"Nepodařilo se změnit roli uživatele: {str(e)}")

# @anvil.server.callable
# @handle_errors
# def smaz_uzivatele(email: str) -> bool:
#     """
#     Smaže uživatele a všechny jeho analýzy.
    
#     Args:
#         email: Email uživatele ke smazání
    
#     Returns:
#         bool: True pokud byl uživatel úspěšně smazán
#     """
#     # Ověření, že volající je admin
#     over_admin_prava()
    
#     zapsat_info(f"Mažu uživatele: {email}")
    
#     uzivatel = app_tables.users.get(email=email)

#     # Kontrola, zda nejde o aktuálně přihlášeného uživatele
#     aktualni_uzivatel = anvil.users.get_user()
#     if aktualni_uzivatel and aktualni_uzivatel['email'] == email:
#         raise ValueError("Nelze smazat vlastní účet, se kterým jste aktuálně přihlášeni.")
    
#     if not uzivatel:
#         raise ValueError(f"Uživatel {email} nebyl nalezen")
        
#     # Nejprve získáme a smažeme všechny analýzy uživatele
#     analyzy = app_tables.analyzy.search(uzivatel=uzivatel)
#     pocet_analyz = 0
    
#     for analyza in analyzy:
#         try:
#             analyza.delete()
#             pocet_analyz += 1
#         except Exception as e:
#             zapsat_chybu(f"Chyba při mazání analýzy: {str(e)}")
#             # Pokračujeme s dalšími analýzami
    
#     # Nakonec smažeme samotného uživatele
#     uzivatel.delete()
#     zapsat_info(f"Uživatel {email} a {pocet_analyz} analýz úspěšně smazáno")
    
#     return True

# =============== Správa analýz uživatelů ===============

@anvil.server.callable
@handle_errors
def nacti_analyzy_uzivatele(limit: Optional[int] = None, sort_by: str = "datum_vytvoreni") -> List[Dict]:
    """
    Načte seznam analýz přihlášeného uživatele.
    
    Args:
        limit: Maximální počet načtených analýz (volitelný)
        sort_by: Pole pro řazení ("datum_vytvoreni" nebo "datum_upravy")
        
    Returns:
        List[Dict]: Seznam analýz s metadaty
    """
    uzivatel = anvil.users.get_user()
    if not uzivatel:
        return []
        
    try:
        # Načtení analýz uživatele podle požadovaného řazení
        if sort_by == "datum_vytvoreni":
            analyzy = list(app_tables.analyzy.search(
                tables.order_by("datum_vytvoreni", ascending=False),
                uzivatel=uzivatel
            ))
        elif sort_by == "datum_upravy":
            analyzy = list(app_tables.analyzy.search(
                tables.order_by("datum_upravy", ascending=False),
                uzivatel=uzivatel
            ))
        else:
            analyzy = list(app_tables.analyzy.search(
                uzivatel=uzivatel
            ))
            
        # Omezení počtu výsledků, pokud je požadováno
        if limit is not None:
            analyzy = analyzy[:limit]
            
        # Sestavení výstupních dat
        result = []
        for a in analyzy:
            item = {
                "id": a.get_id(),
                "nazev": a["nazev"],
                "datum_vytvoreni": a["datum_vytvoreni"],
                "datum_upravy": a["datum_upravy"],
                "popis": a["data_json"].get("popis", "")
            }
            result.append(item)
            
        return result
        
    except Exception as e:
        zapsat_chybu(f"Chyba při načítání analýz uživatele: {str(e)}")
        return []

# @anvil.server.callable
# @handle_errors
# def nacti_analyzy_uzivatele_admin(email: str, sort_by: str = "datum_vytvoreni") -> List[Dict]:
#     """
#     Načte seznam analýz daného uživatele pro admin rozhraní.
    
#     Args:
#         email: Email uživatele
#         sort_by: Pole pro řazení
        
#     Returns:
#         List[Dict]: Seznam analýz s metadaty
#     """
#     # Ověření, že volající je admin
#     over_admin_prava()
    
#     zapsat_info(f"Načítám analýzy pro uživatele: {email}")
    
#     try:
#         # Nejprve získáme objekt uživatele
#         uzivatel = app_tables.users.get(email=email)
#         if not uzivatel:
#             raise ValueError(f"Uživatel {email} nenalezen")
        
#         # Získání analýz uživatele
#         if sort_by == "datum_vytvoreni":
#             analyzy = list(app_tables.analyzy.search(
#                 tables.order_by("datum_vytvoreni", ascending=False),
#                 uzivatel=uzivatel
#             ))
#         elif sort_by == "datum_upravy":
#             analyzy = list(app_tables.analyzy.search(
#                 tables.order_by("datum_upravy", ascending=False),
#                 uzivatel=uzivatel
#             ))
#         else:
#             analyzy = list(app_tables.analyzy.search(
#                 uzivatel=uzivatel
#             ))
        
#         # Sestavení výstupních dat
#         result = []
#         for a in analyzy:
#             item = {
#                 "id": a.get_id(),
#                 "nazev": a["nazev"],
#                 "datum_vytvoreni": a["datum_vytvoreni"],
#                 "datum_upravy": a["datum_upravy"],
#                 "popis": a["data_json"].get("popis", "")
#             }
#             result.append(item)
        
#         zapsat_info(f"Nalezeno {len(result)} analýz pro uživatele {email}")
#         return result
        
#     except Exception as e:
#         zapsat_chybu(f"Chyba při načítání analýz pro uživatele {email}: {str(e)}")
#         raise ValueError(f"Chyba při načítání analýz: {str(e)}")

# @anvil.server.callable
# @handle_errors
# def vrat_pocet_analyz_pro_uzivatele(uzivatel) -> int:
#     """
#     Vrátí počet analýz přidružených k danému uživateli.
    
#     Args:
#         uzivatel: Řádek uživatele z tabulky 'users'
    
#     Returns:
#         int: Celkový počet analýz, které se vážou k danému uživateli
#     """
#     try:
#         zapsat_info(f"Hledám analýzy pro uživatele: {uzivatel['email']}")
        
#         # Převedeme výsledek vyhledávání na list a spočítáme jeho délku
#         analyzy = list(app_tables.analyzy.search(uzivatel=uzivatel))
#         pocet = len(analyzy)
        
#         zapsat_info(f"Nalezeno analýz: {pocet}")
#         return pocet
        
#     except Exception as e:
#         zapsat_chybu(f"Chyba při načítání počtu analýz pro uživatele {uzivatel['email']}: {str(e)}")
#         return 0

# =============== Administrativní funkce ===============
 
@anvil.server.callable
@handle_errors
def nastavit_roli_po_registraci(email: str) -> bool:
    """
    Kontroluje, zda nově registrovaný uživatel má mít automaticky admin roli
    a nastaví výchozí hodnoty parametrů.
    
    Args:
        email: Email registrovaného uživatele
        
    Returns:
        bool: True pokud byla přidělena role admin
    """
    try:
        # Seznam admin emailů
        admin_emaily = ['servisni_ucet@505.kg','saur@utb.cz','langer_l@utb.cz']
        
        # Získání uživatele podle emailu
        uzivatel = app_tables.users.get(email=email)
        if uzivatel:
            # Nastavení výchozích hodnot parametrů ELECTRE
            uzivatel['electre_index_souhlasu'] = 0.7
            uzivatel['electre_index_nesouhlasu'] = 0.3
            
            # Kontrola, zda email patří mezi admin emaily
            if email.lower() in [admin_email.lower() for admin_email in admin_emaily]:
                uzivatel['role'] = 'admin'
                zapsat_info(f"Automaticky přidělena admin role uživateli: {email}")
                return True
    
    except Exception as e:
        zapsat_chybu(f"Chyba při nastavování role a výchozích hodnot: {str(e)}")
    
    return False

# =============== Pomocné funkce ===============

def over_admin_prava():
    """
    Ověří, zda má přihlášený uživatel administrátorská práva.
    
    Raises:
        ValueError: Pokud uživatel nemá administrátorská práva
    """
    uzivatel = anvil.users.get_user()
    if not uzivatel:
        raise ValueError("Pro tuto operaci musíte být přihlášen.")
    
    # Match the logic in Spravce_stavu.py
    try:
        je_admin = uzivatel['role'] == 'admin'
    except KeyError:
        # Handle case where 'role' key doesn't exist
        je_admin = False
    
    if not je_admin:
        raise ValueError("Pro tuto operaci potřebujete administrátorská práva.")

@anvil.server.callable
@handle_errors
def nacti_uzivatelske_nastaveni():
    """
    Načte nastavení přihlášeného uživatele přímo z databáze.
    
    Returns:
        dict: Slovník s nastaveními uživatele
    """
    # Získání přihlášeného uživatele
    current_user = anvil.users.get_user()
    if not current_user:
        zapsat_info("Funkce vrací None - uživatel není přihlášen")
        return None
    
    try:
        # Získání e-mailu přihlášeného uživatele
        email = current_user['email']
        zapsat_info(f"Přihlášený uživatel: {email}")
        
        # Přímé načtení uživatelského řádku
        user_row = app_tables.users.get(email=email)
        
        if not user_row:
            zapsat_info(f"Nenalezen řádek pro uživatele {email}")
            return None
        
        # Vytvoření slovníku s nastavením - přímý přístup ke sloupcům
        try:
            # Přímý přístup ke sloupcům
            index_souhlasu = user_row['electre_index_souhlasu']
            index_nesouhlasu = user_row['electre_index_nesouhlasu']
            stanoveni_vah = user_row['stanoveni_vah']
            
            zapsat_info(f"Načtené hodnoty přímo z DB: souhlasu={index_souhlasu}, nesouhlasu={index_nesouhlasu}, stanoveni_vah={stanoveni_vah}")

            
            # Sestavení výsledku
            result = {
                'electre_index_souhlasu': float(index_souhlasu) if index_souhlasu is not None else 0.7,
                'electre_index_nesouhlasu': float(index_nesouhlasu) if index_nesouhlasu is not None else 0.3,
                'stanoveni_vah': stanoveni_vah if stanoveni_vah else 'manual'
            }
            
            # Výpis pro kontrolu
            zapsat_info(f"Skutečné hodnoty načtené z DB: {result}")
            return result
            
        except Exception as e:
            zapsat_chybu(f"Chyba při přístupu k sloupcům: {str(e)}")
            return {
                'electre_index_souhlasu': 0.7,
                'electre_index_nesouhlasu': 0.3,
                'stanoveni_vah': 'manual'
            }
    
    except Exception as e:
        zapsat_chybu(f"Chyba při načítání nastavení pro uživatele: {str(e)}")
        return None

@anvil.server.callable
@handle_errors
def uloz_uzivatelske_nastaveni(nastaveni):
    """
    Uloží nastavení přihlášeného uživatele.
    
    Args:
        nastaveni: Slovník s nastaveními uživatele
    
    Returns:
        bool: True pokud bylo nastavení úspěšně uloženo
    """
    uzivatel = anvil.users.get_user()
    if not uzivatel:
        raise ValueError("Pro uložení nastavení musíte být přihlášen.")
    
    try:
        # Explicitně získáme hodnoty a ujistíme se, že se nepoužívají výchozí hodnoty
        index_souhlasu = nastaveni.get('electre_index_souhlasu')
        index_nesouhlasu = nastaveni.get('electre_index_nesouhlasu')
        stanoveni_vah = nastaveni.get('stanoveni_vah')
        
        # Kontrola, zda hodnoty nejsou None
        if index_souhlasu is None:
            raise ValueError("Index souhlasu nesmí být prázdný")
        if index_nesouhlasu is None:
            raise ValueError("Index nesouhlasu nesmí být prázdný")
        
        # Ujistíme se, že hodnoty jsou typu float
        index_souhlasu = float(index_souhlasu)
        index_nesouhlasu = float(index_nesouhlasu)
        uzivatel['stanoveni_vah'] = stanoveni_vah
        
        # Kontrola rozsahu hodnot
        if not (0 <= index_souhlasu <= 1):
            raise ValueError("Index souhlasu musí být mezi 0 a 1")
        if not (0 <= index_nesouhlasu <= 1):
            raise ValueError("Index nesouhlasu musí být mezi 0 a 1")
        
        # Kontrola platnosti metody stanovení vah
        if stanoveni_vah not in ['manual', 'rank', 'ahp', 'entropie']:
            stanoveni_vah = 'manual'  # Pokud hodnota není platná, použijeme výchozí
            
        # Uložení nastavení do tabulky users
        uzivatel['electre_index_souhlasu'] = index_souhlasu
        uzivatel['electre_index_nesouhlasu'] = index_nesouhlasu
        uzivatel['stanoveni_vah'] = stanoveni_vah
        
        zapsat_info(f"Uloženo nastavení pro uživatele {uzivatel['email']}: souhlas={index_souhlasu}, nesouhlas={index_nesouhlasu}, stanoveni_vah={stanoveni_vah}")
        return True
        
    except Exception as e:
        zapsat_chybu(f"Chyba při ukládání nastavení pro uživatele {uzivatel['email']}: {str(e)}")
        raise ValueError(f"Chyba při ukládání nastavení: {str(e)}")
