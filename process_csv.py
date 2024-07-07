import io

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

sns.set(style="whitegrid")
plt.rcParams.update(
    {
        "font.size": 12,
        "figure.figsize": (10, 6),
        "axes.titlesize": 14,
        "axes.labelsize": 12,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "axes.grid": True,
        "axes.edgecolor": "0.15",
        "axes.linewidth": 1.25,
        "date.autoformatter.day": "%d/%m/%Y",
    }
)

IMC_ADULT = {
    "18.5": "Bajo Peso",
    "24.9": "Peso Normal",
    "29.9": "Sobrepeso",
    "34.9": "Obesidad Grado 1",
    "39.9": "Obesidad Grado 2",
    "1000": "Obesidad Grado 3",
}
IMC_OLD = {
    "23": "Bajo Peso",
    "27.9": "Peso Normal",
    "31.9": "Sobrepeso",
    "39.9": "Obesidad",
    "1000": "Obesidad Morbida",
}

GRASA_VISCERAL = {"10": "Normal", "100": "Excesivo"}

CC_MEN = {
    "95": "Normal",
    "102": "Riesgo Elevado",
    "1000": "Riesgo Muy Elevado",
}
CC_WOMEN = {
    "82": "Normal",
    "88": "Riesgo Elevado",
    "1000": "Riesgo Muy Elevado",
}
WATER = {
    "45": "Bajo",
    "1000": "Normal",
}
FAT_YOUNG_WOMEN = {
    "21": "Bajo",
    "33": "Saludable",
    "39": "Sobrepeso",
    "1000": "Obesidad",
}
FAT_OLD_WOMEN = {
    "24": "Bajo",
    "36": "Saludable",
    "42": "Sobrepeso",
    "1000": "Obesidad",
}
FAT_YOUNG_MEN = {
    "8": "Bajo",
    "20": "Saludable",
    "25": "Sobrepeso",
    "1000": "Obesidad",
}
FAT_OLD_MEN = {
    "13": "Bajo",
    "25": "Saludable",
    "30": "Sobrepeso",
    "1000": "Obesidad",
}


def get_classification(value: float, reference: dict) -> str:
    for k in list(reference.keys()):
        if value < float(k):
            return reference[k]


def draw_box(c, x, y, width, height, stroke=1):
    c.setLineWidth(stroke)
    c.rect(x, y, width, height)


