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

def vytvor_skladany_sloupovy_graf(varianty, kriteria, vazene_hodnoty):
    """
    Vytvoří skládaný sloupcový graf zobrazující příspěvek jednotlivých kritérií.
    
    Args:
        varianty: Seznam názvů variant
        kriteria: Seznam názvů kritérií
        vazene_hodnoty: 2D list vážených hodnot [varianty][kriteria]
        
    Returns:
        dict: Plotly figure configuration
    """
    try:
        # Vytvoření datových sérií pro každé kritérium
        data = []
        
        # Pro každé kritérium vytvoříme jednu sérii dat
        for j, kriterium in enumerate(kriteria):
            hodnoty_kriteria = [vazene_hodnoty[i][j] for i in range(len(varianty))]
            
            data.append({
                'type': 'bar',
                'name': kriterium,
                'x': varianty,
                'y': hodnoty_kriteria,
                'text': [f'{h:.3f}' for h in hodnoty_kriteria],
                'textposition': 'inside',
            })
            
        # Vytvoření grafu
        fig = {
            'data': data,
            'layout': {
                'title': 'Příspěvek jednotlivých kritérií k celkovému skóre',
                'barmode': 'stack',  # Skládaný sloupcový graf
                'xaxis': {
                    'title': 'Varianty',
                    'tickangle': -45 if len(varianty) > 4 else 0
                },
                'yaxis': {
                    'title': 'Skóre',
                },
                'showlegend': True,
                'legend': {
                    'title': 'Kritéria',
                    'orientation': 'h',  # Horizontální legenda
                    'y': -0.2,  # Umístění pod grafem
                    'x': 0.5,
                    'xanchor': 'center'
                },
                'margin': {'t': 50, 'b': 150}  # Větší spodní okraj pro legendu
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
        # Vytvoření grafu
        fig = {
            'data': [{
                'type': 'heatmap',
                'z': pomer_matice,
                'x': varianty,
                'y': varianty,
                'colorscale': 'YlGnBu',
                'zmin': 0,
                'text': [[f'{val:.3f}' if isinstance(val, (int, float)) else val 
                          for val in row] for row in pomer_matice],
                'hoverinfo': 'text',
                'showscale': True,
                'colorbar': {
                    'title': 'Poměr'
                }
            }],
            'layout': {
                'title': f'Poměry variant (R(A_i/A_j)) - {nazev_metody}',
                'xaxis': {
                    'title': 'Varianta j',
                    'side': 'bottom'  # Přesun popisku na spodní okraj
                },
                'yaxis': {
                    'title': 'Varianta i'
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
                'hoverinfo': 'text',
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

# Pokročilejší generátory HTML obsahu

def vytvor_html_sekci_metodologie(metoda="WSM", default_open=True):
    """
    Vytvoří HTML sekci s popisem metodologie pro danou metodu analýzy, používá CSS místo JavaScriptu.
    
    Args:
        metoda: Kód metody analýzy ("WSM", "WPM", "TOPSIS", atd.)
        default_open: Zda má být sekce ve výchozím stavu otevřená
        
    Returns:
        str: HTML kód s metodologií
    """
    # Vytvoření unikátního ID pro tento přepínač
    toggle_id = f"metodologie-{metoda.lower()}"
    default_class = "default-open" if default_open else ""
    
    if metoda.upper() == "WSM":
        return f"""
        <input type="checkbox" id="{toggle_id}" class="toggle-checkbox" {"checked" if default_open else ""}>
        <label for="{toggle_id}" class="details-toggle {default_class}">
            O metodě WSM (Weighted Sum Model) 
            <span class="toggle-hint">Kliknutím zobrazíte/skryjete</span>
        </label>
        <div class="details-content">
            <div style="padding: 0;">
                <p>WSM, také známý jako Simple Additive Weighting (SAW), je jedna z nejjednodušších a nejpoužívanějších metod vícekriteriálního rozhodování. Je založena na lineárním vážení kritérií.</p>
                
                <h4>Postup metody WSM/SAW:</h4>
                <ol>
                    <li><strong>Sběr dat</strong> - Definice variant, kritérií a hodnocení variant podle kritérií.</li>
                    <li><strong>Normalizace hodnot</strong> - Převod různorodých hodnot kritérií na srovnatelnou škálu 0 až 1 pomocí metody Min-Max.</li>
                    <li><strong>Vážení hodnot</strong> - Vynásobení normalizovaných hodnot vahami kritérií.</li>
                    <li><strong>Výpočet celkového skóre</strong> - Sečtení vážených hodnot pro každou variantu.</li>
                    <li><strong>Seřazení variant</strong> - Seřazení variant podle celkového skóre (vyšší je lepší).</li>
                </ol>
                
                <h4>Výhody metody:</h4>
                <ul>
                    <li>Jednoduchá a intuitivní</li>
                    <li>Transparentní výpočty a výsledky</li>
                    <li>Snadná interpretace</li>
                </ul>
                
                <h4>Omezení metody:</h4>
                <ul>
                    <li>Předpokládá lineární užitek</li>
                    <li>Není vhodná pro silně konfliktní kritéria</li>
                    <li>Méně robustní vůči extrémním hodnotám než některé pokročilejší metody</li>
                </ul>
            </div>
        </div>
        """
    elif metoda.upper() == "WPM":
        return f"""
        <input type="checkbox" id="{toggle_id}" class="toggle-checkbox" {"checked" if default_open else ""}>
        <label for="{toggle_id}" class="details-toggle {default_class}">
            O metodě WPM (Weighted Product Model)
            <span class="toggle-hint">Kliknutím zobrazíte/skryjete</span>
        </label>
        <div class="details-content">
            <div style="padding: 0;">
                <p>WPM (Weighted Product Model) je metoda vícekriteriálního rozhodování, která na rozdíl od WSM používá násobení místo sčítání. Tím je méně citlivá na různé měrné jednotky kritérií a eliminuje potřebu normalizace.</p>
                
                <h4>Postup metody WPM:</h4>
                <ol>
                    <li><strong>Sběr dat</strong> - Definice variant, kritérií a hodnocení variant podle kritérií.</li>
                    <li><strong>Transformace dat</strong> - Pro minimalizační kritéria se použije převrácená hodnota (1/x).</li>
                    <li><strong>Výpočet výsledné hodnoty</strong> - Pro každou variantu se vypočítá součin hodnot kritérií umocněných na příslušné váhy.</li>
                    <li><strong>Seřazení variant</strong> - Seřazení variant podle celkového skóre (vyšší je lepší).</li>
                </ol>
                
                <h4>Matematický zápis:</h4>
                <div class="mcapp-formula-box">
                    <div class="mcapp-formula-row">
                        <span class="mcapp-formula-content">
                            P(A<sub>i</sub>) = ∏<sub>j=1</sub><sup>n</sup> (x<sub>ij</sub>)<sup>w<sub>j</sub></sup>
                        </span>
                    </div>
                </div>
                <p>kde x<sub>ij</sub> je hodnota i-té varianty podle j-tého kritéria a w<sub>j</sub> je váha j-tého kritéria.</p>
                
                <h4>Výhody metody:</h4>
                <ul>
                    <li>Eliminuje potřebu normalizace jednotek</li>
                    <li>Méně citlivá na extrémní hodnoty</li>
                    <li>Vhodná pro data s rozdílnými měrnými jednotkami</li>
                    <li>Odolnější vůči problému "rank reversal" než WSM</li>
                </ul>
                
                <h4>Omezení metody:</h4>
                <ul>
                    <li>Složitější interpretace výsledků</li>
                    <li>Problémy s nulovými hodnotami (ty je třeba nahradit velmi malým číslem)</li>
                    <li>Méně intuitivní než WSM</li>
                </ul>
            </div>
        </div>
        """
    else:
        return f"""
        <input type="checkbox" id="{toggle_id}" class="toggle-checkbox" {"checked" if default_open else ""}>
        <label for="{toggle_id}" class="details-toggle {default_class}">
            O metodě {metoda}
            <span class="toggle-hint">Kliknutím zobrazíte/skryjete</span>
        </label>
        <div class="details-content">
            <div style="padding: 0;">
                <p>Detailní informace o metodě {metoda}.</p>
            </div>
        </div>
        """

def vytvor_html_sekci_normalizace(default_open=True):
    """
    Vytvoří HTML sekci s vysvětlením normalizace hodnot, používá CSS místo JavaScriptu.
    
    Args:
        default_open: Zda má být sekce ve výchozím stavu otevřená
        
    Returns:
        str: HTML kód s vysvětlením normalizace
    """
    # Vytvoření unikátního ID pro tento přepínač
    toggle_id = "normalizace-info"
    default_class = "default-open" if default_open else ""
    
    return f"""
    <input type="checkbox" id="{toggle_id}" class="toggle-checkbox" {"checked" if default_open else ""}>
    <label for="{toggle_id}" class="details-toggle {default_class}">
        Informace o normalizaci hodnot
        <span class="toggle-hint">Kliknutím zobrazíte/skryjete</span>
    </label>
    <div class="details-content">
        <div style="padding: 0;">
            <div class="mcapp-explanation">
                <h4>Princip metody Min-Max normalizace:</h4>
                <div class="mcapp-formula-box">
                    <div class="mcapp-formula-row">
                        <span class="mcapp-formula-label">Pro maximalizační kritéria (čím více, tím lépe):</span>
                        <span class="mcapp-formula-content">Normalizovaná hodnota = (hodnota - minimum) / (maximum - minimum)</span>
                    </div>
                    <div class="mcapp-formula-row">
                        <span class="mcapp-formula-label">Pro minimalizační kritéria (čím méně, tím lépe):</span>
                        <span class="mcapp-formula-content">Normalizovaná hodnota = (maximum - hodnota) / (maximum - minimum)</span>
                    </div>
                </div>
                <div class="mcapp-note">
                    <p>Kde minimum je nejmenší hodnota v daném kritériu a maximum je největší hodnota v daném kritériu.</p>
                    <p>Výsledkem jsou hodnoty v intervalu [0,1], kde 1 je vždy nejlepší hodnota (ať už jde o maximalizační či minimalizační kritérium).</p>
                </div>
            </div>
        </div>
    </div>
    """

def vytvor_sekci_postupu_wsm(norm_matice, vazene_matice, vahy, varianty, kriteria, typy_kriterii):
    """
    Vytvoří HTML sekci s postupem výpočtu.
    
    Args:
        norm_matice: Normalizovaná matice hodnot
        vazene_matice: Vážená matice hodnot
        vahy: Seznam vah kritérií
        varianty: Seznam názvů variant
        kriteria: Seznam názvů kritérií
        typy_kriterii: Seznam typů kritérií (max/min)
            
    Returns:
        str: HTML kód pro sekci postupu výpočtu
    """
    # Vysvětlení normalizace pomocí CSS
    vysvetleni_norm_html = vytvor_html_sekci_normalizace(default_open=False)
    
    # Normalizační tabulka
    normalizace_html = vytvor_html_normalizacni_tabulku(norm_matice, varianty, kriteria)
    
    # Tabulka vah
    vahy_html = vytvor_html_tabulku_vah(vahy, kriteria)
    
    # Tabulka vážených hodnot
    vazene_html = vytvor_html_tabulku_vazenych_hodnot(vazene_matice, varianty, kriteria)

    # Sloučení do sekce
    return f"""
    <div class="mcapp-section mcapp-process">
        <h2>Postup zpracování dat</h2>
        {vysvetleni_norm_html}
        <div class="mcapp-card">
            <h3>Krok 1: Normalizace hodnot</h3>
            {normalizace_html}
        </div>
        <div class="mcapp-card">
            <h3>Krok 2: Vážení hodnot a výpočet skóre</h3>
            {vahy_html}
            {vazene_html}
        </div>
    </div>
    """

def vytvor_kompletni_html_analyzy(analyza_data, vysledky_vypoctu, metoda="WSM"):
    """
    Vytvoří kompletní HTML strukturu pro zobrazení výsledků analýzy s použitím CSS místo JavaScriptu.
    
    Args:
        analyza_data: Slovník s daty analýzy v JSON formátu
        vysledky_vypoctu: Slovník s výsledky výpočtů
        metoda: Kód metody analýzy
        
    Returns:
        str: HTML kód pro zobrazení
    """
    # Extrakce dat v požadovaném formátu
    varianty = vysledky_vypoctu['norm_vysledky']['nazvy_variant']
    kriteria = vysledky_vypoctu['norm_vysledky']['nazvy_kriterii']
    
    # Vytvoření částí HTML dokumentu
    hlavicka_html = vytvor_hlavicku_analyzy(analyza_data['nazev'], metoda)
    vstupni_data_html = vytvor_sekci_vstupnich_dat(analyza_data)
    
    # Rozdílný postup podle metody
    if metoda.upper() == "WSM":
        metodologie_html = vytvor_html_sekci_metodologie(metoda, default_open=True)
        postup_html = vytvor_sekci_postupu_wsm(
            vysledky_vypoctu['norm_vysledky']['normalizovana_matice'],
            vysledky_vypoctu['vazene_matice'],
            vysledky_vypoctu['vahy'],
            varianty,
            kriteria,
            vysledky_vypoctu['typy_kriterii']
        )
        vysledky_html = vytvor_sekci_vysledku(vysledky_vypoctu['wsm_vysledky'])
    elif metoda.upper() == "WPM":
        metodologie_html = vytvor_html_sekci_metodologie(metoda, default_open=True)
        postup_html = vytvor_sekci_postupu_wpm(
            vysledky_vypoctu['matice'],
            vysledky_vypoctu['produktovy_prispevek'],
            vysledky_vypoctu['vahy'],
            varianty,
            kriteria,
            vysledky_vypoctu['typy_kriterii']
        )
        vysledky_html = vytvor_sekci_vysledku(vysledky_vypoctu['wpm_vysledky'])
    elif metoda.upper() == "TOPSIS":
        metodologie_html = vytvor_html_sekci_metodologie_topsis(default_open=True)
        
        # Extrakce dat specifických pro TOPSIS
        topsis_results = vysledky_vypoctu['topsis_vysledky']
        
        # Normalizovaná matice podle Euklidovské normy (je součástí topsis_vysledky)
        norm_matice = topsis_results.get('norm_matice', [[0] * len(kriteria) for _ in range(len(varianty))])
        
        # Ostatní potřebné hodnoty
        ideal = topsis_results.get('ideal', [0] * len(kriteria))
        anti_ideal = topsis_results.get('anti_ideal', [0] * len(kriteria))
        vazena_matice = topsis_results.get('vazena_matice', [[0] * len(kriteria) for _ in range(len(varianty))])
        dist_ideal = topsis_results.get('dist_ideal', [0] * len(varianty))
        dist_anti_ideal = topsis_results.get('dist_anti_ideal', [0] * len(varianty))
        relativni_blizkost = topsis_results.get('relativni_blizkost', [0] * len(varianty))
        
        postup_html = vytvor_sekci_postupu_topsis(
            vysledky_vypoctu['matice'],  # Původní matice
            norm_matice,               # Normalizovaná Euklidovská matice
            vazena_matice,             # Vážená matice
            vysledky_vypoctu['vahy'],  # Váhy
            ideal,                     # Ideální řešení
            anti_ideal,                # Anti-ideální řešení
            dist_ideal,                # Vzdálenosti od ideálního řešení
            dist_anti_ideal,           # Vzdálenosti od anti-ideálního řešení
            relativni_blizkost,        # Relativní blízkost
            varianty,
            kriteria,
            vysledky_vypoctu['typy_kriterii']
        )
        vysledky_html = vytvor_sekci_vysledku_topsis(topsis_results)
    elif metoda.upper() == "ELECTRE":
        # Extrakce dat specifických pro ELECTRE
        electre_results = vysledky_vypoctu['electre_vysledky']
        
        metodologie_html = vytvor_html_sekci_metodologie_electre(default_open=True)
        
        postup_html = vytvor_sekci_postupu_electre(
            electre_results['concordance_matrix'],
            electre_results['discordance_matrix'],
            electre_results['outranking_matrix'],
            varianty,
            electre_results['index_souhlasu'],
            electre_results['index_nesouhlasu']
        )
        
        vysledky_html = vytvor_sekci_vysledku_electre(
            electre_results,
            varianty,
            electre_results['index_souhlasu'],
            electre_results['index_nesouhlasu']
        )
    else:
        # Pro ostatní metody (budoucí implementace)
        metodologie_html = f"<div class='mcapp-card'><h2>Metodologie</h2><p>Metodologie pro metodu {metoda}</p></div>"
        postup_html = f"<div class='mcapp-section'><h2>Postup zpracování dat</h2><p>Postup zpracování dat metodou {metoda}</p></div>"
        vysledky_html = f"<div class='mcapp-section'><h2>Výsledky analýzy</h2><p>Výsledky analýzy metodou {metoda}</p></div>"
    
    # Sloučení všech částí do jednoho dokumentu
    html_obsah = f"""
    <div class="mcapp-wsm-results">
        {hlavicka_html}
        <div class="mcapp-card">
            {metodologie_html}
        </div>
        {vstupni_data_html}
        {postup_html}
        {vysledky_html}
    </div>
    """
    
    return html_obsah

def vytvor_html_normalizacni_tabulku(norm_matice, varianty, kriteria):
    """
    Vytvoří HTML tabulku s normalizovanými hodnotami.
    
    Args:
        norm_matice: 2D list s normalizovanými hodnotami [varianty][kriteria]
        varianty: Seznam názvů variant
        kriteria: Seznam názvů kritérií
        
    Returns:
        str: HTML kód tabulky s normalizovanými hodnotami
    """
    html = """
    <h3>Normalizovaná matice</h3>
    <div class="mcapp-table-container">
        <table class="mcapp-table mcapp-normalized-table">
            <thead>
                <tr>
                    <th>Varianta / Kritérium</th>
    """
    
    for krit in kriteria:
        html += f"<th>{krit}</th>"
    
    html += """
                </tr>
            </thead>
            <tbody>
    """
    
    for i, var in enumerate(varianty):
        html += f"<tr><td>{var}</td>"
        for j in range(len(kriteria)):
            html += f"<td>{norm_matice[i][j]:.3f}</td>"
        html += "</tr>"
    
    html += """
            </tbody>
        </table>
    </div>
    """
    
    return html

def vytvor_html_tabulku_vah(vahy, kriteria):
    """
    Vytvoří HTML tabulku s vahami kritérií.
    
    Args:
        vahy: Seznam vah kritérií
        kriteria: Seznam názvů kritérií
        
    Returns:
        str: HTML kód tabulky s vahami kritérií
    """
    html = """
    <h3>Váhy kritérií</h3>
    <div class="mcapp-table-container">
        <table class="mcapp-table mcapp-weights-table">
            <thead>
                <tr>
                    <th>Kritérium</th>
    """
    
    for krit in kriteria:
        html += f"<th>{krit}</th>"
    
    html += """
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Váha</td>
    """
    
    for i, vaha in enumerate(vahy):
        html += f"<td style='text-align: right;'>{vaha:.3f}</td>"
        
    html += """
                </tr>
            </tbody>
        </table>
    </div>
    """
    
    return html

def vytvor_html_tabulku_vazenych_hodnot(vazene_matice, varianty, kriteria):
    """
    Vytvoří HTML tabulku s váženými hodnotami včetně sloupce s celkovým skóre.
    
    Args:
        vazene_matice: 2D list s váženými hodnotami [varianty][kriteria]
        varianty: Seznam názvů variant
        kriteria: Seznam názvů kritérií
        
    Returns:
        str: HTML kód tabulky s váženými hodnotami
    """
    html = """
    <h3>Vážené hodnoty (normalizované hodnoty × váhy)</h3>
    <div class="mcapp-table-container">
        <table class="mcapp-table mcapp-weighted-table">
            <thead>
                <tr>
                    <th>Varianta / Kritérium</th>
    """
    
    for krit in kriteria:
        html += f"<th>{krit}</th>"
    
    # Přidáme sloupec součtu
    html += "<th style='background-color:#f0f0f0; font-weight:bold;'>Celkové skóre</th>"
    
    html += """
                </tr>
            </thead>
            <tbody>
    """
    
    for i, var in enumerate(varianty):
        html += f"<tr><td>{var}</td>"
        
        soucet = 0
        for j in range(len(kriteria)):
            hodnota = vazene_matice[i][j]
            soucet += hodnota
            html += f"<td>{hodnota:.3f}</td>"
            
        # Přidáme buňku s celkovým skóre
        html += f"<td style='background-color:#f0f0f0; font-weight:bold; text-align:right;'>{soucet:.3f}</td>"
        
        html += "</tr>"
    
    html += """
            </tbody>
        </table>
    </div>
    """
    
    return html

def vytvor_html_produktovou_tabulku(produkt_prispevek, varianty, kriteria):
    """
    Vytvoří HTML tabulku s produktovými příspěvky pro WPM metodu.
    
    Args:
        produkt_prispevek: 2D list s hodnotami umocněnými na váhy [varianty][kriteria]
        varianty: Seznam názvů variant
        kriteria: Seznam názvů kritérií
        
    Returns:
        str: HTML kód tabulky s produktovými příspěvky
    """
    html = """
    <h3>Hodnoty umocněné na váhy kritérií</h3>
    <p class="mcapp-note">
        Metoda WPM používá násobení hodnot kritérií umocněných na váhy místo sčítání.
        Níže jsou zobrazeny hodnoty po transformaci (1/x pro minimalizační kritéria) a umocnění na váhy.
        Celkové skóre je pak součinem všech těchto hodnot v řádku.
    </p>
    <div class="mcapp-table-container">
        <table class="mcapp-table mcapp-product-table">
            <thead>
                <tr>
                    <th>Varianta / Kritérium</th>
    """
    
    for krit in kriteria:
        html += f"<th>{krit}</th>"
    
    # Přidáme sloupec součinu
    html += "<th style='background-color:#f0f0f0; font-weight:bold;'>Celkové skóre</th>"
    
    html += """
                </tr>
            </thead>
            <tbody>
    """
    
    for i, var in enumerate(varianty):
        html += f"<tr><td>{var}</td>"
        
        soucin = 1.0
        for j in range(len(kriteria)):
            hodnota = produkt_prispevek[i][j]
            soucin *= hodnota
            html += f"<td>{hodnota:.3f}</td>"
            
        # Přidáme buňku s celkovým skóre
        html += f"<td style='background-color:#f0f0f0; font-weight:bold; text-align:right;'>{soucin:.3f}</td>"
        
        html += "</tr>"
    
    html += """
            </tbody>
        </table>
    </div>
    """
    
    return html

def vytvor_html_tabulku_vysledku_s_procenty(wsm_vysledky):
    """
    Vytvoří HTML tabulku s výsledky analýzy včetně procenta z maxima.
    
    Args:
        wsm_vysledky: Slovník s výsledky WSM analýzy
        
    Returns:
        str: HTML kód tabulky s výsledky
    """
    html = """
    <h3>Pořadí variant</h3>
    <div class="mcapp-table-container">
        <table class="mcapp-table mcapp-results-table">
            <thead>
                <tr>
                    <th>Pořadí</th>
                    <th>Varianta</th>
                    <th>Skóre</th>
                    <th>% z maxima</th>
                </tr>
            </thead>
            <tbody>
    """
    
    max_skore = wsm_vysledky['nejlepsi_skore']
    
    for varianta, poradi, skore in sorted(wsm_vysledky['results'], key=lambda x: x[1]):
        procento = (skore / max_skore) * 100 if max_skore > 0 else 0
        radek_styl = ""
        
        # Zvýraznění nejlepší a nejhorší varianty
        if varianta == wsm_vysledky['nejlepsi_varianta']:
            radek_styl = " style='background-color: #E0F7FA;'"  # Light Cyan for best
        elif varianta == wsm_vysledky['nejhorsi_varianta']:
            radek_styl = " style='background-color: #FFEBEE;'"  # Light Red for worst
            
        html += f"""
            <tr{radek_styl}>
                <td>{poradi}.</td>
                <td>{varianta}</td>
                <td style="text-align: right;">{skore:.3f}</td>
                <td style="text-align: right;">{procento:.1f}%</td>
            </tr>
        """
    
    html += """
            </tbody>
        </table>
    </div>
    """
    
    return html

def vytvor_html_shrnuti_vysledku_rozsirene(wsm_vysledky):
    """
    Vytvoří HTML shrnutí výsledků analýzy s dodatečnými informacemi.
    
    Args:
        wsm_vysledky: Slovník s výsledky WSM analýzy
        
    Returns:
        str: HTML kód se shrnutím výsledků
    """
    # Vypočítáme procento nejhoršího z maxima
    procento = (wsm_vysledky['nejhorsi_skore'] / wsm_vysledky['nejlepsi_skore'] * 100) if wsm_vysledky['nejlepsi_skore'] > 0 else 0
    
    html = f"""
    <div style="margin-top: 20px;">
        <h3>Shrnutí výsledků</h3>
        <ul style="list-style: none; padding-left: 5px;">
            <li><strong>Nejlepší varianta:</strong> {wsm_vysledky['nejlepsi_varianta']} (skóre: {wsm_vysledky['nejlepsi_skore']:.3f})</li>
            <li><strong>Nejhorší varianta:</strong> {wsm_vysledky['nejhorsi_varianta']} (skóre: {wsm_vysledky['nejhorsi_skore']:.3f})</li>
            <li><strong>Rozdíl nejlepší-nejhorší:</strong> {wsm_vysledky['rozdil_skore']:.3f}</li>
            <li><strong>Poměr nejhorší/nejlepší:</strong> {procento:.1f}% z maxima</li>
        </ul>
    </div>
    """
    
    return html

def vytvor_sekci_vstupnich_dat(analyza_data):
    """
    Vytvoří HTML sekci se vstupními daty analýzy.
    
    Args:
        analyza_data: Slovník s daty analýzy
    
    Returns:
        str: HTML kód pro sekci vstupních dat
    """
    # Tabulka kritérií
    kriteria_html = """
    <h3>Přehled kritérií</h3>
    <div class="mcapp-table-container">
        <table class="mcapp-table mcapp-criteria-table">
            <thead>
                <tr>
                    <th>Název kritéria</th>
                    <th>Typ</th>
                    <th>Váha</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for nazev_krit, krit_data in analyza_data.get('kriteria', {}).items():
        kriteria_html += f"""
            <tr>
                <td>{nazev_krit}</td>
                <td>{krit_data['typ'].upper()}</td>
                <td style="text-align: right;">{krit_data['vaha']:.3f}</td>
            </tr>
        """
    
    kriteria_html += """
            </tbody>
        </table>
    </div>
    """
    
    # Zobrazení prahových hodnot pro ELECTRE
    prahove_hodnoty_html = ""
    if analyza_data.get('metoda', '').upper() == 'ELECTRE' and 'parametry' in analyza_data:
        index_souhlasu = analyza_data.get('parametry', {}).get('index_souhlasu', 0.7)
        index_nesouhlasu = analyza_data.get('parametry', {}).get('index_nesouhlasu', 0.3)
        
        prahove_hodnoty_html = f"""
        <h3>Prahové hodnoty ELECTRE</h3>
        <div class="mcapp-table-container">
            <table class="mcapp-table mcapp-thresholds-table">
                <thead>
                    <tr>
                        <th>Parametr</th>
                        <th>Hodnota</th>
                        <th>Popis</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Index souhlasu (c*)</td>
                        <td style="text-align: center;">{index_souhlasu:.3f}</td>
                        <td>Minimální požadovaná míra souhlasu mezi variantami</td>
                    </tr>
                    <tr>
                        <td>Index nesouhlasu (d*)</td>
                        <td style="text-align: center;">{index_nesouhlasu:.3f}</td>
                        <td>Maximální povolená míra nesouhlasu mezi variantami</td>
                    </tr>
                </tbody>
            </table>
        </div>
        """
    
    # Tabulka variant (zůstává stejná)
    varianty_html = """
    <h3>Přehled variant</h3>
    <div class="mcapp-table-container">
        <table class="mcapp-table mcapp-variants-table">
            <thead>
                <tr>
                    <th>Název varianty</th>
                    <th>Popis</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for nazev_var, var_data in analyza_data.get('varianty', {}).items():
        popis = var_data.get('popis_varianty', '')
        varianty_html += f"""
            <tr>
                <td>{nazev_var}</td>
                <td>{popis}</td>
            </tr>
        """
    
    varianty_html += """
            </tbody>
        </table>
    </div>
    """
    
    # Původní hodnotící matice
    matice_html = """
    <h3>Hodnotící matice</h3>
    <div class="mcapp-table-container">
        <table class="mcapp-table mcapp-matrix-table">
            <thead>
                <tr>
                    <th>Kritérium</th>
    """
    
    # Přidání názvů variant do záhlaví
    varianty = list(analyza_data.get('varianty', {}).keys())
    for var in varianty:
        matice_html += f"<th>{var}</th>"
    
    matice_html += """
                </tr>
            </thead>
            <tbody>
    """
    
    # Přidání hodnot kritérií pro jednotlivé varianty
    kriteria_nazvy = list(analyza_data.get('kriteria', {}).keys())
    for krit in kriteria_nazvy:
        matice_html += f"<tr><td>{krit}</td>"
        
        for var in varianty:
            hodnota = analyza_data.get('varianty', {}).get(var, {}).get(krit, "N/A")
            
            # Formátování hodnoty pokud je číslo
            if isinstance(hodnota, (int, float)):
                hodnota_str = f"{hodnota:.2f}" if isinstance(hodnota, float) else str(hodnota)
            else:
                hodnota_str = str(hodnota)
                
            matice_html += f"<td style='text-align: right;'>{hodnota_str}</td>"
            
        matice_html += "</tr>"
    
    matice_html += """
            </tbody>
        </table>
    </div>
    """
    
    # Pokud existuje popis analýzy, přidáme ho
    popis_html = ""
    if analyza_data.get('popis_analyzy'):
        popis_html = f"""
        <div class="mcapp-description">
            <h3>Popis analýzy</h3>
            <p>{analyza_data.get('popis_analyzy')}</p>
        </div>
        """
    
    # Sloučení do sekce
    return f"""
    <div class="mcapp-section mcapp-input-data">
        <h2>Vstupní data</h2>
        {popis_html}
        <div class="mcapp-card">
            {kriteria_html}
        </div>
        {prahove_hodnoty_html and '<div class="mcapp-card">' + prahove_hodnoty_html + '</div>'}
        <div class="mcapp-card">
            {varianty_html}
        </div>
        <div class="mcapp-card">
            {matice_html}
        </div>
    </div>
    """

def vytvor_hlavicku_analyzy(nazev_analyzy, metoda="WSM"):
    """
    Vytvoří HTML hlavičku pro analýzu.
    
    Args:
        nazev_analyzy: Název analýzy
        metoda: Název použité metody (např. "WSM", "WPM", atd.)
    
    Returns:
        str: HTML kód pro hlavičku analýzy
    """
    metoda_nazev = {
        "WSM": "Weighted Sum Model",
        "WPM": "Weighted Product Model",
        "TOPSIS": "Technique for Order of Preference by Similarity to Ideal Solution",
        "ELECTRE": "Elimination Et Choix Traduisant la Réalité",
        "MABAC": "Multi-Attributive Border Approximation area Comparison"
    }.get(metoda.upper(), metoda)
    
    return f"""
    <div class="mcapp-section mcapp-header">
        <h1>{nazev_analyzy}</h1>
        <div class="mcapp-subtitle">Analýza metodou {metoda} ({metoda_nazev})</div>
    </div>
    """

def vytvor_sekci_vysledku(wsm_vysledky):
    """
    Vytvoří HTML sekci s výsledky analýzy.
    
    Args:
        wsm_vysledky: Slovník s výsledky WSM analýzy
        
    Returns:
        str: HTML kód pro sekci výsledků
    """
    # Tabulka výsledků
    vysledky_html = vytvor_html_tabulku_vysledku_s_procenty(wsm_vysledky)
    
    # Shrnutí výsledků
    shrnuti_html = vytvor_html_shrnuti_vysledku_rozsirene(wsm_vysledky)
    
    # Sloučení do sekce
    return f"""
    <div class="mcapp-section mcapp-results">
        <h2>Výsledky analýzy</h2>
        <div class="mcapp-card">
            {vysledky_html}
            {shrnuti_html}
        </div>
    </div>
    """
def vytvor_sekci_postupu_wpm(matice, produkt_prispevek, vahy, varianty, kriteria, typy_kriterii):
    """
    Vytvoří HTML sekci s postupem výpočtu WPM s použitím CSS místo JavaScriptu.
    
    Args:
        matice: Původní matice hodnot
        produkt_prispevek: 2D list s příspěvky jednotlivých kritérií
        vahy: Seznam vah kritérií
        varianty: Seznam názvů variant
        kriteria: Seznam názvů kritérií
        typy_kriterii: Seznam typů kritérií (max/min)
            
    Returns:
        str: HTML kód pro sekci postupu výpočtu
    """
    # Vytvoření normalizované matice (převrácené hodnoty pro min kritéria)
    norm_matice = []
    for i in range(len(matice)):
        radek = []
        for j in range(len(matice[0])):
            hodnota = matice[i][j]
            if hodnota <= 0:
                hodnota = 0.001  # Ochrana proti nule
                
            # Pro minimalizační kritéria použijeme převrácenou hodnotu
            if typy_kriterii[j].lower() in ("min", "cost"):
                norm_hodnota = 1.0 / hodnota
            else:
                norm_hodnota = hodnota
                
            radek.append(norm_hodnota)
        norm_matice.append(radek)
    
    # Tabulka normalizovaných hodnot
    normalizace_html = """
    <h3>Normalizovaná rozhodovací matice</h3>
    <p>Pro metodu WPM normalizujeme hodnoty tak, aby všechna kritéria byla maximalizační:</p>
    <ul>
        <li>Pro maximalizační kritéria použijeme původní hodnoty</li>
        <li>Pro minimalizační kritéria použijeme převrácené hodnoty (1/hodnota)</li>
    </ul>
    
    <div class="mcapp-table-container">
        <table class="mcapp-table mcapp-normalized-table">
            <thead>
                <tr>
                    <th>Varianta / Kritérium</th>
    """
    
    for i, krit in enumerate(kriteria):
        typ = typy_kriterii[i].upper()
        normalizace_html += f"<th>{krit} ({typ})</th>"
    
    normalizace_html += """
                </tr>
            </thead>
            <tbody>
    """
    
    for i, var in enumerate(varianty):
        normalizace_html += f"<tr><td><strong>{var}</strong></td>"
        for j in range(len(kriteria)):
            hodnota = norm_matice[i][j]
            normalizace_html += f"<td>{hodnota:.6f}</td>"
        normalizace_html += "</tr>"
    
    normalizace_html += """
            </tbody>
        </table>
    </div>
    """
    
    # Alternativní přístup - přidání sekce o poměrech
    alternativni_pristup_html = """
    <h3>Alternativní přístup - poměry mezi variantami</h3>
    <p>Další způsob analýzy WPM je vypočítat poměry mezi variantami:</p>
    <div class="mcapp-formula-box">
        <div class="mcapp-formula-row">
            <span class="mcapp-formula-content">R(A<sub>i</sub>/A<sub>j</sub>) = ∏<sub>k=1</sub><sup>n</sup>(x<sub>ik</sub>/x<sub>jk</sub>)<sup>w<sub>k</sub></sup></span>
        </div>
    </div>
    <p>Pokud R(A<sub>i</sub>/A<sub>j</sub>) ≥ 1, pak varianta A<sub>i</sub> je lepší nebo stejně dobrá jako varianta A<sub>j</sub>.</p>
    """
    
    # Tabulka vah
    vahy_html = """
    <h3>Váhy kritérií</h3>
    <div class="mcapp-table-container">
        <table class="mcapp-table mcapp-weights-table">
            <thead>
                <tr>
                    <th>Kritérium</th>
    """
    
    for krit in kriteria:
        vahy_html += f"<th>{krit}</th>"
    
    vahy_html += """
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Váha</td>
    """
    
    for i, vaha in enumerate(vahy):
        vahy_html += f"<td style='text-align: right;'>{vaha:.3f}</td>"
        
    vahy_html += """
                </tr>
            </tbody>
        </table>
    </div>
    """
    
    # Tabulka produktových příspěvků (bez popisu)
    produkty_html = """
    <h3>Hodnoty umocněné na váhy kritérií</h3>
    <div class="mcapp-table-container">
        <table class="mcapp-table mcapp-product-table">
            <thead>
                <tr>
                    <th>Varianta / Kritérium</th>
    """
    
    for krit in kriteria:
        produkty_html += f"<th>{krit}</th>"
    
    # Přidáme sloupec součinu
    produkty_html += "<th style='background-color:#f0f0f0; font-weight:bold;'>Celkové skóre</th>"
    
    produkty_html += """
                </tr>
            </thead>
            <tbody>
    """
    
    for i, var in enumerate(varianty):
        produkty_html += f"<tr><td>{var}</td>"
        
        soucin = 1.0
        for j in range(len(kriteria)):
            hodnota = produkt_prispevek[i][j]
            soucin *= hodnota
            produkty_html += f"<td>{hodnota:.6f}</td>"
            
        # Přidáme buňku s celkovým skóre
        produkty_html += f"<td style='background-color:#f0f0f0; font-weight:bold; text-align:right;'>{soucin:.6f}</td>"
        
        produkty_html += "</tr>"
    
    produkty_html += """
            </tbody>
        </table>
    </div>
    """

    # Sloučení do sekce
    return f"""
    <div class="mcapp-section mcapp-process">
        <h2>Postup zpracování dat</h2>
        <div class="mcapp-card">
            <h3>Krok 1: Normalizace rozhodovací matice</h3>
            {normalizace_html}
            {alternativni_pristup_html}
        </div>
        <div class="mcapp-card">
            <h3>Krok 2: Výpočet metodou WPM</h3>
            {vahy_html}
            {produkty_html}
        </div>
    </div>
    """

def vytvor_html_sekci_metodologie_topsis(default_open=True):
    """
    Vytvoří HTML sekci s popisem metodologie pro metodu TOPSIS, používá CSS místo JavaScriptu.
    
    Args:
        default_open: Zda má být sekce ve výchozím stavu otevřená
        
    Returns:
        str: HTML kód s metodologií
    """
    # Vytvoření unikátního ID pro tento přepínač
    toggle_id = "metodologie-topsis"
    default_class = "default-open" if default_open else ""
    
    return f"""
    <input type="checkbox" id="{toggle_id}" class="toggle-checkbox" {"checked" if default_open else ""}>
    <label for="{toggle_id}" class="details-toggle {default_class}">
        O metodě TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution)
        <span class="toggle-hint">Kliknutím zobrazíte/skryjete</span>
    </label>
    <div class="details-content">
        <div style="padding: 0;">
            <p>TOPSIS je metoda vícekriteriálního rozhodování založená na konceptu, že vybraná alternativa by měla mít nejkratší vzdálenost od ideálního řešení a nejdelší vzdálenost od negativního ideálního řešení.</p>
            
            <h4>Postup metody TOPSIS:</h4>
            <ol>
                <li><strong>Vektorizace rozhodovací matice</strong> - Normalizace hodnot pomocí Euklidovské normy, což umožňuje srovnávat kritéria s různými měrnými jednotkami.</li>
                <li><strong>Vážení hodnot</strong> - Vynásobení normalizovaných hodnot vahami kritérií.</li>
                <li><strong>Určení ideálního a anti-ideálního řešení</strong> - Pro každé kritérium se určí ideální (nejlepší možná) a anti-ideální (nejhorší možná) hodnota.</li>
                <li><strong>Výpočet vzdáleností</strong> - Pro každou variantu se vypočítá vzdálenost od ideálního a anti-ideálního řešení.</li>
                <li><strong>Výpočet relativní blízkosti k ideálnímu řešení</strong> - Kombinace obou vzdáleností do jednoho ukazatele.</li>
                <li><strong>Seřazení variant</strong> - Varianty jsou seřazeny podle relativní blízkosti k ideálnímu řešení (vyšší hodnota znamená lepší variantu).</li>
            </ol>
            
            <h4>Výhody metody:</h4>
            <ul>
                <li>Zohledňuje nejlepší i nejhorší možné řešení</li>
                <li>Jednoduchá interpretace výsledků - čím blíže k 1, tím lépe</li>
                <li>Robustní vůči změnám v datech</li>
                <li>Vhodná pro velký počet kritérií a variant</li>
            </ul>
            
            <h4>Omezení metody:</h4>
            <ul>
                <li>Může být citlivá na extrémní hodnoty</li>
                <li>Výsledek závisí na volbě způsobu normalizace</li>
                <li>Potenciál "rank reversal" - přidání nové varianty může změnit pořadí stávajících variant</li>
            </ul>
        </div>
    </div>
    """

def vytvor_html_normalizacni_tabulku_euklidovska(matice, norm_matice, varianty, kriteria):
    """
    Vytvoří HTML tabulku s normalizovanými hodnotami podle Euklidovské normy
    s rozšířeným vysvětlením principu.
    
    Args:
        matice: 2D list s původními hodnotami [varianty][kriteria]
        norm_matice: 2D list s normalizovanými hodnotami [varianty][kriteria]
        varianty: Seznam názvů variant
        kriteria: Seznam názvů kritérií
        
    Returns:
        str: HTML kód tabulky s normalizovanými hodnotami
    """
    html = """
    <h3>Normalizovaná matice pomocí Euklidovské normy</h3>
    <div class="mcapp-explanation">
        <p>
            V metodě TOPSIS se pro normalizaci používá Euklidovská norma, která zachovává vzájemné vztahy mezi hodnotami:
        </p>
        <div class="mcapp-formula-box">
            <div class="mcapp-formula-row">
                <span class="mcapp-formula-label">Euklidovská norma sloupce:</span>
                <span class="mcapp-formula-content">norma<sub>j</sub> = √(∑<sub>i=1</sub><sup>m</sup>(x<sub>ij</sub>²))</span>
            </div>
            <div class="mcapp-formula-row">
                <span class="mcapp-formula-label">Normalizovaná hodnota:</span>
                <span class="mcapp-formula-content">r<sub>ij</sub> = x<sub>ij</sub> / norma<sub>j</sub></span>
            </div>
        </div>
        <div class="mcapp-note">
            <p>kde x<sub>ij</sub> je původní hodnota i-té varianty pro j-té kritérium.</p>
            <p>Výsledkem jsou hodnoty v intervalu [0,1], přičemž součet čtverců hodnot v každém sloupci je roven 1.</p>
            <p>Na rozdíl od min-max normalizace, Euklidovská normalizace zachovává vzájemné vztahy mezi hodnotami.</p>
        </div>
    </div>
    
    <div class="mcapp-table-container">
        <table class="mcapp-table mcapp-normalized-table">
            <thead>
                <tr>
                    <th>Kritérium</th>
                    <th>Euklidovská norma</th>
    """
    
    for var in varianty:
        html += f"<th>{var}</th>"
    
    html += """
                </tr>
            </thead>
            <tbody>
    """
    
    for j in range(len(kriteria)):
        html += f"<tr><td>{kriteria[j]}</td>"
        
        # Výpočet Euklidovské normy pro dané kritérium
        sloupec = [matice[i][j] for i in range(len(varianty))]
        norma = (sum(x**2 for x in sloupec)) ** 0.5
        
        html += f"<td>{norma:.4f}</td>"
        
        for i in range(len(varianty)):
            html += f"<td>{norm_matice[i][j]:.4f}</td>"
            
        html += "</tr>"
    
    html += """
            </tbody>
        </table>
    </div>
    """
    
    return html

def vytvor_html_tabulku_vazenych_hodnot_topsis(vazena_matice, ideal, anti_ideal, varianty, kriteria, typy_kriterii):
    """
    Vytvoří HTML tabulku s váženými hodnotami a ideálním/anti-ideálním řešením.
    
    Args:
        vazena_matice: 2D list s váženými hodnotami [varianty][kriteria]
        ideal: Seznam ideálních hodnot pro každé kritérium
        anti_ideal: Seznam anti-ideálních hodnot pro každé kritérium
        varianty: Seznam názvů variant
        kriteria: Seznam názvů kritérií
        typy_kriterii: Seznam typů kritérií (max/min)
        
    Returns:
        str: HTML kód tabulky s váženými hodnotami
    """
    html = """
    <h3>Vážené hodnoty a ideální/anti-ideální řešení</h3>
    <p>
        V tomto kroku vynásobíme normalizované hodnoty váhami jednotlivých kritérií a určíme ideální a anti-ideální řešení.
    </p>
    <div class="mcapp-table-container">
        <table class="mcapp-table mcapp-weighted-table">
            <thead>
                <tr>
                    <th>Varianta / Kritérium</th>
    """
    
    for j, krit in enumerate(kriteria):
        typ = typy_kriterii[j].upper() if j < len(typy_kriterii) else "?"
        html += f"<th>{krit} ({typ})</th>"
    
    html += """
                </tr>
            </thead>
            <tbody>
    """
    
    for i, var in enumerate(varianty):
        html += f"<tr><td>{var}</td>"
        
        for j in range(len(kriteria)):
            hodnota = vazena_matice[i][j]
            html += f"<td>{hodnota:.4f}</td>"
            
        html += "</tr>"
    
    # Přidáme řádek pro ideální řešení
    html += "<tr style='background-color:#E0F7FA; font-weight:bold;'><td>Ideální řešení (A*)</td>"
    for j in range(len(kriteria)):
        html += f"<td>{ideal[j]:.4f}</td>"
    html += "</tr>"
    
    # Přidáme řádek pro anti-ideální řešení
    html += "<tr style='background-color:#FFEBEE; font-weight:bold;'><td>Anti-ideální řešení (A-)</td>"
    for j in range(len(kriteria)):
        html += f"<td>{anti_ideal[j]:.4f}</td>"
    html += "</tr>"
    
    html += """
            </tbody>
        </table>
    </div>
    <p class="mcapp-note">
        Pro maximalizační kritéria je ideální hodnota maximum a anti-ideální minimum.
        Pro minimalizační kritéria je to naopak - ideální hodnota je minimum a anti-ideální maximum.
    </p>
    """
    
    return html

def vytvor_html_tabulku_vzdalenosti_topsis(dist_ideal, dist_anti_ideal, relativni_blizkost, varianty):
    """
    Vytvoří HTML tabulku se vzdálenostmi a relativní blízkostí k ideálnímu řešení.
    
    Args:
        dist_ideal: Seznam vzdáleností od ideálního řešení
        dist_anti_ideal: Seznam vzdáleností od anti-ideálního řešení
        relativni_blizkost: Seznam relativních blízkostí k ideálnímu řešení
        varianty: Seznam názvů variant
        
    Returns:
        str: HTML kód tabulky se vzdálenostmi
    """
    html = """
    <div class="mcapp-explanation">
        <h4>Výpočet vzdáleností a relativní blízkosti k ideálnímu řešení:</h4>
        <div class="mcapp-formula-box">
            <div class="mcapp-formula-row">
                <span class="mcapp-formula-label">Vzdálenost od ideálního řešení (S*):</span>
                <span class="mcapp-formula-content">S*<sub>i</sub> = √(∑<sub>j=1</sub><sup>n</sup> (v<sub>ij</sub> - v<sub>j</sub><sup>+</sup>)<sup>2</sup>)</span>
            </div>
            <div class="mcapp-formula-row">
                <span class="mcapp-formula-label">Vzdálenost od anti-ideálního řešení (S-):</span>
                <span class="mcapp-formula-content">S-<sub>i</sub> = √(∑<sub>j=1</sub><sup>n</sup> (v<sub>ij</sub> - v<sub>j</sub><sup>-</sup>)<sup>2</sup>)</span>
            </div>
            <div class="mcapp-formula-row">
                <span class="mcapp-formula-label">Relativní blízkost k ideálnímu řešení (C*):</span>
                <span class="mcapp-formula-content">C*<sub>i</sub> = S-<sub>i</sub> / (S*<sub>i</sub> + S-<sub>i</sub>)</span>
            </div>
        </div>
        <div class="mcapp-note">
            <p>kde v<sub>ij</sub> je vážená hodnota i-té varianty pro j-té kritérium,
            v<sub>j</sub><sup>+</sup> je j-tá hodnota ideálního řešení a
            v<sub>j</sub><sup>-</sup> je j-tá hodnota anti-ideálního řešení.</p>
            <p>Relativní blízkost C*<sub>i</sub> nabývá hodnot v intervalu [0,1], kde hodnota blížící se 1 znamená ideální řešení
            a hodnota blížící se 0 znamená anti-ideální řešení.</p>
        </div>
    </div>
    
    <div class="mcapp-table-container">
        <table class="mcapp-table mcapp-distances-table">
            <thead>
                <tr>
                    <th>Varianta</th>
                    <th>Vzdálenost od ideálního řešení (S*)</th>
                    <th>Vzdálenost od anti-ideálního řešení (S-)</th>
                    <th>Relativní blízkost k ideálnímu řešení (C*)</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for i, var in enumerate(varianty):
        html += f"""
            <tr>
                <td>{var}</td>
                <td style="text-align: right;">{dist_ideal[i]:.4f}</td>
                <td style="text-align: right;">{dist_anti_ideal[i]:.4f}</td>
                <td style="text-align: right; font-weight: bold;">{relativni_blizkost[i]:.4f}</td>
            </tr>
        """
    
    html += """
            </tbody>
        </table>
    </div>
    <p class="mcapp-note">
        Varianty jsou následně seřazeny podle hodnoty relativní blízkosti k ideálnímu řešení (C*) sestupně.
        Varianta s nejvyšší hodnotou C* je považována za nejlepší.
    </p>
    """
    
    return html

def vytvor_sekci_postupu_topsis(matice, norm_matice, vazena_matice, vahy, ideal, anti_ideal, dist_ideal, dist_anti_ideal, relativni_blizkost, varianty, kriteria, typy_kriterii):
    """
    Vytvoří HTML sekci s postupem výpočtu TOPSIS.
    
    Args:
        matice: Původní matice hodnot
        norm_matice: Normalizovaná matice hodnot podle Euklidovské normy
        vazena_matice: Vážená matice hodnot
        vahy: Seznam vah kritérií
        ideal: Seznam ideálních hodnot pro každé kritérium
        anti_ideal: Seznam anti-ideálních hodnot pro každé kritérium
        dist_ideal: Seznam vzdáleností od ideálního řešení
        dist_anti_ideal: Seznam vzdáleností od anti-ideálního řešení
        relativni_blizkost: Seznam relativních blízkostí k ideálnímu řešení
        varianty: Seznam názvů variant
        kriteria: Seznam názvů kritérií
        typy_kriterii: Seznam typů kritérií (max/min)
            
    Returns:
        str: HTML kód pro sekci postupu výpočtu
    """
    # Normalizační tabulka podle Euklidovské normy
    normalizace_html = vytvor_html_normalizacni_tabulku_euklidovska(matice, norm_matice, varianty, kriteria)
    
    # Tabulka vah
    vahy_html = vytvor_html_tabulku_vah(vahy, kriteria)
    
    # Tabulka vážených hodnot
    vazene_html = vytvor_html_tabulku_vazenych_hodnot_topsis(vazena_matice, ideal, anti_ideal, varianty, kriteria, typy_kriterii)
    
    # Tabulka vzdáleností a relativní blízkosti
    vzdalenosti_html = vytvor_html_tabulku_vzdalenosti_topsis(dist_ideal, dist_anti_ideal, relativni_blizkost, varianty)

    # Sloučení do sekce
    return f"""
    <div class="mcapp-section mcapp-process">
        <h2>Postup zpracování dat</h2>
        <div class="mcapp-card">
            <h3>Krok 1: Vektorizace rozhodovací matice (Euklidovská normalizace)</h3>
            {normalizace_html}
        </div>
        <div class="mcapp-card">
            <h3>Krok 2: Vážení hodnot a určení ideálního a anti-ideálního řešení</h3>
            {vahy_html}
            {vazene_html}
        </div>
        <div class="mcapp-card">
            <h3>Krok 3: Výpočet vzdáleností a relativní blízkosti k ideálnímu řešení</h3>
            {vzdalenosti_html}
        </div>
    </div>
    """

def vytvor_html_tabulku_vysledku_topsis(topsis_vysledky):
    """
    Vytvoří HTML tabulku s výsledky TOPSIS analýzy včetně relativní blízkosti.
    
    Args:
        topsis_vysledky: Slovník s výsledky TOPSIS analýzy
        
    Returns:
        str: HTML kód tabulky s výsledky
    """
    html = """
    <h3>Pořadí variant</h3>
    <div class="mcapp-table-container">
        <table class="mcapp-table mcapp-results-table">
            <thead>
                <tr>
                    <th>Pořadí</th>
                    <th>Varianta</th>
                    <th>Relativní blízkost (C*)</th>
                    <th>% z maxima</th>
                </tr>
            </thead>
            <tbody>
    """
    
    max_skore = topsis_vysledky['nejlepsi_skore']
    
    for varianta, poradi, skore in sorted(topsis_vysledky['results'], key=lambda x: x[1]):
        procento = (skore / max_skore) * 100 if max_skore > 0 else 0
        radek_styl = ""
        
        # Zvýraznění nejlepší a nejhorší varianty
        if varianta == topsis_vysledky['nejlepsi_varianta']:
            radek_styl = " style='background-color: #E0F7FA;'"  # Light Cyan for best
        elif varianta == topsis_vysledky['nejhorsi_varianta']:
            radek_styl = " style='background-color: #FFEBEE;'"  # Light Red for worst
            
        html += f"""
            <tr{radek_styl}>
                <td>{poradi}.</td>
                <td>{varianta}</td>
                <td style="text-align: right;">{skore:.4f}</td>
                <td style="text-align: right;">{procento:.1f}%</td>
            </tr>
        """
    
    html += """
            </tbody>
        </table>
    </div>
    """
    
    return html

def vytvor_html_shrnuti_vysledku_topsis(topsis_vysledky):
    """
    Vytvoří HTML shrnutí výsledků TOPSIS analýzy s dodatečnými informacemi.
    
    Args:
        topsis_vysledky: Slovník s výsledky TOPSIS analýzy
        
    Returns:
        str: HTML kód se shrnutím výsledků
    """
    # Extrakce dat
    nejlepsi_varianta = topsis_vysledky.get('nejlepsi_varianta', 'N/A')
    nejlepsi_skore = topsis_vysledky.get('nejlepsi_skore', 0)
    nejhorsi_varianta = topsis_vysledky.get('nejhorsi_varianta', 'N/A')
    nejhorsi_skore = topsis_vysledky.get('nejhorsi_skore', 0)
    
    # Vypočítáme procento nejhoršího z maxima
    procento = (nejhorsi_skore / nejlepsi_skore * 100) if nejlepsi_skore > 0 else 0
    
    html = f"""
    <div style="margin-top: 20px;">
        <h3>Shrnutí výsledků</h3>
        <ul style="list-style: none; padding-left: 5px;">
            <li><strong>Nejlepší varianta:</strong> {nejlepsi_varianta} (relativní blízkost: {nejlepsi_skore:.4f})</li>
            <li><strong>Nejhorší varianta:</strong> {nejhorsi_varianta} (relativní blízkost: {nejhorsi_skore:.4f})</li>
            <li><strong>Rozdíl nejlepší-nejhorší:</strong> {nejlepsi_skore - nejhorsi_skore:.4f}</li>
            <li><strong>Poměr nejhorší/nejlepší:</strong> {procento:.1f}% z maxima</li>
        </ul>
        <p>
            Relativní blízkost k ideálnímu řešení (C*) nabývá hodnot v intervalu [0,1], kde hodnota blížící se 1 znamená ideální řešení.
            Vyšší hodnota C* indikuje lepší variantu.
        </p>
    </div>
    """
    
    return html

def vytvor_sekci_vysledku_topsis(topsis_vysledky):
    """
    Vytvoří HTML sekci s výsledky TOPSIS analýzy.
    
    Args:
        topsis_vysledky: Slovník s výsledky TOPSIS analýzy
        
    Returns:
        str: HTML kód pro sekci výsledků
    """
    # Tabulka výsledků
    vysledky_html = vytvor_html_tabulku_vysledku_topsis(topsis_vysledky)
    
    # Shrnutí výsledků
    shrnuti_html = vytvor_html_shrnuti_vysledku_topsis(topsis_vysledky)
    
    # Sloučení do sekce
    return f"""
    <div class="mcapp-section mcapp-results">
        <h2>Výsledky analýzy</h2>
        <div class="mcapp-card">
            {vysledky_html}
            {shrnuti_html}
        </div>
    </div>
    """

def vytvor_html_sekci_metodologie_electre(default_open=True):
    """
    Vytvoří HTML sekci s popisem metodologie pro metodu ELECTRE.
    
    Args:
        default_open: Zda má být sekce ve výchozím stavu otevřená
        
    Returns:
        str: HTML kód s metodologií
    """
    # Vytvoření unikátního ID pro tento přepínač
    toggle_id = "metodologie-electre"
    default_class = "default-open" if default_open else ""
    
    return f"""
    <input type="checkbox" id="{toggle_id}" class="toggle-checkbox" {"checked" if default_open else ""}>
    <label for="{toggle_id}" class="details-toggle {default_class}">
        O metodě ELECTRE (Elimination Et Choix Traduisant la Réalité)
        <span class="toggle-hint">Kliknutím zobrazíte/skryjete</span>
    </label>
    <div class="details-content">
        <div style="padding: 0;">
            <p>ELECTRE je metoda vícekriteriálního rozhodování vyvinutá ve Francii, jejíž název znamená "Elimination and Choice Expressing Reality". Je založena na porovnávání párů alternativ a vytváření tzv. outranking (převahových) vztahů.</p>
            
            <h4>Postup metody ELECTRE:</h4>
            <ol>
                <li><strong>Normalizace kritérií</strong> - Převod různorodých kritérií na srovnatelnou škálu pomocí min-max normalizace.</li>
                <li><strong>Výpočet matice souhlasu (concordance matrix)</strong> - Určuje, do jaké míry kritéria podporují tvrzení, že varianta A je alespoň tak dobrá jako varianta B.</li>
                <li><strong>Výpočet matice nesouhlasu (discordance matrix)</strong> - Určuje, do jaké míry existují kritéria, která silně odporují tvrzení, že varianta A je alespoň tak dobrá jako varianta B.</li>
                <li><strong>Vytvoření matice převahy (outranking matrix)</strong> - Zohledňuje jak míru souhlasu, tak nesouhlasu pomocí prahových hodnot.</li>
                <li><strong>Určení dominance a nadvlády</strong> - Z výsledné matice převahy jsou odvozeny vztahy dominance mezi variantami.</li>
                <li><strong>Finální seřazení variant</strong> - Na základě dominanční struktury jsou varianty seřazeny od nejlepší po nejhorší.</li>
            </ol>
            
            <h4>Parametry metody ELECTRE:</h4>
            <ul>
                <li><strong>Index souhlasu (Concordance threshold)</strong> - Určuje minimální požadovanou míru souhlasu (běžně 0.5-0.8).</li>
                <li><strong>Index nesouhlasu (Discordance threshold)</strong> - Určuje maximální povolenou míru nesouhlasu (běžně 0.2-0.4).</li>
            </ul>
            
            <h4>Výhody metody:</h4>
            <ul>
                <li>Schopnost pracovat s nekompletními informacemi a nejistotou</li>
                <li>Zohledňuje možnost neporovnatelnosti alternativ</li>
                <li>Schopnost identifikovat nekompenzovatelné slabiny variant</li>
                <li>Vhodná pro problémy s velkým počtem kritérií a alternativ</li>
            </ul>
            
            <h4>Omezení metody:</h4>
            <ul>
                <li>Složitější interpretace než u jiných metod</li>
                <li>Výsledky jsou citlivé na volbu prahových hodnot</li>
                <li>Ne vždy poskytuje úplné uspořádání alternativ</li>
                <li>Výpočetně složitější než některé jiné metody</li>
            </ul>
        </div>
    </div>
    """

def vytvor_html_prahove_hodnoty_electre(index_souhlasu, index_nesouhlasu):
    """
    Vytvoří HTML box zobrazující aktuální prahové hodnoty pro metodu ELECTRE.
    
    Args:
        index_souhlasu: Aktuální hodnota indexu souhlasu
        index_nesouhlasu: Aktuální hodnota indexu nesouhlasu
    
    Returns:
        str: HTML kód s vysvětlením prahových hodnot
    """
    return f"""
    <div class="mcapp-card" style="margin-top: 16px; margin-bottom: 24px;">
        <h3>Nastavené prahové hodnoty</h3>
        <div class="mcapp-explanation">
            <p>Metoda ELECTRE používá dvě prahové hodnoty, které určují, kdy jedna varianta převyšuje druhou:</p>
            
            <div class="mcapp-formula-box">
                <div class="mcapp-formula-row">
                    <span class="mcapp-formula-label">Index souhlasu (c*):</span>
                    <span class="mcapp-formula-content">{index_souhlasu:.2f}</span>
                </div>
                <div class="mcapp-formula-row">
                    <span class="mcapp-formula-label">Index nesouhlasu (d*):</span>
                    <span class="mcapp-formula-content">{index_nesouhlasu:.2f}</span>
                </div>
            </div>
            
            <div class="mcapp-note">
                <p><strong>Index souhlasu (c*)</strong> - Čím vyšší hodnota, tím přísnější je podmínka pro "souhlas" s tvrzením, že jedna varianta je lepší než druhá.</p>
                <p><strong>Index nesouhlasu (d*)</strong> - Čím nižší hodnota, tím přísnější je podmínka pro "nesouhlas" s tvrzením, že jedna varianta je lepší než druhá.</p>
                <p>Tyto hodnoty lze upravit v sekci Nastavení aplikace.</p>
            </div>
        </div>
    </div>
    """

def vytvor_html_tabulku_concordance_matrix(concordance_matrix, varianty, index_souhlasu):
    """
    Vytvoří HTML tabulku zobrazující matici souhlasu metody ELECTRE.
    
    Args:
        concordance_matrix: 2D matice hodnot souhlasu mezi variantami
        varianty: Seznam názvů variant
        index_souhlasu: Prahová hodnota indexu souhlasu
        
    Returns:
        str: HTML kód tabulky s maticí souhlasu
    """
    html = """
    <h3>Matice souhlasu (Concordance matrix)</h3>
    <div class="mcapp-explanation">
        <p>
            Matice souhlasu vyjadřuje, do jaké míry kritéria podporují tvrzení, že varianta v řádku i je alespoň tak dobrá jako varianta 
            ve sloupci j. Hodnoty blízké 1 znamenají silný souhlas, hodnoty blízké 0 slabý souhlas.
        </p>
    </div>
    <div class="mcapp-table-container">
        <table class="mcapp-table mcapp-concordance-table">
            <thead>
                <tr>
                    <th>C(i,j)</th>
    """
    
    for var in varianty:
        html += f"<th>{var}</th>"
    
    html += """
                </tr>
            </thead>
            <tbody>
    """
    
    for i, var_i in enumerate(varianty):
        html += f"<tr><td><strong>{var_i}</strong></td>"
        
        for j, _ in enumerate(varianty):
            if i == j:
                # Diagonální prvky jsou vždy "-"
                html += "<td style='text-align: center;'>-</td>"
            else:
                hodnota = concordance_matrix[i][j]
                buňka_styl = ""
                if hodnota >= index_souhlasu:
                    buňka_styl = "background-color: #E0F7FA; font-weight: bold;"  # Světle modrá pro hodnoty nad prahem
                html += f"<td style='text-align: center; {buňka_styl}'>{hodnota:.3f}</td>"
                
        html += "</tr>"
    
    html += """
            </tbody>
        </table>
    </div>
    <div class="mcapp-note">
        <p>
            Poznámka: Buňky zvýrazněné světle modrou barvou splňují podmínku C(i,j) ≥ {0}, tedy hodnoty nad prahem souhlasu.
        </p>
    </div>
    """.format(index_souhlasu)
    
    return html

def vytvor_html_tabulku_discordance_matrix(discordance_matrix, varianty, index_nesouhlasu):
    """
    Vytvoří HTML tabulku zobrazující matici nesouhlasu metody ELECTRE.
    
    Args:
        discordance_matrix: 2D matice hodnot nesouhlasu mezi variantami
        varianty: Seznam názvů variant
        index_nesouhlasu: Prahová hodnota indexu nesouhlasu
        
    Returns:
        str: HTML kód tabulky s maticí nesouhlasu
    """
    html = """
    <h3>Matice nesouhlasu (Discordance matrix)</h3>
    <div class="mcapp-explanation">
        <p>
            Matice nesouhlasu vyjadřuje, do jaké míry existují kritéria, která silně odporují tvrzení, že varianta v řádku i je
            alespoň tak dobrá jako varianta ve sloupci j. Hodnoty blízké 0 znamenají slabý nesouhlas, hodnoty blízké 1 silný nesouhlas.
        </p>
    </div>
    <div class="mcapp-table-container">
        <table class="mcapp-table mcapp-discordance-table">
            <thead>
                <tr>
                    <th>D(i,j)</th>
    """
    
    for var in varianty:
        html += f"<th>{var}</th>"
    
    html += """
                </tr>
            </thead>
            <tbody>
    """
    
    for i, var_i in enumerate(varianty):
        html += f"<tr><td><strong>{var_i}</strong></td>"
        
        for j, _ in enumerate(varianty):
            if i == j:
                # Diagonální prvky jsou vždy "-"
                html += "<td style='text-align: center;'>-</td>"
            else:
                hodnota = discordance_matrix[i][j]
                buňka_styl = ""
                if hodnota <= index_nesouhlasu:
                    buňka_styl = "background-color: #FFEBEE; font-weight: bold;"  # Světle červená pro hodnoty pod prahem
                html += f"<td style='text-align: center; {buňka_styl}'>{hodnota:.3f}</td>"
                
        html += "</tr>"
    
    html += """
            </tbody>
        </table>
    </div>
    <div class="mcapp-note">
        <p>
            Poznámka: Buňky zvýrazněné světle červenou barvou splňují podmínku D(i,j) ≤ {0}, tedy hodnoty pod prahem nesouhlasu.
        </p>
    </div>
    """.format(index_nesouhlasu)
    
    return html

def vytvor_html_tabulku_outranking_matrix(outranking_matrix, varianty):
    """
    Vytvoří HTML tabulku zobrazující matici převahy metody ELECTRE.
    
    Args:
        outranking_matrix: 2D binární matice převahy mezi variantami (0/1)
        varianty: Seznam názvů variant
        
    Returns:
        str: HTML kód tabulky s maticí převahy
    """
    html = """
    <h3>Matice převahy (Outranking matrix)</h3>
    <div class="mcapp-explanation">
        <p>
            Matice převahy kombinuje matici souhlasu a nesouhlasu a ukazuje, která varianta převyšuje kterou.
            Hodnota 1 (Ano) znamená, že varianta v řádku i převyšuje variantu ve sloupci j,
            hodnota 0 (Ne) znamená, že varianta i nepřevyšuje variantu j.
        </p>
    </div>
    <div class="mcapp-table-container">
        <table class="mcapp-table mcapp-outranking-table">
            <thead>
                <tr>
                    <th>O(i,j)</th>
    """
    
    for var in varianty:
        html += f"<th>{var}</th>"
    
    html += """
                </tr>
            </thead>
            <tbody>
    """
    
    for i, var_i in enumerate(varianty):
        html += f"<tr><td><strong>{var_i}</strong></td>"
        
        for j, _ in enumerate(varianty):
            if i == j:
                # Diagonální prvky jsou vždy "-"
                html += "<td style='text-align: center;'>-</td>"
            else:
                hodnota = outranking_matrix[i][j]
                buňka_text = "Ano" if hodnota == 1 else "Ne"
                buňka_styl = "background-color: #E8F5E9; font-weight: bold;" if hodnota == 1 else ""  # Světle zelená pro 1
                html += f"<td style='text-align: center; {buňka_styl}'>{buňka_text}</td>"
                
        html += "</tr>"
    
    html += """
            </tbody>
        </table>
    </div>
    """
    
    return html

def vytvor_html_net_flow_ranking(net_flows, varianty):
    """
    Vytvoří HTML tabulku zobrazující pořadí variant podle Net Flow Score.
    
    Args:
        net_flows: List trojic (varianta, pořadí, net_flow)
        varianty: Seznam názvů variant
        
    Returns:
        str: HTML kód tabulky s pořadím variant
    """
    html = """
    <h3>Pořadí variant podle Net Flow Score</h3>
    <div class="mcapp-explanation">
        <p>
            Net Flow Score je pro každou variantu vypočítáno jako rozdíl mezi počtem variant, které daná varianta převyšuje,
            a počtem variant, které převyšují ji. Čím vyšší Net Flow Score, tím lepší je varianta.
        </p>
    </div>
    <div class="mcapp-table-container">
        <table class="mcapp-table mcapp-results-table">
            <thead>
                <tr>
                    <th>Pořadí</th>
                    <th>Varianta</th>
                    <th>Net Flow Score</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # Seřazení podle pořadí
    sorted_net_flows = sorted(net_flows, key=lambda x: x[1])
    
    for varianta, poradi, score in sorted_net_flows:
        radek_styl = ""
        
        # Zvýraznění nejlepší a nejhorší varianty
        if poradi == 1:
            radek_styl = " style='background-color: #E0F7FA;'"  # Světle modrá pro nejlepší
        elif poradi == len(varianty):
            radek_styl = " style='background-color: #FFEBEE;'"  # Světle červená pro nejhorší
            
        html += f"""
            <tr{radek_styl}>
                <td>{poradi}.</td>
                <td>{varianta}</td>
                <td style="text-align: right;">{score}</td>
            </tr>
        """
    
    html += """
            </tbody>
        </table>
    </div>
    """
    
    return html

def vytvor_sekci_postupu_electre(norm_matice, matice, concordance_matrix, discordance_matrix, outranking_matrix, varianty, kriteria, typy_kriterii, index_souhlasu, index_nesouhlasu):
    """
    Vytvoří HTML sekci s postupem výpočtu ELECTRE.
    
    Args:
        norm_matice: Normalizovaná matice hodnot
        matice: Původní matice hodnot
        concordance_matrix: 2D matice hodnot souhlasu
        discordance_matrix: 2D matice hodnot nesouhlasu
        outranking_matrix: 2D binární matice převahy
        varianty: Seznam názvů variant
        kriteria: Seznam názvů kritérií
        typy_kriterii: Seznam typů kritérií
        index_souhlasu: Prahová hodnota indexu souhlasu
        index_nesouhlasu: Prahová hodnota indexu nesouhlasu
            
    Returns:
        str: HTML kód pro sekci postupu výpočtu
    """
    # Krok 1: Normalizace matice
    normalizace_html = vytvor_html_normalizacni_tabulku_minmax(matice, norm_matice, varianty, kriteria, typy_kriterii)
    
    # Krok 2: Výpočet matice souhlasu
    concordance_html = """
    <h3>Matice souhlasu (Concordance matrix)</h3>
    <div class="mcapp-explanation">
        <p>
            Matice souhlasu vyjadřuje, do jaké míry kritéria podporují tvrzení, že varianta v řádku i je alespoň tak dobrá jako varianta 
            ve sloupci j.
        </p>
        <div class="mcapp-formula-box">
            <div class="mcapp-formula-row">
                <span class="mcapp-formula-label">Výpočet indexu souhlasu:</span>
                <span class="mcapp-formula-content">C(i,j) = ∑<sub>k∈K(i,j)</sub> w<sub>k</sub></span>
            </div>
        </div>
        <p>kde K(i,j) je množina kritérií, pro která je varianta i alespoň tak dobrá jako varianta j, a w<sub>k</sub> je váha k-tého kritéria.</p>
    </div>
    <div class="mcapp-table-container">
        <table class="mcapp-table mcapp-concordance-table">
            <thead>
                <tr>
                    <th>C(i,j)</th>
    """
    
    for var in varianty:
        concordance_html += f"<th>{var}</th>"
    
    concordance_html += """
                </tr>
            </thead>
            <tbody>
    """
    
    for i, var_i in enumerate(varianty):
        concordance_html += f"<tr><td><strong>{var_i}</strong></td>"
        
        for j, _ in enumerate(varianty):
            if i == j:
                # Diagonální prvky jsou vždy "-"
                concordance_html += f"<td style='text-align: center;'>-</td>"
            else:
                hodnota = concordance_matrix[i][j]
                buňka_styl = ""
                if hodnota >= index_souhlasu:
                    buňka_styl = "background-color: #E0F7FA; font-weight: bold;"  # Světle modrá pro hodnoty nad prahem
                concordance_html += f"<td style='text-align: center; {buňka_styl}'>{hodnota:.3f}</td>"
                
        concordance_html += "</tr>"
    
    concordance_html += f"""
            </tbody>
        </table>
    </div>
    <div class="mcapp-note">
        <p>
            Poznámka: Buňky zvýrazněné světle modrou barvou splňují podmínku C(i,j) ≥ {index_souhlasu:.3f}, tedy hodnoty nad prahem souhlasu.
        </p>
    </div>
    """
    
    # Krok 3: Výpočet matice nesouhlasu
    discordance_html = """
    <h3>Matice nesouhlasu (Discordance matrix)</h3>
    <div class="mcapp-explanation">
        <p>
            Matice nesouhlasu vyjadřuje, do jaké míry existují kritéria, která silně odporují tvrzení, že varianta v řádku i je
            alespoň tak dobrá jako varianta ve sloupci j.
        </p>
        <div class="mcapp-formula-box">
            <div class="mcapp-formula-row">
                <span class="mcapp-formula-label">Výpočet indexu nesouhlasu:</span>
                <span class="mcapp-formula-content">D(i,j) = max<sub>k∈K'(i,j)</sub> [ (r<sub>jk</sub> - r<sub>ik</sub>) / R ]</span>
            </div>
        </div>
        <p>kde K'(i,j) je množina kritérií, pro která je varianta j lepší než varianta i, r<sub>ik</sub> je normalizovaná hodnota varianty i pro kritérium k a R je rozsah normalizované škály (typicky 1).</p>
    </div>
    <div class="mcapp-table-container">
        <table class="mcapp-table mcapp-discordance-table">
            <thead>
                <tr>
                    <th>D(i,j)</th>
    """
    
    for var in varianty:
        discordance_html += f"<th>{var}</th>"
    
    discordance_html += """
                </tr>
            </thead>
            <tbody>
    """
    
    for i, var_i in enumerate(varianty):
        discordance_html += f"<tr><td><strong>{var_i}</strong></td>"
        
        for j, _ in enumerate(varianty):
            if i == j:
                # Diagonální prvky jsou vždy "-"
                discordance_html += f"<td style='text-align: center;'>-</td>"
            else:
                hodnota = discordance_matrix[i][j]
                buňka_styl = ""
                if hodnota <= index_nesouhlasu:
                    buňka_styl = "background-color: #FFEBEE; font-weight: bold;"  # Světle červená pro hodnoty pod prahem
                discordance_html += f"<td style='text-align: center; {buňka_styl}'>{hodnota:.3f}</td>"
                
        discordance_html += "</tr>"
    
    discordance_html += f"""
            </tbody>
        </table>
    </div>
    <div class="mcapp-note">
        <p>
            Poznámka: Buňky zvýrazněné světle červenou barvou splňují podmínku D(i,j) ≤ {index_nesouhlasu:.3f}, tedy hodnoty pod prahem nesouhlasu.
        </p>
    </div>
    """
    
    # Krok 4: Výpočet matice převahy
    outranking_html = """
    <h3>Matice převahy (Outranking matrix)</h3>
    <div class="mcapp-explanation">
        <p>
            Matice převahy kombinuje matici souhlasu a nesouhlasu a ukazuje, která varianta převyšuje kterou.
            Hodnota 1 (Ano) znamená, že varianta v řádku i převyšuje variantu ve sloupci j,
            hodnota 0 (Ne) znamená, že varianta i nepřevyšuje variantu j.
        </p>
        <div class="mcapp-formula-box">
            <div class="mcapp-formula-row">
                <span class="mcapp-formula-content">
                    O(i,j) = 1, pokud C(i,j) ≥ {0:.3f} a D(i,j) ≤ {1:.3f}
                </span>
            </div>
            <div class="mcapp-formula-row">
                <span class="mcapp-formula-content">
                    O(i,j) = 0, jinak
                </span>
            </div>
        </div>
    </div>
    <div class="mcapp-table-container">
        <table class="mcapp-table mcapp-outranking-table">
            <thead>
                <tr>
                    <th>O(i,j)</th>
    """.format(index_souhlasu, index_nesouhlasu)
    
    for var in varianty:
        outranking_html += f"<th>{var}</th>"
    
    outranking_html += """
                </tr>
            </thead>
            <tbody>
    """
    
    for i, var_i in enumerate(varianty):
        outranking_html += f"<tr><td><strong>{var_i}</strong></td>"
        
        for j, _ in enumerate(varianty):
            if i == j:
                # Diagonální prvky jsou vždy "-"
                outranking_html += f"<td style='text-align: center;'>-</td>"
            else:
                hodnota = outranking_matrix[i][j]
                buňka_text = "Ano" if hodnota == 1 else "Ne"
                buňka_styl = "background-color: #E8F5E9; font-weight: bold;" if hodnota == 1 else ""  # Světle zelená pro 1
                outranking_html += f"<td style='text-align: center; {buňka_styl}'>{buňka_text}</td>"
                
        outranking_html += "</tr>"
    
    outranking_html += """
            </tbody>
        </table>
    </div>
    """
    
    # Sloučení do sekce
    return f"""
    <div class="mcapp-section mcapp-process">
        <h2>Postup zpracování dat</h2>
        <div class="mcapp-card">
            <h3>Krok 1: Normalizace rozhodovací matice</h3>
            {normalizace_html}
        </div>
        <div class="mcapp-card">
            <h3>Krok 2: Výpočet matice souhlasu</h3>
            {concordance_html}
        </div>
        <div class="mcapp-card">
            <h3>Krok 3: Výpočet matice nesouhlasu</h3>
            {discordance_html}
        </div>
        <div class="mcapp-card">
            <h3>Krok 4: Výpočet matice převahy</h3>
            {outranking_html}
        </div>
    </div>
    """

def vytvor_sekci_vysledku_electre(electre_vysledky, varianty, index_souhlasu, index_nesouhlasu):
    """
    Vytvoří HTML sekci s výsledky ELECTRE analýzy.
    
    Args:
        electre_vysledky: Slovník s výsledky ELECTRE analýzy
        varianty: Seznam názvů variant
        index_souhlasu: Prahová hodnota indexu souhlasu
        index_nesouhlasu: Prahová hodnota indexu nesouhlasu
        
    Returns:
        str: HTML kód pro sekci výsledků
    """
    # Prahové hodnoty
    prahove_hodnoty_html = vytvor_html_prahove_hodnoty_electre(index_souhlasu, index_nesouhlasu)
    
    # Tabulka pořadí variant podle Net Flow
    net_flow_html = vytvor_html_net_flow_ranking(electre_vysledky["results"], varianty)
    
    # Sloučení do sekce
    return f"""
    <div class="mcapp-section mcapp-results">
        <h2>Výsledky analýzy</h2>
        <div class="mcapp-card">
            {prahove_hodnoty_html}
            {net_flow_html}
        </div>
    </div>
    """