# client_code/vizualizace.py
# -------------------------------------------------------
# Modul: vizualizace
# Obsahuje sdílené funkce pro tvorbu grafů a vizualizací
# -------------------------------------------------------

import plotly.graph_objects as go
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

def vytvor_heat_mapu(varianty, kriteria, hodnoty, nazev_metody=""):
    """
    Vytvoří teplotní mapu zobrazující vztahy mezi variantami a kritérii.
    
    Args:
        varianty: Seznam názvů variant
        kriteria: Seznam názvů kritérií
        hodnoty: 2D list hodnot [varianty][kriteria]
        nazev_metody: Název metody pro titulek
        
    Returns:
        dict: Plotly figure configuration
    """
    try:
        # Vytvoření grafu
        fig = {
            'data': [{
                'type': 'heatmap',
                'z': hodnoty,
                'x': kriteria,
                'y': varianty,
                'colorscale': 'Blues',
                'text': [[f'{hodnoty[i][j]:.3f}' for j in range(len(kriteria))] for i in range(len(varianty))],
                'hoverinfo': 'text',
                'showscale': True,
                'colorbar': {
                    'title': 'Hodnota'
                },
            }],
            'layout': {
                'title': f'Teplotní mapa hodnot{f" - {nazev_metody}" if nazev_metody else ""}',
                'xaxis': {
                    'title': 'Kritéria',
                    'side': 'top',
                },
                'yaxis': {
                    'title': 'Varianty',
                },
                'margin': {'t': 50, 'b': 50, 'l': 100, 'r': 50}
            }
        }
        
        return fig
    except Exception as e:
        Utils.zapsat_chybu(f"Chyba při vytváření teplotní mapy: {str(e)}")
        # Vrátíme prázdný graf
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

#
# Pomocné funkce pro generování HTML obsahu
#

def vytvor_html_nadpis(text, uroven=1, css_class=""):
    """
    Vytvoří HTML nadpis.
    
    Args:
        text: Text nadpisu
        uroven: Úroveň nadpisu (1-6)
        css_class: Volitelná CSS třída
        
    Returns:
        str: HTML kód nadpisu
    """
    if uroven < 1 or uroven > 6:
        uroven = 1  # Defaultní hodnota, pokud je mimo rozsah
    
    class_attr = f' class="{css_class}"' if css_class else ''
    return f"<h{uroven}{class_attr}>{text}</h{uroven}>"

def vytvor_html_odstavec(text, css_class=""):
    """
    Vytvoří HTML odstavec.
    
    Args:
        text: Text odstavce
        css_class: Volitelná CSS třída
        
    Returns:
        str: HTML kód odstavce
    """
    class_attr = f' class="{css_class}"' if css_class else ''
    return f"<p{class_attr}>{text}</p>"

def vytvor_html_seznam(polozky, serazeny=False, css_class=""):
    """
    Vytvoří HTML seznam.
    
    Args:
        polozky: Seznam položek
        serazeny: True pro číslovaný seznam, False pro odrážkový
        css_class: Volitelná CSS třída
        
    Returns:
        str: HTML kód seznamu
    """
    tag = "ol" if serazeny else "ul"
    class_attr = f' class="{css_class}"' if css_class else ''
    
    html = f"<{tag}{class_attr}>\n"
    for item in polozky:
        html += f"  <li>{item}</li>\n"
    html += f"</{tag}>"
    
    return html

