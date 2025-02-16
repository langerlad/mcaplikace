import anvil.server
import numpy as np
from skcriteria import DecisionMatrix
from skcriteria.preprocessing import scalers

@anvil.server.callable
def vypocet_normalizace(analyza_data):
    """
    Provede normalizaci dat pomocí scikit-criteria.
    
    Args:
        analyza_data: Slovník obsahující data analýzy s klíči:
            - varianty: list slovníků s 'nazev_varianty' a 'popis_varianty'
            - kriteria: list slovníků s 'nazev_kriteria', 'typ' (max/min) a 'vaha'
            - hodnoty: slovník obsahující 'matice_hodnoty' s klíči ve formátu "varianta_kriterium"
    
    Returns:
        Dict obsahující původní a normalizovanou matici plus metadata
    """
    try:
        # Získání názvů variant a kritérií
        varianty = [v['nazev_varianty'] for v in analyza_data['varianty']]
        kriteria = [k['nazev_kriteria'] for k in analyza_data['kriteria']]
        
        # Směry optimalizace a váhy
        smery = ['max' if k['typ'] == 'max' else 'min' for k in analyza_data['kriteria']]
        vahy = [float(k['vaha']) for k in analyza_data['kriteria']]
        
        # Sestavení matice hodnot
        matice = []
        for var in analyza_data['varianty']:
            radek = []
            for krit in analyza_data['kriteria']:
                klic = f"{var['nazev_varianty']}_{krit['nazev_kriteria']}"
                hodnota = float(analyza_data['hodnoty']['matice_hodnoty'].get(klic, 0))
                radek.append(hodnota)
            matice.append(radek)
        
        # Převod na numpy array
        matice = np.array(matice)
        smery = np.array(smery)
        vahy = np.array(vahy)
        
        # Vytvoření rozhodovací matice
        dm = DecisionMatrix(
            matice,
            smery,
            weights=vahy,
            alternatives=varianty,
            criteria=kriteria
        )
        
        # Normalizace
        scaler = scalers.SumScaler()
        normalized = scaler.transform(dm)
        
        return {
            'puvodni_matice': matice.tolist(),
            'normalizovana_matice': normalized.values.tolist(),
            'nazvy_variant': varianty,
            'nazvy_kriterii': kriteria,
            'vahy': vahy.tolist(),
            'smery': smery.tolist()
        }
        
    except Exception as e:
        raise Exception(f"Chyba při normalizaci: {str(e)}")