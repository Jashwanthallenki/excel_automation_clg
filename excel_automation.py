import streamlit as st
from datetime import date
from PIL import Image, ImageDraw, ImageFont
import io
import os

# -------- CONFIGURATION & STYLING --------
st.set_page_config(layout="wide", page_title="Admission Report Generator")

st.markdown("""
    <style>
    /* Improve button visibility on mobile */
    .stButton>button { 
        background-color: #5cb85c; 
        color: white; 
        width: 100%; 
        border-radius: 8px; 
        height: 3.5em; 
        font-weight: bold;
        margin-top: 10px;
    }
    /* Style the expander headers */
    .streamlit-expanderHeader {
        background-color: #f0f2f6;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Admission Report Generator")

# -------- STATE MANAGEMENT --------
campuses = ["Peddamberpet Campus", "Bonguloor Campus", "Adibatla Campus", "Arjun Campus"]

if 'input_data' not in st.session_state:
    st.session_state.input_data = {i: {"today": 0, "this_year": 0, "last_year": 0} for i in range(len(campuses))}

selected_date = st.date_input("Select Date", value=date.today())
formatted_date = selected_date.strftime("%d-%m-%Y")

# -------- MOBILE FRIENDLY INPUT UI (ALL OPEN BY DEFAULT) --------
st.subheader("Enter Admission Details")

data_for_report = []

for i, campus in enumerate(campuses):
    # Setting expanded=True makes all boxes open automatically
    with st.expander(f"📍 {campus}", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            t = st.number_input("Today", min_value=0, key=f"t_{i}", value=st.session_state.input_data[i]["today"])
        with col2:
            ty = st.number_input("This Year As On Date Total", min_value=0, key=f"ty_{i}", value=st.session_state.input_data[i]["this_year"])
        with col3:
            ly = st.number_input("Last Year As On Date Total", min_value=0, key=f"ly_{i}", value=st.session_state.input_data[i]["last_year"])
        
        # Save to state
        st.session_state.input_data[i] = {"today": t, "this_year": ty, "last_year": ly}
        data_for_report.append([i+1, campus, t, ty, ly, ty - ly])
# -------- FONT LOADING HELPER (Same as before) --------
def load_font(size, is_bold=False):
    font_file = "ARIALBD.TTF" if is_bold else "ARIAL.TTF"
    if os.path.exists(font_file):
        try: return ImageFont.truetype(font_file, size)
        except: return ImageFont.load_default()
    folder_path = os.path.join("arial", font_file)
    if os.path.exists(folder_path):
        return ImageFont.truetype(folder_path, size)
    return ImageFont.load_default()

# -------- IMAGE GENERATION ENGINE (Same as before) --------
def generate_final_report_image(rows, date_str):
    width, height = 1200, 1000 
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    
    bright_green, light_green = (146, 208, 80), (226, 239, 218)
    black, white, border_gray = (0, 0, 0), (255, 255, 255), (180, 180, 180)

    f_title = load_font(32, True)
    f_header = load_font(22, True)
    f_data = load_font(22, False) 
    f_total = load_font(28, True)

    draw.rectangle([0, 0, width, 80], fill=bright_green, outline=black)
    draw.text((width//2, 40), "I YEAR ADMISSIONS 2026 - 2027", fill=black, font=f_title, anchor="mm")
    
    draw.rectangle([0, 80, width, 135], fill=white, outline=black)
    draw.text((20, 107), f"DATE: {date_str}", fill=black, font=f_header, anchor="lm")

    y_offset = 135
    col_x = [0, 70, 420, 630, 840, 1040, 1200]
    header_labels = ["S.NO", "CAMPUS NAME", "TODAY'S\nADMISSIONS", "THIS YEAR AS ON\nDATE TOTAL", "LAST YEAR AS ON\nDATE TOTAL", "DIFFERENCE"]
    
    for i in range(len(header_labels)):
        draw.rectangle([col_x[i], y_offset, col_x[i+1], y_offset+110], fill=bright_green, outline=black)
        draw.multiline_text(((col_x[i]+col_x[i+1])//2, y_offset+55), header_labels[i], fill=black, font=f_header, anchor="mm", align="center", spacing=6)

    y_offset += 110
    totals = [0, 0, 0, 0]
    for row in rows:
        row_height = 70
        for i, val in enumerate(row):
            draw.rectangle([col_x[i], y_offset, col_x[i+1], y_offset+row_height], fill=white, outline=border_gray)
            txt_color = "red" if i == 5 and val < 0 else black
            draw.text(((col_x[i]+col_x[i+1])//2, y_offset + (row_height//2)), str(val), fill=txt_color, font=f_data, anchor="mm")
        totals[0]+=row[2]; totals[1]+=row[3]; totals[2]+=row[4]; totals[3]+=row[5]
        y_offset += row_height

    draw.rectangle([0, y_offset, width, y_offset+80], fill=light_green, outline=black)
    total_row = ["", "TOTAL", totals[0], totals[1], totals[2], totals[3]]
    for i, val in enumerate(total_row):
        if i == 0: continue
        txt_color = "red" if i == 5 and val < 0 else black
        draw.text(((col_x[i]+col_x[i+1])//2, y_offset+40), str(val), fill=txt_color, font=f_total, anchor="mm")

    img = img.crop((0, 0, width, y_offset + 80))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

if st.button("Generate Final Report"):
    img_data = generate_final_report_image(data_for_report, formatted_date)
    st.image(img_data, caption="Report Preview")
    st.download_button("⬇️ Download Image (PNG)", img_data, f"Report_{formatted_date}.png", "image/png")