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
      white-space: nowrap;
    }

    .mcapp-table th {
      background-color: #F5F5F5; /* Gray 100 */
      text-align: left;
      font-weight: 500;
      position: sticky;
      top: 0;
      z-index: 10;
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

    /* Kolapsovatelné sekce */
    .collapsible {
      background-color: #F5F5F5;
      cursor: pointer;
      padding: 10px 15px;
      width: 100%;
      border: none;
      text-align: left;
      outline: none;
      font-size: 16px;
      transition: 0.4s;
      border-radius: 2px;
      margin-bottom: 10px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .active, .collapsible:hover {
      background-color: #E0E0E0;
    }

    .collapsible:after {
      content: '\\002B'; /* Unicode for "plus" sign (+) */
      font-size: 18px;
      color: #777;
      margin-left: 5px;
    }

    .active:after {
      content: '\\2212'; /* Unicode for "minus" sign (-) */
    }

    .collapsible-content {
      padding: 0 18px;
      max-height: 0;
      overflow: hidden;
      transition: max-height 0.2s ease-out;
      background-color: white;
      border-radius: 0 0 2px 2px;
    }

    /* Kolapsovatelný obsah, který je ve výchozím stavu otevřený */
    .expanded {
      max-height: 1000px; /* Dostatečně velká hodnota pro zobrazení obsahu */
    }
    """

def ziskej_javascript_kód():
    """
    Vrátí řetězec s JavaScriptovým kódem pro interaktivní prvky.
    
    Returns:
        str: JavaScript kód jako řetězec
    """
    return """
    document.addEventListener('DOMContentLoaded', function() {
        var coll = document.getElementsByClassName('collapsible');
        for (var i = 0; i < coll.length; i++) {
            coll[i].addEventListener('click', function() {
                this.classList.toggle('active');
                var content = this.nextElementSibling;
                if (content.style.maxHeight) {
                    content.style.maxHeight = null;
                } else {
                    content.style.maxHeight = content.scrollHeight + 'px';
                }
            });
            
            // Pokud má tlačítko třídu "default-expanded", klikni na něj automaticky
            if (coll[i].classList.contains('default-expanded')) {
                coll[i].click();
            }
        }
    });
    """

def vloz_styly_do_html(html_obsah):
    """
    Vloží CSS styly a JavaScript do HTML obsahu.
    
    Args:
        html_obsah: HTML obsah ke kterému budou přidány styly
        
    Returns:
        str: HTML obsah se styly a JavaScriptem
    """
    css_styly = ziskej_css_styly()
    js_kod = ziskej_javascript_kód()
    
    return f"""
    <style>
    {css_styly}
    </style>
    <script>
    {js_kod}
    </script>
    {html_obsah}
    """