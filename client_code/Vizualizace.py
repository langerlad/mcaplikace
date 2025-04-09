# client_code/vizualizace.py
# -------------------------------------------------------
# Modul: vizualizace
# Obsahuje sdílené funkce pro tvorbu grafů a vizualizací
# -------------------------------------------------------

import plotly.graph_objects as go
import math
from . import Utils


def vytvor_sloupovy_graf_vysledku(results, nejlepsi_varianta, nejhorsi_varianta, nazev_metody=""):
    """
    Vytvoří sloupcový graf výsledků analýzy.
    
    Args:
        results: List tuple (varianta, poradi, hodnota)
        nejlepsi_varianta: Název nejlepší varianty
        nejhorsi_varianta: Název nejhorší varianty
        nazev_metody: Název použité metody (pro titulek grafu)
        
    Returns:
        dict: Plotly figure configuration
    """
    try:
        # Příprava dat pro graf
        varianty = []
        skore = []
        colors = []  # Barvy pro sloupce
        
        # Seřazení dat podle skóre (sestupně)
        for varianta, _, hodnota in results:
            varianty.append(varianta)
            skore.append(hodnota)
            # Nejlepší varianta bude mít zelenou, nejhorší červenou
            if varianta == nejlepsi_varianta:
                colors.append('#2ecc71')  # zelená
            elif varianta == nejhorsi_varianta:
                colors.append('#e74c3c')  # červená
            else:
                colors.append('#3498db')  # modrá
        
        # Vytvoření grafu
        fig = {
            'data': [{
                'type': 'bar',
                'x': varianty,
                'y': skore,
                'marker': {
                    'color': colors
                },
                'text': [f'{s:.3f}' for s in skore],  # Zobrazení hodnot nad sloupci
                'textposition': 'auto',
            }],
            'layout': {
                'title': f'Celkové skóre variant{f" ({nazev_metody})" if nazev_metody else ""}',
                'xaxis': {
                    'title': 'Varianty',
                    'tickangle': -45 if len(varianty) > 4 else 0  # Natočení popisků pro lepší čitelnost
                },
                'yaxis': {
                    'title': 'Skóre',
                    'range': [0, max(skore) * 1.1] if skore else [0, 1]  # Trochu místa nad sloupci pro hodnoty
                },
                'showlegend': False,
                'margin': {'t': 50, 'b': 100}  # Větší okraje pro popisky
            }
        }
        
        return fig
    except Exception as e:
        Utils.zapsat_chybu(f"Chyba při vytváření sloupcového grafu: {str(e)}")
        # Vrátíme prázdný graf
        return {
            'data': [],
            'layout': {
                'title': 'Chyba při vytváření grafu'
            }
        }

def vytvor_skladany_sloupovy_graf(varianty, kriteria, vazene_hodnoty, serazene_varianty=None):
    """
    Vytvoří skládaný sloupcový graf zobrazující příspěvek jednotlivých kritérií.
    
    Args:
        varianty: Seznam názvů variant
        kriteria: Seznam názvů kritérií
        vazene_hodnoty: 2D list vážených hodnot [varianty][kriteria]
        serazene_varianty: Seznam variant seřazených podle celkového skóre (volitelný)
            Pokud je zadán, použije se toto pořadí pro zobrazení variant v grafu
        
    Returns:
        dict: Plotly figure configuration
    """
    try:
        # Vytvoření mapování pro získání indexu varianty
        var_to_idx = {var: idx for idx, var in enumerate(varianty)}
        
        # Pokud jsou zadány seřazené varianty, přeuspořádáme data podle nich
        if serazene_varianty:
            # Kontrola, zda jsou v serazene_varianty všechny varianty z původního seznamu
            if set(serazene_varianty) != set(varianty):
                Utils.zapsat_chybu("Seznam seřazených variant neobsahuje stejné varianty jako původní seznam")
                serazene_varianty = None  # Nepoužijeme seřazení při neshodě
        
        # Určení pořadí variant pro graf
        zobrazene_varianty = serazene_varianty if serazene_varianty else varianty
        
        # Vytvoření datových sérií pro každé kritérium
        data = []
        
        # Pro každé kritérium vytvoříme jednu sérii dat
        for j, kriterium in enumerate(kriteria):
            hodnoty_kriteria = []
            
            # Připravíme hodnoty v pořadí podle zobrazených variant
            for var in zobrazene_varianty:
                idx = var_to_idx[var]  # Index varianty v původních datech
                hodnoty_kriteria.append(vazene_hodnoty[idx][j])
            
            data.append({
                'type': 'bar',
                'name': kriterium,
                'x': zobrazene_varianty,
                'y': hodnoty_kriteria,
                'text': [f'{h:.3f}' for h in hodnoty_kriteria],
                'textposition': 'inside',
                'hovertemplate': '%{x}<br>' + f'{kriterium}: ' + '%{y:.3f}<extra></extra>'
            })
            
        # Vytvoření grafu
        fig = {
            'data': data,
            'layout': {
                'title': 'Příspěvek jednotlivých kritérií k celkovému skóre',
                'barmode': 'stack',  # Skládaný sloupcový graf
                'xaxis': {
                    'title': 'Varianty',
                    'tickangle': -45 if len(zobrazene_varianty) > 4 else 0
                },
                'yaxis': {
                    'title': 'Skóre',
                },
                'showlegend': True,
                'legend': {
                    'title': 'Kritéria',
                    'orientation': 'h',  # Horizontální legenda
                    'y': -0.3,  # Umístění pod grafem - více místa
                    'x': 0.5,
                    'xanchor': 'center'
                },
                'margin': {'t': 50, 'b': 180}  # Zvětšený spodní okraj pro legendu
            }
        }
        
        return fig
    except Exception as e:
        Utils.zapsat_chybu(f"Chyba při vytváření skládaného grafu: {str(e)}")
        # Vrátíme prázdný graf
        return {
            'data': [],
            'layout': {
                'title': 'Chyba při vytváření grafu složení skóre'
            }
        }

