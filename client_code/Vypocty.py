# client_code/Vypocty.py - modul pro sdílené výpočty

import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from . import Spravce_stavu, Utils


def normalizuj_matici_minmax(matice, typy_kriterii, varianty, kriteria):
    """
    Provede min-max normalizaci hodnot matice.
    
    Args:
        matice: 2D list s hodnotami [varianty][kriteria]
        typy_kriterii: List typů kritérií ("max" nebo "min")
        varianty: List názvů variant
        kriteria: List názvů kritérií
    
    Returns:
        dict: Slovník obsahující normalizovanou matici a metadata
    """
    norm_matice = []
    for i in range(len(matice)):
        norm_radek = []
        for j in range(len(matice[0])):
            sloupec = [row[j] for row in matice]
            min_val = min(sloupec)
            max_val = max(sloupec)
            
            if max_val == min_val:
                norm_hodnota = 1.0  # Všechny hodnoty jsou stejné
            else:
                # Pro MIN kritéria obrátíme normalizaci
                if typy_kriterii[j].lower() in ("min", "cost"):
                    norm_hodnota = (max_val - matice[i][j]) / (max_val - min_val)
                else:
                    norm_hodnota = (matice[i][j] - min_val) / (max_val - min_val)
                
            norm_radek.append(norm_hodnota)
        norm_matice.append(norm_radek)
    
    return {
        'nazvy_variant': varianty,
        'nazvy_kriterii': kriteria,
        'normalizovana_matice': norm_matice
    }

def vytvor_hodnoty_matici(analyza_data):
    """
    Vytvoří matici s hodnotami z dat analýzy.
    
    Args:
        analyza_data: Slovník s daty analýzy
    
    Returns:
        tuple: (matice, typy_kriterii, varianty, kriteria)
    """
    varianty = [v['nazev_varianty'] for v in analyza_data['varianty']]
    kriteria = [k['nazev_kriteria'] for k in analyza_data['kriteria']]
    typy_kriterii = [k['typ'] for k in analyza_data['kriteria']]
    
    # Vytvoření původní matice
    matice = []
    for var in analyza_data['varianty']:
        radek = []
        for krit in analyza_data['kriteria']:
            klic = f"{var['nazev_varianty']}_{krit['nazev_kriteria']}"
            hodnota = float(analyza_data['hodnoty']['matice_hodnoty'].get(klic, 0))
            radek.append(hodnota)
        matice.append(radek)
    
    return matice, typy_kriterii, varianty, kriteria

def vypocitej_vazene_hodnoty(matice, vahy):
    """
    Vypočítá vážené hodnoty (váhy × normalizované hodnoty).
    
    Args:
        matice: 2D list normalizovaných hodnot
        vahy: List vah kritérií
    
    Returns:
        2D list vážených hodnot
    """
    vazene_matice = []
    for radek in matice:
        vazene_radek = [hodnota * vahy[i] for i, hodnota in enumerate(radek)]
        vazene_matice.append(vazene_radek)
    return vazene_matice

# Specifické funkce pro jednotlivé metody

def wsm_vypocet(norm_matice, vahy, varianty):
    """
    Provede výpočet metodou WSM (Weighted Sum Model).
    
    Args:
        norm_matice: 2D list normalizovaných hodnot
        vahy: List vah kritérií
        varianty: List názvů variant
    
    Returns:
        dict: Výsledky analýzy metodou WSM
    """
    vazene_hodnoty = vypocitej_vazene_hodnoty(norm_matice, vahy)
    
    # Sečtení řádků (variant) pro získání skóre
    skore = []
    for i, vazene_radek in enumerate(vazene_hodnoty):
        skore.append((varianty[i], sum(vazene_radek)))
    
    # Seřazení podle skóre sestupně
    serazene = sorted(skore, key=lambda x: x[1], reverse=True)
    
    # Vytvoření seznamu výsledků s pořadím
    results = []
    for poradi, (varianta, hodnota) in enumerate(serazene, 1):
        results.append((varianta, poradi, hodnota))
    
    return {
        'results': results,
        'nejlepsi_varianta': results[0][0],
        'nejlepsi_skore': results[0][2],
        'nejhorsi_varianta': results[-1][0],
        'nejhorsi_skore': results[-1][2],
        'rozdil_skore': results[0][2] - results[-1][2]
    }

def priprav_data_z_json(analyza_data):
    """
    Připraví data z JSON struktury pro výpočty.
    
    Args:
        analyza_data: Slovník s daty analýzy v novém formátu
        
    Returns:
        tuple: (matice, typy_kriterii, varianty, kriteria, vahy)
    """
    try:
        # Získání seznamu kritérií a jejich typů
        kriteria_dict = analyza_data.get('kriteria', {})
        kriteria = list(kriteria_dict.keys())
        typy_kriterii = [kriteria_dict[k]['typ'] for k in kriteria]
        vahy = [float(kriteria_dict[k]['vaha']) for k in kriteria]
        
        # Získání seznamu variant
        varianty_dict = analyza_data.get('varianty', {})
        varianty = list(varianty_dict.keys())
        
        # Vytvoření matice hodnot
        matice = []
        for var_nazev in varianty:
            var_data = varianty_dict[var_nazev]
            radek = []
            for krit_nazev in kriteria:
                # Získáme hodnotu pro kritérium, výchozí je 0 pokud chybí
                hodnota = 0
                if krit_nazev in var_data:
                    try:
                        hodnota = float(var_data[krit_nazev])
                    except (ValueError, TypeError):
                        hodnota = 0
                radek.append(hodnota)
            matice.append(radek)
            
        return matice, typy_kriterii, varianty, kriteria, vahy
        
    except Exception as e:
        raise ValueError(f"Chyba při přípravě dat pro výpočet: {str(e)}")

