import pandas as pd
import matplotlib.pyplot as plt
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from sklearn.cluster import KMeans
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


CSV_PATH = r"C:\Users\User\OneDrive\Documentos\python\dados-pytohn\conjunto_de_dados_do_aluno_com_risco.csv"
OUTPUT_DIR = r"C:\Users\User\OneDrive\Documentos\python\dados-pytohn\relatorios"
os.makedirs(OUTPUT_DIR, exist_ok=True)
PDF_PATH = os.path.join(OUTPUT_DIR, "relatorio_evasao.pdf")


# Etapa 2 – Análise e Tomada de Decisões

def carregar_dados():
    df = pd.read_csv(CSV_PATH)
    return df

def calcular_risco(df):
    # Calcular Risk Score se não existir
    if "Risco_Pontuação" not in df.columns:
        df["Nota_Score"] = 1 - (df["Nota_Media"] / 100)
        df["Freq_Score"] = 1 - (df["Frequencia_pct"] / 100)
        df["Abs_Score"] = df["Absenteismo"] / df["Absenteismo"].max()

        df["Risco_Pontuação"] = (0.5 * df["Nota_Score"] +
                                 0.3 * df["Freq_Score"] +
                                 0.2 * df["Abs_Score"]) * 100

        df["Categoria_de_Risco"] = pd.cut(df["Risco_Pontuação"], bins=[-1,29,59,100],
                                          labels=["Baixo","Médio","Alto"])
    return df

def clustering(df):
    X = df[["Nota_Media", "Frequencia_pct", "Absenteismo"]]
    kmeans = KMeans(n_clusters=3, random_state=42)
    df["Cluster"] = kmeans.fit_predict(X)
    return df

def classificacao(df):
    X = df[["Nota_Media","Frequencia_pct","Absenteismo"]]
    y = df["Evasao"].map({"Sim":1,"Não":0})

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    clf = DecisionTreeClassifier(random_state=42)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    print("\n✅ Classificação (Árvore de Decisão) - Acurácia:", accuracy_score(y_test, y_pred))
    return clf

def estatisticas_gerais(df):
    print("\n===== Estatísticas Gerais =====")
    print(df.describe(include="all"))
    print("\n===== Quantidade por Categoria de Risco =====")
    print(df["Categoria_de_Risco"].value_counts())
    print("\n===== Evasão =====")
    print(df["Evasao"].value_counts())

def gerar_graficos(df):
    plt.figure(figsize=(6,4))
    df["Risco_Pontuação"].hist(bins=20)
    plt.title("Distribuição da Pontuação de Risco")
    plt.xlabel("Pontuação de Risco")
    plt.ylabel("Quantidade de Alunos")
    hist_path = os.path.join(OUTPUT_DIR, "Distribuicao_Risco.png")
    plt.savefig(hist_path)
    plt.close()

    plt.figure(figsize=(6,4))
    plt.scatter(df["Nota_Media"], df["Risco_Pontuação"], alpha=0.6)
    plt.title("Nota Média vs Pontuação de Risco")
    plt.xlabel("Nota Média")
    plt.ylabel("Pontuação de Risco")
    scatter_path = os.path.join(OUTPUT_DIR, "Nota_vs_Risco.png")
    plt.savefig(scatter_path)
    plt.close()

    return hist_path, scatter_path

def gerar_pdf(df, hist_path, scatter_path):
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(PDF_PATH, pagesize=A4)
    story = []

    story.append(Paragraph("<b>Relatório de Evasão Escolar</b>", styles['Title']))
    story.append(Spacer(1,12))

    intro_text = """
     Fonte dos Dados:
    Os dados utilizados neste estudo foram simulados para fins acadêmicos, 
    seguindo os campos obrigatórios do enunciado da atividade 
    (ID, Nome, Nota Média, Frequência, Absenteísmo, Participação em Atividades Extracurriculares, 
    Participação em Programa de Apoio, Participação nas Aulas e Evasão).
    Não se tratam de dados reais de estudantes, mas de uma base fictícia construída 
    para aplicação de técnicas de mineração de dados.
    Este relatório foi gerado automaticamente a partir da base de dados dos alunos.
    Ele apresenta estatísticas, gráficos e a listagem dos 30 alunos com maior risco de evasão escolar.
    """
    story.append(Paragraph(intro_text, styles['Normal']))
    story.append(Spacer(1,12))

    story.append(Paragraph("<b>Distribuição da Pontuação de Risco</b>", styles['Heading2']))
    story.append(Image(hist_path, width=400, height=250))
    story.append(Spacer(1,12))

    story.append(Paragraph("<b>Nota Média vs Pontuação de Risco</b>", styles['Heading2']))
    story.append(Image(scatter_path, width=400, height=250))
    story.append(Spacer(1,12))

    story.append(Paragraph("<b>Top 30 Alunos com Maior Risco</b>", styles['Heading2']))
    top30 = df.sort_values("Risco_Pontuação", ascending=False).head(30)
    table_data = [list(top30.columns)] + top30.values.tolist()
    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.grey),
        ("TEXTCOLOR",(0,0),(-1,0),colors.whitesmoke),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("BOTTOMPADDING",(0,0),(-1,0),6),
        ("BACKGROUND",(0,1),(-1,-1),colors.beige),
        ("GRID",(0,0),(-1,-1),0.5,colors.black),
    ]))
    story.append(table)
    story.append(Spacer(1,12))

    recomendacoes = """
    <b>Estratégias de intervenção:</b><br/>
    - Risco Alto (>= 60): Tutoria individual, contato com a família, plano de recuperação.<br/>
    - Risco Médio (30–59): Monitoramento, incentivo à participação extracurricular, apoio pedagógico.<br/>
    - Risco Baixo (<30): Incentivos para manter engajamento e acompanhamento periódico.<br/>
    """
    story.append(Paragraph(recomendacoes, styles['Normal']))

    doc.build(story)
    print(f"\n✅ Relatório PDF gerado em: {PDF_PATH}")

# =============================
# PROGRAMA PRINCIPAL
# =============================
if __name__ == "__main__":
    df = carregar_dados()
    df = calcular_risco(df)
    df = clustering(df)
    clf = classificacao(df)
    estatisticas_gerais(df)
    hist_path, scatter_path = gerar_graficos(df)
    gerar_pdf(df, hist_path, scatter_path)
