from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

class GastosApp(App):
    def build(self):
        # Layout vertical com espaçamento
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Título
        self.label = Label(text="Meu App de Gastos (Teste APK)", font_size=20)
        layout.add_widget(self.label)
        
        # Campo de Texto (Filtrado para aceitar apenas números/pontos)
        self.txt_valor = TextInput(
            hint_text="Digite o valor (R$)", 
            input_filter="float", 
            multiline=False,
            size_hint_y=None,
            height=50
        )
        layout.add_widget(self.txt_valor)
        
        # Botão Salvar
        btn = Button(text="Salvar Gasto", size_hint_y=None, height=50)
        btn.bind(on_press=self.salvar_gasto)
        layout.add_widget(btn)
        
        return layout

    def salvar_gasto(self, instance):
        valor = self.txt_valor.text
        if valor:
            self.label.text = f"Sucesso: R$ {valor} registrado!"
            self.txt_valor.text = ""
        else:
            self.label.text = "Erro: Digite um valor primeiro."

if __name__ == '__main__':
    GastosApp().run()
