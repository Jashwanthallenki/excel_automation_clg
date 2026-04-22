import streamlit as st
from datetime import date
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(layout="wide")
st.title("📊 Admission Report Generator")

# -------- DATE --------
selected_date = st.date_input("Select Date", value=date.today())
formatted_date = selected_date.strftime("%d-%m-%Y")

# -------- INPUT --------
campuses = [
    "Peddamberpet Campus",
    "Bonguloor Campus",
    "Adibatla Campus",
    "Arjun Campus"
]

data = []

st.subheader("Enter Admission Details")

for i, campus in enumerate(campuses):
    col1, col2, col3 = st.columns(3)

    with col1:
        today = st.number_input(f"{campus} - Today", min_value=0, key=f"{i}t")
    with col2:
        this_year = st.number_input(f"{campus} - This Year", min_value=0, key=f"{i}ty")
    with col3:
        last_year = st.number_input(f"{campus} - Last Year", min_value=0, key=f"{i}ly")

    diff = this_year - last_year
    data.append([i+1, campus, today, this_year, last_year, diff])


# -------- IMAGE GENERATOR --------
def generate_image(data, date_text):

    from PIL import Image, ImageDraw, ImageFont

    # -------- Fonts (Excel-like) --------
    try:
        font_title = ImageFont.truetype("arialbd.ttf", 34)   # bold
        font_header = ImageFont.truetype("arialbd.ttf", 18)
        font_cell = ImageFont.truetype("arial.ttf", 18)
        font_bold = ImageFont.truetype("arialbd.ttf", 18)
    except:
        font_title = font_header = font_cell = font_bold = ImageFont.load_default()

    # -------- Layout (mobile optimized) --------
    col_widths = [70, 260, 140, 200, 200, 120]
    row_height = 60

    total_width = sum(col_widths)
    total_height = 240 + (len(data) + 2) * row_height

    img = Image.new("RGB", (total_width, total_height), "white")
    draw = ImageDraw.Draw(img)

    # -------- Colors --------
    green = (139, 195, 74)
    light_green = (198, 239, 206)
    black = (0, 0, 0)
    red = (220, 0, 0)

    # -------- TITLE --------
    draw.rectangle([0, 0, total_width, 80], fill=green)
    title = "I YEAR ADMISSIONS 2026 - 2027"

    title_w = draw.textlength(title, font=font_title)
    draw.text(((total_width - title_w)/2, 20), title, fill="black", font=font_title)

    # -------- DATE --------
    draw.text((15, 100), f"DATE: {date_text}", fill="black", font=font_header)

    # -------- HEADERS --------
    headers = [
        "S.NO",
        "CAMPUS\nNAME",
        "TODAY'S\nADMISSIONS",
        "THIS YEAR AS ON DATE\nTOTAL ADMISSIONS",
        "LAST YEAR AS ON DATE\nTOTAL ADMISSIONS",
        "DIFFERENCE"
    ]

    y = 140

    for i, h in enumerate(headers):
        x1 = sum(col_widths[:i])
        x2 = x1 + col_widths[i]

        draw.rectangle([x1, y, x2, y+row_height], fill=green, outline=black)

        draw.multiline_text(
            (x1 + col_widths[i]/2, y + row_height/2),
            h,
            fill="black",
            font=font_header,
            anchor="mm",
            align="center"
        )

    # -------- DATA ROWS --------
    y += row_height

    total_today = total_this = total_last = total_diff = 0

    for row in data:
        for i, val in enumerate(row):
            x1 = sum(col_widths[:i])
            x2 = x1 + col_widths[i]

            draw.rectangle([x1, y, x2, y+row_height], outline=black)

            # Negative coloring
            color = red if (i == 5 and val < 0) else black

            draw.text(
                (x1 + col_widths[i]/2, y + row_height/2),
                str(val),
                fill=color,
                font=font_cell,
                anchor="mm"
            )

        total_today += row[2]
        total_this += row[3]
        total_last += row[4]
        total_diff += row[5]

        y += row_height

    # -------- TOTAL ROW --------
    totals = ["", "TOTAL", total_today, total_this, total_last, total_diff]

    for i, val in enumerate(totals):
        x1 = sum(col_widths[:i])
        x2 = x1 + col_widths[i]

        draw.rectangle([x1, y, x2, y+row_height], fill=light_green, outline=black)

        color = red if (i == 5 and val < 0) else black

        font_used = font_bold if i == 1 else font_cell

        draw.text(
            (x1 + col_widths[i]/2, y + row_height/2),
            str(val),
            fill=color,
            font=font_used,
            anchor="mm"
        )

    # -------- SAVE HIGH QUALITY --------
    file = "report.png"
    img.save(file, dpi=(300, 300))

    return file
# -------- BUTTON --------
if st.button("Generate Report"):

    image_file = generate_image(data, formatted_date)

    st.image(image_file)

    with open(image_file, "rb") as f:
        st.download_button("Download Image", f, file_name="report.png")