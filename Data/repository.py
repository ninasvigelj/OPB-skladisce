import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
import Data.auth_public as auth
import datetime
import os
import pandas as pd

DB_PORT = os.environ.get('POSTGRES_PORT', 5432)


class Repo:
    def __init__(self):
        self.conn = psycopg2.connect(
            database=auth.db,
            host=auth.host,
            user=auth.user,
            password=auth.password,
            port=DB_PORT
        )
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    def bdp_po_regijah(self) -> pd.DataFrame:
        """
        Vrne podatke BDP po regijah
        """
        query = """
            SELECT f.leto, r.regija, f.BDP
            FROM fact_bdp_regije f
            JOIN dim_regije r ON f.regija_id = r.regija_id
        """
        df = pd.read_sql(query, self.conn)
        #self.conn.close()
        return df
    
    def stanovanja_po_obcinah_in_regijah(self) -> pd.DataFrame:
        """
        Vrne podatke o stanovanjih po občinah s pridruženimi regijami
        """
        query = """
            SELECT f.leto, o.obcina, o.regija, f.sobe, f.povrsina_m2, f.stevilo
            FROM fact_stanovanja_obcine f
            JOIN dim_obcine o ON f.obcina_id = o.obcina_id
        """ # vrne dataframe s stolpci: leto, obcina, regija, sobe, povrsina_m2, stevilo
        df = pd.read_sql(query, self.conn)
        #self.conn.close()
        return df
    
    def vse_po_regijah(self) -> pd.DataFrame:
        """
        Vrne združene podatke o BDPju, št. podjetij in delovno aktivnih po regijah.
        """
        query = """
            WITH bdp AS (
                SELECT f.leto, r.regija, f.BDP
                FROM fact_bdp_regije f
                JOIN dim_regije r ON f.regija_id = r.regija_id
            ),
            podjetja AS (
                SELECT f.leto, o.regija, SUM(f.stevilo) AS stevilo_podjetij
                FROM fact_st_podjetij f
                JOIN dim_obcine o ON f.obcina_id = o.obcina_id
                GROUP BY f.leto, o.regija
            ),
            delovno AS (
                SELECT f.leto, o.regija, SUM(f.stevilo) AS delovno_aktivno
                FROM fact_delovno_aktivno f
                JOIN dim_obcine o ON f.obcina_id = o.obcina_id
                GROUP BY f.leto, o.regija
            ),
            stanovanja AS (
                SELECT f.leto, o.regija, SUM(f.stevilo) AS stevilo_stanovanj
                FROM fact_stanovanja_obcine f
                JOIN dim_obcine o ON f.obcina_id = o.obcina_id
                GROUP BY f.leto, o.regija
            )
            SELECT bdp.leto, bdp.regija, bdp.BDP, podjetja.stevilo_podjetij, delovno.delovno_aktivno, stanovanja.stevilo_stanovanj
            FROM bdp
            LEFT JOIN podjetja ON bdp.leto = podjetja.leto AND bdp.regija = podjetja.regija
            LEFT JOIN delovno ON bdp.leto = delovno.leto AND bdp.regija = delovno.regija
            LEFT JOIN stanovanja ON bdp.leto = stanovanja.leto AND bdp.regija = stanovanja.regija
        """
        df = pd.read_sql(query, self.conn)
        #self.conn.close()
        return df
    
    def vse_brez_bdp_po_obcinah(self) -> pd.DataFrame:
        """
        Vrne podatke o številu stanovanj, delovno aktivnih in številu podjetij po občinah in letih.
        """
        query = """
            WITH podjetja AS (
                SELECT f.leto, o.obcina, o.regija, SUM(f.stevilo) AS stevilo_podjetij
                FROM fact_st_podjetij f
                JOIN dim_obcine o ON f.obcina_id = o.obcina_id
                GROUP BY f.leto, o.obcina, o.regija
            ),
            delovno AS (
                SELECT f.leto, o.obcina, o.regija, SUM(f.stevilo) AS delovno_aktivno
                FROM fact_delovno_aktivno f
                JOIN dim_obcine o ON f.obcina_id = o.obcina_id
                GROUP BY f.leto, o.obcina, o.regija
            ),
            stanovanja AS (
                SELECT f.leto, o.obcina, o.regija, SUM(f.stevilo) AS stevilo_stanovanj
                FROM fact_stanovanja_obcine f
                JOIN dim_obcine o ON f.obcina_id = o.obcina_id
                GROUP BY f.leto, o.obcina, o.regija
            )
            SELECT COALESCE(podjetja.leto, delovno.leto) AS leto,
                COALESCE(podjetja.obcina, delovno.obcina) AS obcina,
                COALESCE(podjetja.regija, delovno.regija) AS regija,
                stevilo_stanovanj,
                delovno_aktivno,
                stevilo_podjetij
            FROM podjetja
            FULL OUTER JOIN delovno 
                ON podjetja.leto = delovno.leto AND podjetja.obcina = delovno.obcina
            FULL OUTER JOIN stanovanja
                ON COALESCE(podjetja.leto, delovno.leto) = stanovanja.leto AND 
                COALESCE(podjetja.obcina, delovno.obcina) = stanovanja.obcina
        """
        df = pd.read_sql(query, self.conn)
        return df
    
    def close(self):
        self.conn.close()

# repo = Repo()
# bdp = repo.vse_brez_bdp_po_obcinah()
# print(bdp.head())