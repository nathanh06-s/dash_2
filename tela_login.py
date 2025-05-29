from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc

# Layout visual da tela de login
layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H2("🔐 Login", className="text-white text-center mb-4"),
                dbc.Input(id="input-usuario", placeholder="Usuário", type="text", className="mb-3"),
                dbc.Input(id="input-senha", placeholder="Senha", type="password", className="mb-3"),
                dbc.Button("Entrar", id="botao-login", color="primary", className="w-100"),
                html.Div(id="mensagem-login", className="text-danger mt-2 text-center")
            ], className="p-4 bg-dark rounded-3 shadow")
        ], width=4)
    ], justify="center", align="center", className="vh-100")
], fluid=True, className="bg-black")

# Callback de verificação de login
def registrar_callbacks(app):
    @app.callback(
        Output("mensagem-login", "children"),
        Output("url", "pathname"),
        Input("botao-login", "n_clicks"),
        State("input-usuario", "value"),
        State("input-senha", "value"),
        prevent_initial_call=True
    )
    def verificar_login(n_clicks, usuario, senha):
        if usuario == "CSC_Projetos" and senha == "Projetos2025@":
            return "", "/dashboard"
        else:
            return "Usuário ou senha incorretos", "/"