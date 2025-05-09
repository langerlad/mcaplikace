# MCApp - Nástroj pro vícekriteriální rozhodování

![MCApp Logo](theme/assets/grafika_alfa.png)

MCApp je komplexní webová aplikace pro vícekriteriální analýzu rozhodování (MCDA), navržená pro usnadnění složitých rozhodnutí porovnáváním více alternativ podle různých kritérií. Nabízí několik etablovaných MCDA metodik v uživatelsky přívětivém rozhraní.

## Funkce

- **Několik metod analýzy**:
  - WSM (Weighted Sum Model - Model váženého součtu)
  - WPM (Weighted Product Model - Model váženého součinu)
  - TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution - Technika preference pořadí podle podobnosti s ideálním řešením)
  - ELECTRE (Elimination Et Choix Traduisant la Réalité - Eliminace a výběr vyjadřující realitu)
  - MABAC (Multi-Attributive Border Approximation area Comparison - Porovnání více-atributivní hraniční aproximace)

- **Metody stanovení vah kritérií**:
  - Manuální přiřazení vah
  - AHP (Analytic Hierarchy Process - Analytický hierarchický proces) s párovým porovnáním
  - Metoda entropie (automaticky vypočítává váhy na základě variability dat)

- **Interaktivní výsledky**:
  - Detailní numerické výsledky
  - Vizuální reprezentace prostřednictvím různých grafů
  - Analýza citlivosti pro váhy

- **Správa uživatelů**:
  - Uživatelské účty s personalizovanými nástěnkami
  - Přístup založený na rolích (administrátor/uživatel)
  - Funkce pro sdílení a spolupráci

- **Možnosti exportu**:
  - Excel reporty
  - PDF exporty
  - Export dat ve formátu JSON

## Technologický stack

- **Frontend**: Anvil Web Framework (založený na Pythonu)
- **Backend**: Python s Anvil Serverem
- **Databáze**: Vestavěná databázová služba Anvil
- **Vizualizace**: Plotly pro interaktivní grafy

## Začínáme

### Požadavky

Aplikace je postavena na frameworku Anvil, proto budete potřebovat:

- Účet na Anvil
- Základní znalost Pythonu
- (Volitelně) Lokální vývojové prostředí s Python 3.7+ pro testování na straně klienta

### Instalace

1. **Naklonujte tento repozitář**:
   ```
   git clone https://github.com/langerlad/mcaplikace.git
   ```

