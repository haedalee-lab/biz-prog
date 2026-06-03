import streamlit as st
import streamlit.components.v1 as components
import json
import os
import re
import uuid
import time
import random
import math
import datetime

# Page Configuration
st.set_page_config(
    page_title="🎲 seajin and boardgames",
    page_icon="🎲",
    layout="wide",
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
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "1. 룰 검색 및 확인"

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

if "editing_rule_id" not in st.session_state:
    st.session_state.editing_rule_id = None

# New boardgame form states
if "new_name" not in st.session_state:
    st.session_state.new_name = ""
if "new_url" not in st.session_state:
    st.session_state.new_url = ""
if "new_tags" not in st.session_state:
    st.session_state.new_tags = ""
if "new_desc" not in st.session_state:
    st.session_state.new_desc = ""
if "form_error" not in st.session_state:
    st.session_state.form_error = ""
if "form_success" not in st.session_state:
    st.session_state.form_success = ""
if "voted_games" not in st.session_state:
    st.session_state.voted_games = set()
if "rule_page" not in st.session_state:
    st.session_state.rule_page = 1
if "last_search" not in st.session_state:
    st.session_state.last_search = ""
if "sort_by" not in st.session_state:
    st.session_state.sort_by = "등록순"

# Ensure the colors list has exactly num_dice elements
if len(st.session_state.dice_colors) < st.session_state.num_dice:
    while len(st.session_state.dice_colors) < st.session_state.num_dice:
        rand_color = random.choice(pastel_colors[1:])
        st.session_state.dice_colors.append(rand_color)
elif len(st.session_state.dice_colors) > st.session_state.num_dice:
    st.session_state.dice_colors = st.session_state.dice_colors[:st.session_state.num_dice]

# Find the 3D Dice Component directory
parent_dir = os.path.dirname(os.path.abspath(__file__)) # /Users/haedal/Desktop/BIZ_vibe/boardgame

# Load and base64-encode the patchwork image for header background
import base64
patchwork_bg_css = ""
patchwork_path = os.path.join(parent_dir, "patchwork.jpg")
if os.path.exists(patchwork_path):
    try:
        with open(patchwork_path, "rb") as f:
            patchwork_b64 = base64.b64encode(f.read()).decode("utf-8")
        patchwork_bg_css = f"background-image: url(data:image/jpeg;base64,{patchwork_b64});"
    except Exception as e:
        pass

project_root = os.path.dirname(parent_dir) # /Users/haedal/Desktop/BIZ_vibe
component_dir = os.path.join(project_root, "roll the dice", "dice_component")

# Declare the bidirectional custom component
dice_component = components.declare_component("retro_3d_dice", path=component_dir)

# Database Helpers
DB_FILE = os.path.join(parent_dir, "boardgames.json")

def load_games():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Migrate data to include 'likes' if missing
                updated = False
                for game in data:
                    if "likes" not in game:
                        game["likes"] = 0
                        updated = True
                if updated:
                    save_games(data)
                return data
        except Exception:
            return []
    return []

def save_games(games):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(games, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"데이터 저장 중 오류가 발생했습니다: {e}")

def extract_youtube_id(url: str) -> str:
    patterns = [
        r'(?:v=|\/v\/|embed\/|youtu\.be\/|\/shorts\/)([a-zA-Z0-9_-]{11})',
        r'(?:youtube\.com\/watch\?.*v=)([a-zA-Z0-9_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    stripped = url.strip()
    if len(stripped) == 11 and re.match(r'^[a-zA-Z0-9_-]{11}$', stripped):
        return stripped
    return ""

def handle_submit():
    name = st.session_state.get("new_name", "").strip()
    url = st.session_state.get("new_url", "").strip()
    tags_str = st.session_state.get("new_tags", "").strip()
    desc = st.session_state.get("new_desc", "").strip()
    
    if not name:
        st.session_state.form_error = "보드게임 이름을 입력해 주세요!"
        st.session_state.form_success = ""
        return
    elif not url:
        st.session_state.form_error = "유튜브 동영상 링크를 입력해 주세요!"
        st.session_state.form_success = ""
        return
        
    video_id = extract_youtube_id(url)
    if not video_id:
        st.session_state.form_error = "올바른 유튜브 링크를 입력해 주세요. (예: https://www.youtube.com/watch?v=...)"
        st.session_state.form_success = ""
        return
        
    games = load_games()
    if any(g["video_id"] == video_id for g in games):
        st.session_state.form_error = "이미 등록된 동일한 유튜브 영상입니다!"
        st.session_state.form_success = ""
        return
        
    tags = [t.strip() for t in tags_str.split(",") if t.strip()]
    new_game = {
        "id": str(uuid.uuid4()),
        "name": name,
        "youtube_url": url,
        "video_id": video_id,
        "tags": tags,
        "description": desc,
        "likes": 0
    }
    games.append(new_game)
    save_games(games)
    
    # Reset inputs in session state
    st.session_state.new_name = ""
    st.session_state.new_url = ""
    st.session_state.new_tags = ""
    st.session_state.new_desc = ""
    st.session_state.form_error = ""
    st.session_state.form_success = f"'{name}' 게임이 성공적으로 등록되었습니다!"
    st.session_state.current_tab = "1. 룰 검색 및 확인"

# Map active tab key for CSS styling
active_tab = st.session_state.current_tab
active_key = ""
if active_tab == "1. 룰 검색 및 확인":
    active_key = "tab_1"
elif active_tab == "2. roll the dice":
    active_key = "tab_2"
elif active_tab == "3. 새 보드게임 등록":
    active_key = "tab_3"

# Inject Global Retro CSS (matching the pinstripe background, DungGeunMo font, and retro cards)
st.markdown(
    f"""
    <style>
    @font-face {{
        font-family: 'DungGeunMo';
        src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_six@1.2/DungGeunMo.woff') format('woff');
        font-weight: normal;
        font-style: normal;
    }}
    
    /* Force DungGeunMo pixel font on all text elements inside stApp */
    .stApp, .stApp * {{
        font-family: 'DungGeunMo', monospace !important;
    }}
    
    /* Background Canvas with ultra-light milk cream and thin grayish-navy pinstripes */
    .stApp {{
        background-color: #FFFDF5;
        background-image: linear-gradient(90deg, rgba(93, 119, 227, 0.15) 1px, transparent 1px);
        background-size: 24px 100%;
        color: #4a3e3d;
    }}
    
    /* Transparent layout container for page centering */
    .block-container {{
        max-width: 95% !important;
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        margin: auto;
    }}
    
    /* Soft, warm gamebox console card with bevel edges and flat shadows */
    div.st-key-game_card {{
        background: #ffffff !important;
        border: 2px solid rgba(74, 62, 61, 0.18) !important;
        box-shadow: 0 15px 35px rgba(74, 62, 61, 0.08), inset -4px -4px 0px #f5ede0 !important;
        padding: 2.2rem 2.2rem 3rem 2.2rem !important;
        border-radius: 20px;
        width: 100% !important;
        box-sizing: border-box !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: stretch !important;
        justify-content: flex-start !important;
        min-height: 75vh !important;
    }}
    
    /* Header layout */
    .header-container {{
        text-align: center;
        margin-bottom: 1.2rem;
    }}
    
    .patchwork-container {{
        {patchwork_bg_css}
        background-size: cover;
        background-position: center;
        border: 4px solid #4a3e3d;
        box-shadow: 0 8px 0px #4a3e3d;
        border-radius: 20px;
        padding: 18px 30px;
        display: inline-block;
        margin-bottom: 1.2rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        cursor: pointer;
        text-align: center;
        position: relative;
        overflow: hidden;
    }}
    .patchwork-container::before {{
        content: '';
        position: absolute;
        top: 6px; left: 6px; right: 6px; bottom: 6px;
        border: 2px dashed rgba(255, 255, 255, 0.7);
        border-radius: 14px;
        pointer-events: none;
    }}
    .patchwork-container:hover {{
        transform: translateY(-4px);
        box-shadow: 0 12px 0px #4a3e3d;
    }}
    .patchwork-container:active {{
        transform: translateY(2px);
        box-shadow: 0 4px 0px #4a3e3d;
    }}
    .patchwork-title {{
        font-size: 2.2rem !important;
        font-weight: bold !important;
        color: #ffffff !important;
        text-shadow: 2px 2px 0px #4a3e3d, -2px -2px 0px #4a3e3d, 2px -2px 0px #4a3e3d, -2px 2px 0px #4a3e3d, 4px 4px 0px rgba(0,0,0,0.3) !important;
        margin: 0 !important;
        font-family: 'DungGeunMo', monospace !important;
    }}
    
    .instruction {{
        font-size: 0.95rem !important;
        color: #8e7a75 !important;
        margin: 0 !important;
        text-align: center;
    }}
    
    /* Force Streamlit element containers alignment */
    div[data-testid="element-container"] {{
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }}
    
    /* Center all vertical block elements */
    [data-testid="stVerticalBlock"] > div {{
        display: flex !important;
        flex-direction: column !important;
        width: 100% !important;
    }}
    
    /* Retro Buttons Style */
    div.stButton > button {{
        background-color: #5D77E3 !important;
        color: #ffffff !important;
        border: 2px solid rgba(74, 62, 61, 0.22) !important;
        box-shadow: 0 4px 12px rgba(93, 119, 227, 0.2) !important;
        font-size: 1rem !important;
        font-weight: bold !important;
        padding: 9px 18px !important;
        border-radius: 12px !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        display: inline-block !important;
        width: 100% !important;
    }}
    div.stButton > button:hover:not(:disabled) {{
        background-color: #7B92EC !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(93, 119, 227, 0.35) !important;
        border: 2px solid rgba(74, 62, 61, 0.3) !important;
        color: #ffffff !important;
    }}
    div.stButton > button:active:not(:disabled) {{
        transform: translateY(0px) !important;
        box-shadow: 0 2px 6px rgba(93, 119, 227, 0.2) !important;
    }}
    div.stButton > button:disabled {{
        background-color: #e5dec9 !important;
        color: #8e7a75 !important;
        border: 2px solid rgba(74, 62, 61, 0.1) !important;
        box-shadow: none !important;
        opacity: 0.65 !important;
        cursor: not-allowed !important;
    }}
    
    /* Active navigation button styling */
    div.st-key-{active_key} > button {{
        background-color: #fef5c8 !important; /* Pastel Yellow highlight */
        color: #4a3e3d !important;
        border: 2px solid rgba(74, 62, 61, 0.4) !important;
        box-shadow: inset 0px 3px 5px rgba(74, 62, 61, 0.2) !important;
        transform: translateY(1px) !important;
    }}
    
    /* Rule Card container (Tab 1) */
    div[class*="st-key-rule_card_"] {{
        background: #ffffff !important;
        border: 2px solid rgba(74, 62, 61, 0.15) !important;
        box-shadow: 0 8px 20px rgba(74, 62, 61, 0.04), inset -3px -3px 0px #fdfbf7 !important;
        padding: 16px !important;
        border-radius: 16px !important;
        margin-bottom: 20px !important;
        display: flex !important;
        flex-direction: column !important;
    }}
    div[class*="st-key-rule_card_"]:hover {{
        border-color: rgba(74, 62, 61, 0.3) !important;
        box-shadow: 0 12px 25px rgba(74, 62, 61, 0.08), inset -3px -3px 0px #fdfbf7 !important;
        transform: translateY(-2px);
    }}
    
    .rule-title {{
        color: #4a3e3d;
        font-size: 1.25rem;
        font-weight: bold;
        margin-bottom: 4px;
    }}
    .rule-desc {{
        color: #8e7a75;
        font-size: 0.9rem;
        line-height: 1.45;
        margin-bottom: 10px;
        min-height: 40px;
    }}
    
    /* Pill Tags */
    .retro-badge {{
        display: inline-block;
        color: #4a3e3d;
        border: 1px solid rgba(74, 62, 61, 0.15);
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: bold;
        margin-right: 4px;
        margin-bottom: 6px;
    }}
    
    /* Native Video styling overrides */
    div[data-testid="stVideo"] {{
        border: 2px solid rgba(74, 62, 61, 0.15) !important;
        border-radius: 10px !important;
        overflow: hidden !important;
        margin-bottom: 10px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03) !important;
    }}
    
    /* Text Inputs in retro theme */
    div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea {{
        background-color: #ffffff !important;
        color: #4a3e3d !important;
        border: 2px solid rgba(74, 62, 61, 0.18) !important;
        border-radius: 10px !important;
        padding: 8px 12px !important;
        font-size: 0.95rem !important;
        box-shadow: inset 1px 1px 3px rgba(0,0,0,0.03) !important;
    }}
    div[data-testid="stTextInput"] input:focus, div[data-testid="stTextArea"] textarea:focus {{
        border-color: #5D77E3 !important;
        box-shadow: 0 0 6px rgba(93, 119, 227, 0.2) !important;
        outline: none !important;
    }}
    
    /* Selectbox input in retro theme (compact) */
    div[data-testid="stSelectbox"] {{
        max-width: 125px !important;
        margin-left: auto !important;
    }}
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
        background-color: #ffffff !important;
        color: #4a3e3d !important;
        border: 2px solid rgba(74, 62, 61, 0.18) !important;
        border-radius: 8px !important;
        font-size: 0.88rem !important;
        font-family: 'DungGeunMo', monospace !important;
        box-shadow: inset 1px 1px 3px rgba(0,0,0,0.03) !important;
        min-height: 38px !important;
        height: 38px !important;
        padding-top: 0px !important;
        padding-bottom: 0px !important;
    }}
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within {{
        border-color: #5D77E3 !important;
        box-shadow: 0 0 6px rgba(93, 119, 227, 0.2) !important;
    }}
    div[data-testid="stSelectbox"] div[data-baseweb="select"] [data-testid="stSelectboxVal"] {{
        color: #4a3e3d !important;
        font-family: 'DungGeunMo', monospace !important;
        font-size: 0.88rem !important;
        line-height: 34px !important;
    }}
    div[data-testid="stSelectbox"] div[data-baseweb="select"] div[data-baseweb="icon"] {{
        height: 100% !important;
        display: flex !important;
        align-items: center !important;
    }}
    
    /* Selectbox dropdown menu styling */
    div[data-baseweb="popover"] ul {{
        background-color: #ffffff !important;
        border: 2px solid rgba(74, 62, 61, 0.2) !important;
        border-radius: 10px !important;
        box-shadow: 0 10px 25px rgba(74, 62, 61, 0.08) !important;
        font-family: 'DungGeunMo', monospace !important;
    }}
    div[data-baseweb="popover"] li {{
        color: #4a3e3d !important;
        font-family: 'DungGeunMo', monospace !important;
        padding: 8px 12px !important;
        transition: all 0.15s ease !important;
    }}
    div[data-baseweb="popover"] li:hover, div[data-baseweb="popover"] li[aria-selected="true"] {{
        background-color: rgba(93, 119, 227, 0.08) !important;
        color: #5D77E3 !important;
    }}
    
    /* Big centered search input box */
    div.search-bar-container div[data-testid="stTextInput"] input {{
        font-size: 1.05rem !important;
        padding: 10px 16px !important;
        text-align: center !important;
        border-radius: 20px !important;
    }}
    
    /* Labels */
    label {{
        color: #4a3e3d !important;
        font-weight: bold !important;
        font-size: 0.9rem !important;
        margin-bottom: 4px !important;
    }}
    
    /* Delete buttons specifically styling */
    div[class*="st-key-delete_edit_"] button, div[class*="st-key-del_dice_"] button {{
        background-color: rgba(204, 106, 106, 0.1) !important;
        color: #CC6A6A !important;
        border: 2px solid rgba(204, 106, 106, 0.2) !important;
        box-shadow: 0 4px 12px rgba(204, 106, 106, 0.15) !important;
        font-size: 1rem !important;
        font-weight: bold !important;
        padding: 9px 18px !important;
        border-radius: 12px !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }}
    div[class*="st-key-delete_edit_"] button:hover:not(:disabled), div[class*="st-key-del_dice_"] button:hover:not(:disabled) {{
        background-color: #CC6A6A !important;
        color: #FFFFFF !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(204, 106, 106, 0.3) !important;
    }}
    
    /* Style pagination buttons specifically to be small compact squares */
    div[class*="st-key-prev_"] button, div[class*="st-key-next_"] button,
    div[class*="st-key-prev_page_btn"] button, div[class*="st-key-next_page_btn"] button,
    div[class*="st-key-prev_first_btn"] button, div[class*="st-key-next_last_btn"] button,
    div[class*="st-key-rule_prev_"] button, div[class*="st-key-rule_next_"] button {{
        background-color: #5D77E3 !important;
        color: #ffffff !important;
        font-size: 0.9rem !important;
        padding: 4px 8px !important;
        border-radius: 8px !important;
        width: 100% !important;
        max-width: 44px !important;
        min-width: auto !important;
        height: 36px !important;
        min-height: auto !important;
        box-shadow: 0 2px 6px rgba(93, 119, 227, 0.2) !important;
        border: 2px solid rgba(74, 62, 61, 0.15) !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 auto !important;
    }}
    div[class*="st-key-prev_"] button:hover:not(:disabled), div[class*="st-key-next_"] button:hover:not(:disabled),
    div[class*="st-key-rule_prev_"] button:hover:not(:disabled), div[class*="st-key-rule_next_"] button:hover:not(:disabled) {{
        background-color: #7B92EC !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 10px rgba(93, 119, 227, 0.3) !important;
    }}
    
    /* Completely hide Streamlit sidebar, header, and footer controls */
    section[data-testid="stSidebar"] {{
        display: none !important;
    }}
    div[data-testid="collapsedControl"] {{
        display: none !important;
    }}
    header, footer {{
        visibility: hidden;
        height: 0px !important;
    }}
    div[data-testid="stDecoration"] {{
        display: none;
    }}
    
    /* Center the iframe container for dice */
    div[data-testid="stHtml"] {{
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
    }}
    iframe {{
        display: block;
        margin: 0 auto;
        border: none;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Render main webapp inside the retro console card container
with st.container(key="game_card"):
    # 1. Main Game App Header as a Clickable Text Link
    st.markdown(
        """
        <div class="header-container">
            <a href="/" target="_self" style="text-decoration: none;">
                <div class="patchwork-container">
                    <h1 class="patchwork-title">🎮 seajin and boardgames ♟️</h1>
                </div>
            </a>
            <p class="instruction">
                해진씨와 함께하는 보드게임 방에 오신 것을 환영합니다.<br>
                추천 게임 룰 검색 부터, 게임에 필요한 주사위 굴리기까지 함께 즐겨요🤍
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # 2. Horizontal Navigation Buttons
    col_nav1, col_nav2, col_nav3 = st.columns(3)
    with col_nav1:
        if st.button("1. 룰 검색 및 확인 🔍", key="tab_1", use_container_width=True):
            st.session_state.current_tab = "1. 룰 검색 및 확인"
            st.rerun()
    with col_nav2:
        if st.button("2. roll the dice 🎲", key="tab_2", use_container_width=True):
            st.session_state.current_tab = "2. roll the dice"
            st.rerun()
    with col_nav3:
        if st.button("3. 새 보드게임 등록 ➕", key="tab_3", use_container_width=True):
            st.session_state.current_tab = "3. 새 보드게임 등록"
            st.rerun()
            
    st.markdown("<hr style='border-top: 2px dashed rgba(74,62,61,0.15); margin: 15px 0 20px 0;'>", unsafe_allow_html=True)
    
    # 3. Render content based on active tab
    if st.session_state.current_tab == "1. 룰 검색 및 확인":
        # Search & Sort Row
        st.markdown("<div class='search-bar-container'>", unsafe_allow_html=True)
        col_search_field, col_sort_selectbox = st.columns([8.5, 1.5])
        with col_search_field:
            search_query = st.text_input(
                "Search Input",
                placeholder="🔍 검색할 보드게임 이름을 입력해 주세요...",
                key="rule_search_input",
                label_visibility="collapsed"
            )
        with col_sort_selectbox:
            current_sort = st.session_state.get("sort_by", "등록순")
            default_index = 0 if current_sort == "등록순" else 1
            
            selected_option = st.selectbox(
                "정렬 기준",
                options=["등록순 📅", "추천순 👍"],
                index=default_index,
                key="sort_by_select",
                label_visibility="collapsed"
            )
            
            new_sort = "등록순" if "등록순" in selected_option else "추천순"
            if new_sort != st.session_state.sort_by:
                st.session_state.sort_by = new_sort
                st.session_state.rule_page = 1
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Load and Filter Games
        games = load_games()
        if search_query != st.session_state.last_search:
            st.session_state.rule_page = 1
            st.session_state.last_search = search_query
            
        if search_query:
            filtered_games = [g for g in games if search_query.lower() in g["name"].lower()]
        else:
            filtered_games = games

        # Sort Games by selected mode
        if st.session_state.get("sort_by", "등록순") == "추천순":
            filtered_games = sorted(filtered_games, key=lambda g: g.get("likes", 0), reverse=True)
            
        # Pagination calculations for rules
        items_per_page = 4
        total_rules = len(filtered_games)
        total_rule_pages = max(1, math.ceil(total_rules / items_per_page))
        
        if st.session_state.rule_page > total_rule_pages:
            st.session_state.rule_page = total_rule_pages
        if st.session_state.rule_page < 1:
            st.session_state.rule_page = 1
            
        current_page = st.session_state.rule_page
        start_idx = (current_page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        
        page_items = filtered_games[start_idx:end_idx]
        
        # Card Grid
        if not page_items:
            st.markdown(
                """
                <div style="text-align: center; padding: 2.5rem 0;">
                    <p style="font-size: 2.5rem; margin-bottom: 0.5rem;">🔍</p>
                    <p style="color: #8e7a75; font-size: 1rem;">일치하는 보드게임이 없습니다.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            # 2 columns responsive grid
            grid_cols = st.columns(2)
            for idx, game in enumerate(page_items):
                col_idx = idx % 2
                card_col = grid_cols[col_idx]
                
                with card_col:
                    # Check if this card is currently in edit mode
                    if st.session_state.get("editing_rule_id") == game["id"]:
                        with st.container(key=f"rule_card_{game['id']}"):
                            st.markdown(f"#### ✏️ {game['name']} 정보 수정")
                            edit_name = st.text_input("보드게임 이름", value=game["name"], key=f"edit_name_{game['id']}")
                            edit_url = st.text_input("유튜브 링크", value=game["youtube_url"], key=f"edit_url_{game['id']}")
                            edit_tags_str = st.text_input("태그 (쉼표로 구분)", value=", ".join(game.get("tags", [])), key=f"edit_tags_{game['id']}")
                            edit_desc = st.text_area("보드게임 설명", value=game.get("description", ""), key=f"edit_desc_{game['id']}")
                            
                            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                            
                            col_edit_save, col_edit_del, col_edit_cancel = st.columns(3)
                            with col_edit_save:
                                if st.button("수정 완료 💾", key=f"save_edit_{game['id']}", use_container_width=True):
                                    if not edit_name.strip():
                                        st.error("보드게임 이름을 입력해 주세요!")
                                    elif not edit_url.strip():
                                        st.error("유튜브 링크를 입력해 주세요!")
                                    else:
                                        video_id = extract_youtube_id(edit_url)
                                        if not video_id:
                                            st.error("올바른 유튜브 링크를 입력해 주세요.")
                                        else:
                                            all_games_list = load_games()
                                            for idx_g, g_item in enumerate(all_games_list):
                                                if g_item["id"] == game["id"]:
                                                    all_games_list[idx_g] = {
                                                        "id": game["id"],
                                                        "name": edit_name.strip(),
                                                        "youtube_url": edit_url.strip(),
                                                        "video_id": video_id,
                                                        "tags": [t.strip() for t in edit_tags_str.split(",") if t.strip()],
                                                        "description": edit_desc.strip(),
                                                        "likes": g_item.get("likes", 0)
                                                    }
                                                    break
                                            save_games(all_games_list)
                                            st.session_state.editing_rule_id = None
                                            st.toast(f"'{edit_name.strip()}' 수정 완료 🌟")
                                            st.rerun()
                            with col_edit_del:
                                if st.button("게임 삭제 🗑️", key=f"delete_edit_{game['id']}", use_container_width=True):
                                    all_games_list = load_games()
                                    updated_games = [g for g in all_games_list if g["id"] != game["id"]]
                                    save_games(updated_games)
                                    st.session_state.editing_rule_id = None
                                    st.toast(f"'{game['name']}' 삭제 완료")
                                    st.rerun()
                            with col_edit_cancel:
                                if st.button("취소 ❌", key=f"cancel_edit_{game['id']}", use_container_width=True):
                                    st.session_state.editing_rule_id = None
                                    st.rerun()
                    else:
                        with st.container(key=f"rule_card_{game['id']}"):
                            # Badges html
                            badge_spans = []
                            for t_idx, tag in enumerate(game.get("tags", [])):
                                color_info = pastel_colors[t_idx % len(pastel_colors)]
                                bg = color_info["bg"]
                                badge_spans.append(f'<span class="retro-badge" style="background-color: {bg} !important;">#{tag}</span>')
                            badges_html = "".join(badge_spans)
                            
                            st.markdown(f"""
                            <div class="rule-title">{game['name']}</div>
                            <div>{badges_html}</div>
                            <div class="rule-desc">{game.get('description', '')}</div>
                            """, unsafe_allow_html=True)
                            
                            st.video(f"https://www.youtube.com/watch?v={game['video_id']}")
                            
                            # Recommend and Edit action buttons next to each other
                            col_card_l, col_card_r1, col_card_r2 = st.columns([2, 1, 1])
                            with col_card_r1:
                                likes_count = game.get("likes", 0)
                                has_voted = game["id"] in st.session_state.voted_games
                                
                                btn_like_label = f"💖 추천 {likes_count}" if has_voted else f"👍 추천 {likes_count}"
                                
                                if st.button(btn_like_label, key=f"like_rule_{game['id']}", use_container_width=True, disabled=has_voted):
                                    all_games_list = load_games()
                                    for g_item in all_games_list:
                                        if g_item["id"] == game["id"]:
                                            g_item["likes"] = g_item.get("likes", 0) + 1
                                            break
                                    save_games(all_games_list)
                                    st.session_state.voted_games.add(game["id"])
                                    st.toast(f"'{game['name']}' 규칙을 추천했습니다! 💖")
                                    st.rerun()
                                    
                            with col_card_r2:
                                if st.button("✏️ 수정", key=f"edit_rule_{game['id']}", use_container_width=True):
                                    st.session_state.editing_rule_id = game["id"]
                                    st.rerun()
                                    
            # Pagination Controls at the bottom
            if total_rule_pages > 1:
                st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
                col_p_first, col_p_prev, col_p_num, col_p_next, col_p_last = st.columns([1, 1, 3, 1, 1])
                with col_p_first:
                    if st.button("⏪", key="rule_prev_first_btn", disabled=(current_page == 1)):
                        st.session_state.rule_page = 1
                        st.rerun()
                with col_p_prev:
                    if st.button("◀", key="rule_prev_page_btn", disabled=(current_page == 1)):
                        st.session_state.rule_page -= 1
                        st.rerun()
                with col_p_num:
                    st.markdown(
                        f"<p style='text-align: center; font-weight: bold; margin-top: 8px; color: #4a3e3d; font-size: 0.95rem; font-family: \"DungGeunMo\", monospace;'>"
                        f"Page {current_page} / {total_rule_pages}"
                        f"</p>", 
                        unsafe_allow_html=True
                    )
                with col_p_next:
                    if st.button("▶", key="rule_next_page_btn", disabled=(current_page == total_rule_pages)):
                        st.session_state.rule_page += 1
                        st.rerun()
                with col_p_last:
                    if st.button("⏩", key="rule_next_last_btn", disabled=(current_page == total_rule_pages)):
                        st.session_state.rule_page = total_rule_pages
                        st.rerun()
                                
    elif st.session_state.current_tab == "2. roll the dice":
        # Wrap dice component and controls in centered columns for nice alignment on wide screen
        col_dice_l, col_dice_c, col_dice_r = st.columns([1, 4, 1])
        with col_dice_c:
            # Sub-header
            st.markdown(
                """
                <div style="text-align: center; margin-bottom: 0.5rem;">
                    <p style="font-size: 1.1rem; color: #8e7a75; margin: 0; text-align: center;">click the dice to roll</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            iframe_height = 420
            
            # Render the bidirectional 3D Dice Component
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
                
            # Layout columns for Save and History controls
            col_save, col_hist = st.columns(2)
            
            with col_save:
                save_disabled = st.session_state.current_roll is None
                btn_save_label = "Save Roll 💾"
                if st.session_state.current_roll:
                    btn_save_label = f"Save Roll [ {', '.join(map(str, st.session_state.current_roll))} ] 💾"
                
                if st.button(btn_save_label, disabled=save_disabled, key="save_roll_btn"):
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
                    
            # Render the Saved History list panel
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
            
                    # Render list entries with custom retro card layout
                    for item in page_items:
                        colors = item.get("colors")
                        if not colors:
                            colors = [pastel_colors[0]]
                            for i in range(1, len(item["values"])):
                                colors.append(pastel_colors[(i - 1) % (len(pastel_colors) - 1) + 1])
                        
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
                            if st.button("❌", key=f"del_dice_{item['id']}"):
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
            
            # Button to increase dice count
            btn_label = f"add more dice (current: {st.session_state.num_dice}) ➕"
            if st.button(btn_label):
                if st.session_state.num_dice < 6:
                    st.session_state.num_dice += 1
                else:
                    st.session_state.num_dice = 1
                    st.session_state.dice_colors = [pastel_colors[0]]
                st.session_state.current_roll = None
                st.session_state.current_roll_id = None
                st.rerun()
            
    elif st.session_state.current_tab == "3. 새 보드게임 등록":
        # Centering the registration form
        col_form_l, col_form_c, col_form_r = st.columns([1, 2.2, 1])
        with col_form_c:
            # Form to add game rule videos (rethemed in retro style)
            st.markdown("### 📝 새 보드게임 규칙 동영상 등록")
            
            # Error and Success messages
            if st.session_state.form_error:
                st.error(st.session_state.form_error)
                # clear error after rendering
                st.session_state.form_error = ""
            if st.session_state.form_success:
                st.success(st.session_state.form_success)
                st.session_state.form_success = ""
                st.balloons()
            
            # Inputs
            st.text_input("보드게임 이름", placeholder="예: 세틀러 오브 카탄", key="new_name")
            st.text_input("유튜브 링크", placeholder="예: https://youtu.be/...", key="new_url")
            st.text_input("태그 (쉼표로 구분)", placeholder="예: 전략, 입문, 3-4인", key="new_tags")
            st.text_area("보드게임 설명", placeholder="게임 설명 및 룰에 대한 간략한 안내를 남겨보세요.", key="new_desc")
            
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            
            st.button("등록 완료 ✨", key="submit_rule_btn", on_click=handle_submit)