def vytvor_radar_graf(varianty, kriteria, norm_hodnoty):
    """
    Vytvoří radarový (paprskový) graf zobrazující normalizované hodnoty variant ve všech kritériích.
    
    Args:
        varianty: Seznam názvů variant
        kriteria: Seznam názvů kritérií
        norm_hodnoty: 2D list normalizovaných hodnot [varianty][kriteria]
        
    Returns:
        dict: Plotly figure configuration
    """
    try:
        data = []
        
        # Pro každou variantu vytvoříme jednu sérii dat
        for i, varianta in enumerate(varianty):
            # Pro radarový graf musíme uzavřít křivku tak, že opakujeme první hodnotu na konci
            hodnoty = norm_hodnoty[i] + [norm_hodnoty[i][0]]
            labels = kriteria + [kriteria[0]]
            
            data.append({
                'type': 'scatterpolar',
                'r': hodnoty,
                'theta': labels,
                'fill': 'toself',
                'name': varianta
            })
        
        # Vytvoření grafu
        fig = {
            'data': data,
            'layout': {
                'title': 'Porovnání variant podle normalizovaných hodnot kritérií',
                'polar': {
                    'radialaxis': {
                        'visible': True,
                        'range': [0, 1]
                    }
                },
                'showlegend': True,
                'legend': {
                    'title': 'Varianty',
                    'orientation': 'h',
                    'y': -0.2,
                    'x': 0.5,
                    'xanchor': 'center'
                },
                'margin': {'t': 50, 'b': 100}
            }
        }
        
        return fig
    except Exception as e:
        Utils.zapsat_chybu(f"Chyba při vytváření radarového grafu: {str(e)}")
        # Vrátíme prázdný graf
        return {
            'data': [],
            'layout': {
                'title': 'Chyba při vytváření radarového grafu'
            }
        }

def vytvor_graf_citlivosti_skore(analyza_citlivosti, varianty):
    """
    Vytvoří graf analýzy citlivosti pro celkové skóre.
    
    Args:
        analyza_citlivosti: Výsledky analýzy citlivosti
        varianty: Seznam názvů variant
    
    Returns:
        dict: Plotly figure configuration
    """
    try:
        vahy_rozsah = analyza_citlivosti['vahy_rozsah']
        citlivost_skore = analyza_citlivosti['citlivost_skore']
        zvolene_kriterium = analyza_citlivosti['zvolene_kriterium']
        
        # Vytvoření datových sérií pro každou variantu
        data = []
        
        for i, varianta in enumerate(varianty):
            # Pro každou variantu vytvoříme jednu datovou sérii
            data.append({
                'type': 'scatter',
                'mode': 'lines+markers',
                'name': varianta,
                'x': vahy_rozsah,
                'y': [citlivost_skore[j][i] for j in range(len(vahy_rozsah))],
                'marker': {
                    'size': 8
                }
            })
            
        # Vytvoření grafu
        fig = {
            'data': data,
            'layout': {
                'title': f'Analýza citlivosti - vliv změny váhy kritéria "{zvolene_kriterium}" na celkové skóre',
                'xaxis': {
                    'title': f'Váha kritéria {zvolene_kriterium}',
                    'tickformat': '.1f'
                },
                'yaxis': {
                    'title': 'Celkové skóre',
                },
                'showlegend': True,
                'legend': {
                    'title': 'Varianty',
                    'orientation': 'v',
                },
                'grid': {
                    'rows': 1, 
                    'columns': 1
                },
                'margin': {'t': 50, 'b': 80}
            }
        }
        
        return fig
    except Exception as e:
        Utils.zapsat_chybu(f"Chyba při vytváření grafu citlivosti skóre: {str(e)}")
        # Vrátíme prázdný graf
        return {
            'data': [],
            'layout': {
                'title': 'Chyba při vytváření grafu citlivosti skóre'
            }
        }

def vytvor_graf_citlivosti_poradi(analyza_citlivosti, varianty):
    """
    Vytvoří graf analýzy citlivosti pro pořadí variant.
    
    Args:
        analyza_citlivosti: Výsledky analýzy citlivosti
        varianty: Seznam názvů variant
    
    Returns:
        dict: Plotly figure configuration
    """
    try:
        vahy_rozsah = analyza_citlivosti['vahy_rozsah']
        citlivost_poradi = analyza_citlivosti['citlivost_poradi']
        zvolene_kriterium = analyza_citlivosti['zvolene_kriterium']
        
        # Vytvoření datových sérií pro každou variantu
        data = []
        
        for i, varianta in enumerate(varianty):
            # Pro každou variantu vytvoříme jednu datovou sérii
            data.append({
                'type': 'scatter',
                'mode': 'lines+markers',
                'name': varianta,
                'x': vahy_rozsah,
                'y': [citlivost_poradi[j][i] for j in range(len(vahy_rozsah))],
                'marker': {
                    'size': 8
                }
            })
            
        # Vytvoření grafu
        fig = {
            'data': data,
            'layout': {
                'title': f'Analýza citlivosti - vliv změny váhy kritéria "{zvolene_kriterium}" na pořadí variant',
                'xaxis': {
                    'title': f'Váha kritéria {zvolene_kriterium}',
                    'tickformat': '.1f'
                },
                'yaxis': {
                    'title': 'Pořadí',
                    'tickmode': 'linear',
                    'tick0': 1,
                    'dtick': 1,
                    'autorange': 'reversed'  # Obrácené pořadí (1 je nahoře)
                },
                'showlegend': True,
                'legend': {
                    'title': 'Varianty',
                    'orientation': 'v',
                },
                'grid': {
                    'rows': 1, 
                    'columns': 1
                },
                'margin': {'t': 50, 'b': 80}
            }
        }
        
        return fig
    except Exception as e:
        Utils.zapsat_chybu(f"Chyba při vytváření grafu citlivosti pořadí: {str(e)}")
        # Vrátíme prázdný graf
        return {
            'data': [],
            'layout': {
                'title': 'Chyba při vytváření grafu citlivosti pořadí'
            }
        }