2. **Importujte aplikaci do svého Anvil účtu**:
   - Přejděte na [Anvil Builder](https://anvil.works/build)
   - Vytvořte novou aplikaci
   - Použijte možnost "Import from GitHub"
   - Postupujte podle pokynů pro propojení repozitáře

3. **Nakonfigurujte databázové tabulky**:
   - Vytvořte požadované tabulky (users, analyzy)
   - Nastavte vhodné datové typy a vztahy

   #### Databázová struktura aplikace MCApp

Aplikace MCApp používá relační databázový model s následujícími tabulkami:

Tabulka: `users` obsahuje informace o uživatelích aplikace a jejich nastavení.

| Sloupec | Datový typ | Popis |
|---------|------------|-------|
| `email` | Text | Primární klíč, email uživatele |
| `password_hash` | Text | Hashované heslo uživatele |
| `enabled` | Boolean | Zda je účet aktivní |
| `signed_up` | DateTime | Datum registrace uživatele |
| `last_login` | DateTime | Datum posledního přihlášení |
| `role` | Text | Role uživatele ('admin' nebo 'uživatel') |
| `electre_index_souhlasu` | Decimal | Parametr pro metodu ELECTRE (výchozí: 0.7) |
| `electre_index_nesouhlasu` | Decimal | Parametr pro metodu ELECTRE (výchozí: 0.3) |
| `stanoveni_vah` | Text | Preferovaná metoda stanovení vah ('manual', 'rank', 'ahp', 'entropie') |

Tabulka: `analyzy` ukládá analýzy vytvořené uživateli.

| Sloupec | Datový typ | Popis |
|---------|------------|-------|
| `id` | Auto ID | Unikátní identifikátor analýzy |
| `nazev` | Text | Název analýzy |
| `uzivatel` | Reference | Odkaz na uživatele (tabulka users) |
| `datum_vytvoreni` | DateTime | Datum a čas vytvoření analýzy |
| `datum_upravy` | DateTime | Datum a čas poslední úpravy analýzy |
| `data_json` | JSON | Strukturovaná data analýzy v JSON formátu |

Struktura pole `data_json` obsahuje všechna data analýzy v následující struktuře:

```json
{
  "popis_analyzy": "Textový popis analýzy",
  "kriteria": {
    "nazev_kriteria_1": {
      "typ": "max",
      "vaha": 0.4
    },
    "nazev_kriteria_2": {
      "typ": "min",
      "vaha": 0.6
    }
    // další kritéria...
  },
  "varianty": {
    "nazev_varianty_1": {
      "popis_varianty": "Popis varianty 1",
      "nazev_kriteria_1": 42,
      "nazev_kriteria_2": 3.14
      // hodnoty pro všechna kritéria...
    },
    "nazev_varianty_2": {
      "popis_varianty": "Popis varianty 2",
      "nazev_kriteria_1": 24,
      "nazev_kriteria_2": 2.71
      // hodnoty pro všechna kritéria...
    }
    // další varianty...
  }
}
```

Relace mezi tabulkami

- Tabulka `analyzy` obsahuje referenci na tabulku `users` prostřednictvím sloupce `uzivatel`
- Relace mezi uživatelem a analýzami je typu 1:N (jeden uživatel může mít více analýz)

Diagram databázové struktury

```
+----------------+       +-------------------+
|     users      |       |     analyzy       |
+----------------+       +-------------------+
| email (PK)     |       | id (PK)           |
| password_hash  |       | nazev             |
| enabled        |       | uzivatel (FK)     |
| signed_up      +-------+ datum_vytvoreni   |
| last_login     |       | datum_upravy      |
| role           |       | data_json         |
| electre_*      |       |                   |
| stanoveni_vah  |       |                   |
+----------------+       +-------------------+
```

4. **Spusťte aplikaci**:
   - Klikněte na tlačítko "Run" v editoru Anvil
   - Nebo nasaďte na vlastní doménu: Pro self-hosting na vlastním VPS (DigitalOcean, AWS, Linode apod.) použijte oficiální průvodce [Anvil App Server](https://anvil.works/docs/how-to/app-server/cloud-deployment-guides)

## Použití

### Vytvoření nové analýzy

1. Přihlaste se ke svému účtu
2. Klikněte na "Přidat novou analýzu"
3. Postupujte podle průvodce:
   - Nastavte základní informace (název, popis)
   - Definujte kritéria a jejich typy (min/max)
   - Zvolte metodu stanovení vah (manuální, AHP, entropie)
   - Přidejte alternativy
   - Zadejte hodnoty hodnocení
4. Odešlete a zobrazte výsledky

### Interpretace výsledků

Každá metoda analýzy poskytuje různé výstupy:

- **WSM/WPM**: Jednoduché vážené skóre a pořadí
- **TOPSIS**: Relativní blízkost k ideálnímu řešení založená na vzdálenosti
- **ELECTRE**: Vztahy nadřazenosti mezi alternativami
- **MABAC**: Porovnání hraniční aproximace

Systém poskytuje podrobná vysvětlení každé metody a návod k interpretaci.

## Administrace

Administrátoři mohou:
- Spravovat uživatelské účty
- Prohlížet všechny analýzy v systému
- Upravovat nastavení systému
- Přistupovat ke statistikám využití

## Přispívání

Příspěvky jsou vítány! Neváhejte odeslat Pull Request.

1. Forkněte repozitář
2. Vytvořte svou feature větev (`git checkout -b funkce/amazing-feature`)
3. Commitněte své změny (`git commit -m 'Přidána úžasná funkce'`)
4. Pushněte do větve (`git push origin funkce/amazing-feature`)
5. Otevřete Pull Request

## Licence

Tento projekt je licencován pod licencí MIT - podrobnosti viz soubor LICENSE.

## Kontakt

Správce projektu: [LL](mailto:public.epidural736@simplelogin.com)

---

*MCApp - Transformujte složitá rozhodnutí na přesné analýzy*
