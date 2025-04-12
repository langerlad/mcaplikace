import datetime
import logging
import functools
from typing import Dict, List, Optional, Any
import anvil.server
import anvil.users
import anvil.pdf
import io
import xlsxwriter
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil import Media
from . import CRUD_analyzy
from . import Vypocty

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

# =============== Exportní funkce ===============

@anvil.server.callable
@handle_errors
def vytvor_analyzu_pdf(analyza_id, metoda="WSM"):
    """
    Vytvoří PDF s výsledky analýzy s optimalizací pro velké tabulky a grafy.
    
    Args:
        analyza_id: ID analýzy
        metoda: Použitá metoda (WSM, WPM, atd.)
        
    Returns:
        PDF dokument
    """
    analyza_data = CRUD_analyzy.nacti_analyzu(analyza_id)
    
    nazev = analyza_data.get("nazev", "Analyza")
    bezpecny_nazev = nazev.replace(" ", "_").replace("/", "_").replace("\\", "_")
    nazev_souboru = f"{bezpecny_nazev}_{metoda}.pdf"
    
    if metoda == "WSM":
        formular = "Vystup_wsm_komp"
    elif metoda == "WPM":
        formular = "Vystup_wpm_komp"
    elif metoda == "TOPSIS":
        formular = "Vystup_topsis_komp"
    elif metoda == "ELECTRE":
        formular = "Vystup_electre_komp"
    elif metoda == "MABAC":
        formular = "Vystup_mabac_komp"
    else:
        raise ValueError(f"Nepodporovaná metoda: {metoda}")
    
    pdf_renderer = anvil.pdf.PDFRenderer(
        filename=nazev_souboru,
        page_size="A4",
        landscape=False,
    )    
  
    pdf = pdf_renderer.render_form(formular, analyza_id=analyza_id)
    
    return pdf