def vytvor_graf_pomeru_variant(varianty, pomer_matice, nazev_metody="WPM"):
    """
    Vytvoří teplotní mapu (heatmap) zobrazující poměry mezi variantami.
    
    Args:
        varianty: Seznam názvů variant
        pomer_matice: 2D matice poměrů mezi variantami R(A_i/A_j)
        nazev_metody: Název metody pro titulek grafu
        
    Returns:
        dict: Plotly figure configuration
    """
    try:
        # Příprava popisků pro zobrazení při najetí myší
        hover_texts = []
        for i in range(len(varianty)):
            hover_row = []
            for j in range(len(varianty)):
                if i == j:
                    text = "-"  # Pro diagonální prvky
                else:
                    # Pro poměry variant zobrazujeme interpretaci
                    hodnota = pomer_matice[i][j]
                    interpretace = ""
                    if hodnota > 1:
                        interpretace = f"{varianty[i]} je lepší než {varianty[j]}"
                    elif hodnota < 1:
                        interpretace = f"{varianty[i]} je horší než {varianty[j]}"
                    else:
                        interpretace = f"{varianty[i]} je stejně dobrá jako {varianty[j]}"
                    
                    text = f"R({varianty[i]}/{varianty[j]}) = {hodnota:.3f}<br>{interpretace}"
                hover_row.append(text)
            hover_texts.append(hover_row)
            
        # Vytvoření grafu
        fig = {
            'data': [{
                'type': 'heatmap',
                'z': pomer_matice,
                'x': varianty,
                'y': varianty,
                'colorscale': 'Picnic',
                'zmid': 1,
                'xgap':2,       # horizontální mezera (v pixelech)
                'ygap':2,       # vertikální mezera (v pixelech)
                'zsmooth':False, # aby se Plotly nesnažilo hodnoty interpolovat
                'text': [[f'{val:.3f}' if isinstance(val, (int, float)) and i != j else "-" 
                          for j, val in enumerate(row)] for i, row in enumerate(pomer_matice)],
                'texttemplate': '%{text}',
                'hovertext': hover_texts,
                'hoverinfo': 'text',
                'showscale': True,
                'colorbar': {
                    'title': 'Poměr'
                }
            }],
            'layout': {
                'title': f'Poměry variant (R(A_i/A_j)) - {nazev_metody}',
                'plot_bgcolor':'grey',
                'xaxis': {
                    'title': 'Varianta j',
                    'side': 'bottom',
                },
                'yaxis': {
                    'title': 'Varianta i',
                },
                'margin': {'t': 50, 'b': 100, 'l': 100, 'r': 50}
            }
        }
        
        return fig
    except Exception as e:
        Utils.zapsat_chybu(f"Chyba při vytváření grafu poměrů variant: {str(e)}")
        # Vrátíme prázdný graf
        return {
            'data': [],
            'layout': {
                'title': 'Chyba při vytváření grafu poměrů variant'
            }
        }

def vytvor_prazdny_graf(text="Žádná data k zobrazení"):
    """
    Vytvoří prázdný graf s informační zprávou.
    
    Args:
        text: Text k zobrazení ve středu grafu
        
    Returns:
        dict: Plotly figure configuration
    """
    return {
        'data': [],
        'layout': {
            'xaxis': {'visible': False},
            'yaxis': {'visible': False},
            'annotations': [{
                'text': text,
                'xref': 'paper',
                'yref': 'paper',
                'showarrow': False,
                'font': {
                    'size': 16
                }
            }]
        }
    }