def vypocitej_analyzu_citlivosti(norm_matice, vahy, varianty, kriteria, metoda="wsm", typy_kriterii=None, vyber_kriteria=0, pocet_kroku=9):
    """
    Provede analýzu citlivosti změnou váhy vybraného kritéria.
    Podporuje metody WSM, WPM a TOPSIS.
    
    Args:
        norm_matice: 2D list - pro WSM/TOPSIS normalizované hodnoty, pro WPM původní hodnoty
        vahy: List vah kritérií
        varianty: List názvů variant
        kriteria: List názvů kritérií
        metoda: Metoda analýzy ("wsm", "wpm" nebo "topsis")
        typy_kriterii: List typů kritérií (povinný pro WPM)
        vyber_kriteria: Index kritéria, jehož váha se bude měnit (výchozí je první kritérium)
        pocet_kroku: Počet kroků při změně váhy
        
    Returns:
        dict: Výsledky analýzy citlivosti
    """
    try:
        # Kontrola vstupních dat
        if not kriteria or len(kriteria) == 0:
            raise ValueError("Seznam kritérií je prázdný")
            
        if not varianty or len(varianty) == 0:
            raise ValueError("Seznam variant je prázdný")
            
        if not vahy or len(vahy) != len(kriteria):
            raise ValueError(f"Seznam vah má nesprávnou délku: {len(vahy) if vahy else 0}, očekáváno: {len(kriteria)}")
            
        # Kontrola matice a jejích rozměrů
        if not norm_matice or len(norm_matice) == 0:
            raise ValueError("Matice hodnot je prázdná")
            
        for i, radek in enumerate(norm_matice):
            if len(radek) != len(kriteria):
                raise ValueError(f"Řádek {i} matice má nesprávnou délku: {len(radek)}, očekáváno: {len(kriteria)}")
                
        # Kontrola indexu vybraného kritéria
        if vyber_kriteria < 0 or vyber_kriteria >= len(kriteria):
            vyber_kriteria = 0
            
        # Pro WPM je nutné mít typy kritérií
        if metoda.lower() == "wpm":
            if not typy_kriterii or len(typy_kriterii) != len(kriteria):
                raise ValueError("Pro metodu WPM je nutné specifikovat typy kritérií")
        
        # Vytvoření rozsahu vah pro analýzu citlivosti
        vahy_rozsah = []
        for i in range(pocet_kroku):
            # Váha od 0.1 do 0.9
            vahy_rozsah.append(0.1 + (0.8 * i / (pocet_kroku - 1)))
        
        citlivost_skore = []    # Bude obsahovat skóre pro každou kombinaci váhy a varianty
        citlivost_poradi = []   # Bude obsahovat pořadí pro každou kombinaci váhy a varianty
        
        # Pro každou váhu v rozsahu
        for vaha in vahy_rozsah:
            # Vytvoření nových vah
            nove_vahy = vahy.copy()
            nove_vahy[vyber_kriteria] = vaha
            
            # Přepočítání vah zbývajících kritérií proporcionálně
            zbyvajici_vaha = 1 - vaha
            
            suma_zbylych_vah = sum([nove_vahy[i] for i in range(len(nove_vahy)) if i != vyber_kriteria])
            if suma_zbylych_vah > 0:
                for i in range(len(nove_vahy)):
                    if i != vyber_kriteria:
                        nove_vahy[i] = (nove_vahy[i] / suma_zbylych_vah) * zbyvajici_vaha
            
            # Výpočet nových skóre podle metody
            if metoda.lower() == "wsm":
                # WSM metoda - sčítání vážených hodnot
                skore_variant = []
                for i in range(len(varianty)):
                    skore = 0
                    for j in range(len(kriteria)):
                        skore += norm_matice[i][j] * nove_vahy[j]
                    skore_variant.append(skore)
            
            elif metoda.lower() == "wpm":
                # WPM metoda - násobení hodnot umocněných na váhy
                skore_variant = []
                for i in range(len(varianty)):
                    skore = 1.0  # Inicializace na 1 pro násobení
                    for j in range(len(kriteria)):
                        hodnota = norm_matice[i][j]
                        
                        # Kontrola, že hodnoty nejsou nulové nebo záporné
                        if hodnota <= 0:
                            hodnota = 0.001  # Malá kladná hodnota
                        
                        # Pro minimalizační kritéria používáme 1/hodnota
                        if typy_kriterii[j].lower() in ("min", "cost"):
                            hodnota = 1 / hodnota
                        
                        # Umocníme hodnotu na váhu a vynásobíme dosavadní skóre
                        skore *= hodnota ** nove_vahy[j]
                        
                    skore_variant.append(skore)
                    
            elif metoda.lower() == "topsis":
                # TOPSIS metoda - výpočet relativní blízkosti k ideálnímu řešení
                skore_variant = []
                
                # Výpočet vážené normalizované matice
                vazena_matice = []
                for i in range(len(varianty)):
                    radek = []
                    for j in range(len(kriteria)):
                        radek.append(norm_matice[i][j] * nove_vahy[j])
                    vazena_matice.append(radek)
                
                # Výpočet ideálního a anti-ideálního řešení
                ideal = []
                anti_ideal = []
                for j in range(len(kriteria)):
                    sloupec = [vazena_matice[i][j] for i in range(len(varianty))]
                    ideal.append(max(sloupec))
                    anti_ideal.append(min(sloupec))
                
                # Výpočet vzdáleností a relativní blízkosti
                for i in range(len(varianty)):
                    sum_ideal = 0
                    sum_anti_ideal = 0
                    for j in range(len(kriteria)):
                        sum_ideal += (vazena_matice[i][j] - ideal[j]) ** 2
                        sum_anti_ideal += (vazena_matice[i][j] - anti_ideal[j]) ** 2
                    
                    dist_ideal = sum_ideal ** 0.5
                    dist_anti_ideal = sum_anti_ideal ** 0.5
                    
                    # Výpočet relativní blízkosti
                    if dist_ideal + dist_anti_ideal == 0:
                        relativni_blizkost = 0
                    else:
                        relativni_blizkost = dist_anti_ideal / (dist_ideal + dist_anti_ideal)
                    
                    skore_variant.append(relativni_blizkost)
            else:
                raise ValueError(f"Nepodporovaná metoda analýzy: {metoda}")
            
            # Určení pořadí variant pro tyto váhy
            serazene_indexy = sorted(range(len(skore_variant)), 
                                   key=lambda k: skore_variant[k], 
                                   reverse=True)
            poradi_variant = [0] * len(varianty)
            for poradi, idx in enumerate(serazene_indexy, 1):
                poradi_variant[idx] = poradi
            
            citlivost_skore.append(skore_variant)
            citlivost_poradi.append(poradi_variant)
        
        return {
            'vahy_rozsah': vahy_rozsah,
            'citlivost_skore': citlivost_skore,
            'citlivost_poradi': citlivost_poradi,
            'zvolene_kriterium': kriteria[vyber_kriteria],
            'zvolene_kriterium_index': vyber_kriteria
        }
    except Exception as e:
        raise ValueError(f"Chyba při výpočtu analýzy citlivosti: {str(e)}")