@anvil.server.callable
@handle_errors
def vytvor_komplexni_excel_report(analyza_id):
    """
    Vytvoří komplexní Excel soubor obsahující výsledky všech metod 
    vícekriteriální analýzy pro porovnání.
    
    Args:
        analyza_id: ID analýzy
        
    Returns:
        Media: Excel dokument
    """
    # Načtení dat analýzy
    analyza_data = CRUD_analyzy.nacti_analyzu(analyza_id)
    
    # Vypočet výsledků všech metod
    vysledky_wsm = Vypocty.vypocitej_wsm_analyzu(analyza_data)
    vysledky_wpm = Vypocty.vypocitej_wpm_analyzu(analyza_data)
    vysledky_topsis = Vypocty.vypocitej_topsis_analyzu(analyza_data)
    vysledky_electre = Vypocty.vypocitej_electre_analyzu(analyza_data)
    vysledky_mabac = Vypocty.vypocitej_mabac_analyzu(analyza_data)
    
    # Vytvoření Excel souboru v paměti
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    
    # Formáty pro Excel
    header_format = workbook.add_format({
        'bold': True, 
        'bg_color': '#D6E4F0', 
        'border': 1,
        'align': 'center'
    })
    
    subheader_format = workbook.add_format({
        'bold': True,
        'bg_color': '#F0F0F0',
        'border': 1
    })
    
    number_format = workbook.add_format({
        'num_format': '0.000',
        'border': 1
    })
    
    percent_format = workbook.add_format({
        'num_format': '0.0%',
        'border': 1
    })
    
    best_format = workbook.add_format({
        'bold': True,
        'bg_color': '#E0F7FA',
        'border': 1,
        'num_format': '0.000'
    })
    
    worst_format = workbook.add_format({
        'bold': True,
        'bg_color': '#FFEBEE',
        'border': 1,
        'num_format': '0.000'
    })
    
    # 1. List: Základní informace o analýze
    zakladni_sheet = workbook.add_worksheet("Základní informace")
    zakladni_sheet.set_column('A:A', 25)
    zakladni_sheet.set_column('B:B', 50)
    
    zakladni_sheet.write(0, 0, "Název analýzy", header_format)
    zakladni_sheet.write(0, 1, analyza_data["nazev"])
    zakladni_sheet.write(1, 0, "Popis", header_format)
    zakladni_sheet.write(1, 1, analyza_data.get("popis_analyzy", ""))
    zakladni_sheet.write(2, 0, "Datum vytvoření", header_format)
    zakladni_sheet.write(2, 1, str(analyza_data.get("datum_vytvoreni", "")))
    zakladni_sheet.write(3, 0, "Datum poslední úpravy", header_format)
    zakladni_sheet.write(3, 1, str(analyza_data.get("datum_upravy", "")))
    
    # 2. List: Kritéria
    kriteria_sheet = workbook.add_worksheet("Kritéria")
    kriteria_sheet.set_column('A:A', 30)
    kriteria_sheet.set_column('B:B', 15)
    kriteria_sheet.set_column('C:C', 15)
    
    kriteria_sheet.write(0, 0, "Název kritéria", header_format)
    kriteria_sheet.write(0, 1, "Typ", header_format)
    kriteria_sheet.write(0, 2, "Váha", header_format)
    
    kriteria = analyza_data["kriteria"]
    row = 1
    for nazev_krit, krit_data in kriteria.items():
        kriteria_sheet.write(row, 0, nazev_krit)
        kriteria_sheet.write(row, 1, krit_data["typ"].upper())
        kriteria_sheet.write(row, 2, float(krit_data["vaha"]), number_format)
        row += 1
    
    # 3. List: Varianty a hodnoty
    hodnoty_sheet = workbook.add_worksheet("Hodnoty")
    hodnoty_sheet.write(0, 0, "Varianta/Kritérium", header_format)
    
    # Záhlaví - názvy kritérií
    col = 1
    for nazev_krit in kriteria.keys():
        hodnoty_sheet.write(0, col, nazev_krit, header_format)
        col += 1
    
    # Hodnoty variant
    varianty = analyza_data["varianty"]
    row = 1
    for nazev_var, var_data in varianty.items():
        hodnoty_sheet.write(row, 0, nazev_var)
        col = 1
        for nazev_krit in kriteria.keys():
            if nazev_krit in var_data and nazev_krit != "popis_varianty":
                hodnoty_sheet.write(row, col, float(var_data[nazev_krit]), number_format)
            col += 1
        row += 1
    
    # 4. List: Srovnání výsledků všech metod
    srovnani_sheet = workbook.add_worksheet("Srovnání metod")
    srovnani_sheet.set_column('A:A', 30)  # Širší sloupec pro názvy variant
    
    srovnani_sheet.write(0, 0, "Varianta", header_format)
    srovnani_sheet.write(0, 1, "WSM pořadí", header_format)
    srovnani_sheet.write(0, 2, "WSM skóre", header_format)
    srovnani_sheet.write(0, 3, "WPM pořadí", header_format)
    srovnani_sheet.write(0, 4, "WPM skóre", header_format)
    srovnani_sheet.write(0, 5, "TOPSIS pořadí", header_format)
    srovnani_sheet.write(0, 6, "TOPSIS skóre", header_format)
    srovnani_sheet.write(0, 7, "ELECTRE pořadí", header_format)
    srovnani_sheet.write(0, 8, "ELECTRE skóre", header_format)
    srovnani_sheet.write(0, 9, "MABAC pořadí", header_format)
    srovnani_sheet.write(0, 10, "MABAC skóre", header_format)
    srovnani_sheet.write(0, 11, "Průměrné pořadí", header_format)
    
    # Vytvoření slovníků pro každou metodu: varianta -> (pořadí, skóre)
    wsm_dict = {var: (poradi, skore) for var, poradi, skore in vysledky_wsm['wsm_vysledky']['results']}
    wpm_dict = {var: (poradi, skore) for var, poradi, skore in vysledky_wpm['wpm_vysledky']['results']}
    topsis_dict = {var: (poradi, skore) for var, poradi, skore in vysledky_topsis['topsis_vysledky']['results']}
    electre_dict = {var: (poradi, skore) for var, poradi, skore in vysledky_electre['electre_vysledky']['results']}
    mabac_dict = {var: (poradi, skore) for var, poradi, skore in vysledky_mabac['mabac_vysledky']['results']}
    
    # Seznam všech variant
    vsechny_varianty = list(varianty.keys())
    
    # Vyplnění dat do srovnávací tabulky
    row = 1
    for varianta in vsechny_varianty:
        prumerne_poradi = 0
        pocet_metod = 0
        
        srovnani_sheet.write(row, 0, varianta)
        
        # WSM
        if varianta in wsm_dict:
            poradi, skore = wsm_dict[varianta]
            srovnani_sheet.write(row, 1, poradi)
            srovnani_sheet.write(row, 2, skore, number_format)
            prumerne_poradi += poradi
            pocet_metod += 1
        
        # WPM
        if varianta in wpm_dict:
            poradi, skore = wpm_dict[varianta]
            srovnani_sheet.write(row, 3, poradi)
            srovnani_sheet.write(row, 4, skore, number_format)
            prumerne_poradi += poradi
            pocet_metod += 1
        
        # TOPSIS
        if varianta in topsis_dict:
            poradi, skore = topsis_dict[varianta]
            srovnani_sheet.write(row, 5, poradi)
            srovnani_sheet.write(row, 6, skore, number_format)
            prumerne_poradi += poradi
            pocet_metod += 1
        
        # ELECTRE
        if varianta in electre_dict:
            poradi, skore = electre_dict[varianta]
            srovnani_sheet.write(row, 7, poradi)
            srovnani_sheet.write(row, 8, skore, number_format)
            prumerne_poradi += poradi
            pocet_metod += 1
        
        # MABAC
        if varianta in mabac_dict:
            poradi, skore = mabac_dict[varianta]
            srovnani_sheet.write(row, 9, poradi)
            srovnani_sheet.write(row, 10, skore, number_format)
            prumerne_poradi += poradi
            pocet_metod += 1
        
        # Průměrné pořadí
        if pocet_metod > 0:
            avg_poradi = prumerne_poradi / pocet_metod
            srovnani_sheet.write(row, 11, avg_poradi, number_format)
        
        row += 1
    
    # 5. Listy pro každou metodu zvlášť - detailní výsledky
    # WSM
    wsm_sheet = workbook.add_worksheet("WSM")
    _vytvor_list_metody(workbook, wsm_sheet, "WSM", vysledky_wsm, header_format, 
                        subheader_format, number_format, best_format, worst_format)
    
    # WPM
    wpm_sheet = workbook.add_worksheet("WPM")
    _vytvor_list_metody(workbook, wpm_sheet, "WPM", vysledky_wpm, header_format, 
                        subheader_format, number_format, best_format, worst_format)
    
    # TOPSIS
    topsis_sheet = workbook.add_worksheet("TOPSIS")
    _vytvor_list_metody(workbook, topsis_sheet, "TOPSIS", vysledky_topsis, header_format, 
                         subheader_format, number_format, best_format, worst_format)
    
    # ELECTRE
    electre_sheet = workbook.add_worksheet("ELECTRE")
    _vytvor_list_metody(workbook, electre_sheet, "ELECTRE", vysledky_electre, header_format, 
                         subheader_format, number_format, best_format, worst_format)
    
    # MABAC
    mabac_sheet = workbook.add_worksheet("MABAC")
    _vytvor_list_metody(workbook, mabac_sheet, "MABAC", vysledky_mabac, header_format, 
                         subheader_format, number_format, best_format, worst_format)
    
    # Nastavení aktivního listu na srovnání
    srovnani_sheet.activate()
    
    # Ukončení a vytvoření souboru
    workbook.close()
    output.seek(0)
    
    # Vytvoření Media objektu pro stažení
    nazev = analyza_data.get("nazev", "Analyza")
    bezpecny_nazev = nazev.replace(" ", "_").replace("/", "_").replace("\\", "_")
    
    excel_media = Media(
        output.getvalue(), 
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        name=f"{bezpecny_nazev}_komplexni_analyza.xlsx"
    )
    
    return excel_media