def vytvor_graf_relativniho_skore_wpm(results, nejlepsi_varianta, nejlepsi_skore, nejhorsi_varianta, nazev_metody="WPM"):
    """
    Vytvoří graf relativního skóre pro WPM metodu, kde všechny hodnoty jsou
    vyjádřeny jako procentuální podíl nejlepšího skóre.
    
    Args:
        results: List tuple (varianta, poradi, hodnota)
        nejlepsi_varianta: Název nejlepší varianty
        nejlepsi_skore: Skóre nejlepší varianty (pro výpočet relativního skóre)
        nejhorsi_varianta: Název nejhorší varianty
        nazev_metody: Název použité metody (pro titulek grafu)
        
    Returns:
        dict: Plotly figure configuration
    """
    try:
        # Příprava dat pro graf
        varianty = []
        relativni_skore = []
        colors = []  # Barvy pro sloupce
        
        # Seřazení dat podle pořadí (vzestupně)
        serazene_results = sorted(results, key=lambda x: x[1])
        
        for varianta, _, hodnota in serazene_results:
            varianty.append(varianta)
            # Výpočet relativního skóre jako procento nejlepšího skóre
            proc_skore = (hodnota / nejlepsi_skore) * 100 if nejlepsi_skore > 0 else 0
            relativni_skore.append(proc_skore)
            
            # Nejlepší varianta bude mít zelenou, nejhorší červenou
            if varianta == nejlepsi_varianta:
                colors.append('#2ecc71')  # zelená
            elif varianta == nejhorsi_varianta:
                colors.append('#e74c3c')  # červená
            else:
                colors.append('#3498db')  # modrá
        
        # Vytvoření grafu
        fig = {
            'data': [{
                'type': 'bar',
                'x': varianty,
                'y': relativni_skore,
                'marker': {
                    'color': colors
                },
                'text': [f'{s:.1f}%' for s in relativni_skore],  # Zobrazení hodnot nad sloupci
                'textposition': 'auto',
            }],
            'layout': {
                'title': f'Relativní skóre variant {nazev_metody} (% nejlepšího skóre)',
                'xaxis': {
                    'title': 'Varianty',
                    'tickangle': -45 if len(varianty) > 4 else 0  # Natočení popisků pro lepší čitelnost
                },
                'yaxis': {
                    'title': 'Relativní skóre (%)',
                    'range': [0, 105],  # Trochu místa nad sloupci pro hodnoty
                },
                'showlegend': False,
                'margin': {'t': 50, 'b': 100}  # Větší okraje pro popisky
            }
        }
        
        return fig
    except Exception as e:
        Utils.zapsat_chybu(f"Chyba při vytváření grafu relativního skóre: {str(e)}")
        # Vrátíme prázdný graf
        return {
            'data': [],
            'layout': {
                'title': 'Chyba při vytváření grafu relativního skóre'
            }
        }

#----- ELECTRE -----

def vytvor_graf_concordance_electre(matice_souhlasu, varianty):
    """
    Vytvoří teplotní mapu (heatmap) zobrazující matici souhlasu ELECTRE.
    
    Args:
        matice_souhlasu: 2D matice hodnot souhlasu mezi variantami
        varianty: Seznam názvů variant
        
    Returns:
        dict: Plotly figure configuration
    """
    try:
        # Vytvoření grafu
        fig = {
            'data': [{
                'type': 'heatmap',
                'z': matice_souhlasu,
                'x': varianty,
                'y': varianty,
                'colorscale': 'YlGnBu',
                'zmin': 0,
                'zmax': 1,
                'xgap':2,        
                'ygap':2,        
                'zsmooth':False,
                'text': [[f'{val:.3f}' if isinstance(val, (int, float)) else val 
                          for val in row] for row in matice_souhlasu],
                'texttemplate': '%{text}',
                'hoverinfo': 'text',
                'showscale': True,
                'colorbar': {
                    'title': 'Index souhlasu'
                }
            }],
            'layout': {
                'title': 'Matice souhlasu (Concordance matrix)',
                'xaxis': {
                    'title': 'Varianta j',
                    'side': 'bottom'
                },
                'yaxis': {
                    'title': 'Varianta i'
                },
                'margin': {'t': 50, 'b': 100, 'l': 100, 'r': 50}
            }
        }
        
        return fig
    except Exception as e:
        Utils.zapsat_chybu(f"Chyba při vytváření grafu matice souhlasu: {str(e)}")
        # Vrátíme prázdný graf
        return {
            'data': [],
            'layout': {
                'title': 'Chyba při vytváření grafu matice souhlasu'
            }
        }

def vytvor_graf_discordance_electre(matice_nesouhlasu, varianty):
    """
    Vytvoří teplotní mapu (heatmap) zobrazující matici nesouhlasu ELECTRE.
    
    Args:
        matice_nesouhlasu: 2D matice hodnot nesouhlasu mezi variantami
        varianty: Seznam názvů variant
        
    Returns:
        dict: Plotly figure configuration
    """
    try:
        fig = {
            'data': [{
                'type': 'heatmap',
                'z': matice_nesouhlasu,
                'x': varianty,
                'y': varianty,
                'colorscale': 'YlOrRd',
                'zmin': 0,
                'zmax': 1,
                'xgap':2, 
                'ygap':2,      
                'zsmooth':False, 
                'text': [[f'{val:.3f}' if isinstance(val, (int, float)) else val 
                          for val in row] for row in matice_nesouhlasu],
                'texttemplate': '%{text}',
                'hoverinfo': 'text',
                'showscale': True,
                'colorbar': {
                    'title': 'Index nesouhlasu'
                }
            }],
            'layout': {
                'title': 'Matice nesouhlasu (Discordance matrix)',
                'xaxis': {
                    'title': 'Varianta j',
                    'side': 'bottom'
                },
                'yaxis': {
                    'title': 'Varianta i'
                },
                'margin': {'t': 50, 'b': 100, 'l': 100, 'r': 50}
            }
        }
        
        return fig
    except Exception as e:
        Utils.zapsat_chybu(f"Chyba při vytváření grafu matice nesouhlasu: {str(e)}")
        return {
            'data': [],
            'layout': {
                'title': 'Chyba při vytváření grafu matice nesouhlasu'
            }
        }

