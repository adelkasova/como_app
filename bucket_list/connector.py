from mysql.connector import connect
import pandas as pd
from datetime import datetime

class Connector:
    def __init__(self, user: str, password: str, host: str, port: str, database: str) -> None:
        self.__user = user
        self.__password = password
        self.__host = host
        self.__port = int(port)
        self.__database = database
        self.__connection = None
        return
    
    def __connect(self) -> None:
        self.__connection = connect(user=self.__user, password=self.__password, host=self.__host, database=self.__database, port=self.__port)
        return
    
    def __disconnect(self) -> None:
        self.__connection = self.__connection.close()
        return
    
    @staticmethod
    def __custom_sort(item_list):
    # Funkce pro extrahování počátečního čísla, pokud existuje
        def extract_number_prefix(s):
            num = ''
            for char in s:
                if char.isdigit():
                    num += char
                else:
                    break
            return int(num) if num else float('inf')  # Návrat 'inf', pokud není číslo

        # Seřazení pomocí klíčové funkce
        item_list.sort(key=lambda x: (extract_number_prefix(x), x))
    
    def ziskat_kategorie_ukolu(self) -> list:
        """Vrátí seznam všech jedinečných kategorií ukolů, které jsou v databázi"""
        self.__connect()
        cursor = self.__connection.cursor()
        cursor.execute("SELECT kategorie FROM ukoly")
        result = cursor.fetchall()
        self.__disconnect()

        result = [i[0] for i in result]
        result = list(set(result))
        self.__custom_sort(result)

        return result
    
    def ziskat_nazvy_ukolu(self) -> list:
        """Vrátí seznam všech jedinečných názvů ukolů, které jsou v databázi"""
        self.__connect()
        cursor = self.__connection.cursor()
        cursor.execute("SELECT ukol FROM ukoly")
        result = cursor.fetchall()
        self.__disconnect()

        result = [i[0] for i in result]
        self.__custom_sort(result)

        return result
    
    def ziskat_nazvy_ukolu_podle_kategorie(self, kategorie: str) -> list:
        """Vrátí seznam úkolů v dané kategorii"""
        self.__connect()
        cursor = self.__connection.cursor()
        cursor.execute("SELECT ukol FROM ukoly WHERE kategorie = %s", (kategorie,))
        result = cursor.fetchall()
        self.__disconnect()

        result = [i[0] for i in result]
        self.__custom_sort(result)

        return result
    
    def ziskat_ukoly(self) -> pd.DataFrame:
        """Vrátí dataframe se všemi úkoly v databázi"""
        self.__connect()
        cursor = self.__connection.cursor()
        cursor.execute("SELECT * FROM ukoly")
        result = cursor.fetchall()
        self.__disconnect()

        result = pd.DataFrame(result, columns=['id', 'kategorie', 'ukol', 'cas'])
        result = result.set_index('id')
        result.index.name = None

        return result
    
    def pridat_ukol(self, kategorie: str, ukol: str, cas: str) -> None:
        """Přidá úkol do databáze. Je potřeba zadat parametry kategorie, název úkolu a čas."""
        self.__connect()
        cursor = self.__connection.cursor()
        cursor.execute("INSERT INTO ukoly (kategorie, ukol, cas) VALUES (%s, %s, %s)", (kategorie, ukol, cas))
        self.__connection.commit()
        self.__disconnect()
        return
    
    def ziskat_vsechny_uzivatele(self) -> pd.DataFrame:
        """"Vrátí dataframe se všemi uživateli v databázi"""
        self.__connect()
        cursor = self.__connection.cursor()
        cursor.execute("SELECT * FROM login")
        result = cursor.fetchall()
        self.__disconnect()

        result = pd.DataFrame(result, columns=['id', 'jmeno', 'heslo', "datum_narozeni"])
        result = result.set_index('id')
        result.index.name = None

        return result
    
    def pridat_uzivatele(self, jmeno: str, heslo: str, datum_narozeni: datetime) -> None:
        """Přidá uživatele do databáze. Je potřeba zadat parametry jméno, heslo a datum narození."""
#        if not isinstance(datum_narozeni, datetime.date):
#            raise TypeError("Datum narození musí být typu datetime")
        self.__connect()
        cursor = self.__connection.cursor()
        cursor.execute("INSERT INTO login (jmeno, heslo, datum_narozeni) VALUES (%s, %s, %s)", (jmeno, heslo, datum_narozeni))
        self.__connection.commit()
        self.__disconnect()
        return
    
    def ziskat_splnene_ukoly(self) -> pd.DataFrame:
        """Vrátí dataframe se všemi splněnými úkoly v databázi"""
        self.__connect()
        cursor = self.__connection.cursor()
        cursor.execute("SELECT * FROM splnene_ukoly")
        result = cursor.fetchall()
        self.__disconnect()

        result = pd.DataFrame(result, columns=['id', "jmeno", "kategorie", 'ukol', "splneno", 'datum', "poznamka"])
        result = result.set_index('id')
        result.index.name = None

        return result
    
    def pridat_splneny_ukol(self, jmeno: str, kategorie: str, ukol: str, splneno: bool, datum: datetime, poznamka: str = None) -> None:
        """Přidá splněný úkol do databáze. Je potřeba zadat parametry jméno, kategorie, název úkolu, splněno, datum. Parametr poznamka je nepovinný."""
#        if not isinstance(datum, datetime):
#            raise TypeError("Datum musí být typu datetime")
        if not isinstance(splneno, bool):
            raise TypeError("Splněno musí být typu bool (True/False)")
        self.__connect()
        cursor = self.__connection.cursor()
        cursor.execute("INSERT INTO splnene_ukoly (jmeno, kategorie, ukol, splneno, datum, poznamka) VALUES (%s, %s, %s, %s, %s, %s)", (jmeno, kategorie, ukol, splneno, datum, poznamka))
        self.__connection.commit()
        self.__disconnect()
        return
    
    def upravit_tabulku_splnene_ukoly(self, dataframe: pd.DataFrame) -> None:
        """Aktualizuje tabulku splněných úkolů v databázi podle dataframe"""
        self.__connect()
        cursor = self.__connection.cursor()

        cursor.execute("SELECT * FROM splnene_ukoly")
        result = cursor.fetchall()

        splnene_ukoly = pd.DataFrame(result, columns=['id', "jmeno", "kategorie", 'ukol', "splneno", 'datum', "poznamka"])
        splnene_ukoly = splnene_ukoly.set_index('id')
        splnene_ukoly.index.name = None

        # Získat tabulku všech úkolů, kde došlo ke změně
        #dataframe = dataframe[~dataframe.isin(splnene_ukoly)].dropna()

        # Aktualizovat řádky v databázi podle id záznamu
        for index, row in dataframe.iterrows():
            cursor.execute("UPDATE splnene_ukoly SET splneno = %s, datum = %s, poznamka = %s WHERE id = %s", (row['splneno'], row['datum'], row['poznamka'], index))
            self.__connection.commit()

        self.__disconnect()
        return