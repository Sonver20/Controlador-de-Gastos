import re
import json
from kivy.network.urlrequest import UrlRequest
from database import Database

class NotificationProcessor:
    def __init__(self, db_path='gastos.db'):
        self.db = Database(db_path)
        
        # Padrões locais de segurança caso o celular esteja sem internet no momento
        self.padroes_bancos = {
            "com.nu.production": r"compra aprovada no (?P<store>.*?):?\\s*r\$\s*(?P<value>[\d,.]+)"
        }
        
        # URL do arquivo bruto no seu GitHub
        self.url_remota = "https://raw.githubusercontent.com/Sonver20/Controlador-de-Gastos/main/bancos.json"
        self.atualizar_padroes_da_nuvem()

    def atualizar_padroes_da_nuvem(self):
        """Busca o JSON na nuvem sem travar a interface do aplicativo."""
        def sucesso(req, resultado):
            try:
                # Se o resultado já vier como string, converte. Se vier como dict, só atribui.
                self.padroes_bancos = json.loads(resultado) if isinstance(resultado, str) else resultado
                print("[Automação] Sincronização com a nuvem realizada com sucesso.")
            except Exception as e:
                print(f"[Erro Sincronização] JSON remoto malformado: {e}")

        def erro(req, resultado):
            print("[Aviso] Falha ao conectar ao servidor de Regex. Usando cache local.")

        # Dispara a requisição assíncrona
        UrlRequest(self.url_remota, on_success=sucesso, on_failure=erro, on_error=erro, timeout=5)

    def processar_notificacao(self, pacote_origem: str, texto_mensagem: str, callback_ui=None) -> bool:
        """
        O parâmetro 'callback_ui' opcional permite passar uma função da tela 
        para exibir um aviso visual (Snackbar/Popup) caso a validação falhe.
        """
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
            callback_ui(f"Texto não bate com o padrão do banco ({pacote_origem})")
        return False