def topsis_vypocet(matice, vahy, varianty, kriteria, typy_kriterii):
    """
    Vypočítá výsledky metodou TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution).
    Používá normalizaci pomocí Euklidovské normy.
    
    Args:
        matice: 2D list původních (nenormalizovaných) hodnot
        vahy: List vah kritérií
        varianty: List názvů variant
        kriteria: List názvů kritérií
        typy_kriterii: List typů kritérií ("max" nebo "min")
    
    Returns:
        dict: Výsledky analýzy metodou TOPSIS
    """
    try:
        # 1. Vektorizace rozhodovací matice (normalizace pomocí Euklidovské normy)
        norm_matice = []
        for i in range(len(varianty)):
            radek = []
            for j in range(len(kriteria)):
                # Vypočítáme Euklidovskou normu pro každé kritérium
                sloupec = [matice[k][j] for k in range(len(varianty))]
                norma = (sum(x**2 for x in sloupec)) ** 0.5
                
                # Normalizace hodnoty
                hodnota = matice[i][j] / norma if norma != 0 else 0
                radek.append(hodnota)
            norm_matice.append(radek)
        
        # 2. Výpočet vážené normalizované matice
        vazena_matice = []
        for i in range(len(varianty)):
            radek = []
            for j in range(len(kriteria)):
                radek.append(norm_matice[i][j] * vahy[j])
            vazena_matice.append(radek)
        
        # 3. Určení ideálního a anti-ideálního řešení
        ideal = []
        anti_ideal = []
        for j in range(len(kriteria)):
            sloupec = [vazena_matice[i][j] for i in range(len(varianty))]
            
            if typy_kriterii[j].lower() in ("max", "benefit"):
                ideal.append(max(sloupec))
                anti_ideal.append(min(sloupec))
            else:  # min kritéria
                ideal.append(min(sloupec))
                anti_ideal.append(max(sloupec))
        
        # 4. Výpočet vzdáleností od ideálního a anti-ideálního řešení
        dist_ideal = []
        dist_anti_ideal = []
        for i in range(len(varianty)):
            sum_ideal = 0
            sum_anti_ideal = 0
            for j in range(len(kriteria)):
                sum_ideal += (vazena_matice[i][j] - ideal[j]) ** 2
                sum_anti_ideal += (vazena_matice[i][j] - anti_ideal[j]) ** 2
            dist_ideal.append(sum_ideal ** 0.5)
            dist_anti_ideal.append(sum_anti_ideal ** 0.5)
        
        # 5. Výpočet relativní blízkosti k ideálnímu řešení
        relativni_blizkost = []
        for i in range(len(varianty)):
            if dist_ideal[i] + dist_anti_ideal[i] == 0:
                relativni_blizkost.append(0)
            else:
                relativni_blizkost.append(dist_anti_ideal[i] / (dist_ideal[i] + dist_anti_ideal[i]))
        
        # Seřazení variant podle blízkosti (sestupně)
        skore = [(varianty[i], relativni_blizkost[i]) for i in range(len(varianty))]
        serazene = sorted(skore, key=lambda x: x[1], reverse=True)
        
        # Vytvoření seznamu výsledků s pořadím
        results = []
        for poradi, (varianta, hodnota) in enumerate(serazene, 1):
            results.append((varianta, poradi, hodnota))
        
        return {
            'results': results,
            'nejlepsi_varianta': results[0][0],
            'nejlepsi_skore': results[0][2],
            'nejhorsi_varianta': results[-1][0],
            'nejhorsi_skore': results[-1][2],
            'norm_matice': norm_matice,
            'vazena_matice': vazena_matice,
            'ideal': ideal,
            'anti_ideal': anti_ideal,
            'dist_ideal': dist_ideal,
            'dist_anti_ideal': dist_anti_ideal,
            'relativni_blizkost': relativni_blizkost
        }
    except Exception as e:
        raise ValueError(f"Chyba při výpočtu TOPSIS: {str(e)}")

