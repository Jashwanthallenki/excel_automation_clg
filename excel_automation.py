import streamlit as st
from datetime import date
from PIL import Image, ImageDraw, ImageFont
import io

# -------- CONFIGURATION & STYLING --------
st.set_page_config(layout="wide", page_title="Admission Report Generator")

# Inject custom CSS for a cleaner Streamlit UI
st.markdown("""
    <style>
    div[data-testid="stNumberInput"] label { display: none; }
    .stButton>button { background-color: #5cb85c; color: white; width: 100%; height: 3em; border-radius: 5px; }
    .report-header { font-weight: bold; color: #333; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Admission Report Generator")

# -------- STATE MANAGEMENT --------
campuses = ["Peddamberpet Campus", "Bonguloor Campus", "Adibatla Campus", "Arjun Campus"]

# Initialize session state so data persists between reruns
if 'input_data' not in st.session_state:
    st.session_state.input_data = {
        i: {"today": 0, "this_year": 0, "last_year": 0} for i in range(len(campuses))
    }

# -------- DATE SELECTION --------
selected_date = st.date_input("Select Date", value=date.today())
formatted_date = selected_date.strftime("%d-%m-%Y")

# -------- INPUT UI SECTION --------
st.subheader("Enter Admission Details")

# Define columns for the input table
hcol = st.columns([0.5, 2.5, 1.5, 2, 2])
headers = ["#", "Campus Name", "Today's Admissions", "This Year As On Date Total", "Last Year As On Date Total"]

for col, text in zip(hcol, headers):
    col.markdown(f"<div class='report-header'>{text}</div>", unsafe_allow_html=True)

data_for_report = []

for i, campus in enumerate(campuses):
    cols = st.columns([0.5, 2.5, 1.5, 2, 2])
    
    with cols[0]:
        st.write(f"{i+1}")
    with cols[1]:
        st.write(campus)
    with cols[2]: 
        t = st.number_input("T", min_value=0, key=f"t_{i}", value=st.session_state.input_data[i]["today"])
    with cols[3]: 
        ty = st.number_input("TY", min_value=0, key=f"ty_{i}", value=st.session_state.input_data[i]["this_year"])
    with cols[4]: 
        ly = st.number_input("LY", min_value=0, key=f"ly_{i}", value=st.session_state.input_data[i]["last_year"])
    
    # Save values back to session state
    st.session_state.input_data[i] = {"today": t, "this_year": ty, "last_year": ly}
    
    # Calculate Difference (This Year - Last Year)
    diff = ty - ly
    data_for_report.append([i+1, campus, t, ty, ly, diff])

st.divider()

# -------- IMAGE GENERATION ENGINE --------
def generate_final_report_image(rows, date_str):
    # Total canvas width and height
    width, height = 1200, 850
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    
    # Color Palette
    bright_green = (146, 208, 80)
    light_green = (226, 239, 218)
    black = (0, 0, 0)
    white = (255, 255, 255)
    border_gray = (180, 180, 180)

    # Font Handling (Fallback to default if fonts are missing)
    try:
        f_bold = ImageFont.truetype("arialbd.ttf", 28)
        f_reg = ImageFont.truetype("arial.ttf", 22)
        f_title = ImageFont.truetype("arialbd.ttf", 32)
    except:
        f_bold = f_reg = f_title = ImageFont.load_default()

    # 1. Main Green Header (Title)
    draw.rectangle([0, 0, width, 80], fill=bright_green, outline=black)
    draw.text((width//2, 40), "I YEAR ADMISSIONS 2026 - 2027", fill=black, font=f_title, anchor="mm")
    
    # 2. Date Section (White Background)
    draw.rectangle([0, 80, width, 130], fill=white, outline=black)
    draw.text((20, 105), f"DATE: {date_str}", fill=black, font=f_bold, anchor="lm")

    # 3. Table Column Headers
    y_offset = 130
    # Fixed col_x list with one extra item (1200) to prevent IndexError
    col_x = [0, 80, 420, 620, 820, 1020, 1200]
    header_labels = [
        "S.NO", 
        "CAMPUS NAME", 
        "TODAY'S\nADMISSIONS", 
        "THIS YEAR AS ON\nDATE TOTAL", 
        "LAST YEAR AS ON\nDATE TOTAL", 
        "DIFFERENCE"
    ]
    
    for i in range(len(header_labels)):
        draw.rectangle([col_x[i], y_offset, col_x[i+1], y_offset+100], fill=bright_green, outline=black)
        draw.multiline_text(
            ((col_x[i]+col_x[i+1])//2, y_offset+50), 
            header_labels[i], fill=black, font=f_reg, anchor="mm", align="center"
        )

    # 4. Data Rows (White Background)
    y_offset += 100
    totals = [0, 0, 0, 0] # indices 2, 3, 4, 5 from row data

    for row in rows:
        for i, val in enumerate(row):
            # Draw Cell
            draw.rectangle([col_x[i], y_offset, col_x[i+1], y_offset+60], fill=white, outline=border_gray)
            
            # Text color logic: Red if difference is negative
            txt_color = "red" if i == 5 and val < 0 else black
            draw.text(((col_x[i]+col_x[i+1])//2, y_offset+30), str(val), fill=txt_color, font=f_reg, anchor="mm")
        
        # Increment totals
        totals[0] += row[2] # Today
        totals[1] += row[3] # This Year
        totals[2] += row[4] # Last Year
        totals[3] += row[5] # Diff
        y_offset += 60

    # 5. Total Footer Row (Light Green)
    draw.rectangle([0, y_offset, width, y_offset+60], fill=light_green, outline=black)
    total_row_content = ["", "TOTAL", totals[0], totals[1], totals[2], totals[3]]
    
    for i, val in enumerate(total_row_content):
        if i == 0: continue # Skip S.NO cell
        idx = i if i < 2 else i # Map total content to correct col_x index
        
        txt_color = "red" if i == 5 and val < 0 else black
        draw.text(((col_x[i]+col_x[i+1])//2, y_offset+30), str(val), fill=txt_color, font=f_bold, anchor="mm")

    # Crop image based on the number of rows to avoid excessive whitespace
    img = img.crop((0, 0, width, y_offset + 60))
    
    # Save to buffer
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# -------- GENERATE & DOWNLOAD --------
if st.button("Generate Final Report"):
    img_data = generate_final_report_image(data_for_report, formatted_date)
    
    # Preview
    st.image(img_data, caption="Report Preview")
    
    # Download Button
    st.download_button(
        label="⬇️ Download Image (PNG)",
        data=img_data,
        file_name=f"Admission_Report_{formatted_date}.png",
        mime="image/png"
    )