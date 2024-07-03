import io

import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

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
    box_height = 210
    draw_box(c, 50, height - 390, width - 100, box_height)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(60, height - 200, "Resumen de las Evaluaciones")
    c.drawString(
        60,
        height - 220,
        "Indicador                      Actual    Ultimo    General"
        "     Clasificacion",
    )
    c.setFont("Helvetica", 12)
    diff_weight = df["Peso Corporal (Kg)"].iloc[-1] - df["Peso Corporal (Kg)"].iloc[0]
    diff_weight = round(diff_weight, 1)
    diff_weight_last = (
        df["Peso Corporal (Kg)"].iloc[-1] - df["Peso Corporal (Kg)"].iloc[-2]
    )
    diff_weight_last = round(diff_weight_last, 1)

    diff_muscle = df["Masa Muscular (Kg)"].iloc[-1] - df["Masa Muscular (Kg)"].iloc[0]
    diff_muscle = round(diff_muscle, 1)
    diff_muscle_last = (
        df["Masa Muscular (Kg)"].iloc[-1] - df["Masa Muscular (Kg)"].iloc[-2]
    )

    diff_muscle_last = round(diff_muscle_last, 1)
    diff_fat = df["Grasa(%)"].iloc[-1] - df["Grasa(%)"].iloc[0]
    diff_fat = round(diff_fat, 1)
    diff_fat_last = df["Grasa(%)"].iloc[-1] - df["Grasa(%)"].iloc[-2]
    diff_fat_last = round(diff_fat_last, 1)

    diff_cc = df["CC"].iloc[-1] - df["CC"].iloc[0]
    diff_cc = round(diff_cc, 1)
    diff_cc_last = df["CC"].iloc[-1] - df["CC"].iloc[-2]
    diff_cc_last = round(diff_cc_last, 1)
    if df["Genero"].iloc[0] == "M":
        cc_classification = get_classification(df["CC"].iloc[-1], CC_MEN)
    else:
        cc_classification = get_classification(df["CC"].iloc[-1], CC_WOMEN)

    diff_cca = df["CCA"].iloc[-1] - df["CCA"].iloc[0]
    diff_cca = round(diff_cca, 1)
    diff_cca_last = df["CCA"].iloc[-1] - df["CCA"].iloc[-2]
    diff_cca_last = round(diff_cca_last, 1)

    diff_visceral_fat = df["GV"].iloc[-1] - df["GV"].iloc[0]
    diff_visceral_fat = round(diff_visceral_fat, 1)
    diff_visceral_fat_last = df["GV"].iloc[-1] - df["GV"].iloc[-2]
    diff_visceral_fat_last = round(diff_visceral_fat_last, 1)
    visceral_fat_classification = get_classification(df["GV"].iloc[-1], GRASA_VISCERAL)

    diff_imc = df["IMC"].iloc[-1] - df["IMC"].iloc[0]
    diff_imc = round(diff_imc, 1)
    diff_imc_last = df["IMC"].iloc[-1] - df["IMC"].iloc[-2]
    diff_imc_last = round(diff_imc_last, 1)
    if df["Edad"].iloc[0] < 60:
        imc_classification = get_classification(df["IMC"].iloc[-1], IMC_ADULT)
    else:
        imc_classification = get_classification(df["IMC"].iloc[-1], IMC_OLD)

    diff_water = df["Agua (%)"].iloc[-1] - df["Agua (%)"].iloc[0]
    diff_water = round(diff_water, 1)
    diff_water_last = df["Agua (%)"].iloc[-1] - df["Agua (%)"].iloc[-2]
    diff_water_last = round(diff_water_last, 1)

    c.drawString(
        60,
        height - 240,
        f"Peso Corporal                     {df['Peso Corporal (Kg)'].iloc[-1]}kg    "
        f"{f'+{diff_weight_last}' if diff_weight_last > 0 else diff_weight_last}kg    "
        f"{f'+{diff_weight}' if diff_weight > 0 else diff_weight}kg",
    )
    c.drawString(
        60,
        height - 260,
        f"Grasa (%)                          {df['Grasa(%)'].iloc[-1]}%     "
        f"{f'+{diff_fat_last}' if diff_fat_last > 0 else diff_fat_last}%     "
        f"{f'+{diff_fat}' if diff_fat > 0 else diff_fat}%",
    )
    c.drawString(
        60,
        height - 280,
        f"Agua (%)                              {df['Agua (%)'].iloc[-1]}%     "
        f"{f'+{diff_water_last}' if diff_water_last > 0 else diff_water_last}%     "
        f"{f'+{diff_water}' if diff_water > 0 else diff_water}%",
    )
    c.drawString(
        60,
        height - 300,
        f"Masa Muscular                      {df['Masa Muscular (Kg)'].iloc[-1]}kg    "
        f"{f'+{diff_muscle_last}' if diff_muscle_last > 0 else diff_muscle_last}kg    "
        f"{f'+{diff_muscle}' if diff_muscle > 0 else diff_muscle}kg",
    )
    c.drawString(
        60,
        height - 320,
        f"Circunferencia de Cintura          {df['CC'].iloc[-1]}cm    "
        f"{f'+{diff_cc_last}' if diff_cc_last > 0 else diff_cc_last}cm    "
        f"{f'+{diff_cc}' if diff_cc > 0 else diff_cc}cm",
    )
    c.drawString(
        60,
        height - 340,
        f"Circunferencia de Cadera      {df['CCA'].iloc[-1]}cm    "
        f"{f'+{diff_cca_last}' if diff_cca_last > 0 else diff_cca_last}cm    "
        f"{f'+{diff_cca}' if diff_cca > 0 else diff_cca}cm"
        f"            {cc_classification}",
    )
    c.drawString(
        60,
        height - 360,
        f"Grasa Visceral(%)                   {df['GV'].iloc[-1]}%    "
        f"{f'+{diff_visceral_fat_last}' if diff_visceral_fat_last > 0 else diff_visceral_fat_last}%    "
        f"{f'+{diff_visceral_fat}' if diff_visceral_fat > 0 else diff_visceral_fat}%"
        f"            {visceral_fat_classification}",
    )
    c.drawString(
        60,
        height - 380,
        f"IMC                                 {df['IMC'].iloc[-1]}    "
        f"{f'+{diff_imc_last}' if diff_imc_last > 0 else diff_imc_last}    "
        f"{f'+{diff_imc}' if diff_imc > 0 else diff_imc}"
        f"            {imc_classification}",
    )

    # Add Graphs
    def add_plot_to_pdf(c, plot_func, x, y, width, height):
        buffer = io.BytesIO()
        plot_func(buffer)
        buffer.seek(0)
        image = ImageReader(buffer)
        c.drawImage(image, x, y, width=width, height=height)
        buffer.close()

    def plot_grasa(buffer):
        plt.figure(figsize=(5, 3))
        plt.plot(df["Fecha"], df["Grasa(%)"], marker="o")
        plt.title("% Grasa Corporal")
        plt.xlabel("Fecha")
        plt.ylabel("% Grasa")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(buffer, format="png")
        plt.close()

    def plot_peso(buffer):
        plt.figure(figsize=(5, 3))
        plt.plot(df["Fecha"], df["Peso Corporal (Kg)"], marker="o")
        plt.title("Peso Corporal")
        plt.xlabel("Fecha")
        plt.ylabel("Peso (kg)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(buffer, format="png")
        plt.close()

    def plot_masa(buffer):
        plt.figure(figsize=(5, 3))
        plt.plot(df["Fecha"], df["Masa Magra (%)"], label="Masa Magra (%)", marker="o")
        plt.plot(df["Fecha"], df["Grasa(%)"], label="Grasa(%)", marker="o")
        plt.title("Masa Magra (%) y Grasa(%)")
        plt.xlabel("Fecha")
        plt.ylabel("%")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(buffer, format="png")
        plt.close()

    def plot_pie(buffer):
        labels = ["Masa Magra", "Masa Grasa"]
        sizes = [df["Masa Magra (%)"].iloc[-1], df["Grasa(%)"].iloc[-1]]
        colors = ["#ff9999", "#66b3ff"]
        plt.figure(figsize=(4, 4))
        plt.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=140)
        plt.axis("equal")
        plt.title("Último Masa Magra (%) vs Grasa(%)")
        plt.tight_layout()
        plt.savefig(buffer, format="png")
        plt.close()

    def plot_agua(buffer):
        plt.figure(figsize=(5, 3))
        plt.plot(df["Fecha"], df["Agua (%)"], marker="o")
        plt.title("% Agua Corporal")
        plt.xlabel("Fecha")
        plt.ylabel("% Agua")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(buffer, format="png")
        plt.close()

    # Position and size for the graphs
    graph_width = 240
    graph_height = 120
    graph_x = 50

    # Adjusted positions for multiple graphs
    graph_y_grasa = height - 550
    graph_y_peso = height - 550
    graph_y_masa = height - 670
    graph_y_pie = height - 700
    graph_y_agua = height - 790

    add_plot_to_pdf(c, plot_grasa, graph_x, graph_y_grasa, graph_width, graph_height)
    add_plot_to_pdf(c, plot_peso, width - 300, graph_y_peso, graph_width, graph_height)
    add_plot_to_pdf(c, plot_masa, graph_x, graph_y_masa, graph_width, graph_height)
    add_plot_to_pdf(c, plot_pie, width - 220, graph_y_pie, 150, 150)
    add_plot_to_pdf(c, plot_agua, graph_x, graph_y_agua, graph_width, graph_height)

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