def wpm_vypocet(matice, vahy, typy_kriterii, varianty, kriteria):
    """
    Vypočítá výsledky metodou WPM (Weighted Product Model).
    
    Args:
        matice: 2D list původních hodnot
        vahy: List vah kritérií
        typy_kriterii: List typů kritérií ("max" nebo "min")
        varianty: List názvů variant
        kriteria: List názvů kritérií
    
    Returns:
        dict: Výsledky analýzy metodou WPM
    """
    try:
        # Pro WPM používáme přímo původní hodnoty, nikoliv normalizované
        # Inicializace výsledných hodnot na 1 pro násobení
        skore = [1.0] * len(varianty)
        
        for i in range(len(varianty)):
            for j in range(len(kriteria)):
                hodnota = matice[i][j]
                
                # Kontrola, že hodnoty nejsou nulové nebo záporné
                if hodnota <= 0:
                    hodnota = 0.001  # Malá kladná hodnota
                
                # Pro minimalizační kritéria používáme 1/hodnota
                if typy_kriterii[j].lower() in ("min", "cost"):
                    hodnota = 1 / hodnota
                
                # Umocníme hodnotu na váhu a vynásobíme dosavadní skóre
                skore[i] *= hodnota ** vahy[j]
        
        # Seřazení variant podle skóre (sestupně)
        skore_varianty = [(varianty[i], skore[i]) for i in range(len(varianty))]
        serazene = sorted(skore_varianty, key=lambda x: x[1], reverse=True)
        
        # Vytvoření seznamu výsledků s pořadím
        results = []
        for poradi, (varianta, hodnota) in enumerate(serazene, 1):
            results.append((varianta, poradi, hodnota))
        
        return {
            'results': results,
            'nejlepsi_varianta': results[0][0],
            'nejlepsi_skore': results[0][2],
            'nejhorsi_varianta': results[-1][0],
            'nejhorsi_skore': results[-1][2],
            'rozdil_skore': results[0][2] - results[-1][2] if len(results) > 1 else 0
        }
    except Exception as e:
        raise ValueError(f"Chyba při výpočtu WPM: {str(e)}")

# Doplnění modulu Vypocty.py o centralizovanou funkci pro výpočty WSM


def validuj_vstupni_data_analyzy(analyza_data):
    """
    Validuje vstupní data analýzy před výpočtem.
    
    Args:
        analyza_data: Slovník s daty analýzy
        
    Returns:
        tuple: (je_validni, chybova_zprava)
    """
    # Kontrola povinných klíčů
    if not isinstance(analyza_data, dict):
        return False, "Data analýzy musí být slovník"
    
    if not all(key in analyza_data for key in ["kriteria", "varianty"]):
        return False, "Data analýzy musí obsahovat 'kriteria' a 'varianty'"
    
    # Kontrola kritérií
    if not analyza_data["kriteria"]:
        return False, "Analýza musí obsahovat alespoň jedno kritérium"
    
    # Kontrola variant
    if not analyza_data["varianty"]:
        return False, "Analýza musí obsahovat alespoň jednu variantu"
    
    # Kontrola vah kritérií
    vahy = [float(k_data['vaha']) for k_data in analyza_data["kriteria"].values()]
    soucet_vah = sum(vahy)
    if abs(soucet_vah - 1.0) > 0.001:
        return False, f"Součet vah musí být 1.0 (aktuálně: {soucet_vah:.3f})"
    
    # Kontrola hodnot variant
    for var_nazev, var_data in analyza_data["varianty"].items():
        for krit_nazev in analyza_data["kriteria"].keys():
            if krit_nazev not in var_data and krit_nazev != "popis_varianty":
                return False, f"Varianta '{var_nazev}' nemá hodnotu pro kritérium '{krit_nazev}'"
            elif krit_nazev in var_data and krit_nazev != "popis_varianty":
                # Kontrola, že hodnota je číslo
                try:
                    float(var_data[krit_nazev])
                except (ValueError, TypeError):
                    return False, f"Hodnota pro variantu '{var_nazev}', kritérium '{krit_nazev}' musí být číslo"
    
    return True, ""

