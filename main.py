from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from database import Database
from notification_processor import NotificationProcessor
from kivymd.uix.screen import MDScreen
from kivy.utils import platform
if platform == 'android':
    from jnius import autoclass

# ... (seu código existente) ...

class TelaConfiguracoes(MDScreen):
    def abrir_permissao_android(self):
        if platform == 'android':
            try:
                Intent = autoclass('android.content.Intent')
                Settings = autoclass('android.provider.Settings')
                intent = Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS)
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                activity = PythonActivity.mActivity
                activity.startActivity(intent)
            except Exception as e:
                print(f"Erro ao abrir permissão: {e}")
        else:
            print("Configuração de permissão apenas no Android.")

class TelaTestadorNotificacao(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.processor = NotificationProcessor()

    def simular_chegada(self, pacote, mensagem):
        # Executa a limpeza por regex e inserção no banco
        sucesso = self.processor.processar_notificacao(pacote, mensagem)
        if sucesso:
            # Você pode disparar um snackbar ou apenas printar
            print("Inserido com sucesso via simulação de Push!")

class MenuLateral(Popup):
    pass

class PopupEditar(Popup):
    def __init__(self, id_item, categoria, descricao, valor, callback_atualizar, **kwargs):
        super().__init__(**kwargs)
        self.id_item = id_item
        self.callback_atualizar = callback_atualizar
        self.ids.txt_cat.text = str(categoria)
        self.ids.txt_desc.text = str(descricao)
        self.ids.txt_val.text = str(valor)

    def salvar_alteracao(self, nova_cat, nova_desc, novo_val):
        cat = nova_cat.strip()
        desc = nova_desc.strip()
        val_txt = Filter = novo_val.strip()

        if not cat or not desc or not val_txt:
            return
        try:
            val_float = float(val_txt)
            app = MDApp.get_running_app()
            app.db.editar_despesa(self.id_item, cat, desc, val_float)
            self.dismiss()
            self.callback_atualizar()
        except ValueError:
            pass

class TelaCadastro(MDScreen):
    def adicionar_gasto(self, input_cat, input_desc, input_val):
        app = MDApp.get_running_app()
        cat = input_cat.text.strip()
        desc = input_desc.text.strip()
        val_txt = input_val.text.strip()

        if not cat or not desc or not val_txt:
            app.mostrar_alerta("Erro", "Preencha todos os campos.")
            return
        try:
            val = float(val_txt)
            app.db.salvar_despesa(cat, desc, val)
            input_desc.text = ""
            input_val.text = ""
            app.mostrar_alerta("Sucesso", "Item gravado.")
        except ValueError:
            app.mostrar_alerta("Erro", "Valor inválido.")

class TelaCadastroMassa(MDScreen):
    def processar_massa(self, cat_texto, bloco_texto):
        app = MDApp.get_running_app()
        cat = cat_texto.strip()
        texto = bloco_texto.strip()

        if not cat or not texto:
            app.mostrar_alerta("Erro", "Forneça a categoria e os itens.")
            return

        linhas = texto.split('\n')
        itens_validos = []
        erros = 0

        for linha in linhas:
            linha = linha.strip()
            if not linha:
                continue
            if ',' in linha:
                partes = linha.rsplit(',', 1)
                desc = partes[0].strip()
                val_str = partes[1].strip()
                try:
                    val = float(val_str)
                    if desc:
                        itens_validos.append((desc, val))
                    else:
                        erros += 1
                except ValueError:
                    erros += 1
            else:
                erros += 1

        if itens_validos:
            app.db.salvar_despesas_massa(cat, itens_validos)
            self.ids.txt_bloco.text = ""
            msg = f"{len(itens_validos)} itens processados."
            if erros > 0:
                msg += f"\n({erros} linhas ignoradas)."
            app.mostrar_alerta("Carga Concluída", msg)
        else:
            app.mostrar_alerta("Erro", "Nenhum item válido. Use o formato:\nNome, Valor")

class TelaVisualizacao(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.estado_atual = 'meses'
        self.mes_selecionado = None
        self.categoria_selecionada = None

    def on_enter(self):
        self.renderizar_arvore()

    def renderizar_arvore(self):
        app = MDApp.get_running_app()
        layout = self.ids.grid_lista
        layout.clear_widgets()
        self.ids.btn_voltar.disabled = (self.estado_atual == 'meses')

        if self.estado_atual == 'meses':
            self.ids.lbl_titulo_contexto.text = "Meses"
            for linha in app.db.listar_meses_com_totais():
                mes = linha['mes']
                total = linha['total']
                btn = MDRaisedButton(text=f"{mes}  |  R$ {total:.2f}", size_hint_x=1, height=50)
                btn.bind(on_release=lambda inst, m=mes: self.selecionar_mes(m))
                layout.add_widget(btn)

        elif self.estado_atual == 'categorias':
            self.ids.lbl_titulo_contexto.text = f"Mês: {self.mes_selecionado}"
            for linha in app.db.listar_categorias_por_mes(self.mes_selecionado):
                cat = inline_cat = linha['categoria']
                total = linha['total']
                btn = MDRaisedButton(text=f"{cat}  |  R$ {total:.2f}", size_hint_x=1, height=50, md_bg_color=(0.2, 0.4, 0.5, 1))
                btn.bind(on_release=lambda inst, c=cat: self.selecionar_categoria(c))
                layout.add_widget(btn)

        elif self.estado_atual == 'itens':
            self.ids.lbl_titulo_contexto.text = f"{self.categoria_selecionada}"
            for linha in app.db.listar_itens_de_categoria(self.mes_selecionado, self.categoria_selecionada):
                id_item = linha['id']
                desc = linha['descricao']
                val = linha['valor']

                row = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
                row.add_widget(MDLabel(text=str(desc), size_hint_x=0.4, theme_text_color="Primary"))
                row.add_widget(MDLabel(text=f"R$ {val:.2f}", size_hint_x=0.3, theme_text_color="Secondary"))
                
                btn_edit = MDRaisedButton(text="E", size_hint_x=0.15, md_bg_color=(0.1, 0.5, 0.2, 1))
                btn_edit.bind(on_release=lambda inst, i=id_item, d=desc, v=val: self.abrir_edicao(i, d, v))
                row.add_widget(btn_edit)

                btn_del = MDRaisedButton(text="X", size_hint_x=0.15, md_bg_color=(0.7, 0.1, 0.1, 1))
                btn_del.bind(on_release=lambda inst, i=id_item: self.deletar_item(i))
                row.add_widget(btn_del)
                layout.add_widget(row)

    def selecionar_mes(self, mes):
        self.mes_selecionado = mes
        self.estado_atual = 'categorias'
        self.renderizar_arvore()

    def selecionar_categoria(self, cat):
        self.categoria_selecionada = cat
        self.estado_atual = 'itens'
        self.renderizar_arvore()

    def voltar_nivel(self):
        if self.estado_atual == 'itens':
            self.estado_atual = 'categorias'
            self.categoria_selecionada = None
        elif self.estado_atual == 'categorias':
            self.estado_atual = 'meses'
            self.mes_selecionado = None
        self.renderizar_arvore()

    def abrir_edicao(self, id_item, desc, val):
        popup = PopupEditar(
            id_item=id_item, 
            categoria=self.categoria_selecionada, 
            descricao=desc, 
            valor=val, 
            callback_atualizar=self.renderizar_arvore
        )
        popup.open()

    def deletar_item(self, id_item):
        app = MDApp.get_running_app()
        app.db.deletar_despesa(id_item)
        self.renderizar_arvore()

class ControladorGastos(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Indigo"
        self.db = Database()
        Window.bind(on_keyboard=self.gerenciar_teclado)
        
        self.sm = MDScreenManager()
        self.sm.add_widget(TelaCadastro(name='cadastro'))
        self.sm.add_widget(TelaCadastroMassa(name='cadastro_massa'))
        self.sm.add_widget(TelaVisualizacao(name='visualizacao'))
        self.sm.add_widget(TelaTestadorNotificacao(name='testador_notificacao'))
        self.sm.add_widget(TelaConfiguracoes(name='configuracoes'))
        
        self.menu = None
        return self.sm

    def abrir_menu(self):
        if not self.menu:
            self.menu = MenuLateral()
        self.menu.open()

    def mudar_tela(self, nome_tela):
        self.sm.current = nome_tela

    def mostrar_alerta(self, titulo, message):
        dialog = MDDialog(
            title=titulo,
            text=message,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()

    def gerenciar_teclado(self, window, key, scancode, codepoint, modifiers):
        if key == 27:
            if self.sm.current == 'visualizacao' and self.sm.get_screen('visualizacao').estado_atual != 'meses':
                self.sm.get_screen('visualizacao').voltar_nivel()
                return True
            self.encerrar_app()
            return True  
        return False

    def encerrar_app(self, *args):
        if hasattr(self, 'db') and self.db:
            self.db.close()
        self.stop()

if __name__ == '__main__':
    try:
        ControladorGastos().run()
    except Exception as e:
        import traceback
        with open('erro_real.txt', 'w') as f:
            traceback.print_exc(file=f)