def generate_pdf(df, output_filename):
    c = canvas.Canvas(output_filename, pagesize=A4)
    width, height = A4

    # Set Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 50, "Control Corporal (Método: Bioimpedancia)")

    # Basic Information
    box_height = 100
    draw_box(c, 50, height - 160, width - 100, box_height)
    c.setFont("Helvetica", 12)
    c.drawString(60, height - 90, f"Nombre: {df['Nombre'].iloc[0]}")
    c.drawString(60, height - 110, f"Genero: {df['Genero'].iloc[0]}")
    c.drawString(
        60, height - 130, f"Fecha: {df['Fecha'].dt.strftime('%d/%m/%Y').iloc[-1]}"
    )
    c.drawString(60, height - 150, f"Altura: {df['Altura'].iloc[0]} cm")

    # Evaluation Summary
    box_height = 230
    draw_box(c, 50, height - 410, width - 100, box_height)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(60, height - 200, "Resumen de las Evaluaciones")
    headers = ["Indicador", "Actual", "Ultimo", "General", "Clasificacion"]
    x = 60
    y = height - 220
    coor_x = [x]
    for header in headers:
        c.drawString(x, y, header)
        x += 80
        coor_x.append(x)
    c.line(coor_x[0] - 8, y - 8, coor_x[-1] + 30, y - 8)
    y -= 20

    c.setFont("Helvetica", 12)
    data = []
    diff_days = df["Fecha"].iloc[-1] - df["Fecha"].iloc[0]
    diff_days_last = df["Fecha"].iloc[-1] - df["Fecha"].iloc[-2]
    data.append(
        ["Tiempo", "", f"{diff_days_last.days} dias", f"{diff_days.days} dias", ""]
    )

    diff_imc = df["IMC"].iloc[-1] - df["IMC"].iloc[0]
    diff_imc = round(diff_imc, 1)
    diff_imc_last = df["IMC"].iloc[-1] - df["IMC"].iloc[-2]
    diff_imc_last = round(diff_imc_last, 1)
    if df["Edad"].iloc[0] < 60:
        imc_classification = get_classification(df["IMC"].iloc[-1], IMC_ADULT)
    else:
        imc_classification = get_classification(df["IMC"].iloc[-1], IMC_OLD)

    diff_weight = df["Peso Corporal (Kg)"].iloc[-1] - df["Peso Corporal (Kg)"].iloc[0]
    diff_weight = round(diff_weight, 1)
    diff_weight_last = (
        df["Peso Corporal (Kg)"].iloc[-1] - df["Peso Corporal (Kg)"].iloc[-2]
    )
    diff_weight_last = round(diff_weight_last, 1)
    data.append(
        [
            "Peso (Kg)",
            df["Peso Corporal (Kg)"].iloc[-1],
            diff_weight_last,
            diff_weight,
            imc_classification,
        ]
    )

    diff_muscle = df["Masa Muscular (Kg)"].iloc[-1] - df["Masa Muscular (Kg)"].iloc[0]
    diff_muscle = round(diff_muscle, 1)
    diff_muscle_last = (
        df["Masa Muscular (Kg)"].iloc[-1] - df["Masa Muscular (Kg)"].iloc[-2]
    )
    data.append(
        [
            "MM (Kg)",
            df["Masa Muscular (Kg)"].iloc[-1],
            diff_muscle_last,
            diff_muscle,
            "",
        ]
    )

    diff_muscle_last = round(diff_muscle_last, 1)
    diff_fat = df["Grasa(%)"].iloc[-1] - df["Grasa(%)"].iloc[0]
    diff_fat = round(diff_fat, 1)
    diff_fat_last = df["Grasa(%)"].iloc[-1] - df["Grasa(%)"].iloc[-2]
    diff_fat_last = round(diff_fat_last, 1)
    if df["Genero"].iloc[0] == "M" and df["Edad"].iloc[0] < 60:
        fat_classification = get_classification(df["Grasa(%)"].iloc[-1], FAT_YOUNG_MEN)
    elif df["Genero"].iloc[0] == "M" and df["Edad"].iloc[0] > 59:
        fat_classification = get_classification(df["Grasa(%)"].iloc[-1], FAT_OLD_MEN)
    elif df["Genero"].iloc[0] == "F" and df["Edad"].iloc[0] > 59:
        fat_classification = get_classification(df["Grasa(%)"].iloc[-1], FAT_OLD_WOMEN)
    else:
        fat_classification = get_classification(
            df["Grasa(%)"].iloc[-1], FAT_YOUNG_WOMEN
        )
    data.append(
        [
            "Grasa (%)",
            df["Grasa(%)"].iloc[-1],
            diff_fat_last,
            diff_fat,
            fat_classification,
        ]
    )

    diff_cc = df["CC"].iloc[-1] - df["CC"].iloc[0]
    diff_cc = round(diff_cc, 1)
    diff_cc_last = df["CC"].iloc[-1] - df["CC"].iloc[-2]
    diff_cc_last = round(diff_cc_last, 1)
    if df["Genero"].iloc[0] == "M":
        cc_classification = get_classification(df["CC"].iloc[-1], CC_MEN)
    else:
        cc_classification = get_classification(df["CC"].iloc[-1], CC_WOMEN)
    data.append(
        ["CC (cm)", df["CC"].iloc[-1], diff_cc_last, diff_cc, cc_classification]
    )

    diff_cca = df["CCA"].iloc[-1] - df["CCA"].iloc[0]
    diff_cca = round(diff_cca, 1)
    diff_cca_last = df["CCA"].iloc[-1] - df["CCA"].iloc[-2]
    diff_cca_last = round(diff_cca_last, 1)
    data.append(["CCA (cm)", df["CCA"].iloc[-1], diff_cca_last, diff_cca, ""])

    diff_visceral_fat = df["GV"].iloc[-1] - df["GV"].iloc[0]
    diff_visceral_fat = round(diff_visceral_fat, 1)
    diff_visceral_fat_last = df["GV"].iloc[-1] - df["GV"].iloc[-2]
    diff_visceral_fat_last = round(diff_visceral_fat_last, 1)
    visceral_fat_classification = get_classification(df["GV"].iloc[-1], GRASA_VISCERAL)
    data.append(
        [
            "GV (%)",
            df["GV"].iloc[-1],
            diff_visceral_fat_last,
            diff_visceral_fat,
            visceral_fat_classification,
        ]
    )

    data.append(
        ["IMC", df["IMC"].iloc[-1], diff_imc_last, diff_imc, imc_classification]
    )

    diff_water = df["Agua (%)"].iloc[-1] - df["Agua (%)"].iloc[0]
    diff_water = round(diff_water, 1)
    diff_water_last = df["Agua (%)"].iloc[-1] - df["Agua (%)"].iloc[-2]
    diff_water_last = round(diff_water_last, 1)
    water_classification = get_classification(df["Agua (%)"].iloc[-1], WATER)
    data.append(
        [
            "Agua (%)",
            df["Agua (%)"].iloc[-1],
            diff_water_last,
            diff_water,
            water_classification,
        ]
    )

    count = 0
    for d in data:
        count += 1
        for i in range(0, len(d)):
            c.drawString(
                coor_x[i],
                y,
                str(d[i]),
            )
        if count < len(data):
            c.line(coor_x[0] - 8, y - 8, coor_x[-1] + 30, y - 8)
        y -= 20

    # Add Graphs
    def add_plot_to_pdf(c, plot_func, x, y, width, height):
        buffer = io.BytesIO()
        plot_func(buffer)
        buffer.seek(0)
        image = ImageReader(buffer)
        c.drawImage(image, x, y, width=width, height=height)
        buffer.close()

    def plot_peso(buffer):
        plt.figure(figsize=(10, 6))
        plt.plot(
            df["Fecha"].to_list(),
            df["Peso Corporal (Kg)"].to_list(),
            marker="o",
            color="tab:green",
            linewidth=3,
        )
        plt.title("Peso Corporal")
        plt.xlabel("Fecha")
        plt.ylabel("Peso (kg)")
        plt.xticks(df["Fecha"].to_list())
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(buffer, format="png")
        plt.close()

    def plot_masa(buffer):
        plt.figure(figsize=(10, 6))
        plt.plot(
            df["Fecha"].to_list(),
            df["Masa Magra (%)"].to_list(),
            label="Masa Magra (%)",
            marker="o",
            color="tab:orange",
            linewidth=3,
        )
        plt.bar(
            df["Fecha"].to_list(),
            df["Grasa(%)"].to_list(),
            label="Grasa(%)",
            color="tab:blue",
            width=8,
        )
        plt.title("Masa Magra (%) y Grasa(%)")
        plt.xlabel("Fecha")
        plt.ylabel("%")
        plt.xticks(df["Fecha"].to_list())
        plt.legend()
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(buffer, format="png")
        plt.close()

    def plot_agua(buffer):
        plt.figure(figsize=(10, 6))
        plt.plot(
            df["Fecha"].to_list(),
            df["Agua (%)"].to_list(),
            marker="o",
            color="tab:cyan",
            linewidth=3,
        )
        plt.title("% Agua Corporal")
        plt.xlabel("Fecha")
        plt.ylabel("% Agua")
        plt.xticks(rotation=45)
        plt.xticks(df["Fecha"].to_list())
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(buffer, format="png")
        plt.close()

    # Position and size for the graphs
    graph_width = 280
    graph_height = 200
    graph_x = 15

    # Adjusted positions for multiple graphs
    graph_y_peso = height - 615
    graph_y_masa = height - 810
    graph_y_agua = height - 810

    add_plot_to_pdf(c, plot_peso, width - 450, graph_y_peso, graph_width, graph_height)
    add_plot_to_pdf(c, plot_masa, graph_x, graph_y_masa, graph_width, graph_height)
    add_plot_to_pdf(c, plot_agua, width - 300, graph_y_agua, graph_width, graph_height)

    # Save the PDF
    c.showPage()
    c.save()


def process_csv(file_path):
    # Read CSV file
    df = pd.read_csv(file_path)
    df["Fecha"] = pd.to_datetime(df["Fecha"], format="%d/%m/%Y")
    df = df.sort_values(by=["Fecha"], ascending=True)

    df["Peso Corporal (Kg)"] = (
        df["Peso Corporal (Kg)"].str.replace(",", ".").astype(float)
    )
    df["Masa Muscular (Kg)"] = (
        df["Masa Muscular (Kg)"].str.replace(",", ".").astype(float)
    )
    df["Masa Magra (%)"] = df["Masa Magra (%)"].str.replace(",", ".").astype(float)
    df["Agua (%)"] = df["Agua (%)"].str.replace(",", ".").astype(float)
    df["Grasa(%)"] = df["Grasa(%)"].str.replace(",", ".").astype(float)
    df["IMC"] = df["IMC"].str.replace(",", ".").astype(float)

    # Generate PDF for the entire CSV
    output_filename = "./informe.pdf"
    generate_pdf(df, output_filename)

    return output_filename