def vytvor_graf_outranking_relace(outranking_matrix, varianty):
    """
    Vytvoří síťový graf znázorňující outrankingové relace (vztahy převahy) mezi variantami
    z ELECTRE analýzy.
    
    Args:
        outranking_matrix: 2D binární matice převahy mezi variantami (0/1)
        varianty: Seznam názvů variant
        
    Returns:
        dict: Plotly figure configuration
    """
    try:
        # Vytvoření uzlů (nodes) pro graf
        node_x = []
        node_y = []
        node_hover_texts = []
        
        # Spočítáme počet převyšujících a převyšovaných variant pro každý uzel
        prevysuje_count = []
        prevysovano_count = []
        
        for i in range(len(varianty)):
            # Počet variant, které tato varianta převyšuje
            prevysuje = sum(outranking_matrix[i])
            prevysuje_count.append(prevysuje)
            
            # Počet variant, které převyšují tuto variantu
            prevysovano = sum(outranking_matrix[j][i] for j in range(len(varianty)))
            prevysovano_count.append(prevysovano)
        
        # Pomocí kruhového layoutu rozmístíme uzly
        n_variants = len(varianty)
        radius = 1.0
        for i, varianta in enumerate(varianty):
            angle = 2 * math.pi * i / n_variants  # Úhel pro rozmístění do kruhu
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            
            node_x.append(x)
            node_y.append(y)
            
            # Vytvoření bohatšího hover textu s informacemi o převyšování
            hover_text = f"<b>{varianta}</b><br>" + \
                         f"Převyšuje: {prevysuje_count[i]} variant<br>" + \
                         f"Je převyšována: {prevysovano_count[i]} variantami<br>" + \
                         f"Net Flow: {prevysuje_count[i] - prevysovano_count[i]}"
            node_hover_texts.append(hover_text)
        
        # Vytvoření hran (edges) pro graf
        edge_x = []
        edge_y = []
        edge_annotations = []
        
        for i in range(n_variants):
            for j in range(n_variants):
                if i != j and outranking_matrix[i][j] == 1:
                    # Pro každý vztah převahy vytvoříme šipku
                    x0, y0 = node_x[i], node_y[i]
                    x1, y1 = node_x[j], node_y[j]
                    
                    # Mírně upravíme koncové body šipky aby nezasahovaly do uzlů
                    edge_length = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
                    
                    dx = (x1 - x0) / edge_length
                    dy = (y1 - y0) / edge_length
                    
                    x0_adj = x0 + dx * (radius * 0.3)
                    y0_adj = y0 + dy * (radius * 0.3)
                    x1_adj = x1 - dx * (radius * 0.3)
                    y1_adj = y1 - dy * (radius * 0.3)
                    
                    # Přidání hrany do seznamu
                    edge_x.extend([x0_adj, x1_adj, None])
                    edge_y.extend([y0_adj, y1_adj, None])
                    
                    # Přidání šipky jako anotace
                    edge_annotations.append({
                        'ax': x0_adj,
                        'ay': y0_adj,
                        'axref': 'x',
                        'ayref': 'y',
                        'x': x1_adj,
                        'y': y1_adj,
                        'xref': 'x',
                        'yref': 'y',
                        'showarrow': True,
                        'arrowhead': 2,
                        'arrowsize': 1.5,
                        'arrowwidth': 2,
                        'arrowcolor': '#636363'
                    })
        
        # Nastavení velikosti uzlů podle jejich "důležitosti" (Net Flow)
        node_sizes = [15 + 10 * abs(prevysuje_count[i] - prevysovano_count[i]) for i in range(n_variants)]
        
        # Nastavení barev uzlů podle jejich Net Flow (zelená pro pozitivní, červená pro negativní)
        node_colors = []
        for i in range(n_variants):
            net_flow = prevysuje_count[i] - prevysovano_count[i]
            if net_flow > 0:
                intensity = min(255, 100 + 20 * net_flow)
                node_colors.append(f'rgba(0, {intensity}, 0, 0.8)')
            elif net_flow < 0:
                intensity = min(255, 100 + 20 * abs(net_flow))
                node_colors.append(f'rgba({intensity}, 0, 0, 0.8)')
            else:
                node_colors.append('rgba(100, 100, 100, 0.8)')  # Šedá pro neutrální
        
        # Vytvoření grafu
        fig = {
            'data': [
                # Hrany
                {
                    'x': edge_x,
                    'y': edge_y,
                    'mode': 'lines',
                    'line': {
                        'width': 1,
                        'color': '#888'
                    },
                    'hoverinfo': 'none'
                },
                # Uzly
                {
                    'x': node_x,
                    'y': node_y,
                    'mode': 'markers+text',
                    'marker': {
                        'size': node_sizes,
                        'color': node_colors,
                        'line': {
                            'width': 2,
                            'color': 'darkblue'
                        }
                    },
                    'text': varianty,
                    'textposition': 'middle center',
                    'hoverinfo': 'text',
                    'hovertext': node_hover_texts
                }
            ],
            'layout': {
                'title': 'Outranking relace (šipka znázorňuje převyšování)',
                'showlegend': False,
                'xaxis': {
                    'showgrid': False,
                    'zeroline': False,
                    'showticklabels': False,
                    'range': [-1.3, 1.3]
                },
                'yaxis': {
                    'showgrid': False,
                    'zeroline': False,
                    'showticklabels': False,
                    'range': [-1.3, 1.3],
                    'scaleanchor': 'x',
                    'scaleratio': 1
                },
                'annotations': edge_annotations,
                'hovermode': 'closest',
                'margin': {'t': 50, 'b': 20, 'l': 20, 'r': 20},
                'plot_bgcolor': 'white'
            }
        }
        
        return fig
        
    except Exception as e:
        Utils.zapsat_chybu(f"Chyba při vytváření grafu outrankingových relací: {str(e)}")
        # Vrátíme prázdný graf
        return {
            'data': [],
            'layout': {
                'title': 'Chyba při vytváření grafu outrankingových relací'
            }
        }

