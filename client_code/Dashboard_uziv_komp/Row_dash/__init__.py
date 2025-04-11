from ._anvil_designer import Row_dashTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Row_dash(Row_dashTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def link_export_click(self, **event_args):
    """This method is called when the link is clicked"""
    pass

  def link_vizualizace_click(self, **event_args):
    """This method is called when the link is clicked"""
    pass

  def link_upravit_click(self, **event_args):
    """This method is called when the link is clicked"""
    pass

  def link_klonovat_click(self, **event_args):
    """This method is called when the link is clicked"""
    pass

  def link_json_click(self, **event_args):
    """This method is called when the link is clicked"""
    pass

  def link_smazat_click(self, **event_args):
    """This method is called when the link is clicked"""
    pass