def vypocitej_analyzu(analyza_data, metoda="wsm"):
    """
    Obecná funkce pro výpočet libovolné metody vícekriteriální analýzy.
    
    Args:
        analyza_data: Slovník s daty analýzy v JSON formátu
        metoda: Kód metody analýzy ('wsm', 'wpm', 'topsis', 'electre', 'mabac')
        
    Returns:
        dict: Výsledky analýzy ve standardizovaném formátu
        
    Raises:
        ValueError: Pokud metoda není podporována
    """
    metoda = metoda.lower()
    
    if metoda == "wsm":
        return vypocitej_wsm_analyzu(analyza_data)
    elif metoda == "wpm":
        return vypocitej_wpm_analyzu(analyza_data)
    elif metoda == "topsis":
        return vypocitej_topsis_analyzu(analyza_data)
    elif metoda == "electre":
        return vypocitej_electre_analyzu(analyza_data)
    elif metoda == "mabac":
        # Zde by byla implementace pro MABAC
        raise ValueError("Metoda MABAC není v této verzi implementována")
    else:
        raise ValueError(f"Nepodporovaná metoda analýzy: {metoda}")
      
def vypocitej_wsm_analyzu(analyza_data):
    """
    Centralizovaná funkce pro výpočet WSM analýzy z dat.
    Provádí všechny kroky WSM analýzy a vrací strukturovaný výsledek.
    
    Args:
        analyza_data: Slovník s daty analýzy
        
    Returns:
        dict: Strukturovaný výsledek s normalizovanou maticí, váženými hodnotami a výsledky
        
    Raises:
        ValueError: Pokud data nejsou validní nebo nelze provést výpočet
    """
    try:
        # Kontrola validity dat
        je_validni, chyba = validuj_vstupni_data_analyzy(analyza_data)
        if not je_validni:
            raise ValueError(f"Neplatná vstupní data: {chyba}")
            
        # 1. Příprava dat z JSON formátu
        matice, typy_kriterii, varianty, kriteria, vahy = priprav_data_z_json(analyza_data)
        
        # 2. Normalizace matice pomocí min-max metody
        norm_vysledky = normalizuj_matici_minmax(matice, typy_kriterii, varianty, kriteria)
        
        # 3. Výpočet vážených hodnot
        vazene_matice = vypocitej_vazene_hodnoty(
            norm_vysledky['normalizovana_matice'], 
            vahy
        )
        
        # 4. Výpočet WSM výsledků
        wsm_vysledky = wsm_vypocet(
            norm_vysledky['normalizovana_matice'], 
            vahy, 
            varianty
        )
        
        # 5. Sestavení strukturovaného výsledku
        vysledek = {
            'norm_vysledky': norm_vysledky,
            'vazene_matice': vazene_matice,
            'vahy': vahy,
            'wsm_vysledky': wsm_vysledky,
            'matice': matice,
            'typy_kriterii': typy_kriterii,
            'metoda': 'WSM',
            'popis_metody': 'Weighted Sum Model'
        }
        
        return vysledek
        
    except Exception as e:
        raise ValueError(f"Chyba při výpočtu WSM analýzy: {str(e)}")

def vypocitej_wpm_analyzu(analyza_data):
    """
    Centralizovaná funkce pro výpočet WPM analýzy z dat.
    Provádí všechny kroky WPM analýzy a vrací strukturovaný výsledek.
    
    Args:
        analyza_data: Slovník s daty analýzy
        
    Returns:
        dict: Strukturovaný výsledek s normalizovanou maticí, produktovými příspěvky a výsledky
        
    Raises:
        ValueError: Pokud data nejsou validní nebo nelze provést výpočet
    """
    try:
        # Kontrola validity dat
        je_validni, chyba = validuj_vstupni_data_analyzy(analyza_data)
        if not je_validni:
            raise ValueError(f"Neplatná vstupní data: {chyba}")
            
        # 1. Příprava dat z JSON formátu
        matice, typy_kriterii, varianty, kriteria, vahy = priprav_data_z_json(analyza_data)
        
        # 2. Normalizace matice pomocí min-max metody pro vizualizaci
        # (pro samotný výpočet WPM není normalizace nutná,
        # ale pro konzistenci s WSM ji zahrnujeme do výstupu)
        norm_vysledky = normalizuj_matici_minmax(matice, typy_kriterii, varianty, kriteria)
        
        # 3. Výpočet WPM výsledků
        wpm_vysledky = wpm_vypocet(
            matice, 
            vahy, 
            typy_kriterii, 
            varianty,
            kriteria
        )
        
        # 4. Výpočet produktového příspěvku (pro vizualizaci)
        produktovy_prispevek = vypocitej_produktovy_prispevek(matice, vahy, typy_kriterii)
        
        # 5. Výpočet matice poměrů variant
        pomery_variant = vypocitej_matici_pomeru_variant(matice, vahy, typy_kriterii)
        
        # 6. Sestavení strukturovaného výsledku
        vysledek = {
            'norm_vysledky': norm_vysledky,
            'vahy': vahy,
            'wpm_vysledky': wpm_vysledky,
            'matice': matice,
            'typy_kriterii': typy_kriterii,
            'produktovy_prispevek': produktovy_prispevek,
            'pomery_variant': pomery_variant,  # Přidáno
            'metoda': 'WPM',
            'popis_metody': 'Weighted Product Model'
        }
        
        return vysledek
        
    except Exception as e:
        raise ValueError(f"Chyba při výpočtu WPM analýzy: {str(e)}")