def vytvor_html_tabulku_hodnot(varianty, kriteria, hodnoty, caption="", css_class="", formatovaci_funkce=None):
    """
    Vytvoří HTML tabulku s hodnotami pro zobrazení v RichText komponentě.
    
    Args:
        varianty: Seznam názvů variant
        kriteria: Seznam názvů kritérií
        hodnoty: 2D list hodnot [varianty][kriteria]
        caption: Volitelný nadpis tabulky
        css_class: Volitelná CSS třída pro tabulku
        formatovaci_funkce: Volitelná funkce pro formátování hodnot (float -> str)
        
    Returns:
        str: HTML kód tabulky
    """
    class_attr = f' class="{css_class}"' if css_class else ''
    
    html = f"""
    <table{class_attr} style="width:100%; border-collapse:collapse; margin-bottom:20px;">
    """
    
    if caption:
        html += f'<caption style="font-weight:bold; margin-bottom:10px;">{caption}</caption>'
    
    # Hlavička tabulky
    html += """
    <thead>
        <tr>
            <th style="border:1px solid #ddd; padding:8px; text-align:left; background-color:#f2f2f2;">Varianta / Kritérium</th>
    """
    
    for krit in kriteria:
        html += f'<th style="border:1px solid #ddd; padding:8px; text-align:center; word-break:break-word; background-color:#f2f2f2;">{krit}</th>'
    
    html += """
        </tr>
    </thead>
    <tbody>
    """
    
    # Tělo tabulky
    for i, var in enumerate(varianty):
        row_style = ' style="background-color:#f9f9f9;"' if i % 2 == 0 else ''
        html += f'<tr{row_style}><td style="border:1px solid #ddd; padding:8px; font-weight:bold;">{var}</td>'
        
        for j, _ in enumerate(kriteria):
            hodnota = hodnoty[i][j]
            
            # Formátování hodnoty podle funkce nebo výchozí formát
            if formatovaci_funkce:
                hodnota_str = formatovaci_funkce(hodnota)
            elif isinstance(hodnota, float):
                hodnota_str = f"{hodnota:.3f}"
            else:
                hodnota_str = str(hodnota)
                
            html += f'<td style="border:1px solid #ddd; padding:8px; text-align:right;">{hodnota_str}</td>'
        
        html += '</tr>'
    
    html += """
    </tbody>
    </table>
    """
    
    return html

def vytvor_html_tabulku_kriterii(kriteria_dict, caption="Kritéria", css_class=""):
    """
    Vytvoří HTML tabulku kritérií z formátu slovníku.
    
    Args:
        kriteria_dict: Slovník kritérií ve formátu {nazev_kriteria: {typ: "max/min", vaha: 0.5}}
        caption: Nadpis tabulky
        css_class: Volitelná CSS třída
        
    Returns:
        str: HTML kód tabulky
    """
    class_attr = f' class="{css_class}"' if css_class else ''
    
    html = f"""
    <table{class_attr} style="width:100%; border-collapse:collapse; margin-bottom:20px;">
    """
    
    if caption:
        html += f'<caption style="font-weight:bold; margin-bottom:10px;">{caption}</caption>'
    
    # Hlavička tabulky
    html += """
    <thead>
        <tr>
            <th style="border:1px solid #ddd; padding:8px; text-align:left; background-color:#f2f2f2;">Název kritéria</th>
            <th style="border:1px solid #ddd; padding:8px; text-align:center; background-color:#f2f2f2;">Typ</th>
            <th style="border:1px solid #ddd; padding:8px; text-align:right; background-color:#f2f2f2;">Váha</th>
        </tr>
    </thead>
    <tbody>
    """
    
    # Tělo tabulky
    for i, (nazev_krit, krit_data) in enumerate(kriteria_dict.items()):
        row_style = ' style="background-color:#f9f9f9;"' if i % 2 == 0 else ''
        vaha = float(krit_data['vaha'])
        html += f"""
        <tr{row_style}>
          <td style="border:1px solid #ddd; padding:8px; word-break:break-word;">{nazev_krit}</td>
          <td style="border:1px solid #ddd; padding:8px; text-align:center;">{krit_data['typ'].upper()}</td>
          <td style="border:1px solid #ddd; padding:8px; text-align:right;">{vaha:.3f}</td>
        </tr>
        """
    
    html += """
    </tbody>
    </table>
    """
    
    return html

def vytvor_html_tabulku_variant(varianty_dict, caption="Varianty", css_class=""):
    """
    Vytvoří HTML tabulku variant z formátu slovníku.
    
    Args:
        varianty_dict: Slovník variant ve formátu {nazev_varianty: {popis_varianty: "popis", ...}}
        caption: Nadpis tabulky
        css_class: Volitelná CSS třída
        
    Returns:
        str: HTML kód tabulky
    """
    class_attr = f' class="{css_class}"' if css_class else ''
    
    html = f"""
    <table{class_attr} style="width:100%; border-collapse:collapse; margin-bottom:20px;">
    """
    
    if caption:
        html += f'<caption style="font-weight:bold; margin-bottom:10px;">{caption}</caption>'
    
    # Hlavička tabulky
    html += """
    <thead>
        <tr>
            <th style="border:1px solid #ddd; padding:8px; text-align:left; background-color:#f2f2f2;">Název varianty</th>
            <th style="border:1px solid #ddd; padding:8px; text-align:left; background-color:#f2f2f2;">Popis</th>
        </tr>
    </thead>
    <tbody>
    """
    
    # Tělo tabulky
    for i, (nazev_var, var_data) in enumerate(varianty_dict.items()):
        row_style = ' style="background-color:#f9f9f9;"' if i % 2 == 0 else ''
        popis = var_data.get('popis_varianty', '')
        html += f"""
        <tr{row_style}>
          <td style="border:1px solid #ddd; padding:8px; font-weight:bold;">{nazev_var}</td>
          <td style="border:1px solid #ddd; padding:8px;">{popis}</td>
        </tr>
        """
    
    html += """
    </tbody>
    </table>
    """
    
    return html

