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
    """
    Uloží do DB úplnou definici analýzy:
      - kritéria (kriteria)
      - varianty
      - hodnoty (matice).
    Pracujeme s row_id, abychom správně uměli smazat a upravovat záznamy,
    i když uživatel změní jejich názvy.
    
    Parametry:
      analyza_id ... ID záznamu v tabulce 'analyza'
      kriteria  ... list dictů, např.:
                    [
                      {'id': 'RBy7TJqP2BoiZ2Ok', 'nazev_kriteria': 'Cena', 'typ': 'min', 'vaha': 0.3},
                      {'id': None, 'nazev_kriteria': 'Kvalita', 'typ': 'max', 'vaha': 0.7},
                      ...
                    ]
      varianty  ... list dictů, s klíči 'id', 'nazev_varianty', 'popis_varianty'
      hodnoty   ... list dictů, např.:
                    [
                      {'varianta_id': 'Auto A', 'kriterium_id': 'Cena', 'hodnota': 20000.0},
                      ...
                    ]
                    # Zde je 'varianta_id' = nazev_varianty, 'kriterium_id' = nazev_kriteria
                    # (Pokud byste chtěli i tady row_id, pošlete sem 'var_id', 'krit_id' atd.)
    """
    analyza = app_tables.analyza.get_by_id(analyza_id)
    if not analyza:
        raise Exception(f"Analýza s ID {analyza_id} neexistuje.")

    #############################################
    # 1) ULOŽIT/AKTUALIZOVAT KRITÉRIA
    #############################################
    
    # a) Projdu předané kriteria. Pokud mají 'id', vyhledám záznam v DB a updatuji.
    #    Pokud ne, založím nový řádek (add_row).
    for k in kriteria:
        row_id = k.get("id", None)
        if row_id:
            db_krit = app_tables.kriterium.get_by_id(row_id)
            if db_krit:
                db_krit.update(
                    nazev_kriteria=k["nazev_kriteria"],
                    typ=k["typ"],
                    vaha=k["vaha"]
                )
            else:
                # Nedohledal se záznam s row_id => teoreticky chybové stavy
                # nebo ho prostě přidám jako nový
                new_krit = app_tables.kriterium.add_row(
                    analyza=analyza,
                    nazev_kriteria=k["nazev_kriteria"],
                    typ=k["typ"],
                    vaha=k["vaha"]
                )
                # volitelně: k["id"] = new_krit.get_id()
        else:
            # Nový záznam
            new_krit = app_tables.kriterium.add_row(
                analyza=analyza,
                nazev_kriteria=k["nazev_kriteria"],
                typ=k["typ"],
                vaha=k["vaha"]
            )
            # volitelně: k["id"] = new_krit.get_id()

    # b) Smazat z DB kritéria, která nejsou ve "kriteria"
    #    1. Sestavím množinu ID, která mám v clientském listu
    client_kriteria_ids = {k["id"] for k in kriteria if k.get("id")}
    #    2. Projdu kritéria v DB a co není v client_kriteria_ids, smažu
    for db_k in app_tables.kriterium.search(analyza=analyza):
        if db_k.get_id() not in client_kriteria_ids:
            # Smazat navázané "hodnota" záznamy
            for h in app_tables.hodnota.search(analyza=analyza, kriterium=db_k):
                h.delete()
            # Smazat samotné kritérium
            db_k.delete()

    #############################################
    # 2) ULOŽIT/AKTUALIZOVAT VARIANTY
    #############################################
    
    # a) Projít varianty, update nebo add
    for v in varianty:
        var_id = v.get("id", None)
        if var_id:
            db_var = app_tables.varianta.get_by_id(var_id)
            if db_var:
                db_var.update(
                    nazev_varianty=v["nazev_varianty"],
                    popis_varianty=v["popis_varianty"]
                )
            else:
                new_var = app_tables.varianta.add_row(
                    analyza=analyza,
                    nazev_varianty=v["nazev_varianty"],
                    popis_varianty=v["popis_varianty"]
                )
                # v["id"] = new_var.get_id()  # volitelně
        else:
            new_var = app_tables.varianta.add_row(
                analyza=analyza,
                nazev_varianty=v["nazev_varianty"],
                popis_varianty=v["popis_varianty"]
            )
            # v["id"] = new_var.get_id()

    # b) Smazat z DB varianty, které nejsou v clientském seznamu
    client_varianty_ids = {v["id"] for v in varianty if v.get("id")}
    for db_v in app_tables.varianta.search(analyza=analyza):
        if db_v.get_id() not in client_varianty_ids:
            # Smazat navázané "hodnota"
            for h in app_tables.hodnota.search(analyza=analyza, varianta=db_v):
                h.delete()
            db_v.delete()

    #############################################
    # 3) ULOŽIT/AKTUALIZOVAT HODNOTY
    #############################################
    # Tady můžeme dohledat varianty/kritéria buď přes row_id,
    # nebo (jako zde) přes nazev_varianty + nazev_kriteria.
    
    # Zkompilujeme si dict existujících "hodnota" řádků, klíč = (variant_name, krit_name)
    existing_hodnoty = {}
    for hrow in app_tables.hodnota.search(analyza=analyza):
        var_name = hrow['varianta']['nazev_varianty']
        krit_name = hrow['kriterium']['nazev_kriteria']
        existing_hodnoty[(var_name, krit_name)] = hrow

    # a) Update / add
    for h in hodnoty:
        # variant_name = h['varianta_id']  # např. 'Auto A'
        # kriterium_name = h['kriterium_id'] # např. 'Cena'
        key = (h['varianta_id'], h['kriterium_id'])
        
        # Najdeme variantu a kritérium v DB (dle názvu)
        # (Pokud chcete i pro 'hodnoty' používat row_id, 
        #  musíte posílat do frontendu var_id, krit_id a dohledat get_by_id(var_id).)
        var_db = app_tables.varianta.get(
            analyza=analyza,
            nazev_varianty=h['varianta_id']
        )
        krit_db = app_tables.kriterium.get(
            analyza=analyza,
            nazev_kriteria=h['kriterium_id']
        )
        if key in existing_hodnoty:
            existing_hodnoty[key].update(hodnota=h['hodnota'])
        else:
            # add_row
            app_tables.hodnota.add_row(
                analyza=analyza,
                varianta=var_db,
                kriterium=krit_db,
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
    if not analyza:
        return []
    
    vysledek = []
    for k in app_tables.kriterium.search(analyza=analyza):
        vysledek.append({
            "id": k.get_id(),                 # Unikátní ID z tabulky
            "nazev_kriteria": k["nazev_kriteria"],
            "typ": k["typ"],
            "vaha": k["vaha"]
        })
    return vysledek

@anvil.server.callable
def nacti_varianty(analyza_id):
    analyza = app_tables.analyza.get_by_id(analyza_id)
    if not analyza:
        return []
    
    vysledek = []
    for v in app_tables.varianta.search(analyza=analyza):
        vysledek.append({
            "id": v.get_id(),                 # row_id
            "nazev_varianty": v["nazev_varianty"],
            "popis_varianty": v["popis_varianty"]
        })
    return vysledek

@anvil.server.callable
def nacti_hodnoty(analyza_id):
    analyza = app_tables.analyza.get_by_id(analyza_id)
    if not analyza:
        return {"matice_hodnoty": {}}
    
    hodnoty = {"matice_hodnoty": {}}
    for h in app_tables.hodnota.search(analyza=analyza):
        # tady row_id nepotřebujeme, pokud identifikujeme podle varianty + kritéria
        variant_name = h['varianta']['nazev_varianty']
        kriterium_name = h['kriterium']['nazev_kriteria']
        key = f"{variant_name}_{kriterium_name}"
        hodnoty["matice_hodnoty"][key] = h['hodnota']
    
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