def vypocitej_produktovy_prispevek(matice, vahy, typy_kriterii):
    """
    Vypočítá příspěvek jednotlivých kritérií pro WPM jako matici umocněných hodnot.
    Pro vizualizaci WPM, kde se používá násobení místo sčítání.
    
    Args:
        matice: 2D list původních hodnot [varianty][kriteria]
        vahy: List vah kritérií
        typy_kriterii: List typů kritérií ("max" nebo "min")
    
    Returns:
        2D list transformovaných hodnot umocněných na váhy
    """
    try:
        produktovy_prispevek = []
        
        for i in range(len(matice)):
            radek = []
            for j in range(len(matice[0])):
                hodnota = matice[i][j]
                
                # Kontrola, že hodnoty nejsou nulové nebo záporné
                if hodnota <= 0:
                    hodnota = 0.001  # Malá kladná hodnota
                
                # Pro minimalizační kritéria používáme 1/hodnota
                if typy_kriterii[j].lower() in ("min", "cost"):
                    hodnota = 1 / hodnota
                
                # Umocníme hodnotu na váhu a uložíme
                prispevek = hodnota ** vahy[j]
                radek.append(prispevek)
                
            produktovy_prispevek.append(radek)
            
        return produktovy_prispevek
        
    except Exception as e:
        raise ValueError(f"Chyba při výpočtu produktového příspěvku: {str(e)}")

def vypocitej_matici_pomeru_variant(matice, vahy, typy_kriterii):
    """
    Vypočítá matici poměrů variant pro metodu WPM.
    Pro každý pár variant (A_i, A_j) vypočítá poměr R(A_i/A_j).
    
    Args:
        matice: 2D list původních hodnot [varianty][kriteria]
        vahy: List vah kritérií
        typy_kriterii: List typů kritérií ("max" nebo "min")
    
    Returns:
        2D matice poměrů mezi variantami
    """
    try:
        n_variant = len(matice)
        pomer_matice = []
        
        # Nejprve vypočítáme produktové skóre pro každou variantu
        produkty_variant = []
        for i in range(n_variant):
            produkt = 1.0
            for j in range(len(vahy)):
                hodnota = matice[i][j]
                
                # Kontrola, že hodnoty nejsou nulové nebo záporné
                if hodnota <= 0:
                    hodnota = 0.001  # Malá kladná hodnota
                
                # Pro minimalizační kritéria používáme 1/hodnota
                if typy_kriterii[j].lower() in ("min", "cost"):
                    hodnota = 1 / hodnota
                
                # Umocníme hodnotu na váhu a vynásobíme dosavadní produkt
                produkt *= hodnota ** vahy[j]
            
            produkty_variant.append(produkt)
        
        # Nyní vypočítáme matici poměrů
        for i in range(n_variant):
            radek = []
            for j in range(n_variant):
                # Poměr variant i a j
                if produkty_variant[j] == 0:
                    pomer = float('inf')  # Zabránění dělení nulou
                else:
                    pomer = produkty_variant[i] / produkty_variant[j]
                radek.append(pomer)
            
            pomer_matice.append(radek)
            
        return pomer_matice
        
    except Exception as e:
        raise ValueError(f"Chyba při výpočtu matice poměrů variant: {str(e)}")