def vytvor_graf_electre_vysledky(net_flows, varianty):
    """
    Vytvoří sloupcový graf pro vizualizaci výsledků ELECTRE.
    
    Args:
        net_flows: Seznam trojic (varianta, pořadí, net_flow)
        varianty: Seznam názvů variant
        
    Returns:
        dict: Plotly figure configuration
    """
    try:
        # Extrakce dat pro graf
        var_nazvy = []
        net_flow_hodnoty = []
        colors = []
        
        # Seřazení podle pořadí
        sorted_net_flows = sorted(net_flows, key=lambda x: x[1])
        
        for varianta, poradi, score in sorted_net_flows:
            var_nazvy.append(varianta)
            net_flow_hodnoty.append(score)
            
            # Přidání barvy podle hodnoty - pozitivní jsou zelené, negativní červené
            if score >= 0:
                colors.append('#2ecc71')  # zelená pro pozitivní
            else:
                colors.append('#e74c3c')  # červená pro negativní
        
        # Vytvoření grafu
        fig = {
            'data': [{
                'type': 'bar',
                'x': var_nazvy,
                'y': net_flow_hodnoty,
                'marker': {
                    'color': colors
                },
                'text': [f'{hodnota}' for hodnota in net_flow_hodnoty],
                'textposition': 'auto',
            }],
            'layout': {
                'title': 'Výsledky ELECTRE analýzy',
                'xaxis': {
                    'title': 'Varianty',
                    'tickangle': -45 if len(varianty) > 4 else 0
                },
                'yaxis': {
                    'title': 'Net Flow skóre',
                    'zeroline': True,
                    'zerolinecolor': 'black',
                    'zerolinewidth': 1,
                    'gridcolor': 'rgba(0,0,0,0.1)',
                    'gridwidth': 1
                },
                'showlegend': False,
                'margin': {'t': 50, 'b': 100},
                'plot_bgcolor': 'rgba(255,255,255,1)',
                'paper_bgcolor': 'rgba(255,255,255,1)',
            }
        }
        
        return fig
    except Exception as e:
        Utils.zapsat_chybu(f"Chyba při vytváření grafu výsledků ELECTRE: {str(e)}")
        # Vrátíme prázdný graf
        return {
            'data': [],
            'layout': {
                'title': 'Chyba při vytváření grafu výsledků ELECTRE'
            }
        }

#----- TOPSIS ----

def vytvor_graf_vzdalenosti_topsis(topsis_vysledky, varianty):
    """
    Vytvoří sloupcový graf vzdáleností od ideálního a anti-ideálního řešení.
    
    Args:
        topsis_vysledky: Slovník s výsledky TOPSIS analýzy
        varianty: Seznam názvů variant
        
    Returns:
        dict: Plotly figure configuration
    """
    try:
        # Extrakce dat pro vzdálenosti
        dist_ideal = topsis_vysledky.get('dist_ideal', [])
        dist_anti_ideal = topsis_vysledky.get('dist_anti_ideal', [])
        
        if not dist_ideal or not dist_anti_ideal:
            return vytvor_prazdny_graf("Chybí data o vzdálenostech od ideálního řešení")
        
        # Vytvoření grafu
        fig = {
            'data': [
                {
                    'type': 'bar',
                    'x': varianty,
                    'y': dist_ideal,
                    'name': 'Vzdálenost od ideálního řešení (S*)',
                    'marker': {
                        'color': '#e74c3c',  # červená pro vzdálenost od ideálního (menší je lepší)
                    },
                    'text': [f'{val:.4f}' for val in dist_ideal],
                    'textposition': 'auto',
                },
                {
                    'type': 'bar',
                    'x': varianty,
                    'y': dist_anti_ideal,
                    'name': 'Vzdálenost od anti-ideálního řešení (S-)',
                    'marker': {
                        'color': '#2ecc71',  # zelená pro vzdálenost od anti-ideálního (větší je lepší)
                    },
                    'text': [f'{val:.4f}' for val in dist_anti_ideal],
                    'textposition': 'auto',
                }
            ],
            'layout': {
                'title': 'Vzdálenosti od ideálního a anti-ideálního řešení',
                'xaxis': {
                    'title': 'Varianty',
                    'tickangle': -45 if len(varianty) > 4 else 0
                },
                'yaxis': {
                    'title': 'Vzdálenost',
                },
                'barmode': 'group',
                'showlegend': True,
                'legend': {
                    'orientation': 'h',
                    'y': -0.2,
                    'x': 0.5,
                    'xanchor': 'center'
                },
                'margin': {'t': 50, 'b': 100}
            }
        }
        
        return fig
    except Exception as e:
        Utils.zapsat_chybu(f"Chyba při vytváření grafu vzdáleností TOPSIS: {str(e)}")
        return vytvor_prazdny_graf("Chyba při vytváření grafu vzdáleností")

