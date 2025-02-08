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

  # Uložit kritéria
  kriteria_ids = {}
  for k in kriteria:
    kr = app_tables.kriterium.add_row(
      analyza=analyza,
      nazev_kriteria=k['nazev_kriteria'],
      typ=k['typ'],
      vaha=k['vaha']
    )
    kriteria_ids[k['nazev_kriteria']] = kr.get_id()

  # Uložit varianty
  varianty_ids = {}
  for v in varianty:
    var = app_tables.varianta.add_row(
      analyza=analyza,
      nazev_varianty=v['nazev_varianty'],
      popis_varianty=v['popis_varianty']
    )
    varianty_ids[v['nazev_varianty']] = var.get_id()

  # Uložit hodnoty
  for h in hodnoty:
    app_tables.hodnota.add_row(
      analyza=analyza,
      varianta=app_tables.varianta.get_by_id(h['varianta_id']),
      kriterium=app_tables.kriterium.get_by_id(h['kriterium_id']),
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
