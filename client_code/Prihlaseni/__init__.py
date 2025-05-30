from ._anvil_designer import PrihlaseniTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil import open_form
from .. import Spravce_stavu, Utils

class Prihlaseni(PrihlaseniTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        
        # Inicializace správce stavu
        self.spravce = Spravce_stavu.Spravce_stavu()
        
        # Inicálně zobrazíme pouze přihlašovací formulář
        self.panel_login.visible = True
        self.panel_signup.visible = False
        
        # Nastavení placeholder textu
        self.text_box_email.placeholder = "Email"
        self.text_box_heslo.placeholder = "Heslo"
        
        self.text_box_email_reg.placeholder = "Email"
        self.text_box_heslo_reg.placeholder = "Zvolte heslo"
        self.text_box_heslo2_reg.placeholder = "Zadejte heslo znovu"
        
        # Skryjeme chybové zprávy
        self.label_chyba_login.visible = False
        self.label_chyba_signup.visible = False
        
        # Kontrola, zda již je uživatel přihlášen
        uzivatel = self.spravce.nacti_uzivatele()
        if uzivatel:
            self.presmeruj_do_aplikace()

    def presmeruj_do_aplikace(self):
        """Přesměruje uživatele do hlavní aplikace"""
        open_form('Hlavni_okno')
  
    def link_prepni_na_signup_click(self, **event_args):
        """Přepne formulář na registraci"""
        self.panel_login.visible = False
        self.panel_signup.visible = True
        
    def link_prepni_na_login_click(self, **event_args):
        """Přepne formulář na přihlášení"""
        self.panel_login.visible = True
        self.panel_signup.visible = False
    
    def button_prihlasit_click(self, **event_args):
        """Obsluha přihlášení"""
        self.label_chyba_login.visible = False
        email = self.text_box_email.text
        heslo = self.text_box_heslo.text
        
        if not email or not heslo:
            self.label_chyba_login.text = "Zadejte email a heslo"
            self.label_chyba_login.visible = True
            return
            
        try:
            # Pokus o přihlášení
            uzivatel = anvil.users.login_with_email(email, heslo, remember=True)
            if uzivatel:
                # Úspěšné přihlášení, aktualizace stavu
                self.spravce.nacti_uzivatele()
                self.presmeruj_do_aplikace()
            else:
                self.label_chyba_login.text = "Neplatný email nebo heslo"
                self.label_chyba_login.visible = True
                
        except Exception as e:
            self.label_chyba_login.text = f"Chyba při přihlašování: {str(e)}"
            self.label_chyba_login.visible = True
            Utils.zapsat_chybu(f"Chyba při přihlašování: {str(e)}")
    
    def button_registrovat_click(self, **event_args):
        """Obsluha registrace nového uživatele"""
        self.label_chyba_signup.visible = False
        email = self.text_box_email_reg.text
        heslo = self.text_box_heslo_reg.text
        heslo2 = self.text_box_heslo2_reg.text
        
        # Validace vstupů
        if not email or not heslo or not heslo2:
            self.label_chyba_signup.text = "Vyplňte všechna pole"
            self.label_chyba_signup.visible = True
            return

        # Validace emailu
        if not self.validuj_email(email):
            self.label_chyba_signup.text = "Zadejte platný email"
            self.label_chyba_signup.visible = True
            return
                
        if heslo != heslo2:
            self.label_chyba_signup.text = "Hesla se neshodují"
            self.label_chyba_signup.visible = True
            return
                
        if len(heslo) < 6:
            self.label_chyba_signup.text = "Heslo musí mít alespoň 6 znaků"
            self.label_chyba_signup.visible = True
            return
                
        try:
            # Volání serverové funkce pro vytvoření uživatele
            result = anvil.server.call('registruj_noveho_uzivatele', email, heslo)
            if result:
                # Uživatel byl vytvořen, aktualizujeme stav a přesměrujeme do aplikace
                Utils.zapsat_info(f"Uživatel {email} úspěšně vytvořen")
                self.spravce.nacti_uzivatele()
                self.presmeruj_do_aplikace()
            else:
                self.label_chyba_signup.text = "Registrace se nezdařila"
                self.label_chyba_signup.visible = True
                    
        except anvil.users.UserExists:
            self.label_chyba_signup.text = "Uživatel s tímto emailem již existuje"
            self.label_chyba_signup.visible = True
        except Exception as e:
            self.label_chyba_signup.text = f"Chyba při registraci: {str(e)}"
            self.label_chyba_signup.visible = True
            Utils.zapsat_chybu(f"Chyba při registraci: {str(e)}")
    
    def validuj_email(self, email):
        """Jednoduchá validace emailu"""
        if not email:
            return False
        return '@' in email and '.' in email and email.index('@') < email.rindex('.')
    
    def text_box_email_reg_lost_focus(self, **event_args):
        """Validuje email při ztrátě fokusu"""
        email = self.text_box_email_reg.text
        if email and not self.validuj_email(email):
            self.label_chyba_signup.text = "Zadejte platný email"
            self.label_chyba_signup.visible = True
        else:
            self.label_chyba_signup.visible = False
