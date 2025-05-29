from dash import html, dcc
import dash_bootstrap_components as dbc

def layout_dashboard():
    return dbc.Container([
        # Título
        html.Div([
            html.H2("Dashboard de Solicitações", className="text-white fw-bold display-5 mb-0"),
            html.Hr(className="border-secondary mt-2 mb-4")
        ], className="text-center"),

        # Linha de filtros
        dbc.Row([
            dbc.Col([
                html.Label("Fluxo", className="text-light fw-semibold small"),
                dcc.Dropdown(id="filtro-fluxo", options=[], multi=True, placeholder="Selecione o(s) fluxo(s)")
            ], width=2),

            dbc.Col([
                html.Label("Regional", className="text-light fw-semibold small"),
                dcc.Dropdown(id="filtro-regional", options=[], multi=True, placeholder="Selecione a(s) regionais")
            ], width=2),

            dbc.Col([
                html.Label("Tipo de Unidade", className="text-light fw-semibold small"),
                dcc.Dropdown(
                    id="filtro-tipo",
                    options=[
                        {"label": "Hospital", "value": "Hospital"},
                        {"label": "Operadora", "value": "Operadora"}
                    ],
                    multi=True,
                    placeholder="Selecione"
                )
            ], width=2),

            dbc.Col([
                html.Label("Ano", className="text-light fw-semibold small"),
                dcc.Dropdown(
                    id="filtro-ano",
                    options=[
                        {"label": "2024", "value": 2024},
                        {"label": "2025", "value": 2025}
                    ],
                    multi=False,
                    placeholder="Selecione o ano"
                )
            ], width=2),

            dbc.Col([
                html.Label("Mês", className="text-light fw-semibold small"),
                dcc.Dropdown(id="filtro-mes", options=[], multi=True, placeholder="Selecione o(s) mês(es)")
            ], width=2),

            dbc.Col([
                html.Label("Situação", className="text-light fw-semibold small"),
                dcc.Dropdown(id="filtro-situacao", options=[], multi=True, placeholder="Selecione a(s) situação(ões)")
            ], width=2),
        ], className="mb-4"),

        # Cards
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("Total de Solicitações", className="text-secondary"),
                    html.H3("0000", id="card-total", className="text-primary fw-bold")
                ])
            ], className="shadow-sm border-0 rounded-4 bg-gradient"), width=2),

            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("Requisitantes Ativos", className="text-secondary"),
                    html.H3("0000", id="card-requisitantes", className="text-success fw-bold")
                ])
            ], className="shadow-sm border-0 rounded-4 bg-gradient"), width=2),

            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("Média/Mês", className="text-secondary"),
                    html.H3("00", id="card-media", className="text-warning fw-bold")
                ])
            ], className="shadow-sm border-0 rounded-4 bg-gradient"), width=2),

            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("% NF Serviço", className="text-secondary"),
                    html.H3("0%", id="card-servico", className="text-info fw-bold")
                ])
            ], className="shadow-sm border-0 rounded-4 bg-gradient"), width=3),

            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("% NF Produto", className="text-secondary"),
                    html.H3("0%", id="card-produto", className="text-danger fw-bold")
                ])
            ], className="shadow-sm border-0 rounded-4 bg-gradient"), width=3),
        ], className="mb-4"),

        # Gráficos principais
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("Solicitações por Fluxo", className="grafico-titulo"),
                    dcc.Graph(id="grafico-fluxo", config={"displayModeBar": False}, className="grafico-box")
                ])
            ], width=6),

            dbc.Col([
                html.Div([
                    html.H5("Solicitações por Mês", className="grafico-titulo"),
                    dcc.Graph(id="grafico-mes", config={"displayModeBar": False}, className="grafico-box")
                ])
            ], width=6),
        ], className="mb-4"),

        # Gráficos por regional e tipo NF
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("Distribuição por Regional", className="grafico-titulo"),
                    dcc.Graph(id="grafico-mapa", config={"displayModeBar": False}, className="grafico-box")
                ])
            ], width=6),

            dbc.Col([
                html.Div([
                    html.H5("Proporção de tipo NF", className="grafico-titulo"),
                    dcc.Graph(id="grafico-pizza", config={"displayModeBar": False}, className="grafico-box")
                ])
            ], width=6),    
        ], className="mb-4"),

        # NOVO gráfico comparativo por regional
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("Comparativo por Regional (2024 x 2025)", className="grafico-titulo"),
                    dcc.Graph(id="grafico-regional-comparativo", config={"displayModeBar": False}, className="grafico-box")
                ])
            ], width=12)
        ], className="mb-2")

    ], fluid=True, className="bg-dark text-light px-4 pt-3 pb-5")