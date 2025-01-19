from ._anvil_designer import Hlavni_oknoTemplate
from anvil import *


class Hlavni_okno(Hlavni_oknoTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def link_domu_click(self, **event_args):
    """This method is called when the link is clicked"""
    pass

  def link_pridat_analyzu_click(self, **event_args):
    """This method is called when the link is clicked"""
    pass

  def link_nastaveni_click(self, **event_args):
    """This method is called when the link is clicked"""
    pass

  def link_info_click(self, **event_args):
    """This method is called when the link is clicked"""
    pass

  def link_administrace_click(self, **event_args):
    """This method is called when the link is clicked"""
    pass

  def link_ucet_click(self, **event_args):
    """This method is called when the link is clicked"""
    pass
