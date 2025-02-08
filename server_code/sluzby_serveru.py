# -------------------------------------------------------
# Modul: Sluzby_serveru
# -------------------------------------------------------
import datetime
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server


@anvil.server.callable
def pridej_analyzu(nazev, popis, zvolena_metoda):
  datum_vytvoreni = datetime.datetime.now()
  uzivatel = anvil.users.get_user()
  if not uzivatel:
    raise Exception("Neznámý uživatel nemůže volat metodu pridej_analyzu.")
  
  analyza = app_tables.analyza.add_row(
    nazev=nazev,
    popis=popis,
    datum_vytvoreni=datum_vytvoreni,
    zvolena_metoda=zvolena_metoda,
    uzivatel=uzivatel,
    datum_upravy=None,
    stav=None
  )
  return analyza.get_id()

@anvil.server.callable
def uloz_kompletni_analyzu(analyza_id, kriteria, varianty, hodnoty):
    analyza = app_tables.analyza.get_by_id(analyza_id)
    if not analyza:
        raise Exception("Analýza neexistuje")

    # Keep track of what we want to keep
    new_kriteria_names = {k['nazev_kriteria'] for k in kriteria}
    new_varianty_names = {v['nazev_varianty'] for v in varianty}
    
    # Remove kriteria that are no longer present
    for k in app_tables.kriterium.search(analyza=analyza):
        if k['nazev_kriteria'] not in new_kriteria_names:
            # First remove related hodnoty
            for h in app_tables.hodnota.search(analyza=analyza, kriterium=k):
                h.delete()
            k.delete()

    # Remove varianty that are no longer present
    for v in app_tables.varianta.search(analyza=analyza):
        if v['nazev_varianty'] not in new_varianty_names:
            # First remove related hodnoty
            for h in app_tables.hodnota.search(analyza=analyza, varianta=v):
                h.delete()
            v.delete()

    # Update or add kriteria
    for k in kriteria:
        existing_kriterium = app_tables.kriterium.get(
            analyza=analyza,
            nazev_kriteria=k['nazev_kriteria']
        )
        if existing_kriterium:
            existing_kriterium.update(
                typ=k['typ'],
                vaha=k['vaha']
            )
        else:
            app_tables.kriterium.add_row(
                analyza=analyza,
                nazev_kriteria=k['nazev_kriteria'],
                typ=k['typ'],
                vaha=k['vaha']
            )

    # Update or add varianty
    for v in varianty:
        existing_varianta = app_tables.varianta.get(
            analyza=analyza,
            nazev_varianty=v['nazev_varianty']
        )
        if existing_varianta:
            existing_varianta.update(
                popis_varianty=v['popis_varianty']
            )
        else:
            app_tables.varianta.add_row(
                analyza=analyza,
                nazev_varianty=v['nazev_varianty'],
                popis_varianty=v['popis_varianty']
            )

    # Remove all existing hodnoty and add new ones
    for h in app_tables.hodnota.search(analyza=analyza):
        h.delete()

    # Add new hodnoty
    for h in hodnoty:
        varianta = app_tables.varianta.get(
            analyza=analyza,
            nazev_varianty=h['varianta_id']
        )
        kriterium = app_tables.kriterium.get(
            analyza=analyza,
            nazev_kriteria=h['kriterium_id']
        )
        
        app_tables.hodnota.add_row(
            analyza=analyza,
            varianta=varianta,
            kriterium=kriterium,
            hodnota=h['hodnota']
        )

@anvil.server.callable
def smaz_analyzu(analyza_id):
  analyza = app_tables.analyza.get_by_id(analyza_id)
  if not analyza:
    return
    
  for hodnota in app_tables.hodnota.search(analyza=analyza):
    hodnota.delete()
  for varianta in app_tables.varianta.search(analyza=analyza):
    varianta.delete()
  for kriterium in app_tables.kriterium.search(analyza=analyza):
    kriterium.delete()
  analyza.delete()

@anvil.server.callable
def nacti_analyzy_uzivatele():
  uzivatel = anvil.users.get_user()
  if not uzivatel:
    return []
  return list(app_tables.analyza.search(
    tables.order_by("datum_vytvoreni", ascending=False),
    uzivatel=uzivatel)
             )

