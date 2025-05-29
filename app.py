from dash import Dash, Input, Output, State, dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from layout import layout_dashboard
from dados import df_geral
from tela_login import layout as login_layout, registrar_callbacks

app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.DARKLY])
app.title = "Dashboard de Solicitações"
server = app.server
registrar_callbacks(app)

app.layout = html.Div([
    dcc.Location(id="url"),
    html.Div(id="pagina-conteudo")
])

@app.callback(
    Output("pagina-conteudo", "children"),
    Input("url", "pathname")
)
def navegar(pathname):
    if pathname == "/dashboard":
        return layout_dashboard()
    else:
        return login_layout

ordem_meses = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

# ================== Preencher filtro de mês com base no ano ==================
@app.callback(
    Output("filtro-mes", "options"),
    Input("filtro-ano", "value")
)
def atualizar_meses(ano):
    if ano is None:
        return []
    df = df_geral[df_geral["Início"].dt.year == ano]
    meses_disponiveis = df["Mes"].dropna().unique()
    return [{"label": m, "value": m} for m in ordem_meses if m in meses_disponiveis]

# ================== Preencher filtros gerais ==================
@app.callback(
    Output("filtro-fluxo", "options"),
    Output("filtro-regional", "options"),
    Output("filtro-situacao", "options"),
    Input("filtro-tipo", "value")
)
def preencher_filtros(tipo_selecionado):
    df = df_geral.copy()
    if tipo_selecionado:
        df = df[df["Tipo_Unidade"].isin(tipo_selecionado)]
    op_fluxo = [{"label": f, "value": f} for f in sorted(df["Fluxo"].dropna().unique())]
    op_regional = [{"label": r, "value": r} for r in sorted(df["Regional"].dropna().unique())]
    op_situacao = [{"label": s, "value": s} for s in sorted(df["Situação"].dropna().unique())]
    return op_fluxo, op_regional, op_situacao

# ================== Filtrar dados com base em todos os filtros ==================
def aplicar_filtros(fluxo, regional, tipo, ano, mes, situacao):
    df = df_geral.copy()
    if fluxo:
        df = df[df["Fluxo"].isin(fluxo)]
    if regional:
        df = df[df["Regional"].isin(regional)]
    if tipo:
        df = df[df["Tipo_Unidade"].isin(tipo)]
    if ano:
        df = df[df["Início"].dt.year == ano]
    if mes:
        df = df[df["Mes"].isin(mes)]
    if situacao:
        df = df[df["Situação"].isin(situacao)]
    return df

# ================== Cards ==================
@app.callback(
    Output("card-total", "children"),
    Output("card-media", "children"),
    Output("card-requisitantes", "children"),
    Output("card-servico", "children"),
    Output("card-produto", "children"),
    Input("filtro-fluxo", "value"),
    Input("filtro-regional", "value"),
    Input("filtro-tipo", "value"),
    Input("filtro-ano", "value"),
    Input("filtro-mes", "value"),
    Input("filtro-situacao", "value")
)
def atualizar_cards(fluxo, regional, tipo, ano, mes, situacao):
    df = aplicar_filtros(fluxo, regional, tipo, ano, mes, situacao)
    total = len(df)
    media = round(df.groupby("Mes").size().mean()) if not df.empty else 0
    requisitantes = df["Requisitante"].nunique() if "Requisitante" in df.columns else 0
    total_servico = len(df[df["Tipo_NF"] == "Serviço"])
    total_produto = len(df[df["Tipo_NF"] == "Produto"])
    perc_servico = round((total_servico / total) * 100) if total > 0 else 0
    perc_produto = round((total_produto / total) * 100) if total > 0 else 0
    return (
        f"{total:,}".replace(",", "."),
        f"{media:,}".replace(",", "."),
        f"{requisitantes}",
        f"{perc_servico}%",
        f"{perc_produto}%"
    )

# ================== Gráfico de Fluxo ==================
@app.callback(
    Output("grafico-fluxo", "figure"),
    Input("filtro-fluxo", "value"),
    Input("filtro-regional", "value"),
    Input("filtro-tipo", "value"),
    Input("filtro-ano", "value"),
    Input("filtro-mes", "value"),
    Input("filtro-situacao", "value")
)
def atualizar_grafico_fluxo(fluxo, regional, tipo, ano, mes, situacao):
    df = aplicar_filtros(fluxo, regional, tipo, ano, mes, situacao)
    fluxo_agg = df["Fluxo"].value_counts().sort_values(ascending=False)
    if fluxo_agg.empty:
        fig = go.Figure()
        fig.update_layout(title="Nenhum dado disponível", paper_bgcolor="#1a1c23",
                          plot_bgcolor="#1a1c23", font_color="white")
        return fig
    fig = px.bar(fluxo_agg, x=fluxo_agg.index, y=fluxo_agg.values,
                 labels={"x": "Fluxo", "y": "Solicitações"}, text_auto=True)
    fig.update_layout(plot_bgcolor="#1a1c23", paper_bgcolor="#1a1c23",
                      font_color="white", title_font_size=20, margin=dict(l=40, r=20, t=30, b=30),
                      xaxis=dict(showgrid=False), yaxis=dict(showgrid=False), showlegend=False)
    return fig