def vytvor_radar_graf_topsis(topsis_vysledky, varianty, kriteria):
    """
    Vytvoří vylepšený radarový graf porovnávající varianty s ideálním a anti-ideálním řešením.
    Používá průhlednou výplň s výraznými obrysy pro lepší čitelnost.
    
    Args:
        topsis_vysledky: Slovník s výsledky TOPSIS analýzy
        varianty: Seznam názvů variant
        kriteria: Seznam názvů kritérií
        
    Returns:
        dict: Plotly figure configuration
    """
    try:
        vazena_matice = topsis_vysledky.get('vazena_matice', [])
        ideal = topsis_vysledky.get('ideal', [])
        anti_ideal = topsis_vysledky.get('anti_ideal', [])
        
        if not vazena_matice or not ideal or not anti_ideal:
            return vytvor_prazdny_graf("Chybí data pro radarový graf")
        
        # 1) Vytvoříme zkrácené názvy pro osu (theta)...
        zkracena_kriteria = []
        for krit in kriteria:
            if len(krit) > 15:
                zkracena_kriteria.append(krit[:12] + "...")
            else:
                zkracena_kriteria.append(krit)
        
        # ...ale pro hover si uchováme původní (plné) názvy
        # Aby se snadno přiřazovalo, budeme je mít ve stejném pořadí
        plna_kriteria = list(kriteria)  # kopie
        
        # 2) Najdeme globální min/max pro nastavení radiální osy,
        #    abychom se vyhnuli tomu, že některá hodnota "přeteče" mimo graf
        vsechny_hodnoty = []
        vsechny_hodnoty.extend(ideal)
        vsechny_hodnoty.extend(anti_ideal)
        for row in vazena_matice:
            vsechny_hodnoty.extend(row)
        
        global_min = min(vsechny_hodnoty)
        global_max = max(vsechny_hodnoty)
        if global_min == global_max:
            # Pokud jsou všechny hodnoty stejné, nastavíme je např. 0 a 1, aby osa nebyla degenerate
            global_min = 0
            global_max = 1
        
        offset = (global_max - global_min) * 0.1
        radial_min = global_min - offset
        radial_max = global_max + offset
        
        # Můžete případně zajistit, aby osa nezačínala pod nulou:
        radial_min = min(0, radial_min)
        
        # 3) Definice barev pro varianty (jen příklad – 10 barev, cyklicky)
        barvy = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ]
        
        data = []
        
        # Funkce, která připraví "theta" a "customdata" = pro uzavření okruhu opakujeme první prvek
        def uzavrit_kruh(kratke, plne):
            return (kratke + [kratke[0]], plne + [plne[0]])
        
        # 4) Ideální řešení
        short_theta, full_crit = uzavrit_kruh(zkracena_kriteria, plna_kriteria)
        data.append({
            'type': 'scatterpolar',
            'r': ideal + [ideal[0]],  # Uzavření tvaru
            'theta': short_theta,
            'customdata': full_crit,  # Plné názvy pro hover
            'fill': 'none',
            'name': 'Ideální řešení',
            'line': {'color': 'black', 'width': 2},
            # V hoveru zobrazíme název kritéria + hodnotu
            'hovertemplate': (
                "Kritérium: %{customdata}<br>"
                "Hodnota: %{r:.4f}<extra></extra>"
            )
        })
        
        # 5) Anti-ideální řešení
        data.append({
            'type': 'scatterpolar',
            'r': anti_ideal + [anti_ideal[0]],
            'theta': short_theta,
            'customdata': full_crit,
            'fill': 'none',
            'name': 'Anti-ideální řešení',
            'line': {'color': 'gray', 'width': 2, 'dash': 'dash'},
            'hovertemplate': (
                "Kritérium: %{customdata}<br>"
                "Hodnota: %{r:.4f}<extra></extra>"
            )
        })
        
        # 6) Každá varianta
        for i, varianta in enumerate(varianty):
            if i >= len(vazena_matice):
                continue  # ochrana, kdyby nebylo dost řádků ve vazena_matice
            
            hodnoty = vazena_matice[i]
            
            # Uzavřeme první hodnotu, abychom vytvořili "kruh"
            uzavrene_hodnoty = hodnoty + [hodnoty[0]]
            
            barva_idx = i % len(barvy)
            barva = barvy[barva_idx]
            
            r = int(barva[1:3], 16)
            g = int(barva[3:5], 16)
            b = int(barva[5:7], 16)
            fill_color = f'rgba({r},{g},{b},0.15)'  # lehce průhledná výplň
            
            data.append({
                'type': 'scatterpolar',
                'r': uzavrene_hodnoty,
                'theta': short_theta,
                'customdata': full_crit,
                'fill': 'toself',
                'fillcolor': fill_color,
                'name': varianta,
                'line': {'color': barva, 'width': 2},
                'hovertemplate': (
                    f"Varianta: {varianta}<br>"
                    "Kritérium: %{customdata}<br>"
                    "Hodnota: %{r:.4f}<extra></extra>"
                )
            })
        
        # 7) Sestavení layoutu
        fig = {
            'data': data,
            'layout': {
                'title': 'Porovnání variant s ideálním a anti-ideálním řešením (Radar)',
                'polar': {
                    'radialaxis': {
                        'visible': True,
                        'showticklabels': True,
                        'range': [radial_min, radial_max],
                    },
                    'angularaxis': {
                        'tickfont': {'size': 10},
                        # Případně rotation, direction, atd.
                    }
                },
                'showlegend': True,
                'legend': {
                    'orientation': 'h',
                    'y': -0.15,
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 10}
                },
                'margin': {'t': 80, 'b': 100, 'l': 80, 'r': 80},
                'annotations': [
                    {
                        'text': 'Popisky kritérií jsou zkrácené, plné názvy uvidíte v hoveru.',
                        'xref': 'paper',
                        'yref': 'paper',
                        'x': 0,
                        'y': -0.1,
                        'showarrow': False,
                        'font': {'size': 10, 'color': 'gray'}
                    }
                ]
            }
        }
        
        return fig
    except Exception as e:
        Utils.zapsat_chybu(f"Chyba při vytváření radarového grafu TOPSIS: {str(e)}")
        return vytvor_prazdny_graf("Chyba při vytváření radarového grafu")

