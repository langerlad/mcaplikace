from ._anvil_designer import Vystup_wsm_htmTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. import Spravce_stavu, Utils, Vypocty, Vizualizace
# Import nového modulu se styly
from .. import mcapp_styly


class Vystup_wsm_htm(Vystup_wsm_htmTemplate):
    """
    Formulář pro zobrazení výsledků WSM analýzy (Weighted Sum Model) s využitím HTML.
    Využívá sdílené moduly pro výpočty a vizualizace a zobrazuje výstup s bohatým formátováním.
    """
    
    def __init__(self, analyza_id=None, **properties):
        """
        Inicializace formuláře s ID analýzy.
        
        Args:
            analyza_id: ID analýzy k zobrazení, pokud None, použije aktivní analýzu ze správce
        """
        self.init_components(**properties)
        # Inicializace správce stavu
        self.spravce = Spravce_stavu.Spravce_stavu()
        
        # Použijeme ID z parametrů nebo z aktivní analýzy ve správci
        self.analyza_id = analyza_id or self.spravce.ziskej_aktivni_analyzu()
        
        # Data, která budeme používat v celém formuláři
        self.analyza_data = None
        self.wsm_vysledky = None
        self._data_pro_grafy = None
        
    def form_show(self, **event_args):
        """Načte a zobrazí data analýzy při zobrazení formuláře."""
        if not self.analyza_id:
            self._zobraz_prazdny_formular()
            return
            
        try:
            Utils.zapsat_info(f"Načítám data analýzy ID: {self.analyza_id}")
            
            # Načtení dat analýzy z JSON struktury
            self.analyza_data = anvil.server.call('nacti_analyzu', self.analyza_id)
            
            # Zobrazení výsledků
            self._zobraz_kompletni_analyzu(self.analyza_data)
            
            Utils.zapsat_info("Výsledky WSM analýzy úspěšně zobrazeny")
            
        except Exception as e:
            Utils.zapsat_chybu(f"Chyba při načítání analýzy: {str(e)}")
            alert(f"Chyba při načítání analýzy: {str(e)}")

    def _zobraz_prazdny_formular(self):
        """Zobrazí prázdný formulář s informací o chybějících datech."""
        Utils.zapsat_info("Zobrazuji prázdný formulář WSM HTML - chybí ID analýzy")
        chyba_html = self._vytvor_html_chybova_zprava("Nepřišlo žádné ID analýzy.")
        # Vložení CSS stylů i do chybové zprávy
        self.html_1.html = mcapp_styly.vloz_styly_do_html(chyba_html)
        self.plot_wsm_vysledek.visible = False
        self.plot_wsm_skladba.visible = False
        self.plot_citlivost_skore.visible = False
        self.plot_citlivost_poradi.visible = False

    def _vytvor_html_chybova_zprava(self, zprava):
        """Vytvoří HTML zobrazení chybové zprávy."""
        return f"""
        <div class="mcapp-error-message">
            <div class="mcapp-error-icon"><i class="fa fa-exclamation-circle"></i></div>
            <div class="mcapp-error-text">{zprava}</div>
        </div>
        """
            
    def _zobraz_kompletni_analyzu(self, analyza_data):
        """
        Zobrazí kompletní analýzu včetně všech výpočtů a vizualizací.
        
        Args:
            analyza_data: Slovník s daty analýzy v JSON formátu
        """
        try:
            # Provedení výpočtů
            matice, typy_kriterii, varianty, kriteria, vahy = Vypocty.priprav_data_z_json(analyza_data)
            
            # Normalizace matice
            norm_vysledky = Vypocty.normalizuj_matici_minmax(matice, typy_kriterii, varianty, kriteria)
            
            # Výpočet vážených hodnot
            vazene_matice = Vypocty.vypocitej_vazene_hodnoty(
                norm_vysledky['normalizovana_matice'], 
                vahy
            )
            
            # Výpočet WSM výsledků
            wsm_vysledky = Vypocty.wsm_vypocet(
                norm_vysledky['normalizovana_matice'], 
                vahy, 
                varianty
            )
            
            # Uložení dat pro další použití
            self._data_pro_grafy = {
                'norm_vysledky': norm_vysledky,
                'vazene_matice': vazene_matice,
                'vahy': vahy,
                'wsm_vysledky': wsm_vysledky,
                'matice': matice,
                'typy_kriterii': typy_kriterii
            }
            
            # Uložíme výsledky do instance
            self.wsm_vysledky = wsm_vysledky
            
            # Vytvoření a nastavení HTML obsahu
            self._vytvor_a_nastav_html_obsah()
            
            # Vytvoření a nastavení grafů
            self._vytvor_a_nastav_grafy()
            
        except Exception as e:
            Utils.zapsat_chybu(f"Chyba při výpočtu WSM výsledků: {str(e)}")
            chyba_html = self._vytvor_html_chybova_zprava(f"Chyba při výpočtu: {str(e)}")
            # Vložení CSS stylů i do chybové zprávy
            self.html_1.html = mcapp_styly.vloz_styly_do_html(chyba_html)
            self.plot_wsm_vysledek.visible = False
            self.plot_wsm_skladba.visible = False
            self.plot_citlivost_skore.visible = False
            self.plot_citlivost_poradi.visible = False
    
    def _vytvor_a_nastav_html_obsah(self):
        """Vytvoří a nastaví HTML obsah pro zobrazení výsledků."""
        html_obsah = self._vytvor_html_struktura()
        # Vložení CSS stylů přímo do HTML obsahu
        html_s_styly = mcapp_styly.vloz_styly_do_html(html_obsah)
        self.html_1.html = html_s_styly
    
    def _vytvor_a_nastav_grafy(self):
        """Vytvoří a nastaví grafy pro vizualizaci výsledků."""
        try:
            # Graf výsledků
            self.plot_wsm_vysledek.figure = Vizualizace.vytvor_sloupovy_graf_vysledku(
                self.wsm_vysledky['results'], 
                self.wsm_vysledky['nejlepsi_varianta'], 
                self.wsm_vysledky['nejhorsi_varianta'], 
                "WSM"
            )
            self.plot_wsm_vysledek.visible = True
            
            # Graf skladby skóre
            data = self._data_pro_grafy
            self.plot_wsm_skladba.figure = Vizualizace.vytvor_skladany_sloupovy_graf(
                data['norm_vysledky']['nazvy_variant'],
                data['norm_vysledky']['nazvy_kriterii'],
                data['vazene_matice']
            )
            self.plot_wsm_skladba.visible = True
            
            # Analýza citlivosti - povolená pouze pokud máme více než jedno kritérium
            if len(data['norm_vysledky']['nazvy_kriterii']) > 1:
                # Výpočet analýzy citlivosti pro první kritérium
                analyza_citlivosti = Vypocty.vypocitej_analyzu_citlivosti(
                    data['norm_vysledky']['normalizovana_matice'], 
                    data['vahy'], 
                    data['norm_vysledky']['nazvy_variant'], 
                    data['norm_vysledky']['nazvy_kriterii']
                )
                
                # Grafy citlivosti
                self.plot_citlivost_skore.figure = Vizualizace.vytvor_graf_citlivosti_skore(
                    analyza_citlivosti, data['norm_vysledky']['nazvy_variant'])
                self.plot_citlivost_skore.visible = True
                
                self.plot_citlivost_poradi.figure = Vizualizace.vytvor_graf_citlivosti_poradi(
                    analyza_citlivosti, data['norm_vysledky']['nazvy_variant'])
                self.plot_citlivost_poradi.visible = True
            else:
                # Skryjeme grafy citlivosti, pokud máme jen jedno kritérium
                self.plot_citlivost_skore.visible = False  
                self.plot_citlivost_poradi.visible = False
                
        except Exception as e:
            Utils.zapsat_chybu(f"Chyba při vytváření grafů: {str(e)}")
            self.plot_wsm_vysledek.visible = False
            self.plot_wsm_skladba.visible = False
            self.plot_citlivost_skore.visible = False
            self.plot_citlivost_poradi.visible = False
    
    def _vytvor_html_struktura(self):
        """
        Vytvoří kompletní HTML strukturu pro zobrazení výsledků analýzy.
        
        Returns:
            str: HTML kód pro zobrazení
        """
        data = self._data_pro_grafy
        analyza_data = self.analyza_data
        wsm_vysledky = self.wsm_vysledky
        
        # Extrakce dat v požadovaném formátu pro HTML tabulky
        varianty = data['norm_vysledky']['nazvy_variant']
        kriteria = data['norm_vysledky']['nazvy_kriterii']
        
        # Vytvoření částí HTML dokumentu
        hlavicka_html = self._vytvor_hlavicku_html()
        vstupni_data_html = self._vytvor_vstupni_data_html(analyza_data)
        postup_html = self._vytvor_postup_html(
            data['matice'],
            data['norm_vysledky']['normalizovana_matice'],
            data['vazene_matice'],
            data['vahy'],
            varianty,
            kriteria,
            data['typy_kriterii']
        )
        vysledky_html = self._vytvor_vysledky_html(wsm_vysledky, varianty)
        
        # Sloučení všech částí do jednoho dokumentu
        html_obsah = f"""
        <div class="mcapp-wsm-results">
            {hlavicka_html}
            {vstupni_data_html}
            {postup_html}
            {vysledky_html}
        </div>
        """
        
        return html_obsah
    
    def _vytvor_hlavicku_html(self):
        """Vytvoří HTML pro hlavičku analýzy."""
        return f"""
        <div class="mcapp-section mcapp-header">
            <h1>{self.analyza_data['nazev']}</h1>
            <div class="mcapp-subtitle">Analýza metodou WSM (Weighted Sum Model)</div>
        </div>
        """
    
    def _vytvor_vstupni_data_html(self, analyza_data):
        """
        Vytvoří HTML sekci se vstupními daty analýzy.
        
        Args:
            analyza_data: Slovník s daty analýzy
        
        Returns:
            str: HTML kód pro sekci vstupních dat
        """
        # Tabulka kritérií
        kriteria_html = Vizualizace.vytvor_html_tabulku_kriterii(
            analyza_data.get('kriteria', {}),
            "Přehled kritérií",
            "mcapp-table mcapp-criteria-table"
        )
        
        # Tabulka variant
        varianty_html = Vizualizace.vytvor_html_tabulku_variant(
            analyza_data.get('varianty', {}),
            "Přehled variant",
            "mcapp-table mcapp-variants-table"
        )
        
        # Původní hodnotící matice
        matice_html = Vizualizace.vytvor_html_matici_hodnot(
            list(analyza_data.get('varianty', {}).keys()),
            list(analyza_data.get('kriteria', {}).keys()),
            analyza_data.get('varianty', {}),
            "Hodnotící matice",
            "mcapp-table mcapp-matrix-table"
        )
        
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
    
    def _vytvor_postup_html(self, matice, norm_matice, vazene_matice, vahy, varianty, kriteria, typy_kriterii):
        """
        Vytvoří HTML sekci s postupem výpočtu.
        
        Args:
            matice: Původní matice hodnot
            norm_matice: Normalizovaná matice hodnot
            vazene_matice: Vážená matice hodnot
            vahy: Seznam vah kritérií
            varianty: Seznam názvů variant
            kriteria: Seznam názvů kritérií
            typy_kriterii: Seznam typů kritérií (max/min)
            
        Returns:
            str: HTML kód pro sekci postupu výpočtu
        """
        # Kroky metodologie
        metodologie_html = """
        <div class="mcapp-methodology">
            <h3>Postup metody WSM/SAW</h3>
            <ol>
                <li><strong>Sběr dat</strong> - Definice variant, kritérií a hodnocení variant podle kritérií.</li>
                <li><strong>Normalizace hodnot</strong> - Převod různorodých hodnot kritérií na srovnatelnou škálu 0 až 1 pomocí metody Min-Max.</li>
                <li><strong>Vážení hodnot</strong> - Vynásobení normalizovaných hodnot vahami kritérií.</li>
                <li><strong>Výpočet celkového skóre</strong> - Sečtení vážených hodnot pro každou variantu.</li>
                <li><strong>Seřazení variant</strong> - Seřazení variant podle celkového skóre (vyšší je lepší).</li>
            </ol>
        </div>
        """
        
        # Normalizační tabulka
        normalizace_html = Vizualizace.vytvor_html_tabulku_hodnot(
            varianty, kriteria, norm_matice,
            "Normalizovaná matice",
            "mcapp-table mcapp-normalized-table"
        )
        
        # Vysvětlení normalizace
        vysvetleni_norm_html = """
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
        """
        
        # Tabulka vah
        vahy_html = """
        <div class="mcapp-weights">
            <h4>Váhy kritérií</h4>
            <table class="mcapp-table mcapp-weights-table">
                <tr>
                    <th>Kritérium</th>
        """
        for krit in kriteria:
            vahy_html += f"<th>{krit}</th>"
        
        vahy_html += """
                </tr>
                <tr>
                    <th>Váha</th>
        """
        
        for i, vaha in enumerate(vahy):
            vahy_html += f"<td>{vaha:.3f}</td>"
            
        vahy_html += """
                </tr>
            </table>
        </div>
        """
        
        # Tabulka vážených hodnot
        vazene_html = Vizualizace.vytvor_html_tabulku_hodnot(
            varianty, kriteria, vazene_matice,
            "Vážené hodnoty (normalizované hodnoty × váhy)",
            "mcapp-table mcapp-weighted-table",
            lambda x: f"{x:.3f}"
        )
        
        # Přidání sloupce s celkovým skóre
        vazene_html = vazene_html.replace("</tbody>", self._vytvor_sloupec_souctu(vazene_matice, varianty) + "</tbody>")
        
        # Sloučení do sekce
        return f"""
        <div class="mcapp-section mcapp-process">
            <h2>Postup zpracování dat</h2>
            <div class="mcapp-card">
                {metodologie_html}
            </div>
            <div class="mcapp-card">
                <h3>Krok 1: Normalizace hodnot</h3>
                {normalizace_html}
                {vysvetleni_norm_html}
            </div>
            <div class="mcapp-card">
                <h3>Krok 2: Vážení hodnot a výpočet skóre</h3>
                {vahy_html}
                {vazene_html}
            </div>
        </div>
        """
    
    def _vytvor_sloupec_souctu(self, vazene_matice, varianty):
        """
        Vytvoří HTML pro sloupec celkového součtu v tabulce vážených hodnot.
        
        Args:
            vazene_matice: Matice vážených hodnot
            varianty: Seznam názvů variant
            
        Returns:
            str: HTML kód s řádky pro sloupec souctu
        """
        html = ""
        
        # Přidání záhlaví sloupce součtu (přidá se do již existující tabulky)
        html += """
        <th style="background-color:#f0f0f0; font-weight:bold;">Celkové skóre</th>
        """
        
        # Výpočet součtů pro každou variantu
        for i, var in enumerate(varianty):
            radek = vazene_matice[i]
            soucet = sum(radek)
            html += f"""
            <td style="background-color:#f0f0f0; font-weight:bold; text-align:right;">{soucet:.3f}</td>
            """
            
        return html
    
    def _vytvor_vysledky_html(self, wsm_vysledky, varianty):
        """
        Vytvoří HTML sekci s výsledky analýzy.
        
        Args:
            wsm_vysledky: Slovník s výsledky WSM analýzy
            varianty: Seznam názvů variant
            
        Returns:
            str: HTML kód pro sekci výsledků
        """
        # Tabulka výsledků
        vysledky_html = Vizualizace.vytvor_html_tabulku_vysledku(
            wsm_vysledky['results'],
            {0: "Pořadí", 1: "Varianta", 2: "Skóre"},
            "Pořadí variant",
            "mcapp-table mcapp-results-table"
        )
        
        # Vypočítáme procento z maxima
        procento = (wsm_vysledky['nejhorsi_skore'] / wsm_vysledky['nejlepsi_skore'] * 100) if wsm_vysledky['nejlepsi_skore'] > 0 else 0
        
        # Shrnutí výsledků
        shrnuti_html = Vizualizace.vytvor_html_shrnuti_vysledku(
            wsm_vysledky['nejlepsi_varianta'],
            wsm_vysledky['nejlepsi_skore'],
            wsm_vysledky['nejhorsi_varianta'],
            wsm_vysledky['nejhorsi_skore'],
            {
                "Rozdíl nejlepší-nejhorší": wsm_vysledky['rozdil_skore'],
                "Poměr nejhorší/nejlepší": f"{procento:.1f}% z maxima"
            }
        )
        
        # Popis metody
        o_metode_html = Vizualizace.vytvor_html_shrnuti_metody(
            "WSM (Weighted Sum Model)",
            "WSM, také známý jako Simple Additive Weighting (SAW), je jedna z nejjednodušších a nejpoužívanějších metod vícekriteriálního rozhodování. Je založena na lineárním vážení kritérií.",
            [
                "Jednoduchá a intuitivní - snadno pochopitelná i pro netechnické uživatele",
                "Transparentní výpočty a výsledky - každý krok lze snadno vysvětlit",
                "Snadná interpretace - výsledky přímo odpovídají váženému průměru hodnocení"
            ],
            [
                "Předpokládá lineární užitek - nemusí odpovídat realitě u všech kritérií",
                "Není vhodná pro silně konfliktní kritéria - může dojít k vzájemnému vyrušení",
                "Méně robustní vůči extrémním hodnotám než některé pokročilejší metody"
            ]
        )
        
        # Sloučení do sekce
        return f"""
        <div class="mcapp-section mcapp-results">
            <h2>Výsledky analýzy</h2>
            <div class="mcapp-card">
                {vysledky_html}
                {shrnuti_html}
            </div>
            <div class="mcapp-card">
                {o_metode_html}
            </div>
        </div>
        """