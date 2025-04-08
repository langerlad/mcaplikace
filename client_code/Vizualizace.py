# client_code/vizualizace.py
# -------------------------------------------------------
# Modul: vizualizace
# Obsahuje sdílené funkce pro tvorbu grafů a vizualizací
# -------------------------------------------------------

import plotly.graph_objects as go
from . import Utils

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
                'text': [[f'{val:.3f}' if isinstance(val, (int, float)) else val 
                          for val in row] for row in matice_souhlasu],
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
        # Vytvoření grafu
        fig = {
            'data': [{
                'type': 'heatmap',
                'z': matice_nesouhlasu,
                'x': varianty,
                'y': varianty,
                'colorscale': 'YlOrRd',  # Jiná barevná škála než pro souhlas
                'zmin': 0,
                'zmax': 1,
                'text': [[f'{val:.3f}' if isinstance(val, (int, float)) else val 
                          for val in row] for row in matice_nesouhlasu],
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
        # Vrátíme prázdný graf
        return {
            'data': [],
            'layout': {
                'title': 'Chyba při vytváření grafu matice nesouhlasu'
            }
        }

def vytvor_graf_outranking_electre(outranking_matice, varianty):
    """
    Vytvoří teplotní mapu (heatmap) zobrazující outranking matrix metody ELECTRE.
    
    Args:
        outranking_matice: 2D binární matice převahy mezi variantami (0/1)
        varianty: Seznam názvů variant
        
    Returns:
        dict: Plotly figure configuration
    """
    try:
        # Vytvoření grafu
        fig = {
            'data': [{
                'type': 'heatmap',
                'z': outranking_matice,
                'x': varianty,
                'y': varianty,
                'colorscale': [[0, 'white'], [1, 'green']],  # Binární barevná škála
                'zmin': 0,
                'zmax': 1,
                'text': [[f'{int(val)}' if isinstance(val, (int, float)) else val 
                          for val in row] for row in outranking_matice],
                'hoverinfo': 'text',
                'showscale': True,
                'colorbar': {
                    'title': 'Převaha',
                    'tickvals': [0, 1],
                    'ticktext': ['Ne', 'Ano']
                }
            }],
            'layout': {
                'title': 'Matice převahy (Outranking matrix)',
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
        Utils.zapsat_chybu(f"Chyba při vytváření grafu matice převahy: {str(e)}")
        # Vrátíme prázdný graf
        return {
            'data': [],
            'layout': {
                'title': 'Chyba při vytváření grafu matice převahy'
            }
        }

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

def vytvor_heat_mapu(varianty, kriteria, hodnoty, nazev_metody=""):
    """
    Vytvoří teplotní mapu zobrazující vztahy mezi variantami a kritérii
    s použitím barevné škály YlGnBu a dynamickým nastavením rozsahu barev.
    
    Args:
        varianty: Seznam názvů variant (řádky)
        kriteria: Seznam názvů kritérií (sloupce)
        hodnoty: 2D list hodnot [varianty][kriteria]
        nazev_metody: Název metody pro titulek (volitelný)
        
    Returns:
        dict: Konfigurace Plotly figure
    """
    try:
        # Získání všech hodnot a výpočet minimální a maximální hodnoty
        all_values = [val for row in hodnoty for val in row]
        z_min = min(all_values)
        z_max = max(all_values)
        
        # Příprava popisků pro zobrazení při najetí myší
        hover_texts = []
        for i in range(len(varianty)):
            hover_row = []
            for j in range(len(kriteria)):
                # Formát: Varianta: X, Kritérium: Y, Hodnota: Z
                text = f"Varianta: {varianty[i]}<br>Kritérium: {kriteria[j]}<br>Hodnota: {hodnoty[i][j]:.3f}"
                hover_row.append(text)
            hover_texts.append(hover_row)
        
        fig = {
            'data': [{
                'type': 'heatmap',
                'z': hodnoty,
                'x': kriteria,
                'y': varianty,
                'colorscale': 'YlGnBu',  # Použití požadované barevné škály
                'zmin': z_min,
                'zmax': z_max,
                # Přidání anotací s hodnotami do každé buňky
                'text': [[f'{hodnoty[i][j]:.3f}' for j in range(len(kriteria))]
                         for i in range(len(varianty))],
                'hovertext': hover_texts,  # Vylepšené popisky při najetí myší
                'hoverinfo': 'text',  # Zobrazení pouze vlastních popisků
                'showscale': True,
                'colorbar': {
                    'title': 'Hodnota',
                    'titleside': 'right',
                    'tickformat': '.3f',
                },
            }],
            'layout': {
                'title': {
                    'text': f'Teplotní mapa hodnot{f" - {nazev_metody}" if nazev_metody else ""}',
                    'x': 0.5,
                    'xanchor': 'center'
                },
                'xaxis': {
                    'title': 'Kritéria',
                    'side': 'bottom',  # Umístění popisku osy X pod grafem
                    'automargin': True
                },
                'yaxis': {
                    'title': 'Varianty',
                    'automargin': True,
                    'tickmode': 'array',          # Zajistí, že se zobrazí všechny varianty
                    'tickvals': list(range(len(varianty))),
                    'ticktext': varianty
                },
                'margin': {'t': 60, 'b': 80, 'l': 80, 'r': 80},
                'template': 'plotly_white',
                'width': 800,   # Velikost grafu odpovídající figsize=(8,6)
                'height': 600,
            }
        }
        
        return fig
    except Exception as e:
        Utils.zapsat_chybu(f"Chyba při vytváření teplotní mapy: {str(e)}")
        return {
            'data': [],
            'layout': {
                'title': 'Chyba při vytváření teplotní mapy'
            }
        }



def vytvor_histogram_vah(kriteria, vahy):
    """
    Vytvoří histogram vah kritérií.
    
    Args:
        kriteria: Seznam názvů kritérií
        vahy: Seznam vah kritérií
        
    Returns:
        dict: Plotly figure configuration
    """
    try:
        # Vytvoření grafu
        fig = {
            'data': [{
                'type': 'bar',
                'x': kriteria,
                'y': vahy,
                'marker': {
                    'color': '#3498db',
                },
                'text': [f'{v:.3f}' for v in vahy],
                'textposition': 'auto',
            }],
            'layout': {
                'title': 'Váhy kritérií',
                'xaxis': {
                    'title': 'Kritéria',
                    'tickangle': -45 if len(kriteria) > 4 else 0
                },
                'yaxis': {
                    'title': 'Váha',
                    'range': [0, max(vahy) * 1.1] if vahy else [0, 1]
                },
                'showlegend': False,
                'margin': {'t': 50, 'b': 100}
            }
        }
        
        return fig
    except Exception as e:
        Utils.zapsat_chybu(f"Chyba při vytváření histogramu vah: {str(e)}")
        # Vrátíme prázdný graf
        return {
            'data': [],
            'layout': {
                'title': 'Chyba při vytváření histogramu vah'
            }
        }

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
    Vytvoří radarový graf porovnávající varianty s ideálním a anti-ideálním řešením.
    
    Args:
        topsis_vysledky: Slovník s výsledky TOPSIS analýzy
        varianty: Seznam názvů variant
        kriteria: Seznam názvů kritérií
        
    Returns:
        dict: Plotly figure configuration
    """
    try:
        # Extrakce dat
        vazena_matice = topsis_vysledky.get('vazena_matice', [])
        ideal = topsis_vysledky.get('ideal', [])
        anti_ideal = topsis_vysledky.get('anti_ideal', [])
        
        if not vazena_matice or not ideal or not anti_ideal:
            return vytvor_prazdny_graf("Chybí data pro radarový graf")
        
        # Vytvoření dat pro radarový graf
        data = []
        
        # Přidání dat pro ideální řešení
        data.append({
            'type': 'scatterpolar',
            'r': ideal + [ideal[0]],  # Pro uzavření křivky opakujeme první hodnotu
            'theta': kriteria + [kriteria[0]],  # Pro uzavření křivky opakujeme první hodnotu
            'fill': 'none',
            'name': 'Ideální řešení',
            'line': {
                'color': 'black',
                'width': 2
            }
        })
        
        # Přidání dat pro anti-ideální řešení
        data.append({
            'type': 'scatterpolar',
            'r': anti_ideal + [anti_ideal[0]],
            'theta': kriteria + [kriteria[0]],
            'fill': 'none',
            'name': 'Anti-ideální řešení',
            'line': {
                'color': 'gray',
                'width': 2,
                'dash': 'dash'
            }
        })
        
        # Přidání dat pro každou variantu
        colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6']
        for i, varianta in enumerate(varianty):
            color_idx = i % len(colors)  # Cyklické použití barev
            
            if i >= len(vazena_matice):
                continue  # Ochrana proti nedostatku dat
                
            # Pro radarový graf musíme uzavřít křivku tak, že opakujeme první hodnotu na konci
            hodnoty = vazena_matice[i] + [vazena_matice[i][0]]
            labels = kriteria + [kriteria[0]]
            
            data.append({
                'type': 'scatterpolar',
                'r': hodnoty,
                'theta': labels,
                'fill': 'toself',
                'name': varianta,
                'line': {
                    'color': colors[color_idx]
                },
                'fillcolor': colors[color_idx],
                'opacity': 0.1
            })
        
        # Vytvoření grafu
        fig = {
            'data': data,
            'layout': {
                'title': 'Porovnání variant s ideálním a anti-ideálním řešením',
                'polar': {
                    'radialaxis': {
                        'visible': True
                    }
                },
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
        Utils.zapsat_chybu(f"Chyba při vytváření radarového grafu TOPSIS: {str(e)}")
        return vytvor_prazdny_graf("Chyba při vytváření radarového grafu")

def vytvor_2d_graf_vzdalenosti_topsis(topsis_vysledky, varianty):
    """
    Vytvoří 2D rozptylový graf vzdáleností od ideálního a anti-ideálního řešení.
    
    Args:
        topsis_vysledky: Slovník s výsledky TOPSIS analýzy
        varianty: Seznam názvů variant
        
    Returns:
        dict: Plotly figure configuration
    """
    try:
        # Extrakce dat
        dist_ideal = topsis_vysledky.get('dist_ideal', [])
        dist_anti_ideal = topsis_vysledky.get('dist_anti_ideal', [])
        relativni_blizkost = topsis_vysledky.get('relativni_blizkost', [])
        
        if not dist_ideal or not dist_anti_ideal or not relativni_blizkost:
            return vytvor_prazdny_graf("Chybí data o vzdálenostech od ideálního řešení")
        
        # Vytvoření grafu
        fig = {
            'data': [{
                'type': 'scatter',
                'x': dist_ideal,
                'y': dist_anti_ideal,
                'mode': 'markers+text',
                'marker': {
                    'size': 12,
                    'color': relativni_blizkost,
                    'colorscale': 'Viridis',
                    'colorbar': {
                        'title': 'Relativní blízkost (C*)',
                        'titleside': 'right'
                    }
                },
                'text': varianty,
                'textposition': 'top center',
                'textfont': {
                    'size': 10
                },
                'hovertemplate': '%{text}<br>S*: %{x:.4f}<br>S-: %{y:.4f}<extra></extra>'
            }],
            'layout': {
                'title': '2D vizualizace vzdáleností - čím níže vpravo, tím lépe',
                'xaxis': {
                    'title': 'Vzdálenost od ideálního řešení (S*)'
                },
                'yaxis': {
                    'title': 'Vzdálenost od anti-ideálního řešení (S-)',
                    'autorange': 'reversed'  # Otočení osy y
                },
                'hovermode': 'closest',
                'showlegend': False,
                'annotations': [
                    {
                        'x': 0.98,
                        'y': 0.02,
                        'xref': 'paper',
                        'yref': 'paper',
                        'text': 'Lepší řešení',
                        'showarrow': True,
                        'arrowhead': 2,
                        'ax': -60,
                        'ay': 60
                    }
                ],
                'grid': {
                    'rows': 1, 
                    'columns': 1
                },
                'margin': {'t': 50, 'b': 80}
            }
        }
        
        return fig
    except Exception as e:
        Utils.zapsat_chybu(f"Chyba při vytváření 2D grafu vzdáleností TOPSIS: {str(e)}")
        return vytvor_prazdny_graf("Chyba při vytváření 2D grafu vzdáleností")

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
        prevysovane_hodnoty = []
        prevysujici_hodnoty = []
        
        # Seřazení podle pořadí
        sorted_net_flows = sorted(net_flows, key=lambda x: x[1])
        
        for varianta, poradi, score in sorted_net_flows:
            var_nazvy.append(varianta)
            
            # Rozdělíme net_flow na pozitivní a negativní komponenty
            if score > 0:
                prevysovane_hodnoty.append(score)
                prevysujici_hodnoty.append(0)
            else:
                prevysovane_hodnoty.append(0)
                prevysujici_hodnoty.append(abs(score))
        
        # Vytvoření grafu
        fig = {
            'data': [
                {
                    'type': 'bar',
                    'x': var_nazvy,
                    'y': prevysovane_hodnoty,
                    'name': 'Převyšující (pozitivní vliv)',
                    'marker': {
                        'color': '#2ecc71'  # zelená
                    }
                },
                {
                    'type': 'bar',
                    'x': var_nazvy,
                    'y': prevysujici_hodnoty,
                    'name': 'Převyšované (negativní vliv)',
                    'marker': {
                        'color': '#e74c3c'  # červená
                    }
                }
            ],
            'layout': {
                'title': 'Výsledky ELECTRE analýzy',
                'xaxis': {
                    'title': 'Varianty',
                    'tickangle': -45 if len(varianty) > 4 else 0
                },
                'yaxis': {
                    'title': 'Počet variant'
                },
                'barmode': 'stack',
                'showlegend': True,
                'legend': {
                    'orientation': 'h',
                    'y': -0.2,
                    'x': 0.5,
                    'xanchor': 'center'
                },
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