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
    
    #
    # 1) ULOŽIT/AKTUALIZOVAT K R I T E R I A
    #
    # - Každé kritérium v argumentu 'kriteria' může mít "id" (původní) nebo nemusí (nové).
    # - Najdeme v DB row podle ID, pokud existuje => update, jinak => add_row
    #
    for k in kriteria:
        row_id = k.get("id", None)
        if row_id:
            # zkus vyhledat existující row
            db_krit = app_tables.kriterium.get_by_id(row_id)
            if db_krit:
                db_krit.update(
                    nazev_kriteria=k["nazev_kriteria"],
                    typ=k["typ"],
                    vaha=k["vaha"]
                )
            else:
                # Může nastat teoreticky, pokud ID není validní v DB:
                novy = app_tables.kriterium.add_row(
                    analyza=analyza,
                    nazev_kriteria=k["nazev_kriteria"],
                    typ=k["typ"],
                    vaha=k["vaha"]
                )
                # Kdybychom chtěli, můžeme zapsat novy.get_id() zpět do k["id"]
        else:
            # Nový záznam (nemá id)
            novy = app_tables.kriterium.add_row(
                analyza=analyza,
                nazev_kriteria=k["nazev_kriteria"],
                typ=k["typ"],
                vaha=k["vaha"]
            )
            # Kdybychom chtěli zpětně doplnit ID do listu kriteria:
            # k["id"] = novy.get_id()
    
    # 1b) SMAZAT KRITÉRIA, KTERÉ UŽIVATEL V CLIENT KÓDU ODSTRANIL
    # (Z DB vybereme všechna kritéria; ta, co nejsou v 'kriteria' seznamu => smazat)
    client_kriterium_ids = {k["id"] for k in kriteria if k.get("id")}
    for db_k in app_tables.kriterium.search(analyza=analyza):
        if db_k.get_id() not in client_kriterium_ids:
            # smazat navázané hodnoty
            for h in app_tables.hodnota.search(analyza=analyza, kriterium=db_k):
                h.delete()
            # pak smazat samo kritérium
            db_k.delete()
    
    #
    # 2) ULOŽIT/AKTUALIZOVAT V A R I A N T Y
    #
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
                novy_var = app_tables.varianta.add_row(
                    analyza=analyza,
                    nazev_varianty=v["nazev_varianty"],
                    popis_varianty=v["popis_varianty"]
                )
        else:
            novy_var = app_tables.varianta.add_row(
                analyza=analyza,
                nazev_varianty=v["nazev_varianty"],
                popis_varianty=v["popis_varianty"]
            )
            # v["id"] = novy_var.get_id()  # Volitelně
    
    # 2b) SMAZAT VARIANTY, KTERÉ NEJSOU UŽ V CLIENT KÓDU
    client_varianta_ids = {v["id"] for v in varianty if v.get("id")}
    for db_v in app_tables.varianta.search(analyza=analyza):
        if db_v.get_id() not in client_varianta_ids:
            # smazat navázané hodnoty
            for h in app_tables.hodnota.search(analyza=analyza, varianta=db_v):
                h.delete()
            # smazat samotnou variantu
            db_v.delete()
    
    #
    # 3) ULOŽIT/AKTUALIZOVAT H O D N O T Y
    #
    # Tady obvykle dohledáváme kritérium a variantu buď
    #   a) přes row_id z frontendu
    #   b) nebo old style: get_by nazev_varianty/nazev_kriteria
    # Lepší je a) (posílat i do "hodnoty" row_id), abychom přejmenování
    # nevyhodnotili jako úplně novou variantu.
    #
    # Zde ponechávám starší styl klíče (varianta_id => nazev_varianty),
    # kritterium_id => nazev_kriteria).
    # Ale ideálně i v 'hodnoty' mějte "var_id" a "krit_id" = row_id.
    
    existing_hodnoty = {
        (h['varianta']['nazev_varianty'], h['kriterium']['nazev_kriteria']): h
        for h in app_tables.hodnota.search(analyza=analyza)
    }
    
    for h in hodnoty:
        # Tady dohledáváme variantu/kriterium spíš podle row_id => if you store them
        # Zde ale děláme starý styl s 'nazev_varianty', 'nazev_kriteria'
        var_db = app_tables.varianta.get(analyza=analyza, nazev_varianty=h['varianta_id'])
        krit_db = app_tables.kriterium.get(analyza=analyza, nazev_kriteria=h['kriterium_id'])
        key = (h['varianta_id'], h['kriterium_id'])
        
        if key in existing_hodnoty:
            existing_hodnoty[key].update(hodnota=h['hodnota'])
        else:
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