import anvil.server
import numpy as np
from skcriteria import DecisionMatrix
from skcriteria.preprocessing import invert_objectives
from skcriteria.preprocessing import scalers
from skcriteria.madm import simple

@anvil.server.callable
def vypocet_normalizace(analyza_data):
    """
    Provede normalizaci dat pomocí scikit-criteria.
    
    Args:
        analyza_data: Slovník obsahující data analýzy
        
    Returns:
        Dict obsahující normalizovanou matici a metadata
    """
    try:
        varianty = analyza_data['varianty']
        kriteria = analyza_data['kriteria']
        matice_hodnot = analyza_data['hodnoty']['matice_hodnoty']

        # Příprava jmen a parametrů
        anames = [v['nazev_varianty'] for v in varianty]
        cnames = [k['nazev_kriteria'] for k in kriteria]
        
        # Určení směru optimalizace
        objectives = np.array(['max' if k['typ'] == 'max' else 'min' for k in kriteria])
        
        # Váhy kritérií
        weights = np.array([float(k['vaha']) for k in kriteria])
        
        # Sestavení matice hodnot
        mtx = []
        for var in varianty:
            row = []
            for krit in kriteria:
                klic = f"{var['nazev_varianty']}_{krit['nazev_kriteria']}"
                hod = float(matice_hodnot.get(klic, 0))
                row.append(hod)
            mtx.append(row)
        
        # Vytvoření rozhodovací matice
        mtx = np.array(mtx)
        dm = DecisionMatrix(
            mtx,  # První parametr je přímo matice
            objectives=objectives,
            weights=weights,
            dtypes=None,
            criteria_names=cnames,
            alternative_names=anames
        )

        # Normalizace pomocí sum scaler
        scaler = scalers.SumScaler()
        normalized_dm = scaler.transform(dm)
        
        # Převod výsledků do formátu pro klienta
        return {
            'puvodni_matice': mtx.tolist(),
            'normalizovana_matice': normalized_dm.values.tolist(),
            'nazvy_variant': anames,
            'nazvy_kriterii': cnames,
            'vahy': weights.tolist(),
            'smery': objectives.tolist()
        }
        
    except Exception as e:
        raise Exception(f"Chyba při normalizaci: {str(e)}")