def vytvor_html_matici_hodnot(varianty, kriteria, hodnoty_dict, caption="Hodnotící matice", css_class=""):
    """
    Vytvoří HTML tabulku původní matice hodnot z JSON formátu.
    
    Args:
        varianty: Seznam názvů variant
        kriteria: Seznam názvů kritérií
        hodnoty_dict: Slovník hodnot ve formátu {nazev_varianty: {nazev_kriteria: hodnota}}
        caption: Nadpis tabulky
        css_class: Volitelná CSS třída
        
    Returns:
        str: HTML kód tabulky
    """
    class_attr = f' class="{css_class}"' if css_class else ''
    
    html = f"""
    <table{class_attr} style="width:100%; border-collapse:collapse; margin-bottom:20px;">
    """
    
    if caption:
        html += f'<caption style="font-weight:bold; margin-bottom:10px;">{caption}</caption>'
    
    # Hlavička tabulky
    html += """
    <thead>
        <tr>
            <th style="border:1px solid #ddd; padding:8px; text-align:left; background-color:#f2f2f2;">Kritérium</th>
    """
    
    for var in varianty:
        html += f'<th style="border:1px solid #ddd; padding:8px; text-align:center; background-color:#f2f2f2;">{var}</th>'
    
    html += """
        </tr>
    </thead>
    <tbody>
    """
    
    # Tělo tabulky
    for i, krit in enumerate(kriteria):
        row_style = ' style="background-color:#f9f9f9;"' if i % 2 == 0 else ''
        html += f'<tr{row_style}><td style="border:1px solid #ddd; padding:8px; font-weight:bold;">{krit}</td>'
        
        for var in varianty:
            # Získání hodnoty - může být různého typu
            hodnota = "N/A"
            var_data = hodnoty_dict.get(var, {})
            
            if krit in var_data:
                hodnota_raw = var_data[krit]
                if isinstance(hodnota_raw, (int, float)):
                    hodnota = f"{hodnota_raw:.2f}"
                else:
                    hodnota = str(hodnota_raw)
            
            html += f'<td style="border:1px solid #ddd; padding:8px; text-align:right;">{hodnota}</td>'
        
        html += '</tr>'
    
    html += """
    </tbody>
    </table>
    """
    
    return html

def vytvor_html_tabulku_vysledku(results, popis_sloupcu=None, caption="Výsledky analýzy", css_class=""):
    """
    Vytvoří HTML tabulku s výsledky analýzy.
    
    Args:
        results: Seznam výsledků ve formátu [(varianta, poradi, skore)]
        popis_sloupcu: Volitelný slovník s popisem sloupců {index: "popis"}
        caption: Nadpis tabulky
        css_class: Volitelná CSS třída
        
    Returns:
        str: HTML kód tabulky
    """
    class_attr = f' class="{css_class}"' if css_class else ''
    
    # Výchozí popisky sloupců
    if not popis_sloupcu:
        popis_sloupcu = {
            0: "Pořadí",
            1: "Varianta",
            2: "Skóre"
        }
    
    html = f"""
    <table{class_attr} style="width:100%; border-collapse:collapse; margin-bottom:20px;">
    """
    
    if caption:
        html += f'<caption style="font-weight:bold; margin-bottom:10px;">{caption}</caption>'
    
    # Hlavička tabulky
    html += """
    <thead>
        <tr>
    """
    
    for i in range(len(popis_sloupcu)):
        html += f'<th style="border:1px solid #ddd; padding:8px; text-align:center; background-color:#f2f2f2;">{popis_sloupcu[i]}</th>'
    
    html += """
        </tr>
    </thead>
    <tbody>
    """
    
    # Tělo tabulky - seřazené podle pořadí (index 1)
    for i, result_row in enumerate(sorted(results, key=lambda x: x[1])):
        row_style = ' style="background-color:#f9f9f9;"' if i % 2 == 0 else ''
        html += f'<tr{row_style}>'
        
        # Pořadí
        html += f'<td style="border:1px solid #ddd; padding:8px; text-align:center;">{result_row[1]}.</td>'
        
        # Název varianty
        html += f'<td style="border:1px solid #ddd; padding:8px; font-weight:bold;">{result_row[0]}</td>'
        
        # Skóre
        skore = result_row[2]
        html += f'<td style="border:1px solid #ddd; padding:8px; text-align:right;">{skore:.3f}</td>'
        
        html += '</tr>'
    
    html += """
    </tbody>
    </table>
    """
    
    return html

