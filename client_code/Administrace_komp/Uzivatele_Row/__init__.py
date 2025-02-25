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
        self.link_email.text = self.item['email']

        # Nastavení přepínače role podle aktuální role uživatele
        self.check_box_admin.checked = self.item['role'] == 'admin'

    def link_email_click(self, **event_args):
      """Handler pro klik na email uživatele."""
      # Vyvoláme událost se zvoleným uživatelem
      self.parent.raise_event('x-uzivatel-zvolen', uzivatel=self.item)

    def link_odstranit_click(self, **event_args):
      """Handler pro klik na odstranění uživatele."""
      try:
          email = self.item['email']

          # Kontrola, zda nejde o aktuálně přihlášeného uživatele
          current_user = anvil.users.get_user()
          if current_user and current_user['email'] == email:
            alert("Nemůžete smazat svůj vlastní účet, se kterým jste přihlášeni.")
            return
          
          # Potvrzení od uživatele
          if confirm(f"Opravdu chcete odstranit uživatele {email} a všechny jeho analýzy?", 
                  dismissible=True, 
                  buttons=[("Ano", True), ("Ne", False)]):
              
              # Zavolání serverové funkce pro smazání
              result = anvil.server.call('smaz_uzivatele', email)
              
              if result:
                  # Vyvoláme událost pro obnovení seznamu uživatelů
                  self.parent.raise_event('x-refresh')
                  
                  # Informujeme administrátora
                  alert(f"Uživatel {email} byl úspěšně smazán včetně všech jeho analýz.")
              
      except Exception as e:
          # Informujeme o chybě
          alert(f"Chyba při mazání uživatele: {str(e)}")

    def check_box_admin_change(self, **event_args):
        """Handler pro změnu role uživatele."""
        try:
            email = self.item['email']
            nova_role = 'admin' if self.check_box_admin.checked else 'uživatel'
            
            # Debug výpis
            print(f"Změna role pro {email} na {nova_role}, checkbox: {self.check_box_admin.checked}")
            
            # Potvrzení od uživatele
            if confirm(f"Opravdu chcete změnit roli účtu {email} na {nova_role}?", 
                     dismissible=True, 
                     buttons=[("Ano", True), ("Ne", False)]):
                
                # Zavolání serverové funkce pro změnu role
                result = anvil.server.call('zmenit_roli_uzivatele', email, nova_role)
                
                if result:
                    # Vyvoláme událost pro obnovení seznamu uživatelů
                    self.parent.raise_event('x-refresh')
                    
                    # Informujeme administrátora
                    alert(f"Role účtu {email} byla úspěšně změněna na {nova_role}.")
            else:
                # Vrátíme checkbox do původního stavu
                self.check_box_admin.checked = not self.check_box_admin.checked
                print(f"Akce zrušena, vracím checkbox na: {self.check_box_admin.checked}")
                
        except Exception as e:
            # Informujeme o chybě a vrátíme checkbox do původního stavu
            alert(f"Chyba při změně role uživatele: {str(e)}")
            self.check_box_admin.checked = not self.check_box_admin.checked
            print(f"Chyba, vracím checkbox na: {self.check_box_admin.checked}")