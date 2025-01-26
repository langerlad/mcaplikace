import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


__uzivatel = None

# ptáme se anvilu na stav uživatele - přihlášený / bez účtu
def je_prihlase(): 
  global __uzivatel

  if __uzivatel:
    print("přhlášený uživatel (cache): {}".format(__uzivatel['email']))
    return __uzivatel

  __uzivatel = anvil.users.get_user()
  return __uzivatel

def logout():
  global __uzivatel
  __uzivatel = None
