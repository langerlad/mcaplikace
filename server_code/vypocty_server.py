import anvil.server

# Důležité importy ze scikit-criteria
from skcriteria.core.objectives import Objective
from skcriteria.core.data import mkdm
from skcriteria.madm.simple import WeightedSum

MIN = Objective.MIN
MAX = Objective.MAX

@anvil.server.callable
def vypocet_normalizace(analyza_data):
    """
    Provede normalizaci analýzy pomocí scikit-criteria (WeightedSum s nastavenou normalizací).
    V tomto příkladu zatím ignorujeme celkové skóre a pořadí, 
    soustředíme se jen na normalizovanou matici.

    Args:
        analyza_data (dict): Data analýzy se strukturou:
            {
              'varianty': [{'nazev_varianty':..., ...}, ...],
              'kriteria': [{'nazev_kriteria':..., 'typ':..., 'vaha':...}, ...],
              'hodnoty': {
                'matice_hodnoty': { 'DodavatelA_Cena': 123, ... }
              }
            }

    Returns:
        dict: Slovník s normalizovanou maticí a dalším infem. Příklad:
        {
            'nazvy_variant': [...],
            'nazvy_kriterii': [...],
            'normalizovana_matice': [[...], [...], ...],  # 2D list
            'zprava': "OK"
        }
    """
    # 1) Načtení a příprava vstupů
    varianty = analyza_data['varianty']   # [{ 'nazev_varianty': 'DodavatelA', ...}, ...]
    kriteria = analyza_data['kriteria']   # [{ 'nazev_kriteria': 'Cena', 'typ': 'min', 'vaha': ...}, ...]
    matice_hodnot = analyza_data['hodnoty']['matice_hodnoty']

    # Názvy pro scikit-criteria
    anames = [v['nazev_varianty'] for v in varianty]
    cnames = [k['nazev_kriteria'] for k in kriteria]

    # Definice cílů (benefit/cost) – v scikit-criteria: 'max' => MAX, 'min' => MIN
    objectives = []
    for k in kriteria:
        if k['typ'].lower() in ("max", "benefit"):
            objectives.append(MAX)
        else:
            objectives.append(MIN)

    # Váhy (pokud je budete chtít i pro finální skóre)
    weights = [float(k['vaha']) for k in kriteria]

    # 2) Sestavení matice (list of lists)
    mtx = []
    for var in varianty:
        row = []
        for krit in kriteria:
            # klíč ve tvaru "DodavatelA_Cena"
            kl = f"{var['nazev_varianty']}_{krit['nazev_kriteria']}"
            hod = matice_hodnot.get(kl, 0)
            row.append(float(hod))
        mtx.append(row)

    # 3) Vytvoření DataMatrix (mkdm)
    data_matrix = mkdm(
        matrix=mtx,
        objectives=objectives,
        weights=weights,
        alternatives=anames,
        criteria=cnames,
    )

    # 4) WeightedSum s určitým typem normalizace
    #    "normalization='minmax'" => min-max normalizace,
    #    "normalization='vector'" => vektorová normalizace atd.
    #    "wnorm='sum'" => normalizace vah. Záleží na vašem záměru.
    decisor = WeightedSum(normalization='minmax', wnorm='sum')

    # 5) Rozhodnutí (proběhne i normalizace)
    result = decisor.decide(data_matrix)

    # 6) Normalizovaná matice se uloží do result.e_.nmtx (numpy array)
    #    Převedeme ji na list of lists, aby se dala poslat klientovi
    normalizovana = result.e_.nmtx.tolist()

    # 7) Vrácení dat klientovi
    return {
        'nazvy_variant': anames,
        'nazvy_kriterii': cnames,
        'normalizovana_matice': normalizovana,
        'zprava': "OK - Normalizace hotová"
    }
