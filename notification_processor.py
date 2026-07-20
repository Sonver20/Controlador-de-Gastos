import re
import json
from kivy.network.urlrequest import UrlRequest
from database import Database

class NotificationProcessor:
    def __init__(self, db_path='gastos.db'):
        self.db = Database(db_path)
        
        # RESTAURADO: Todos os bancos agora são o padrão local padrão.
        # O teste vai funcionar offline mesmo que a requisição de rede falhe.
        self.padroes_bancos = {
            "com.nu.production": r"compra aprovada no (?P<store>.*?):?\\s*r\$\s*(?P<value>[\d,.]+)",
            "br.com.itau": r"itaucard:\s*compra aprovada no (?P<store>.*?)\s+valor\s+r\$\s*(?P<value>[\d,.]+)",
            "com.itau.production": r"compra aprovada de\s*r\$\s*(?P<value>[\d,.]+)\s+na\s+(?P<store>.*)",
            "com.intermedium": r"inter:\s*compra no (?P<store>.*?)\s+de\s+r\$\s*(?P<value>[\d,.]+)"
        }
        
        # URL fictícia. Enquanto você não mudar para o seu link real do GitHub,
        # o app vai disparar o erro no log, mas usará os dados acima normalmente.
        self.url_remota = "https://raw.githubusercontent.com/Sonver20/Controlador-de-Gastos/main/banco.json"
        self.atualizar_padroes_da_nuvem()

    def atualizar_padroes_da_nuvem(self):
        """Tenta atualizar os padrões pela internet sem quebrar o funcionamento local."""
        def sucesso(req, resultado):
            try:
                self.padroes_bancos = json.loads(resultado) if isinstance(resultado, str) else resultado
                print("[Automação] Sincronização com a nuvem realizada com sucesso.")
            except Exception as e:
                print(f"[Erro Sincronização] JSON remoto malformado: {e}")

        def erro(req, resultado):
            # O app cai aqui por causa da URL falsa, mantendo o dicionário local intacto
            print("[Aviso] Usando banco de dados de Regex local padrão.")

        UrlRequest(self.url_remota, on_success=sucesso, on_failure=erro, on_error=erro, timeout=2)

    def processar_notificacao(self, pacote_origem: str, texto_mensagem: str, callback_ui=None) -> bool:
        if pacote_origem not in self.padroes_bancos:
            if callback_ui: 
                callback_ui(f"Pacote não monitorado: {pacote_origem}")
            return False  

        padrao = self.padroes_bancos[pacote_origem]
        match = re.search(padrao, texto_mensagem, re.IGNORECASE)

        if match:
            estabelecimento = match.group("store").strip().rstrip('.')
            valor_str = match.group("value").replace(".", "").replace(",", ".")
            
            try:
                valor = float(valor_str)
                self.db.salvar_despesa(
                    categoria="Cartão de Crédito",
                    descricao=estabelecimento,
                    valor=valor
                )
                return True
            except ValueError:
                if callback_ui: callback_ui("Erro crítico na conversão do valor.")
                return False
        
        if callback_ui: 
            callback_ui(f"Texto não condiz com o padrão do banco ({pacote_origem})")
        return False