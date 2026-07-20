import re

class QRCodeParser:
    def __init__(self):
        # A chave de acesso da NFC-e sempre possui exatamente 44 caracteres numéricos
        self.padrao_chave = r"(?P<chave>\d{44})"

    def extrair_chave(self, url_qrcode: str) -> str:
        """
        Recebe a URL lida do QR Code da nota fiscal e extrai a chave de 44 dígitos.
        Retorna a string da chave ou None se for inválida.
        """
        # Remove espaços e limpa a string
        url_limpa = url_qrcode.strip()
        
        match = re.search(self.padrao_chave, url_limpa)
        if match:
            chave = match.group("chave")
            print(f"[Parser] Chave de Acesso detectada: {chave}")
            return chave
            
        print("[Parser Erro] Nenhuma Chave de Acesso de 44 dígitos encontrada na URL.")
        return None

    def extrair_dados_da_chave(self, chave: str) -> dict:
        """
        A chave de acesso não é um número aleatório. Ela é estruturada.
        Este método quebra a chave para extrair metadados úteis para o seu banco.
        """
        if not chave or len(chave) != 44:
            return {}
            
        return {
            "estado_ibge": chave[0:2],     # Estado de emissão
            "ano_mes": f"20{chave[2:4]}-{chave[4:6]}", # Ano e Mês da compra
            "cnpj_emitente": chave[6:20],  # CNPJ do supermercado/loja
            "modelo": chave[20:22],        # Modelo da nota (geralmente 65 para NFC-e)
            "serie": chave[22:25],
            "numero_nota": chave[25:34]
        }