def vytvor_html_karta(obsah, titulek=None, css_class=""):
    """
    Vytvoří stylovanou HTML kartu kolem obsahu.
    
    Args:
        obsah: HTML obsah karty
        titulek: Volitelný titulek karty
        css_class: Volitelná CSS třída
        
    Returns:
        str: HTML kód karty
    """
    class_attr = f' class="{css_class}"' if css_class else ''
    
    html = f"""
    <div{class_attr} style="border:1px solid #ddd; border-radius:4px; padding:15px; margin-bottom:20px; background-color:white; box-shadow:0 2px 4px rgba(0,0,0,0.1);">
    """
    
    if titulek:
        html += f'<div style="border-bottom:1px solid #eee; margin-bottom:15px; padding-bottom:10px;"><h3 style="margin:0;">{titulek}</h3></div>'
    
    html += f"""
        {obsah}
    </div>
    """
    
    return html

def vytvor_html_shrnuti_metody(nazev_metody, popis, vyhody=None, nevyhody=None, css_class=""):
    """
    Vytvoří HTML shrnutí metody s popisem, výhodami a nevýhodami.
    
    Args:
        nazev_metody: Název metody
        popis: Popis metody
        vyhody: Seznam výhod metody
        nevyhody: Seznam nevýhod metody
        css_class: Volitelná CSS třída
        
    Returns:
        str: HTML kód shrnutí
    """
    class_attr = f' class="{css_class}"' if css_class else ''
    
    html = f"""
    <div{class_attr} style="margin-bottom:20px;">
        <h3>O metodě {nazev_metody}</h3>
        <p>{popis}</p>
    """
    
    if vyhody:
        html += """
        <h4>Výhody metody:</h4>
        <ul>
        """
        for vyhoda in vyhody:
            html += f'<li>{vyhoda}</li>'
        html += '</ul>'
    
    if nevyhody:
        html += """
        <h4>Omezení metody:</h4>
        <ul>
        """
        for nevyhoda in nevyhody:
            html += f'<li>{nevyhoda}</li>'
        html += '</ul>'
    
    html += '</div>'
    
    return html

def vytvor_html_shrnuti_vysledku(nejlepsi_varianta, nejlepsi_skore, nejhorsi_varianta=None, nejhorsi_skore=None, vlastnosti=None, css_class=""):
    """
    Vytvoří HTML shrnutí výsledků analýzy.
    
    Args:
        nejlepsi_varianta: Název nejlepší varianty
        nejlepsi_skore: Skóre nejlepší varianty
        nejhorsi_varianta: Volitelně název nejhorší varianty
        nejhorsi_skore: Volitelně skóre nejhorší varianty
        vlastnosti: Volitelný slovník dalších vlastností {nazev: hodnota}
        css_class: Volitelná CSS třída
        
    Returns:
        str: HTML kód shrnutí
    """
    class_attr = f' class="{css_class}"' if css_class else ''
    
    html = f"""
    <div{class_attr} style="margin-bottom:20px;">
        <h3>Shrnutí výsledků</h3>
        <ul style="list-style:none; padding-left:5px;">
          <li><strong>Nejlepší varianta:</strong> {nejlepsi_varianta} (skóre: {nejlepsi_skore:.3f})</li>
    """
    
    if nejhorsi_varianta and nejhorsi_skore is not None:
        html += f'<li><strong>Nejhorší varianta:</strong> {nejhorsi_varianta} (skóre: {nejhorsi_skore:.3f})</li>'
        html += f'<li><strong>Rozdíl nejlepší-nejhorší:</strong> {(nejlepsi_skore - nejhorsi_skore):.3f}</li>'
    
    if vlastnosti:
        for nazev, hodnota in vlastnosti.items():
            # Formátování hodnoty podle typu
            if isinstance(hodnota, float):
                hodnota_str = f"{hodnota:.3f}"
            else:
                hodnota_str = str(hodnota)
                
            html += f'<li><strong>{nazev}:</strong> {hodnota_str}</li>'
    
    html += '</ul></div>'
    
    return html