def vypocitej_topsis_analyzu(analyza_data):
    """
    Centralizovaná funkce pro výpočet TOPSIS analýzy z dat.
    Provádí všechny kroky TOPSIS analýzy a vrací strukturovaný výsledek.
    
    Args:
        analyza_data: Slovník s daty analýzy
        
    Returns:
        dict: Strukturovaný výsledek s normalizovanou maticí, vzdálenostmi a výsledky
        
    Raises:
        ValueError: Pokud data nejsou validní nebo nelze provést výpočet
    """
    try:
        # Kontrola validity dat
        je_validni, chyba = validuj_vstupni_data_analyzy(analyza_data)
        if not je_validni:
            raise ValueError(f"Neplatná vstupní data: {chyba}")
            
        # 1. Příprava dat z JSON formátu
        matice, typy_kriterii, varianty, kriteria, vahy = priprav_data_z_json(analyza_data)
        
        # 2. Pro TOPSIS používáme původní matici a normalizujeme ji v samotné metodě TOPSIS
        # Pro kompatibilitu s ostatními funkcemi vytvoříme také min-max normalizovanou matici
        norm_vysledky = normalizuj_matici_minmax(matice, typy_kriterii, varianty, kriteria)
        
        # 3. Výpočet TOPSIS výsledků - předáváme původní matici, ne normalizovanou
        topsis_vysledky = topsis_vypocet(
            matice, 
            vahy, 
            varianty,
            kriteria,
            typy_kriterii
        )

        # 4. Sestavení strukturovaného výsledku
        vysledek = {
            'norm_vysledky': norm_vysledky,  # Min-max normalizace pro kompatibilitu
            'vahy': vahy,
            'topsis_vysledky': topsis_vysledky,  # Obsahuje výsledky s Euklidovskou normalizací
            'matice': matice,
            'typy_kriterii': typy_kriterii,
            'metoda': 'TOPSIS',
            'popis_metody': 'Technique for Order of Preference by Similarity to Ideal Solution'
        }
        
        return vysledek
        
    except Exception as e:
        raise ValueError(f"Chyba při výpočtu TOPSIS analýzy: {str(e)}")

def vypocitej_electre_analyzu(analyza_data):
    """
    Centralizovaná funkce pro výpočet ELECTRE analýzy z dat.
    Provádí všechny kroky ELECTRE analýzy a vrací strukturovaný výsledek.
    
    Args:
        analyza_data: Slovník s daty analýzy
        
    Returns:
        dict: Strukturovaný výsledek s maticemi souhlasu, nesouhlasu a výsledky
        
    Raises:
        ValueError: Pokud data nejsou validní nebo nelze provést výpočet
    """
    try:
        # Kontrola validity dat
        je_validni, chyba = validuj_vstupni_data_analyzy(analyza_data)
        if not je_validni:
            raise ValueError(f"Neplatná vstupní data: {chyba}")
            
        # 1. Příprava dat z JSON formátu
        matice, typy_kriterii, varianty, kriteria, vahy = priprav_data_z_json(analyza_data)
        
        # 2. Získání parametrů ELECTRE z nastavení uživatele
        from . import Spravce_stavu
        spravce = Spravce_stavu.Spravce_stavu()
        electre_params = spravce.ziskej_nastaveni_electre()
        index_souhlasu = electre_params['index_souhlasu'] 
        index_nesouhlasu = electre_params['index_nesouhlasu']
        
        # Přidejme kontrolní výpis
        Utils.zapsat_info(f"Použity parametry ELECTRE: souhlas={index_souhlasu}, nesouhlas={index_nesouhlasu}")
        
        # 3. Normalizace matice pomocí min-max metody pro další výpočty
        norm_vysledky = normalizuj_matici_minmax(matice, typy_kriterii, varianty, kriteria)
        norm_matice = norm_vysledky['normalizovana_matice']
        
        # 4. Výpočet ELECTRE
        # 4.1 Výpočet matice souhlasu (concordance matrix)
        concordance_matrix = vypocitej_concordance_matrix(norm_matice, vahy, len(varianty))
        
        # 4.2 Výpočet matice nesouhlasu (discordance matrix)
        discordance_matrix = vypocitej_discordance_matrix(norm_matice, len(varianty))
        
        # 4.3 Výpočet matice převahy (outranking matrix)
        outranking_matrix = vypocitej_outranking_matrix(concordance_matrix, discordance_matrix, 
                                                       index_souhlasu, index_nesouhlasu, len(varianty))
        
        # 4.4 Výpočet Net Flow pro každou variantu
        net_flows = vypocitej_net_flows(outranking_matrix, varianty)
        
        # 4.5 Seřazení variant podle Net Flow
        results = []
        for i, (varianta, net_flow) in enumerate(net_flows):
            results.append((varianta, i+1, net_flow))
        
        # Najdeme nejlepší a nejhorší variantu
        nejlepsi_var = results[0][0]
        nejhorsi_var = results[-1][0]
        nejlepsi_score = results[0][2]
        nejhorsi_score = results[-1][2]
        
        # 5. Sestavení strukturovaného výsledku
        electre_vysledky = {
            'results': results,
            'nejlepsi_varianta': nejlepsi_var,
            'nejhorsi_varianta': nejhorsi_var,
            'nejlepsi_skore': nejlepsi_score,
            'nejhorsi_skore': nejhorsi_score,
            'concordance_matrix': concordance_matrix,
            'discordance_matrix': discordance_matrix,
            'outranking_matrix': outranking_matrix,
            'index_souhlasu': index_souhlasu,
            'index_nesouhlasu': index_nesouhlasu
        }
        
        vysledek = {
            'norm_vysledky': norm_vysledky,
            'vahy': vahy,
            'electre_vysledky': electre_vysledky,
            'matice': matice,
            'typy_kriterii': typy_kriterii,
            'parametry': {
                'index_souhlasu': index_souhlasu,
                'index_nesouhlasu': index_nesouhlasu
            },
            'metoda': 'ELECTRE',
            'popis_metody': 'Elimination Et Choix Traduisant la Réalité'
        }
        
        return vysledek
        
    except Exception as e:
        raise ValueError(f"Chyba při výpočtu ELECTRE analýzy: {str(e)}")

