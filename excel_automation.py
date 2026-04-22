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

    # Fonts
    try:
        font_title = ImageFont.truetype("arial.ttf", 24)
        font_header = ImageFont.truetype("arial.ttf", 14)
        font_cell = ImageFont.truetype("arial.ttf", 14)
    except:
        font_title = font_header = font_cell = ImageFont.load_default()

    # Layout
    col_widths = [80, 320, 150, 220, 220, 120]
    row_height = 45

    total_width = sum(col_widths)
    total_height = 200 + (len(data) + 2) * row_height

    img = Image.new("RGB", (total_width, total_height), "white")
    draw = ImageDraw.Draw(img)

    # Colors
    green = (139, 195, 74)
    light_green = (198, 239, 206)
    black = (0, 0, 0)
    red = (255, 0, 0)

    # -------- TITLE --------
    draw.rectangle([0, 0, total_width, 60], fill=green)
    title = "I YEAR ADMISSIONS 2026 - 2027"
    w = draw.textlength(title, font=font_title)
    draw.text(((total_width - w) / 2, 15), title, fill="black", font=font_title)

    # -------- DATE --------
    draw.text((10, 75), f"DATE: {date_text}", fill="black", font=font_header)

    # -------- HEADER --------
    headers = [
        "S.NO",
        "CAMPUS NAME",
        "TODAY'S",
        "THIS YEAR TOTAL",
        "LAST YEAR TOTAL",
        "DIFFERENCE"
    ]

    y = 110

    for i, h in enumerate(headers):
        x1 = sum(col_widths[:i])
        x2 = x1 + col_widths[i]

        draw.rectangle([x1, y, x2, y+row_height], fill=green, outline=black)

        text_w = draw.textlength(h, font=font_header)
        draw.text(
            (x1 + (col_widths[i] - text_w)/2, y + 12),
            h,
            fill="black",
            font=font_header
        )

    # -------- DATA ROWS --------
    y += row_height

    total_today = total_this = total_last = total_diff = 0

    for row in data:
        for i, val in enumerate(row):
            x1 = sum(col_widths[:i])
            x2 = x1 + col_widths[i]

            draw.rectangle([x1, y, x2, y+row_height], outline=black)

            # 🔥 Handle Difference column
            if i == 5:
                color = red if val < 0 else black
                text = str(val)
            else:
                color = black
                text = str(val)

            text_w = draw.textlength(text, font=font_cell)

            draw.text(
                (x1 + (col_widths[i] - text_w)/2, y + 12),
                text,
                fill=color,
                font=font_cell
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

        if i == 5:
            color = red if val < 0 else black
        else:
            color = black

        text = str(val)
        text_w = draw.textlength(text, font=font_cell)

        draw.text(
            (x1 + (col_widths[i] - text_w)/2, y + 12),
            text,
            fill=color,
            font=font_cell
        )

    # Save
    file = "report.png"
    img.save(file)

    return file


# -------- BUTTON --------
if st.button("Generate Report"):

    image_file = generate_image(data, formatted_date)

    st.image(image_file)

    with open(image_file, "rb") as f:
        st.download_button("Download Image", f, file_name="report.png")