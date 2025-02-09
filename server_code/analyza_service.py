# -------------------------------------------------------
# Modul: analyza_service
# -------------------------------------------------------
import datetime
import logging
from typing import Dict, List, Optional, Any
import anvil.server
import anvil.users
import anvil.tables as tables
from anvil.tables import app_tables
from .. import Konstanty

class AnalyzaService:
    """
    Služba pro práci s analýzami.
    Obsahuje business logiku pro práci s analýzami a jejich komponentami.
    """
    
    @staticmethod
    def validuj_nazev_analyzy(nazev: str) -> None:
        """Validuje název analýzy."""
        if not nazev:
            raise ValueError(Konstanty.ZPRAVY_CHYB['NAZEV_PRAZDNY'])
        if len(nazev) > Konstanty.VALIDACE['MAX_DELKA_NAZEV']:
            raise ValueError(Konstanty.ZPRAVY_CHYB['NAZEV_DLOUHY'])

    @staticmethod
    def validuj_kriteria(kriteria: List[Dict]) -> None:
        """Validuje seznam kritérií."""
        if not kriteria:
            raise ValueError(Konstanty.ZPRAVY_CHYB['MIN_KRITERIA'])
        
        try:
            vahy_suma = sum(float(k['vaha']) for k in kriteria)
            if abs(vahy_suma - 1.0) > Konstanty.VALIDACE['TOLERANCE_SOUCTU_VAH']:
                raise ValueError(Konstanty.ZPRAVY_CHYB['SUMA_VAH'].format(vahy_suma))
        except (ValueError, TypeError):
            raise ValueError(Konstanty.ZPRAVY_CHYB['NEPLATNA_VAHA'])

    @staticmethod
    def vytvor_analyzu(nazev: str, popis: str, zvolena_metoda: str) -> str:
        """
        Vytvoří novou analýzu.
        
        Returns:
            str: ID nově vytvořené analýzy
        """
        uzivatel = anvil.users.get_user()
        if not uzivatel:
            raise ValueError(Konstanty.ZPRAVY_CHYB['NEZNAMY_UZIVATEL'])

        AnalyzaService.validuj_nazev_analyzy(nazev)
        
        try:
            analyza = app_tables.analyza.add_row(
                nazev=nazev,
                popis=popis,
                datum_vytvoreni=datetime.datetime.now(),
                zvolena_metoda=zvolena_metoda,
                uzivatel=uzivatel,
                datum_upravy=None,
                stav=None
            )
            return analyza.get_id()
        except Exception as e:
            logging.error(f"Chyba při vytváření analýzy: {str(e)}")
            raise

    @staticmethod
    def nacti_analyzu(analyza_id: str) -> Dict:
        """Načte detaily analýzy."""
        try:
            analyza = app_tables.analyza.get_by_id(analyza_id)
            if not analyza:
                raise ValueError(Konstanty.ZPRAVY_CHYB['ANALYZA_NEEXISTUJE'].format(analyza_id))
                
            return {
                'nazev': analyza['nazev'],
                'popis': analyza['popis'],
                'zvolena_metoda': analyza['zvolena_metoda'],
                'datum_vytvoreni': analyza['datum_vytvoreni']
            }
        except Exception as e:
            logging.error(f"Chyba při načítání analýzy {analyza_id}: {str(e)}")
            raise

    @staticmethod
    def nacti_analyzy_uzivatele() -> List[Dict]:
        """Načte seznam analýz přihlášeného uživatele."""
        uzivatel = anvil.users.get_user()
        if not uzivatel:
            return []
            
        try:
            analyzy = list(app_tables.analyza.search(
                tables.order_by("datum_vytvoreni", ascending=False),
                uzivatel=uzivatel
            ))
            
            return [{
                'id': a.get_id(),
                'nazev': a['nazev'],
                'popis': a['popis'],
                'datum_vytvoreni': a['datum_vytvoreni'],
                'zvolena_metoda': a['zvolena_metoda']
            } for a in analyzy]
        except Exception as e:
            logging.error(f"Chyba při načítání analýz uživatele: {str(e)}")
            return []

    @staticmethod
    def uloz_kriteria(analyza: Any, kriteria: List[Dict]) -> None:
        """Uloží kritéria analýzy."""
        for k in kriteria:
            try:
                vaha = float(k['vaha'])
                app_tables.kriterium.add_row(
                    analyza=analyza,
                    nazev_kriteria=k['nazev_kriteria'],
                    typ=k['typ'],
                    vaha=vaha
                )
            except (ValueError, TypeError):
                raise ValueError(
                    Konstanty.ZPRAVY_CHYB['NEPLATNA_VAHA_KRITERIA'].format(k['nazev_kriteria'])
                )

    @staticmethod
    def uloz_varianty(analyza: Any, varianty: List[Dict]) -> None:
        """Uloží varianty analýzy."""
        for v in varianty:
            app_tables.varianta.add_row(
                analyza=analyza,
                nazev_varianty=v['nazev_varianty'],
                popis_varianty=v['popis_varianty']
            )

    @staticmethod
    def uloz_hodnoty(analyza: Any, hodnoty: Dict) -> None:
        """Uloží hodnoty pro kombinace variant a kritérií."""
        if not isinstance(hodnoty, dict) or 'matice_hodnoty' not in hodnoty:
            raise ValueError("Neplatný formát dat pro hodnoty")
            
        for key, hodnota in hodnoty['matice_hodnoty'].items():
            try:
                varianta_id, kriterium_id = key.split('_')
                
                varianta = app_tables.varianta.get(
                    analyza=analyza,
                    nazev_varianty=varianta_id
                )
                kriterium = app_tables.kriterium.get(
                    analyza=analyza,
                    nazev_kriteria=kriterium_id
                )
                
                if varianta and kriterium:
                    try:
                        if isinstance(hodnota, str):
                            hodnota = hodnota.replace(',', '.')
                        hodnota_float = float(hodnota)
                        app_tables.hodnota.add_row(
                            analyza=analyza,
                            varianta=varianta,
                            kriterium=kriterium,
                            hodnota=hodnota_float
                        )
                    except (ValueError, TypeError):
                        raise ValueError(
                            Konstanty.ZPRAVY_CHYB['NEPLATNA_HODNOTA'].format(varianta_id, kriterium_id)
                        )
            except Exception as e:
                raise ValueError(f"Chyba při ukládání hodnoty: {str(e)}")

    @staticmethod
    def smaz_analyzu(analyza_id: str) -> None:
        """Smaže analýzu a všechna související data."""
        try:
            analyza = app_tables.analyza.get_by_id(analyza_id)
            if not analyza:
                return  # If analysis doesn't exist, silently return
                
            # Delete related data first
            for hodnota in app_tables.hodnota.search(analyza=analyza):
                hodnota.delete()
            for varianta in app_tables.varianta.search(analyza=analyza):
                varianta.delete()
            for kriterium in app_tables.kriterium.search(analyza=analyza):
                kriterium.delete()
                
            # Finally delete the analysis itself
            analyza.delete()
            
        except Exception as e:
            logging.error(f"Chyba při mazání analýzy {analyza_id}: {str(e)}")
            raise ValueError("Nepodařilo se smazat analýzu")