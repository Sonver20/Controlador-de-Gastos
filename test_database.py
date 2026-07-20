import os
import datetime
import pytest
from database import Database
from qrcode_parser import QRCodeParser

def test_extrair_chave_sefaz_real():
    parser = QRCodeParser()
    
    # Exemplo de URL real que a SEFAZ gera no QR Code (Simulada com chave válida de 44 dígitos)
    url_fake_sefaz = "https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx?p=43260790245579000108650010002598341123456789|2|1|1|CBE2A"
    
    chave_extraida = parser.extrair_chave(url_fake_sefaz)
    
    assert chave_extraida == "43260790245579000108650010002598341123456789"
    
    # Valida se a decomposição da chave está correta
    dados = parser.extrair_dados_da_chave(chave_extraida)
    assert dados["ano_mes"] == "2026-07"
    assert dados["cnpj_emitente"] == "90245579000108"

@pytest.fixture
def db_teste(tmp_path):
    """
    Fixture que cria um banco de dados temporário para cada teste.
    Garante o isolamento total: o que acontece em um teste não afeta o outro.
    """
    arquivo_db = tmp_path / "test_banco.db"
    return Database(str(arquivo_db))

def test_inicializacao_tabelas(db_teste):
    """Garante que a tabela 'despesas' é criada corretamente na inicialização."""
    with db_teste.conectar() as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='despesas';"
        )
        tabela = cursor.fetchone()
        assert tabela is not None
        assert tabela['name'] == 'despesas'

def test_salvar_e_listar_meses_com_totais(db_teste):
    """Testa a inserção individual e o agrupamento por meses com somas corretas."""
    db_teste.salvar_despesa("Alimentação", "Almoço", 35.50)
    db_teste.salvar_despesa("Transporte", "Uber", 15.00)
    
    mes_atual = datetime.datetime.now().strftime('%Y-%m')
    totais = db_teste.listar_meses_com_totais()
    
    assert len(totais) == 1
    assert totais[0]['mes'] == mes_atual
    assert totais[0]['total'] == 50.50

def test_salvar_despesas_massa(db_teste):
    """Testa o comportamento do executemany dentro do método de carga em massa."""
    itens = [
        ("Arroz 5kg", 22.90),
        ("Feijão 1kg", 8.50),
        ("Óleo de Soja", 6.20)
    ]
    db_teste.salvar_despesas_massa("Mercado", itens)
    
    mes_atual = datetime.datetime.now().strftime('%Y-%m')
    categorias = db_teste.listar_categorias_por_mes(mes_atual)
    
    assert len(categorias) == 1
    assert categorias[0]['categoria'] == "Mercado"
    assert categorias[0]['total'] == 37.60

def test_listar_itens_de_categoria(db_teste):
    """Garante a recuperação correta e ordenada dos itens detalhados de uma categoria."""
    db_teste.salvar_despesa("Lazer", "Cinema", 40.00)
    db_teste.salvar_despesa("Lazer", "Pipoca", 25.00)
    
    mes_atual = datetime.datetime.now().strftime('%Y-%m')
    itens = db_teste.listar_itens_de_categoria(mes_atual, "Lazer")
    
    assert len(itens) == 2
    assert itens[0]['descricao'] == "Pipoca"  # Ordenação descrescente por ID
    assert itens[1]['descricao'] == "Cinema"

def test_editar_despesa(db_teste):
    """Verifica se a alteração de dados via ID é persistida corretamente."""
    db_teste.salvar_despesa("Saúde", "Remédio Antigo", 10.00)
    mes_atual = datetime.datetime.now().strftime('%Y-%m')
    
    item = db_teste.listar_itens_de_categoria(mes_atual, "Saúde")[0]
    id_item = item['id']
    
    # Executa a alteração
    db_teste.editar_despesa(id_item, "Saúde", "Remédio Novo", 45.50)
    
    itens_atualizados = db_teste.listar_itens_de_categoria(mes_atual, "Saúde")
    assert itens_atualizados[0]['descricao'] == "Remédio Novo"
    assert itens_atualizados[0]['valor'] == 45.50

def test_deletar_despesa(db_teste):
    """Garante que a remoção física do registro funciona."""
    db_teste.salvar_despesa("Outros", "Taxa Desconhecida", 99.00)
    mes_atual = datetime.datetime.now().strftime('%Y-%m')
    
    item = db_teste.listar_itens_de_categoria(mes_atual, "Outros")[0]
    id_item = item['id']
    
    db_teste.deletar_despesa(id_item)
    
    itens_restantes = db_teste.listar_itens_de_categoria(mes_atual, "Outros")
    assert len(itens_restantes) == 0

def test_atomicidade_rollback_em_erro(db_teste):
    """
    TESTE CRÍTICO DO GERENCIADOR DE CONTEXTO:
    Garante que se uma exceção disparar no meio de uma operação,
    o banco executará o ROLLBACK e nenhuma sujeira será salva.
    """
    try:
        with db_teste.conectar() as conn:
            conn.execute(
                "INSERT INTO despesas (categoria, descricao, valor) VALUES (?, ?, ?)",
                ("Invasão", "Dado Fantasma", 1000.00)
            )
            # Força um erro bizarro logo após a inserção simulada
            raise RuntimeError("Falha catastrófica simulada no meio da transação")
    except RuntimeError:
        pass

    # Se o contextmanager funcionar, o Dado Fantasma NÃO pode estar no banco
    mes_atual = datetime.datetime.now().strftime('%Y-%m')
    assert len(db_teste.listar_categorias_por_mes(mes_atual)) == 0