def vytvor_2d_graf_vzdalenosti_topsis(topsis_vysledky, varianty):
    """
    Vytvoří 2D rozptylový graf vzdáleností od ideálního (S*) a anti-ideálního (S-) řešení v TOPSIS.
    - Osa X = S* (menší je lepší)
    - Osa Y = S- (větší je lepší)
    
    Args:
        topsis_vysledky: Slovník s výsledky TOPSIS (obsahující klíče:
                         'dist_ideal', 'dist_anti_ideal', 'relativni_blizkost')
        varianty: Seznam názvů variant
        
    Returns:
        dict: Plotly figure (konfigurace pro vykreslení)
    """
    try:
        dist_ideal = topsis_vysledky.get('dist_ideal', [])
        dist_anti_ideal = topsis_vysledky.get('dist_anti_ideal', [])
        relativni_blizkost = topsis_vysledky.get('relativni_blizkost', [])
        
        if not dist_ideal or not dist_anti_ideal or not relativni_blizkost:
            return vytvor_prazdny_graf("Chybí data o vzdálenostech od ideálního/anti-ideálního řešení")
        
        # Seřazení pro zobrazení v barevné škále podle C* (relativni_blizkost)
        serazene_indexy = sorted(
            range(len(relativni_blizkost)), 
            key=lambda i: relativni_blizkost[i], 
            reverse=True
        )
        
        # Připravíme data pro scatter
        x_data = []
        y_data = []
        marker_colors = []
        text_labels = []
        
        for idx in serazene_indexy:
            x_data.append(dist_ideal[idx])
            y_data.append(dist_anti_ideal[idx])
            marker_colors.append(relativni_blizkost[idx])
            
            # Přidání detailu k popisku (hover)
            poradi = serazene_indexy.index(idx) + 1
            text_labels.append(
                f"{varianty[idx]}<br>"
                f"C*: {relativni_blizkost[idx]:.4f}<br>"
                f"Pořadí: {poradi}"
            )
        
        # Zjistíme min/max pro nastavení range a paddingu
        x_min, x_max = min(x_data), max(x_data)
        y_min, y_max = min(y_data), max(y_data)
        
        # Ochrana proti situaci, kdy x_min == x_max apod. (např. jediná varianta)
        x_range = None
        if x_max > x_min:
            x_padding = (x_max - x_min) * 0.2
            x_range = [x_min - x_padding, x_max + x_padding]
        
        y_range = None
        if y_max > y_min:
            y_padding = (y_max - y_min) * 0.2
            y_range = [y_min - y_padding, y_max + y_padding]
        
        fig = {
            'data': [{
                'type': 'scatter',
                'x': x_data,
                'y': y_data,
                'mode': 'markers+text',
                'marker': {
                    'size': 12,
                    'color': marker_colors,
                    'colorscale': 'Viridis',
                    'showscale': True,
                    'colorbar': {
                        'title': 'Relativní blízkost (C*)'
                    },
                    'line': {
                        'width': 1,
                        'color': 'black'
                    }
                },
                'text': [varianty[idx] for idx in serazene_indexy],
                'textposition': 'top center',
                'textfont': {'size': 10},
                'hovertext': text_labels,
                'hoverinfo': 'text'
            }],
            'layout': {
                'title': '2D vizualizace vzdáleností v metodě TOPSIS',
                'xaxis': {
                    'title': 'Vzdálenost od ideálního řešení (S*) - menší je lepší',
                    'zeroline': True,
                    'zerolinecolor': 'gray',
                    'zerolinewidth': 1,
                    'range': x_range  # Může zůstat None, pak Plotly zvolí auto
                },
                'yaxis': {
                    'title': 'Vzdálenost od anti-ideálního řešení (S-) - větší je lepší',
                    'range': y_range
                },
                'hovermode': 'closest',
                'showlegend': False,
                'annotations': [
                    # Levý horní roh - "Optimální oblast"
                    {
                        'xref': 'paper',
                        'yref': 'paper',
                        'x': 0.03,
                        'y': 0.98,
                        'text': 'Optimální oblast',
                        'showarrow': True,
                        'arrowhead': 3,
                        'arrowsize': 1.2,
                        'arrowwidth': 2,
                        'arrowcolor': '#2ecc71',  # Zelená šipka
                        'ax': 20,
                        'ay': -20
                    },
                    # Pravý dolní roh - "Nejhorší oblast"
                    {
                        'xref': 'paper',
                        'yref': 'paper',
                        'x': 0.96,
                        'y': 0.04,
                        'text': 'Nejhorší oblast',
                        'showarrow': True,
                        'arrowhead': 3,
                        'arrowsize': 1.2,
                        'arrowwidth': 2,
                        'arrowcolor': '#e74c3c',  # Červená šipka
                        'ax': -20,
                        'ay': 20
                    },
                    # Malá vysvětlující poznámka
                    {
                        'xref': 'paper',
                        'yref': 'paper',
                        'x': 0.5,
                        'y': 1.07,
                        'text': 'Nejlepší varianty: menší S* (X) a větší S- (Y) → levý horní roh grafu',
                        'showarrow': False,
                        'font': {
                            'size': 10,
                            'color': 'gray'
                        },
                        'align': 'center'
                    }
                ],
                'margin': {'t': 80, 'b': 80, 'l': 80, 'r': 80}
            }
        }
        
        return fig
    
    except Exception as e:
        Utils.zapsat_chybu(f"Chyba při vytváření 2D grafu vzdáleností TOPSIS: {str(e)}")
        return vytvor_prazdny_graf("Chyba při vytváření 2D grafu vzdáleností")
