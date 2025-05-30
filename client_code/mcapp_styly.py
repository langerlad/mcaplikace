# -------------------------------------------------------
# Modul: mcapp_styly
# Obsahuje styly pro formátování výstupů analýz
# -------------------------------------------------------

def ziskej_css_styly():
    """
    Vrátí řetězec s CSS styly pro výstupy analýz.
    
    Returns:
        str: CSS styly jako řetězec
    """
    return """
    /* Hlavní kontejner pro výsledky */
    .mcapp-wsm-results {
      font-family: 'Roboto', Arial, sans-serif;
      color: rgba(0, 0, 0, 0.87);
      line-height: 1.5;
      max-width: 100%;
      margin: 0 auto;
    }

    /* Sekce */
    .mcapp-section {
      margin-bottom: 32px;
    }

    .mcapp-section h2 {
      font-size: 24px;
      margin-bottom: 16px;
      color: #1976D2; /* Primary 700 */
      border-bottom: 2px solid #E0E0E0; /* Gray 300 */
      padding-bottom: 8px;
    }

    .mcapp-section h3 {
      font-size: 20px;
      margin-top: 16px;
      margin-bottom: 8px;
      color: #2196F3; /* Primary 500 */
    }

    .mcapp-section h4 {
      font-size: 16px;
      margin-top: 12px;
      margin-bottom: 8px;
      color: #424242; /* Gray 800 */
    }

    /* Hlavička */
    .mcapp-header {
      text-align: center;
      margin-bottom: 24px;
    }

    .mcapp-header h1 {
      font-size: 28px;
      margin-bottom: 4px;
      color: #1976D2; /* Primary 700 */
    }

    .mcapp-subtitle {
      font-size: 18px;
      color: #757575; /* Gray 600 */
    }

    /* Karty */
    .mcapp-card {
      background-color: white;
      border-radius: 2px;
      padding: 16px 20px;
      margin-bottom: 24px;
      /* 2dp */  
      box-shadow: 0 2px 2px 0 rgba(0, 0, 0, 0.14), 0 3px 1px -2px rgba(0, 0, 0, 0.2), 0 1px 5px 0 rgba(0, 0, 0, 0.12);
    }

    /* Popis analýzy */
    .mcapp-description {
      background-color: #F5F5F5; /* Gray 100 */
      padding: 12px 16px;
      border-radius: 2px;
      margin-bottom: 16px;
    }

    .mcapp-description p {
      margin: 8px 0;
    }

    /* Metodologie */
    .mcapp-methodology ol {
      margin-left: 16px;
      padding-left: 16px;
    }

    .mcapp-methodology li {
      margin-bottom: 8px;
    }

    /* Vysvětlení */
    .mcapp-explanation {
      background-color: #F5F5F5; /* Gray 100 */
      padding: 16px;
      margin: 16px 0;
      border-radius: 2px;
    }

    /* Box s vzorci */
    .mcapp-formula-box {
      background-color: white;
      border: 1px solid #E0E0E0; /* Gray 300 */
      padding: 12px 16px;
      margin: 12px 0;
      border-radius: 2px;
    }

    .mcapp-formula-row {
      display: flex;
      margin-bottom: 8px;
    }

    .mcapp-formula-label {
      flex: 0 0 40%;
      font-weight: 500;
      padding-right: 16px;
    }

    .mcapp-formula-content {
      flex: 0 0 60%;
      font-family: 'Roboto Mono', monospace;
    }

    /* Poznámky */
    .mcapp-note {
      font-size: 14px;
      font-style: italic;
      color: #757575; /* Gray 600 */
      margin-top: 8px;
    }

    .mcapp-note p {
      margin: 4px 0;
    }

    /* Tabulky */
    .mcapp-table-container {
      width: 100%;
      overflow-x: auto;
      margin-bottom: 16px;
    }

    .mcapp-table {
      width: 100%;
      border-collapse: collapse;
      margin: 0;
      font-size: 14px;
      min-width: 100%;
    }

    .mcapp-table caption {
      font-weight: bold;
      margin-bottom: 8px;
      text-align: left;
      font-size: 16px;
    }

    .mcapp-table th, .mcapp-table td {
      border: 1px solid #E0E0E0; /* Gray 300 */
      padding: 8px 12px;
      /* Umožňujeme zalomení textu (změna proti původní verzi) */
      white-space: normal;
      word-wrap: break-word;
    }

    /* Omezení šířky sloupců pro lepší přehlednost */
    .mcapp-table th {
      background-color: #F5F5F5; /* Gray 100 */
      text-align: left;
      font-weight: 500;
      position: sticky;
      top: 0;
      z-index: 10;
      max-width: 200px; /* Omezení šířky pro lepší přehlednost */
    }
    
    /* Řádkové buňky mohou být širší */
    .mcapp-table td:first-child {
      max-width: 300px;
    }

    .mcapp-table tr:nth-child(even) {
      background-color: #FAFAFA; /* Gray 50 */
    }

    /* Specifická pravidla pro tabulky */
    .mcapp-criteria-table th:first-child,
    .mcapp-variants-table th:first-child {
      width: 30%;
    }

    .mcapp-normalized-table td,
    .mcapp-weighted-table td {
      text-align: right;
    }

    .mcapp-results-table th:first-child,
    .mcapp-results-table td:first-child {
      text-align: center;
      width: 60px;
    }

    .mcapp-results-table td:last-child {
      text-align: right;
      font-weight: 500;
    }

    /* Tabulka výsledků */
    .mcapp-results-table tr:first-child td {
      background-color: #E0F7FA; /* Light Cyan */
      font-weight: bold;
    }

    .mcapp-results-table tr:last-child td {
      background-color: #FFEBEE; /* Light Red */
    }

    /* Shrnutí výsledků */
    .mcapp-section .mcapp-results ul {
      list-style: none;
      padding-left: 5px;
      margin: 16px 0;
    }

    .mcapp-section .mcapp-results li {
      margin-bottom: 8px;
    }

    /* Chybové zprávy */
    .mcapp-error-message {
      background-color: #FFEBEE; /* Light Red */
      border-left: 4px solid #F44336; /* Red */
      padding: 16px 20px;
      margin: 20px 0;
      display: flex;
      align-items: center;
    }

    .mcapp-error-icon {
      font-size: 24px;
      color: #F44336; /* Red */
      margin-right: 16px;
    }

    .mcapp-error-text {
      font-size: 16px;
      color: #D32F2F; /* Dark Red */
    }

    /* CSS řešení pro skrývání/zobrazování obsahu (náhrada za JavaScript) */
    /* 1) Skryjeme samotný checkbox, aby uživatel viděl jen label */
    .toggle-checkbox {
      display: none;
    }
    
    /* 2) Label jako “tlačítko” */
    .details-toggle {
      display: block;
      width: 100%;
      background-color: #F5F5F5;
      padding: 10px 15px;
      margin-bottom: 10px;
      border: none;
      border-radius: 2px;
      font-size: 16px;
      text-align: left;
      cursor: pointer;
      position: relative;
    }
    
    /* Změna pozadí při najetí myší */
    .details-toggle:hover {
      background-color: #E0E0E0;
    }
    
    /* 3) Trojúhelník (dolů) ve výchozím stavu */
    .details-toggle::after {
      content: '▼';
      position: absolute;
      right: 15px;
      transition: transform 0.3s;
    }
    
    /* 4) Samotný obsah, který se má skrývat */
    .details-content {
      background-color: white;
      padding: 15px;
      margin-bottom: 20px;
      border-radius: 0 0 2px 2px;
      overflow: hidden;
    }
    
    /* Výchozí stav: skrytý obsah (div je za labelem, který je za inputem) */
    .toggle-checkbox + .details-toggle + .details-content {
      display: none;
    }
    
    /* Při zaškrtnutí (checkbox:checked) se obsah zobrazí */
    .toggle-checkbox:checked + .details-toggle + .details-content {
      display: block;
    }
    
    /* 5) Rotace šipky (trojúhelníku) při rozbalení */
    .toggle-checkbox:checked + .details-toggle::after {
      transform: rotate(180deg);
    }
    
    /* Volitelná drobná stylizace popisku */
    .toggle-hint {
      font-size: 12px;
      color: #757575;
      margin-left: 10px;
    }

    /* Specifické styly pro tisk a PDF export */
    @media print {
      /* Vypnutí skrolování u tabulek - zajistí zobrazení celých tabulek */
      .mcapp-table-container {
        overflow: visible !important;
        width: auto !important;
        height: auto !important;
      }
      
      /* Optimalizace velikosti tabulek */
      .mcapp-table {
        font-size: 8pt !important;
        width: 100% !important;
        max-width: none !important;
      }
      
      /* Zmenšení odsazení buněk v tabulkách */
      .mcapp-table th, .mcapp-table td {
        padding: 2px 4px !important;
      }
      
      /* Zamezení rozdělení tabulek, karet a sekcí přes stránky */
      .mcapp-table-container, .mcapp-card, .mcapp-section {
        page-break-inside: avoid !important;
        break-inside: avoid !important;
      }
      
      /* Plotly grafy - obecné třídy používané Plotly knihovnou */
      .js-plotly-plot, .plotly-graph-div, .plot-container, [data-component-type="Plot"] {
        page-break-inside: avoid !important;
        break-inside: avoid !important;
        height: auto !important;
        min-height: 0 !important;
        max-height: none !important;
      }
      
      /* Anvil Plot komponenty - přesnější cílení */
      .anvil-component[data-component-type="Plot"], 
      .anvil-container > [id^="plotly-"],
      .anvil-component-container > div[class*="plotly"] {
        page-break-inside: avoid !important;
        break-inside: avoid !important;
        overflow: visible !important;
      }
      
      /* Vždy zobrazit obsah detailů (nepoužívat skrývání/zobrazování) */
      .details-content {
        display: block !important;
      }
      
      /* Skrytí tlačítek a prvků interakce */
      .toggle-hint, .btn, button {
        display: none !important;
      }
      
      /* Zajištění, že PDF má bílé pozadí */
      body, .mcapp-wsm-results {
        background-color: white !important;
      }
      
      /* Nastavení pro kontejnery Anvil */
      .anvil-container {
        width: 100% !important;
        overflow: visible !important;
      }
      
      /* Zajistit, že všechny skrolovací elementy zobrazí celý obsah */
      * {
        overflow: visible !important;
      }
    }
    """

def vloz_styly_do_html(html_obsah):
    """
    Vloží CSS styly do HTML obsahu bez JavaScriptu.
    
    Args:
        html_obsah: HTML obsah ke kterému budou přidány styly
        
    Returns:
        str: HTML obsah se styly
    """
    css_styly = ziskej_css_styly()
    
    return f"""
    <style>
    {css_styly}
    </style>
    {html_obsah}
    """