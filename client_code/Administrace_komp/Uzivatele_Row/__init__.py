from ._anvil_designer import Uzivatele_RowTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Uzivatele_Row(Uzivatele_RowTemplate):
    def __init__(self, **properties):
        """Inicializace komponenty řádku uživatele."""
        self.init_components(**properties)
