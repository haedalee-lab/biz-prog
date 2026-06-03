import streamlit as st
import streamlit.components.v1 as components
import os
import time
import json
import random

# Page Configuration
st.set_page_config(
    page_title="🎲 주사위 굴리기",
    page_icon="🎲",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Pastel color definitions matching index.html
pastel_colors = [
    {"bg": "#dfc2ab", "core": "#cba88e"}, # 0: Wooden Tan (Designated first color)
    {"bg": "#ffd1dc", "core": "#eab5c3"}, # 1: Soft Pink
    {"bg": "#d0e8f2", "core": "#b6d6e3"}, # 2: Soft Blue
    {"bg": "#d2ebd4", "core": "#b7d6b9"}, # 3: Soft Green
    {"bg": "#fef5c8", "core": "#e7ddaa"}, # 4: Soft Yellow
    {"bg": "#e5dbf0", "core": "#ccbcd9"}, # 5: Soft Purple
    {"bg": "#fce2cc", "core": "#e3c6ac"}, # 6: Soft Coral
    {"bg": "#d1f2e5", "core": "#b3ded0"}  # 7: Soft Mint
]

# Initialize Session States
if "num_dice" not in st.session_state:
    st.session_state.num_dice = 1

if "dice_colors" not in st.session_state:
    st.session_state.dice_colors = [pastel_colors[0]]

if "saved_history" not in st.session_state:
    st.session_state.saved_history = []

if "current_roll" not in st.session_state:
    st.session_state.current_roll = None

if "current_roll_id" not in st.session_state:
    st.session_state.current_roll_id = None

if "show_history" not in st.session_state:
    st.session_state.show_history = False

if "history_page" not in st.session_state:
    st.session_state.history_page = 1

# Load the HTML content directly
parent_dir = os.path.dirname(os.path.abspath(__file__))
component_dir = os.path.join(parent_dir, "dice_component")

# Declare the 3D Dice Component as a formal custom bidirectional component
dice_component = components.declare_component("retro_3d_dice", path=component_dir)

# Ensure the colors list has exactly num_dice elements
if len(st.session_state.dice_colors) < st.session_state.num_dice:
    while len(st.session_state.dice_colors) < st.session_state.num_dice:
        # Choose from index 1-7 to keep them colorful and distinct from the first wood-colored dice
        rand_color = random.choice(pastel_colors[1:])
        st.session_state.dice_colors.append(rand_color)
elif len(st.session_state.dice_colors) > st.session_state.num_dice:
    st.session_state.dice_colors = st.session_state.dice_colors[:st.session_state.num_dice]

# Fixed height equivalent to 6 dice (2 rows) to keep the white card size constant and avoid shifting
iframe_height = 420

# Inject Retro Pixel CSS (forces pixel font globally and sets pastel palette)
st.markdown(
    """
    <style>
    @font-face {
        font-family: 'DungGeunMo';
        src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_six@1.2/DungGeunMo.woff') format('woff');
        font-weight: normal;
        font-style: normal;
    }
    
    /* Force DungGeunMo pixel font on all text elements inside stApp */
    .stApp, .stApp * {
        font-family: 'DungGeunMo', monospace !important;
    }
    
    /* Background Canvas with ultra-light milk cream and thin grayish-navy pinstripes */
    .stApp {
        background-color: #FFFDF5;
        background-image: linear-gradient(90deg, rgba(16, 40, 140, 0.15) 1px, transparent 1px);
        background-size: 24px 100%;
        color: #4a3e3d;
    }
    
    /* Transparent layout container for page centering */
    .block-container {
        max-width: 740px !important;
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        margin: auto;
    }
    
    /* Soft, warm gamebox console card with bevel edges and flat shadows */
    div.st-key-game_card {
        background: #ffffff !important;
        border: 2px solid rgba(74, 62, 61, 0.18) !important;
        box-shadow: 0 15px 35px rgba(74, 62, 61, 0.08), inset -4px -4px 0px #f5ede0 !important;
        padding: 2.5rem 2.5rem 3.5rem 2.5rem !important;
        border-radius: 20px;
        width: 100% !important;
        box-sizing: border-box !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: flex-start !important;
        min-height: 70vh !important;
    }
    
    .header-container {
        text-align: center;
        margin-bottom: 1.2rem;
    }
    
    .title {
        font-size: 2.4rem !important;
        font-weight: bold !important;
        margin: 0 0 0.5rem 0 !important;
        color: #4a3e3d !important;
        text-align: center !important; /* Ensure centered title font */
    }
    
    .instruction {
        font-size: 1rem !important;
        color: #8e7a75 !important;
        margin: 0 !important;
    }
    
    /* Force all Streamlit element containers to center their content horizontally */
    div[data-testid="element-container"] {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }
    
    /* Center all vertical block elements generated by Streamlit to prevent left-side drift */
    [data-testid="stVerticalBlock"] > div {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
    }
    
    /* Center the button container itself */
    div.stButton {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
        margin-top: 15px !important;
    }
    
    /* Style the Streamlit Button into a centered cute retro mechanical button in lavender blue */
    div.stButton > button {
        background-color: #455FCC !important;
        color: #ffffff !important;
        border: 2px solid rgba(74, 62, 61, 0.22) !important;
        box-shadow: 0 4px 12px rgba(69, 95, 204, 0.25) !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
        padding: 10px 24px !important;
        border-radius: 12px !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        display: inline-block !important;
        width: 100% !important;
        max-width: 320px !important;
        margin: 0 auto !important;
    }
    div.stButton > button:hover:not(:disabled) {
        background-color: #5c72f2 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(69, 95, 204, 0.35) !important;
        border: 2px solid rgba(74, 62, 61, 0.3) !important;
        color: #ffffff !important;
    }
    div.stButton > button:active:not(:disabled) {
        transform: translateY(0px) !important;
        box-shadow: 0 2px 6px rgba(69, 95, 204, 0.2) !important;
    }
    div.stButton > button:disabled {
        background-color: #e5dec9 !important;
        color: #8e7a75 !important;
        border: 2px solid rgba(74, 62, 61, 0.1) !important;
        box-shadow: none !important;
        opacity: 0.65 !important;
        cursor: not-allowed !important;
    }
    /* Style the delete button specific style (small borderless red text button) */
    div[class*="st-key-del_"] {
        margin-top: 18px !important;
    }
    div[class*="st-key-del_"] button {
        background-color: transparent !important;
        color: #CC6A6A !important;
        border: none !important;
        box-shadow: none !important;
        font-size: 0.95rem !important;
        padding: 4px 8px !important;
        width: auto !important;
        min-width: auto !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 !important;
        font-weight: normal !important;
        transition: transform 0.2s ease, color 0.2s ease !important;
    }
    div[class*="st-key-del_"] button:hover:not(:disabled) {
        background-color: rgba(204, 106, 106, 0.1) !important;
        color: #e08585 !important;
        transform: scale(1.15) !important;
        box-shadow: none !important;
        border: none !important;
    }
    div[class*="st-key-del_"] button:active:not(:disabled) {
        transform: scale(0.95) !important;
        box-shadow: none !important;
    }

    /* Style pagination buttons specifically to be small compact squares */
    div[class*="st-key-prev_"] button, div[class*="st-key-next_"] button {
        background-color: #455FCC !important;
        color: #ffffff !important;
        font-size: 0.9rem !important;
        padding: 4px 8px !important;
        border-radius: 8px !important;
        width: 100% !important;
        max-width: 44px !important;
        min-width: auto !important;
        height: 36px !important;
        min-height: auto !important;
        box-shadow: 0 2px 6px rgba(69, 95, 204, 0.2) !important;
        border: 2px solid rgba(74, 62, 61, 0.15) !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 auto !important;
    }
    div[class*="st-key-prev_"] button:hover:not(:disabled), div[class*="st-key-next_"] button:hover:not(:disabled) {
        background-color: #5c72f2 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 10px rgba(69, 95, 204, 0.3) !important;
    }
    div[class*="st-key-prev_"] button:active:not(:disabled), div[class*="st-key-next_"] button:active:not(:disabled) {
        transform: translateY(0px) !important;
    }
    div[class*="st-key-prev_"] button:disabled, div[class*="st-key-next_"] button:disabled {
        background-color: #e5dec9 !important;
        color: #8e7a75 !important;
        border: 2px solid rgba(74, 62, 61, 0.05) !important;
        box-shadow: none !important;
        opacity: 0.55 !important;
        cursor: not-allowed !important;
        transform: none !important;
    }
    div[class*="st-key-prev_"], div[class*="st-key-next_"] {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }

    /* Completely hide Streamlit sidebar, header, and footer controls */
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    div[data-testid="collapsedControl"] {
        display: none !important;
    }
    header, footer {
        visibility: hidden;
        height: 0px !important;
    }
    div[data-testid="stDecoration"] {
        display: none;
    }
    
    /* Center the iframe container */
    div[data-testid="stHtml"] {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
    }
    iframe {
        display: block;
        margin: 0 auto;
        border: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Render the main app layout inside a custom game_card container for stable layout expansion
with st.container(key="game_card"):
    # Header
    st.markdown(
        """
        <div class="header-container">
            <h1 class="title">roll the dice! 🤍</h1>
            <p class="instruction">click the dice to roll</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Render the bidirectional 3D Dice Component (automatically sends roll results back to Python)
    roll_event = dice_component(
        num_dice=st.session_state.num_dice,
        dice_colors=st.session_state.dice_colors,
        key=f"retro_dice_comp_{st.session_state.num_dice}",
        height=iframe_height
    )
    
    # Listen to roll landing event from the iframe JS and capture results
    if roll_event and roll_event.get("roll_id") != st.session_state.current_roll_id:
        st.session_state.current_roll = roll_event.get("results")
        st.session_state.current_roll_id = roll_event.get("roll_id")
        st.rerun()
    
    # Layout columns for Save and History controls (now aligned perfectly outside the 3D window)
    col_save, col_hist = st.columns(2)
    
    with col_save:
        save_disabled = st.session_state.current_roll is None
        btn_save_label = "Save Roll 💾"
        if st.session_state.current_roll:
            btn_save_label = f"Save Roll [ {', '.join(map(str, st.session_state.current_roll))} ] 💾"
        
        if st.button(btn_save_label, disabled=save_disabled, key="save_roll_btn"):
            import datetime
            now = datetime.datetime.now()
            time_str = now.strftime("%H:%M:%S")
            
            # Verify it is not already in the history to avoid duplicate clicks
            if not any(item["id"] == st.session_state.current_roll_id for item in st.session_state.saved_history):
                entry = {
                    "id": st.session_state.current_roll_id or int(time.time()),
                    "values": st.session_state.current_roll,
                    "sum": sum(st.session_state.current_roll),
                    "time": time_str,
                    "colors": list(st.session_state.dice_colors)
                }
                st.session_state.saved_history.insert(0, entry)
                st.toast("Roll Saved Successfully! 🤍")
                st.rerun()
    
    with col_hist:
        hist_count = len(st.session_state.saved_history)
        btn_hist_label = f"View History ({hist_count}) 📋"
        if st.button(btn_hist_label, key="toggle_history_btn"):
            st.session_state.show_history = not st.session_state.show_history
            st.rerun()
    
    # Render the Saved History list panel natively
    if st.session_state.show_history:
        st.markdown("<hr style='border-top: 2px dashed rgba(74,62,61,0.15); margin: 15px 0 10px 0;'>", unsafe_allow_html=True)
        st.markdown("### 📋 Saved History")
        
        if not st.session_state.saved_history:
            st.markdown("<p style='text-align: center; color: #8e7a75;'>No saved rolls yet!</p>", unsafe_allow_html=True)
        else:
            col_clear, _ = st.columns([1, 2])
            with col_clear:
                if st.button("🗑️ Clear All", key="clear_all_btn"):
                    st.session_state.saved_history = []
                    st.rerun()
                    
            import math
            items_per_page = 5
            total_items = len(st.session_state.saved_history)
            total_pages = max(1, math.ceil(total_items / items_per_page))
            
            # Clamp current page to valid range
            if st.session_state.history_page > total_pages:
                st.session_state.history_page = total_pages
            if st.session_state.history_page < 1:
                st.session_state.history_page = 1
                
            current_page = st.session_state.history_page
            start_idx = (current_page - 1) * items_per_page
            end_idx = start_idx + items_per_page
            
            page_items = st.session_state.saved_history[start_idx:end_idx]
    
            # Render list entries with custom retro card layout (only for the current page)
            for item in page_items:
                # Fallback for older items that don't have saved colors
                colors = item.get("colors")
                if not colors:
                    colors = [pastel_colors[0]]
                    for i in range(1, len(item["values"])):
                        colors.append(pastel_colors[(i - 1) % (len(pastel_colors) - 1) + 1])
                
                # Build HTML for each dice value colored with its body color (inline to avoid markdown parser rendering raw text)
                val_spans = []
                for val, color_info in zip(item['values'], colors):
                    bg_color = color_info.get("bg", "#dfc2ab")
                    val_spans.append(
                        f'<span style="display:inline-block;background-color:{bg_color};color:#3d2a23;border:1px solid rgba(74,62,61,0.2);border-radius:5px;padding:1px 6px;margin:0 2px;font-weight:bold;font-size:0.95rem;box-shadow:inset -1px -1px 0px rgba(74,62,61,0.15),1px 1px 2px rgba(74,62,61,0.08);line-height:1.2;">{val}</span>'
                    )
                val_html = "".join(val_spans)
    
                item_html = (
                    f'<div style="display:flex;flex-direction:column;gap:4px;background-color:#fcf9f2;border:1px solid rgba(74,62,61,0.1);border-radius:8px;padding:10px 14px;margin-bottom:8px;font-family:\'DungGeunMo\',monospace;">'
                    f'<div style="display:flex;align-items:center;height:24px;">'
                    f'<span style="color:#8e7a75;font-weight:bold;font-size:1.1rem;margin-right:2px;">[</span>'
                    f'{val_html}'
                    f'<span style="color:#8e7a75;font-weight:bold;font-size:1.1rem;margin-left:2px;">]</span>'
                    f'</div>'
                    f'<div style="display:flex;align-items:center;gap:12px;margin-top:4px;">'
                    f'<span style="font-weight:bold;color:#4a3e3d;font-size:0.85rem;">Sum: {item["sum"]}</span>'
                    f'<span style="font-size:0.75rem;color:#8e7a75;">{item["time"]}</span>'
                    f'</div>'
                    f'</div>'
                )
                col_item, col_del = st.columns([8, 1])
                with col_item:
                    st.markdown(item_html, unsafe_allow_html=True)
                with col_del:
                    if st.button("❌", key=f"del_{item['id']}"):
                        st.session_state.saved_history = [x for x in st.session_state.saved_history if x["id"] != item["id"]]
                        st.rerun()
    
            # Render pagination controls if multiple pages exist
            if total_pages > 1:
                st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
                col_prev_first, col_prev, col_page_num, col_next, col_next_last = st.columns([1, 1, 3, 1, 1])
                with col_prev_first:
                    if st.button("⏪", key="prev_first_btn", disabled=(current_page == 1)):
                        st.session_state.history_page = 1
                        st.rerun()
                with col_prev:
                    if st.button("◀", key="prev_page_btn", disabled=(current_page == 1)):
                        st.session_state.history_page -= 1
                        st.rerun()
                with col_page_num:
                    st.markdown(
                        f"<p style='text-align: center; font-weight: bold; margin-top: 8px; color: #4a3e3d; font-size: 0.95rem; font-family: \"DungGeunMo\", monospace;'>"
                        f"Page {current_page} / {total_pages}"
                        f"</p>", 
                        unsafe_allow_html=True
                    )
                with col_next:
                    if st.button("▶", key="next_page_btn", disabled=(current_page == total_pages)):
                        st.session_state.history_page += 1
                        st.rerun()
                with col_next_last:
                    if st.button("⏩", key="next_last_btn", disabled=(current_page == total_pages)):
                        st.session_state.history_page = total_pages
                        st.rerun()
    
    st.markdown("<hr style='border-top: 1px solid rgba(74,62,61,0.08); margin: 20px 0;'>", unsafe_allow_html=True)
    
    # Retro styled Button to increase dice count
    btn_label = f"add more dice (current: {st.session_state.num_dice}) ➕"
    if st.button(btn_label):
        if st.session_state.num_dice < 6:
            st.session_state.num_dice += 1
        else:
            st.session_state.num_dice = 1
            st.session_state.dice_colors = [pastel_colors[0]] # Reset colors to just the first wood color
        st.session_state.current_roll = None # Clear active roll to disable save on reset
        st.session_state.current_roll_id = None
        st.rerun()