# ================== Gráfico de Mês comparando 2024 vs 2025 ==================
@app.callback(
    Output("grafico-mes", "figure"),
    Input("filtro-fluxo", "value"),
    Input("filtro-regional", "value"),
    Input("filtro-tipo", "value"),
    Input("filtro-situacao", "value"),
    Input("filtro-ano", "value")  # <- AGORA com esse input
)
def grafico_comparativo_mensal(fluxo, regional, tipo, situacao, ano):
    df = df_geral.copy()
    
    if fluxo:
        df = df[df["Fluxo"].isin(fluxo)]
    if regional:
        df = df[df["Regional"].isin(regional)]
    if tipo:
        df = df[df["Tipo_Unidade"].isin(tipo)]
    if situacao:
        df = df[df["Situação"].isin(situacao)]

    # ✅ Filtro dinâmico de ano
    anos_filtrados = [2024, 2025]
    if ano:
        anos_filtrados = [ano] if isinstance(ano, int) else ano
    df = df[df["Início"].dt.year.isin(anos_filtrados)]

    df["Ano"] = df["Início"].dt.year
    df["Mes"] = pd.Categorical(df["Mes"], categories=ordem_meses, ordered=True)
    df_group = df.groupby(["Ano", "Mes"]).size().reset_index(name="Contagem")

    fig = px.line(
        df_group,
        x="Mes",
        y="Contagem",
        color="Ano",
        markers=True,
        category_orders={"Mes": ordem_meses},
        color_discrete_map={2024: "#1f77b4", 2025: "#ff7f0e"},
        labels={"Contagem": "Solicitações"}
    )

    fig.update_layout(
        plot_bgcolor="#1a1c23",
        paper_bgcolor="#1a1c23",
        font_color="white",
        margin=dict(l=40, r=20, t=30, b=30),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        legend=dict(title=None)
    )

    return fig

# ================== Gráfico Regional ==================
@app.callback(
    Output("grafico-mapa", "figure"),
    Input("filtro-fluxo", "value"),
    Input("filtro-regional", "value"),
    Input("filtro-tipo", "value"),
    Input("filtro-ano", "value"),
    Input("filtro-mes", "value"),
    Input("filtro-situacao", "value")
)
def atualizar_grafico_regional(fluxo, regional, tipo, ano, mes, situacao):
    df = aplicar_filtros(fluxo, regional, tipo, ano, mes, situacao)
    reg_agg = df["Regional"].value_counts().sort_values(ascending=True)
    fig = px.bar(reg_agg, x=reg_agg.values, y=reg_agg.index, orientation="h",
                 labels={"x": "Solicitações", "y": "Regional"}, text_auto=True,
                 color=reg_agg.values, color_continuous_scale="Blues")
    fig.update_layout(plot_bgcolor="#1a1c23", paper_bgcolor="#1a1c23", font_color="white",
                      margin=dict(l=60, r=20, t=30, b=30), coloraxis_showscale=False,
                      xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
    return fig

# ================== Gráfico de Pizza ==================
@app.callback(
    Output("grafico-pizza", "figure"),
    Input("filtro-fluxo", "value"),
    Input("filtro-regional", "value"),
    Input("filtro-tipo", "value"),
    Input("filtro-ano", "value"),
    Input("filtro-mes", "value"),
    Input("filtro-situacao", "value")
)
def atualizar_grafico_pizza(fluxo, regional, tipo, ano, mes, situacao):
    df = aplicar_filtros(fluxo, regional, tipo, ano, mes, situacao)
    valores = df["Tipo_NF"].value_counts()
    labels = valores.index.tolist()
    values = valores.values.tolist()
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3,
                                 textinfo="label+percent+value",
                                 marker=dict(colors=["#1f77b4", "#ff4136"]))])
    fig.update_layout(paper_bgcolor="#1a1c23", font=dict(color="white"),
                      margin=dict(t=30, b=0))
    return fig

# ================== NOVO Gráfico Comparativo por Regional (2024 x 2025) ==================
@app.callback(
    Output("grafico-regional-comparativo", "figure"),
    Input("filtro-fluxo", "value"),
    Input("filtro-regional", "value"),
    Input("filtro-tipo", "value"),
    Input("filtro-situacao", "value")
)
def grafico_comparativo_regional(fluxo, regional, tipo, situacao):
    df = df_geral.copy()
    if fluxo:
        df = df[df["Fluxo"].isin(fluxo)]
    if regional:
        df = df[df["Regional"].isin(regional)]
    if tipo:
        df = df[df["Tipo_Unidade"].isin(tipo)]
    if situacao:
        df = df[df["Situação"].isin(situacao)]

    df = df[df["Início"].dt.year.isin([2024, 2025])]
    df["Ano"] = df["Início"].dt.year

    df_group = df.groupby(["Ano", "Regional"]).size().reset_index(name="Solicitações")

    # Reordena regionais com base no total (2024 + 2025)
    ordem = df_group.groupby("Regional")["Solicitações"].sum().sort_values(ascending=False).index.tolist()
    df_group["Regional"] = pd.Categorical(df_group["Regional"], categories=ordem, ordered=True)

    fig = px.bar(
        df_group,
        x="Solicitações",
        y="Regional",
        color="Ano",
        barmode="group",
        orientation="h",
        category_orders={"Regional": ordem},
        color_discrete_map={2024: "#1f77b4", 2025: "#ff7f0e"},
        labels={"Regional": "Regional", "Solicitações": "Qtd. Solicitações", "Ano": "Ano"}
    )

    fig.update_layout(
        plot_bgcolor="#1a1c23",
        paper_bgcolor="#1a1c23",
        font_color="white",
        margin=dict(l=60, r=20, t=30, b=30),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        coloraxis_showscale=False,
        legend=dict(title=None)
    )

    return fig

if __name__ == "__main__":
    app.run_server(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 8050)),
        debug=False
    )