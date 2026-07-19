import sqlite3
from contextlib import contextmanager

class Database:
    def __init__(self, caminho_db='gastos.db'):
        self.caminho_db = caminho_db
        self._criar_tabelas()

    @contextmanager
    def conectar(self):
        """Gerenciador de contexto centralizado para conexões isoladas."""
        conn = sqlite3.connect(self.caminho_db)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _criar_tabelas(self):
        with self.conectar() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS despesas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    categoria TEXT NOT NULL,
                    descricao TEXT NOT NULL,
                    valor REAL NOT NULL,
                    data TEXT DEFAULT (strftime('%Y-%m-%d', 'now'))
                );
            """)

    def _listar(self, query: str, parametros: tuple = ()) -> list:
        """Helper genérico para retornar múltiplos registros (rows) de forma segura."""
        with self.conectar() as conn:
            cursor = conn.execute(query, parametros)
            return cursor.fetchall()

    def salvar_despesa(self, categoria, descricao, valor):
        with self.conectar() as conn:
            conn.execute("""
                INSERT INTO despesas (categoria, descricao, valor) 
                VALUES (?, ?, ?)
            """, (categoria, descricao, valor))

    def salvar_despesas_massa(self, categoria, lista_itens):
        with self.conectar() as conn:
            conn.executemany("""
                INSERT INTO despesas (categoria, descricao, valor) 
                VALUES (?, ?, ?)
            """, [(categoria, desc, val) for desc, val in lista_itens])

    def listar_meses_com_totais(self):
        query = """
            SELECT strftime('%Y-%m', data) AS mes, SUM(valor) AS total 
            FROM despesas 
            GROUP BY mes 
            ORDER BY mes DESC
        """
        return self._listar(query)

    def listar_categorias_por_mes(self, mes):
        query = """
            SELECT categoria, SUM(valor) AS total 
            FROM despesas 
            WHERE strftime('%Y-%m', data) = ? 
            GROUP BY categoria
            ORDER BY total DESC
        """
        return self._listar(query, (mes,))

    def listar_itens_de_categoria(self, mes, categoria):
        query = """
            SELECT id, descricao, valor 
            FROM despesas 
            WHERE strftime('%Y-%m', data) = ? AND categoria = ?
            ORDER BY id DESC
        """
        return self._listar(query, (mes, categoria))

    def editar_despesa(self, id_item, categoria, descricao, valor):
        with self.conectar() as conn:
            conn.execute("""
                UPDATE despesas 
                SET categoria = ?, descricao = ?, valor = ? 
                WHERE id = ?
            """, (categoria, descricao, valor, id_item))

    def deletar_despesa(self, id_item):
        with self.conectar() as conn:
            conn.execute("DELETE FROM despesas WHERE id = ?", (id_item,))

    def close(self):
        pass