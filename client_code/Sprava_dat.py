# -------------------------------------------------------
# Modul: Sprava_dat
# -------------------------------------------------------
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

__uzivatel = None

def je_prihlasen():
  global __uzivatel
  if __uzivatel:
    return __uzivatel
  __uzivatel = anvil.users.get_user()
  return __uzivatel

def logout():
  global __uzivatel
  __uzivatel = None