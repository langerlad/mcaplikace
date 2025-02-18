from ._anvil_designer import Dashboard_uziv_kompTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
from .. import Navigace


class Dashboard_uziv_komp(Dashboard_uziv_kompTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.repeating_panel_dashboard.set_event_handler('x-refresh', self.load_analyzy)
        self.load_analyzy()
    
    def load_analyzy(self, **event_args):
        analyzy = anvil.server.call('nacti_analyzy_uzivatele')
        if not analyzy:
            self.label_no_analyzy.visible = True
            self.repeating_panel_dashboard.visible = False
            return
        
        self.label_no_analyzy.visible = False
        self.repeating_panel_dashboard.visible = True
        self.repeating_panel_dashboard.items = [
            {
                'id': a.get_id(),
                'nazev': a['nazev'],
                'popis': a['popis'],
                'datum_vytvoreni': a['datum_vytvoreni'].strftime("%d.%m.%Y"),
                'zvolena_metoda': a['zvolena_metoda']
            } for a in analyzy
        ]

    def button_pridat_analyzu_click(self, **event_args):
      Navigace.go('pridat_analyzu')
