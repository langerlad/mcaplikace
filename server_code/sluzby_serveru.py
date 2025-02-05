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

@anvil.server.callable
def pridej_variantu(analyza_id, nazev_varianty, popis_varianty):
  """Přidá novou variantu do databáze"""
  analyza = app_tables.analyza.get_by_id(analyza_id)

  if not analyza:
    raise ValueError("Analýza s tímto ID neexistuje.")

  app_tables.varianta.add_row(
    analyza=analyza,
    nazev_varianty=nazev_varianty,
    popis_varianty=popis_varianty
  )

@anvil.server.callable
def nacti_varianty(analyza_id):
  """Načte varianty z databáze pro danou analýzu"""
  analyza = app_tables.analyza.get_by_id(analyza_id)
  if analyza:
    return list(app_tables.varianta.search(analyza=analyza))
  return []

@anvil.server.callable
def smazat_variantu(varianta_id):
  """Odstraní variantu z databáze podle jejího ID"""
  varianta = app_tables.varianta.get_by_id(varianta_id)
  if varianta:
    varianta.delete()

@anvil.server.callable
def nacti_existujici_hodnotu(analyza_id, varianta_id, kriterium_id):
    """Načte existující hodnotu pro danou variantu a kritérium"""
    analyza = app_tables.analyza.get_by_id(analyza_id)
    varianta = app_tables.varianta.get_by_id(varianta_id)
    kriterium = app_tables.kriterium.get_by_id(kriterium_id)
    
    # Hledání existující hodnoty
    existujici_hodnota = app_tables.hodnota.get(
        analyza=analyza, 
        varianta=varianta, 
        kriterium=kriterium
    )
    
    # Vrátí první nalezená hodnota nebo None
    return existujici_hodnota['hodnota'] if existujici_hodnota else None

# @anvil.server.callable
# def uloz_hodnoty_matice(analyza_id, hodnoty):
#     print(f"Server received {len(hodnoty)} values")
#     analyza = app_tables.analyza.get_by_id(analyza_id)
    
#     for hodnota_item in hodnoty:
#         print(f"Processing: {hodnota_item}")
#         varianta = app_tables.varianta.get_by_id(hodnota_item['id_varianty'])
#         kriterium = app_tables.kriterium.get_by_id(hodnota_item['id_kriteria'])
        
#         existujici = app_tables.hodnota.get(
#             analyza=analyza, 
#             varianta=varianta, 
#             kriterium=kriterium
#         )
        
#         if existujici:
#             existujici['hodnota'] = hodnota_item['hodnota']
#         else:
#             app_tables.hodnota.add_row(
#                 analyza=analyza,
#                 varianta=varianta,
#                 kriterium=kriterium,
#                 hodnota=hodnota_item['hodnota']
#             )

@anvil.server.callable
def nacti_matice_data(analyza_id):
    analyza = app_tables.analyza.get_by_id(analyza_id)
    varianty = list(app_tables.varianta.search(analyza=analyza))
    kriteria = list(app_tables.kriterium.search(analyza=analyza))
    hodnoty = {(h['varianta'].get_id(), h['kriterium'].get_id()): h['hodnota'] 
               for h in app_tables.hodnota.search(analyza=analyza)}
    
    return [prepare_variant_data(v, kriteria, hodnoty) for v in varianty]

def prepare_variant_data(varianta, kriteria, hodnoty):
    return {
        'nazev_varianty': varianta['nazev_varianty'],
        'id_varianty': varianta.get_id(),
        'kriteria': [{
            'nazev_kriteria': k['nazev_kriteria'],
            'id_kriteria': k.get_id(),
            'hodnota': hodnoty.get((varianta.get_id(), k.get_id()), '')
        } for k in kriteria]
    }

@anvil.server.callable
def uloz_hodnoty_matice(analyza_id, hodnoty):
    analyza = app_tables.analyza.get_by_id(analyza_id)
    for hodnota_item in hodnoty:
        varianta = app_tables.varianta.get_by_id(hodnota_item['id_varianty'])
        kriterium = app_tables.kriterium.get_by_id(hodnota_item['id_kriteria'])
        
        existujici = app_tables.hodnota.get(
            analyza=analyza, 
            varianta=varianta, 
            kriterium=kriterium
        )
        
        if existujici:
            existujici['hodnota'] = hodnota_item['hodnota']
        else:
            app_tables.hodnota.add_row(
                analyza=analyza,
                varianta=varianta,
                kriterium=kriterium,
                hodnota=hodnota_item['hodnota']
            )