def _vytvor_list_metody(workbook, sheet, nazev_metody, vysledky, header_format, 
                        subheader_format, number_format, best_format, worst_format):
    """
    Pomocná funkce pro vytvoření listu s výsledky konkrétní metody.
    """
    sheet.set_column('A:A', 5)     # Pořadí
    sheet.set_column('B:B', 30)    # Název varianty
    sheet.set_column('C:C', 15)    # Skóre
    
    # Záhlaví
    sheet.write(0, 0, f"Výsledky metody {nazev_metody}", header_format)
    sheet.merge_range('A1:C1', f"Výsledky metody {nazev_metody}", header_format)
    
    sheet.write(2, 0, "Pořadí", subheader_format)
    sheet.write(2, 1, "Varianta", subheader_format)
    sheet.write(2, 2, "Skóre", subheader_format)
    
    # Určení klíče pro přístup k výsledkům podle metody
    vysledky_klic = f"{nazev_metody.lower()}_vysledky"
    
    # Vyplnění výsledků
    row = 3
    results = vysledky[vysledky_klic]['results']
    nejlepsi_var = vysledky[vysledky_klic]['nejlepsi_varianta']
    nejhorsi_var = vysledky[vysledky_klic]['nejhorsi_varianta']
    
    for varianta, poradi, skore in sorted(results, key=lambda x: x[1]):
        if varianta == nejlepsi_var:
            sheet.write(row, 0, poradi, best_format)
            sheet.write(row, 1, varianta, best_format)
            sheet.write(row, 2, skore, best_format)
        elif varianta == nejhorsi_var:
            sheet.write(row, 0, poradi, worst_format)
            sheet.write(row, 1, varianta, worst_format)
            sheet.write(row, 2, skore, worst_format)
        else:
            sheet.write(row, 0, poradi)
            sheet.write(row, 1, varianta)
            sheet.write(row, 2, skore, number_format)
        row += 1
    
    # Přidání souhrnu
    row += 2
    sheet.write(row, 0, "Souhrn:", subheader_format)
    sheet.merge_range(f'A{row+1}:B{row+1}', "Nejlepší varianta:", subheader_format)
    sheet.write(row+1, 2, nejlepsi_var)
    
    sheet.merge_range(f'A{row+2}:B{row+2}', "Nejlepší skóre:", subheader_format)
    sheet.write(row+2, 2, vysledky[vysledky_klic]['nejlepsi_skore'], number_format)
    
    sheet.merge_range(f'A{row+3}:B{row+3}', "Nejhorší varianta:", subheader_format)
    sheet.write(row+3, 2, nejhorsi_var)
    
    sheet.merge_range(f'A{row+4}:B{row+4}', "Nejhorší skóre:", subheader_format)
    sheet.write(row+4, 2, vysledky[vysledky_klic]['nejhorsi_skore'], number_format)