def vypocitej_concordance_matrix(norm_matice, vahy, pocet_variant):
    """
    Vypočítá matici souhlasu (concordance matrix) pro metodu ELECTRE.
    
    Args:
        norm_matice: Normalizovaná matice hodnot
        vahy: Seznam vah kritérií
        pocet_variant: Počet variant v analýze
        
    Returns:
        2D list: Matice souhlasu
    """
    # Inicializace matice souhlasu
    concordance_matrix = [[0 for _ in range(pocet_variant)] for _ in range(pocet_variant)]
    
    # Pro každou dvojici variant i a j
    for i in range(pocet_variant):
        for j in range(pocet_variant):
            if i != j:  # Vynecháme diagonálu
                # Souhlasná množina - kritéria, ve kterých je varianta i alespoň tak dobrá jako j
                concordance_sum = 0
                
                for k in range(len(vahy)):
                    # Pokud je varianta i alespoň tak dobrá jako j v kritériu k
                    if norm_matice[i][k] >= norm_matice[j][k]:
                        concordance_sum += vahy[k]
                
                concordance_matrix[i][j] = concordance_sum
    
    return concordance_matrix

def vypocitej_discordance_matrix(norm_matice, pocet_variant):
    """
    Vypočítá matici nesouhlasu (discordance matrix) pro metodu ELECTRE.
    
    Args:
        norm_matice: Normalizovaná matice hodnot
        pocet_variant: Počet variant v analýze
        
    Returns:
        2D list: Matice nesouhlasu
    """
    # Inicializace matice nesouhlasu
    discordance_matrix = [[0 for _ in range(pocet_variant)] for _ in range(pocet_variant)]
    
    # Pro každou dvojici variant i a j
    for i in range(pocet_variant):
        for j in range(pocet_variant):
            if i != j:  # Vynecháme diagonálu
                # Nesouhlasná množina - maximální normalizovaný rozdíl ve prospěch j nad i
                max_diff = 0
                
                for k in range(len(norm_matice[0])):
                    # Rozdíl mezi j a i v kritériu k (pokud j je lepší než i)
                    diff = max(0, norm_matice[j][k] - norm_matice[i][k])
                    max_diff = max(max_diff, diff)
                
                # Maximální možný rozdíl v normalizované matici je 1
                discordance_matrix[i][j] = max_diff
    
    return discordance_matrix

def vypocitej_outranking_matrix(concordance_matrix, discordance_matrix, index_souhlasu, index_nesouhlasu, pocet_variant):
    """
    Vypočítá matici převahy (outranking matrix) pro metodu ELECTRE.
    
    Args:
        concordance_matrix: Matice souhlasu
        discordance_matrix: Matice nesouhlasu
        index_souhlasu: Prahová hodnota indexu souhlasu
        index_nesouhlasu: Prahová hodnota indexu nesouhlasu
        pocet_variant: Počet variant v analýze
        
    Returns:
        2D list: Binární matice převahy (0/1)
    """
    # Inicializace matice převahy
    outranking_matrix = [[0 for _ in range(pocet_variant)] for _ in range(pocet_variant)]
    
    # Pro každou dvojici variant i a j
    for i in range(pocet_variant):
        for j in range(pocet_variant):
            if i != j:  # Vynecháme diagonálu
                # Varianta i převyšuje variantu j, pokud:
                # 1. Index souhlasu je větší nebo roven prahu
                # 2. Index nesouhlasu je menší nebo roven prahu
                if (concordance_matrix[i][j] >= index_souhlasu and 
                    discordance_matrix[i][j] <= index_nesouhlasu):
                    outranking_matrix[i][j] = 1
    
    return outranking_matrix

def vypocitej_net_flows(outranking_matrix, varianty):
    """
    Vypočítá Net Flow pro každou variantu na základě matice převahy.
    
    Args:
        outranking_matrix: Binární matice převahy
        varianty: Seznam názvů variant
        
    Returns:
        list: Seznam dvojic (varianta, net_flow) seřazený sestupně podle net_flow
    """
    pocet_variant = len(varianty)
    net_flows = []
    
    for i in range(pocet_variant):
        # Počet variant, které i převyšuje
        vychazejici = sum(outranking_matrix[i])
        
        # Počet variant, které převyšují i
        prichazejici = sum(outranking_matrix[j][i] for j in range(pocet_variant))
        
        # Net Flow = vychazejici - prichazejici
        net_flow = vychazejici - prichazejici
        net_flows.append((varianty[i], net_flow))
    
    # Seřazení podle net_flow sestupně
    return sorted(net_flows, key=lambda x: x[1], reverse=True)

