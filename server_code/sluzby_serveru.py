import datetime
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.

#@anvil.server.callable
# def moje_analyzy():
#   uzivatel = anvil.users.get_user()
#   if not uzivatel:
#     return []

#   soupis_analyz = app_tables.Analyza.search(tables.order_by("datum_vytvoreni", ascending=True), User=uzivatel)

#   return soupis_analyz

@anvil.server.callable
def pridej_analyzu(nazev, popis, zvolena_metoda):
  datum_vytvoreni = datetime.datetime.now()
  uzivatel = anvil.users.get_user()
  datum_upravy = None
  stav = None
  if not uzivatel:
    raise Exception("Neznámý uživatel nemuže volat metodu pridej_analyzu.")
    
  analyza = app_tables.analyza.add_row(nazev=nazev, 
                                      popis=popis, 
                                      datum_vytvoreni=datum_vytvoreni,
                                      zvolena_metoda=zvolena_metoda, 
                                      uzivatel=uzivatel,
                                      datum_upravy=datum_upravy,
                                      stav=stav)

  return analyza.get_id()

@anvil.server.callable
def pridej_kriterium(analyza_id, nazev_kriteria, typ, vaha):
  analyza = app_tables.analyza.get_by_id(analyza_id)

  if not analyza:
        raise ValueError("Analýza s tímto ID neexistuje.")
  
  app_tables.kriterium.add_row(analyza=analyza,
                              nazev_kriteria=nazev_kriteria,
                              typ=typ,
                              vaha=vaha)

@anvil.server.callable
def nacti_kriteria(analyza_id):
    """Načte kritéria z databáze pro danou analýzu"""
    analyza = app_tables.analyza.get_by_id(analyza_id)
    if analyza:
        return list(app_tables.kriterium.search(analyza=analyza))
    return []

@anvil.server.callable
def smazat_kriterium(kriterium_id):
    """Odstraní kritérium z databáze podle jeho row_id"""
    kriterium = app_tables.kriterium.get_by_id(kriterium_id)
    if kriterium:
        kriterium.delete()

@anvil.server.callable
def uprav_kriterium(kriterium_id, updated_data):
    """Aktualizuje existující kritérium v databáze podle jeho ID"""
    kriterium = app_tables.kriterium.get_by_id(kriterium_id)
    if kriterium:
        kriterium.update(
            nazev_kriteria=updated_data['nazev_kriteria'],
            typ=updated_data['typ'],
            vaha=updated_data['vaha']
        )
    else:
        raise Exception("Ops ... kriterium neexistuje")

