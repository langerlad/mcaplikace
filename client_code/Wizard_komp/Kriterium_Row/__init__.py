# -------------------------------------------------------
# RowTemplate: Kriterium_Row
# -------------------------------------------------------
from ._anvil_designer import Kriterium_RowTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...Uprava_kriteria_form import Uprava_kriteria_form
from .. import Wizard_komp


class Kriterium_Row(Kriterium_RowTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

  def get_main_form(self):
    """
    Projde hierarchy parentů, dokud nenajde instanci Wizard_komp
    """
    current = self
    while current and not isinstance(current, Wizard_komp):
      current = current.parent
    return current

  def link_smazat_kriterium_click(self, **event_args):
    if confirm("Opravdu chcete smazat toto kritérium?", dismissible=True,
        buttons=[("Ano", True), ("Ne", False)]):
      main_form = self.get_main_form()
      main_form.cached_kriteria = [
        k for k in main_form.cached_kriteria
        if k['nazev_kriteria'] != self.item['nazev_kriteria']
      ]
      self.parent.raise_event('x-refresh')

  def link_upravit_kriterium_click(self, **event_args):
    kriterium_kopie = {
      'nazev_kriteria': self.item['nazev_kriteria'],
      'typ': self.item['typ'],
      'vaha': self.item['vaha']
    }
    edit_form = Uprava_kriteria_form(item=kriterium_kopie)
    main_form = self.get_main_form()

    while True:
      save_clicked = alert(
        content=edit_form,
        title="Upravit kritérium",
        large=True,
        dismissible=True,
        buttons=[("Uložit", True), ("Zrušit", False)]
      )
      if not save_clicked:
        break

      updated_data = edit_form.ziskej_upravena_data()
      if updated_data:
        for k in main_form.cached_kriteria:
          if k['nazev_kriteria'] == self.item['nazev_kriteria']:
            k.update(updated_data)
            break
        self.parent.raise_event('x-refresh')
        break