@anvil.server.callable
def nacti_analyzu(analyza_id):
    analyza = app_tables.analyza.get_by_id(analyza_id)
    if not analyza:
        raise Exception(f"Analýza s ID {analyza_id} nebyla nalezena")
    return {
        'nazev': analyza['nazev'],
        'popis': analyza['popis'],
        'zvolena_metoda': analyza['zvolena_metoda'],
        'datum_vytvoreni': analyza['datum_vytvoreni']
    }

@anvil.server.callable
def set_edit_analyza_id(analyza_id):
    print(f"Setting edit_analyza_id: {analyza_id}")
    anvil.server.session['edit_analyza_id'] = analyza_id

@anvil.server.callable
def get_edit_analyza_id():
    edit_id = anvil.server.session.get('edit_analyza_id')
    print(f"Getting edit_analyza_id: {edit_id}")
    return edit_id

@anvil.server.callable
def nacti_kriteria(analyza_id):
    analyza = app_tables.analyza.get_by_id(analyza_id)
    if analyza:
        kriteria = list(app_tables.kriterium.search(analyza=analyza))
        return [{
            'nazev_kriteria': k['nazev_kriteria'],
            'typ': k['typ'],
            'vaha': k['vaha']
        } for k in kriteria]
    return []

@anvil.server.callable
def nacti_varianty(analyza_id):
    analyza = app_tables.analyza.get_by_id(analyza_id)
    if analyza:
        varianty = list(app_tables.varianta.search(analyza=analyza))
        return [{
            'nazev_varianty': v['nazev_varianty'],
            'popis_varianty': v['popis_varianty']
        } for v in varianty]
    return []

@anvil.server.callable
def nacti_hodnoty(analyza_id):
    analyza = app_tables.analyza.get_by_id(analyza_id)
    hodnoty = {'matice_hodnoty': {}}
    
    if analyza:
        print("Found analyza:", analyza)
        for h in app_tables.hodnota.search(analyza=analyza):
            print("Checking hodnota:", h)
            if h['varianta'] and h['kriterium']:
                # Create string key instead of tuple
                key = f"{h['varianta']['nazev_varianty']}_{h['kriterium']['nazev_kriteria']}"
                hodnoty['matice_hodnoty'][key] = h['hodnota']
                print(f"Successfully mapped hodnota {h['hodnota']} to {key}")
    
    return hodnoty

@anvil.server.callable
def nacti_hodnotu_pro_variantu_kriterium(analyza_id, nazev_varianty, nazev_kriteria):
    print(f"Loading hodnota for analyza:{analyza_id}, varianta:{nazev_varianty}, kriterium:{nazev_kriteria}")
    
    analyza = app_tables.analyza.get_by_id(analyza_id)
    if not analyza:
        print("Analyza not found")
        return None
        
    # Debug print to see what's in the database
    varianty = list(app_tables.varianta.search(analyza=analyza))
    kriteria = list(app_tables.kriterium.search(analyza=analyza))
    print("Available varianty:", [v['nazev_varianty'] for v in varianty])
    print("Available kriteria:", [k['nazev_kriteria'] for k in kriteria])
    
    varianta = app_tables.varianta.get(
        analyza=analyza,
        nazev_varianty=nazev_varianty
    )
    print(f"Looking for varianta: {nazev_varianty}, found: {varianta}")
    
    kriterium = app_tables.kriterium.get(
        analyza=analyza,
        nazev_kriteria=nazev_kriteria
    )
    print(f"Looking for kriterium: {nazev_kriteria}, found: {kriterium}")
    
    if varianta and kriterium:
        hodnota = app_tables.hodnota.get(
            analyza=analyza,
            varianta=varianta,
            kriterium=kriterium
        )
        print(f"Found hodnota record: {hodnota}")
        if hodnota:
            print(f"Returning hodnota value: {hodnota['hodnota']}")
            return str(hodnota['hodnota'])
    
    return ''

@anvil.server.callable
def uprav_analyzu(analyza_id, nazev, popis, zvolena_metoda):
    analyza = app_tables.analyza.get_by_id(analyza_id)
    if not analyza:
        raise Exception(f"Analýza s ID {analyza_id} neexistuje.")
    analyza.update(
        nazev=nazev,
        popis=popis,
        zvolena_metoda=zvolena_metoda,
        datum_upravy=datetime.datetime.now()
    )