def vytvor_html_vysledek_analyzy(analyza_data, wsm_vysledky, metoda="WSM"):
    """
    Vytvoří kompletní HTML dokument s výsledky analýzy.
    
    Args:
        analyza_data: Slovník s daty analýzy
        wsm_vysledky: Slovník s výsledky WSM analýzy
        metoda: Název metody
        
    Returns:
        str: HTML kód výsledku analýzy
    """
    # Hlavička dokumentu
    html = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6;">
        <h2>{analyza_data['nazev']} - Výsledky analýzy {metoda}</h2>
    """
    
    # Sekce výsledky - tabulka s výsledky
    vysledky_sekce = vytvor_html_tabulku_vysledku(
        wsm_vysledky['results'],
        {0: "Pořadí", 1: "Varianta", 2: "Skóre"},
        "Pořadí variant"
    )
    
    # Sekce shrnutí
    procento = (wsm_vysledky['nejhorsi_skore'] / wsm_vysledky['nejlepsi_skore'] * 100) if wsm_vysledky['nejlepsi_skore'] > 0 else 0
    
    shrnuti_sekce = vytvor_html_shrnuti_vysledku(
        wsm_vysledky['nejlepsi_varianta'],
        wsm_vysledky['nejlepsi_skore'],
        wsm_vysledky['nejhorsi_varianta'],
        wsm_vysledky['nejhorsi_skore'],
        {"Poměr nejhorší/nejlepší": f"{procento:.1f}% z maxima"}
    )
    
    # Sekce metoda
    metoda_sekce = vytvor_html_shrnuti_metody(
        metoda,
        f"{metoda}, také známý jako Simple Additive Weighting (SAW), je jedna z nejjednodušších a nejpoužívanějších metod vícekriteriálního rozhodování.",
        [
            "Jednoduchá a intuitivní",
            "Transparentní výpočty a výsledky",
            "Snadná interpretace"
        ],
        [
            "Předpokládá lineární užitek",
            "Není vhodná pro silně konfliktní kritéria",
            "Méně robustní vůči extrémním hodnotám než některé pokročilejší metody"
        ]
    )
    
    # Sloučení všech sekcí do jedné karty
    vysledky_karta = vytvor_html_karta(
        vysledky_sekce + shrnuti_sekce + metoda_sekce,
        "Výsledek analýzy"
    )
    
    html += vysledky_karta
    html += '</div>'
    
    return html

# Doplnění modulu o pokročilejší generátory HTML obsahu

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
                <p>WPM je metoda vícekriteriálního rozhodování, která na rozdíl od WSM používá násobení místo sčítání.</p>
                
                <h4>Postup metody WPM:</h4>
                <ol>
                    <li><strong>Sběr dat</strong> - Definice variant, kritérií a hodnocení variant podle kritérií.</li>
                    <li><strong>Určení vah kritérií</strong> - Přiřazení vah jednotlivým kritériím.</li>
                    <li><strong>Porovnání variant</strong> - Výpočet poměrů hodnot variant, umocněných na váhy kritérií.</li>
                    <li><strong>Výpočet celkového skóre</strong> - Násobení těchto poměrů pro každou variantu.</li>
                    <li><strong>Seřazení variant</strong> - Seřazení variant podle celkového skóre.</li>
                </ol>
                
                <h4>Výhody metody:</h4>
                <ul>
                    <li>Eliminuje potřebu normalizace jednotek</li>
                    <li>Méně citlivá na extrémní hodnoty</li>
                    <li>Výhodnější pro některé typy rozhodovacích problémů</li>
                </ul>
                
                <h4>Omezení metody:</h4>
                <ul>
                    <li>Složitější interpretace výsledků</li>
                    <li>Problémy s nulovými hodnotami</li>
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

def vytvor_sekci_postupu(norm_matice, vazene_matice, vahy, varianty, kriteria, typy_kriterii):
    """
    Vytvoří HTML sekci s postupem výpočtu s použitím CSS místo JavaScriptu.
    
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
    metodologie_html = vytvor_html_sekci_metodologie(metoda, default_open=True)
    vstupni_data_html = vytvor_sekci_vstupnich_dat(analyza_data)
    postup_html = vytvor_sekci_postupu(
        vysledky_vypoctu['norm_vysledky']['normalizovana_matice'],
        vysledky_vypoctu['vazene_matice'],
        vysledky_vypoctu['vahy'],
        varianty,
        kriteria,
        vysledky_vypoctu['typy_kriterii']
    )
    vysledky_html = vytvor_sekci_vysledku(vysledky_vypoctu['wsm_vysledky'])
    
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
    
    # Tabulka variant
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
