import streamlit as st
from datetime import date
from PIL import Image, ImageDraw, ImageFont
import io
import os

# -------- CONFIGURATION & STYLING --------
st.set_page_config(layout="wide", page_title="Admission Report Generator")

st.markdown("""
    <style>
    div[data-testid="stNumberInput"] label { display: none; }
    .stButton>button { background-color: #5cb85c; color: white; width: 100%; border-radius: 5px; height: 3em; }
    .report-header { font-weight: bold; color: #333; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Admission Report Generator")

# -------- STATE MANAGEMENT --------
campuses = ["Peddamberpet Campus", "Bonguloor Campus", "Adibatla Campus", "Arjun Campus"]

if 'input_data' not in st.session_state:
    st.session_state.input_data = {i: {"today": 0, "this_year": 0, "last_year": 0} for i in range(len(campuses))}

selected_date = st.date_input("Select Date", value=date.today())
formatted_date = selected_date.strftime("%d-%m-%Y")

# -------- INPUT UI SECTION --------
st.subheader("Enter Admission Details")
hcol = st.columns([0.5, 2.5, 1.5, 2, 2])
headers = ["#", "Campus Name", "Today's Admissions", "This Year Total", "Last Year Total"]
for col, text in zip(hcol, headers):
    col.markdown(f"<div class='report-header'>{text}</div>", unsafe_allow_html=True)

data_for_report = []
for i, campus in enumerate(campuses):
    cols = st.columns([0.5, 2.5, 1.5, 2, 2])
    with cols[0]: st.write(f"{i+1}")
    with cols[1]: st.write(campus)
    with cols[2]: t = st.number_input("T", min_value=0, key=f"t_{i}", value=st.session_state.input_data[i]["today"])
    with cols[3]: ty = st.number_input("TY", min_value=0, key=f"ty_{i}", value=st.session_state.input_data[i]["this_year"])
    with cols[4]: ly = st.number_input("LY", min_value=0, key=f"ly_{i}", value=st.session_state.input_data[i]["last_year"])
    
    st.session_state.input_data[i] = {"today": t, "this_year": ty, "last_year": ly}
    data_for_report.append([i+1, campus, t, ty, ly, ty - ly])

# -------- FONT LOADING HELPER --------
def load_font(size, is_bold=False):
    """
    Looks for fonts in the current directory. 
    Make sure these files are uploaded to your GitHub!
    """
    font_file = "arialbd.ttf" if is_bold else "arial.ttf"
    
    if os.path.exists(font_file):
        return ImageFont.truetype(font_file, size)
    else:
        # Fallback if you forget to upload fonts
        return ImageFont.load_default()

# -------- IMAGE GENERATION ENGINE --------
def generate_final_report_image(rows, date_str):
    width, height = 1200, 850
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    
    bright_green = (146, 208, 80)
    light_green = (226, 239, 218)
    black, white = (0, 0, 0), (255, 255, 255)
    border_gray = (180, 180, 180)

    # Load specific fonts
    f_title = load_font(32, True)
    f_bold = load_font(26, True)
    f_reg = load_font(22, False)

    # 1. Main Header
    draw.rectangle([0, 0, width, 80], fill=bright_green, outline=black)
    draw.text((width//2, 40), "I YEAR ADMISSIONS 2026 - 2027", fill=black, font=f_title, anchor="mm")
    
    # 2. Date Section
    draw.rectangle([0, 80, width, 130], fill=white, outline=black)
    draw.text((20, 105), f"DATE: {date_str}", fill=black, font=f_bold, anchor="lm")

    # 3. Table Headers
    y_offset = 130
    col_x = [0, 80, 420, 620, 820, 1020, 1200]
    header_labels = ["S.NO", "CAMPUS NAME", "TODAY'S\nADMISSIONS", "THIS YEAR AS ON\nDATE TOTAL", "LAST YEAR AS ON\nDATE TOTAL", "DIFFERENCE"]
    
    for i in range(len(header_labels)):
        draw.rectangle([col_x[i], y_offset, col_x[i+1], y_offset+100], fill=bright_green, outline=black)
        draw.multiline_text(((col_x[i]+col_x[i+1])//2, y_offset+50), header_labels[i], fill=black, font=f_bold, anchor="mm", align="center")

    # 4. Data Rows
    y_offset += 100
    totals = [0, 0, 0, 0]
    for row in rows:
        for i, val in enumerate(row):
            draw.rectangle([col_x[i], y_offset, col_x[i+1], y_offset+60], fill=white, outline=border_gray)
            txt_color = "red" if i == 5 and val < 0 else black
            draw.text(((col_x[i]+col_x[i+1])//2, y_offset+30), str(val), fill=txt_color, font=f_reg, anchor="mm")
        
        totals[0] += row[2]
        totals[1] += row[3]
        totals[2] += row[4]
        totals[3] += row[5]
        y_offset += 60

    # 5. Total Row
    draw.rectangle([0, y_offset, width, y_offset+60], fill=light_green, outline=black)
    total_row = ["", "TOTAL", totals[0], totals[1], totals[2], totals[3]]
    for i, val in enumerate(total_row):
        if i == 0: continue
        txt_color = "red" if i == 5 and val < 0 else black
        draw.text(((col_x[i]+col_x[i+1])//2, y_offset+30), str(val), fill=txt_color, font=f_bold, anchor="mm")

    img = img.crop((0, 0, width, y_offset + 60))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

if st.button("Generate Final Report"):
    img_data = generate_final_report_image(data_for_report, formatted_date)
    st.image(img_data, caption="Report Preview")
    st.download_button("⬇️ Download Image (PNG)", img_data, f"Report_{formatted_date}.png", "image/png") 