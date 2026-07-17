import streamlit as st
import datetime
from PIL import Image
import io

# 1. Page Configuration
st.set_page_config(page_title="Pro Python Chat", page_icon="💬", layout="wide")

ADMIN_PASSWORD = "1234$#@!1234$#@!"   # Secret password to clear the entire chat
MAX_MESSAGES = 50               # Automatically deletes oldest messages to save RAM

# 2. Setup Global/Shared Store using Streamlit's Cache
@st.cache_resource
def get_global_data():
    return {
        "messages": [],         # List of chat messages
        "active_users": set()   # Set of unique active users online
    }

global_data = get_global_data()

# Initialize session state variables
if "username" not in st.session_state:
    st.session_state.username = ""
if "user_emoji" not in st.session_state:
    st.session_state.user_emoji = "👤"

# --- SCREEN 1: NICKNAME & PROFILE EMOJI SETUP (Now the very first screen!) ---
if not st.session_state.username:
    st.title("💬 Welcome to the Chatroom!")
    st.write("Set up your profile to join the conversation instantly.")
    
    # Let them pick a cool avatar emoji
    emoji_choice = st.selectbox("Choose your profile avatar:", 
        ["👤", "🦊", "🦁", "🐉", "🤖", "👽", "🥷", "🧙", "🍕", "🎈", "🚀", "⚡"]
    )
    username_input = st.text_input("Enter your nickname to join:")
    
    if st.button("Join Chat"):
        username_clean = username_input.strip()
        if username_clean:
            # Check if username is already taken
            if username_clean in global_data["active_users"]:
                st.error("This nickname is already in use! Try another one.")
            else:
                st.session_state.username = username_clean
                st.session_state.user_emoji = emoji_choice
                global_data["active_users"].add(username_clean) # Add to online list
                st.rerun()

# --- SCREEN 2: THE CHATROOM ---
else:
    # Sidebar showing active users and actions
    with st.sidebar:
        st.title("👥 Chat Lounge")
        st.write(f"Logged in as: **{st.session_state.user_emoji} {st.session_state.username}**")
        
        # Display Active Users List
        st.subheader("🟢 Online Now:")
        for user in global_data["active_users"]:
            st.write(f"• {user}")
        
        st.write("---")
        if st.button("🚪 Leave Chat"):
            # Remove user from online list when they leave
            if st.session_state.username in global_data["active_users"]:
                global_data["active_users"].remove(st.session_state.username)
            st.session_state.username = ""
            st.rerun()
            
        # Admin Clear Button
        st.subheader("🛠️ Admin Controls")
        admin_key = st.text_input("Admin Password:", type="password")
        if st.button("🚨 Clear All Chat"):
            if admin_key == ADMIN_PASSWORD:
                global_data["messages"] = []
                st.success("Chat wiped clean!")
                st.rerun()
            else:
                st.error("Invalid Admin Pass!")

    # Main Chat Interface
    st.title("💬 Global Real-Time Chat")
    
    # Display Existing Messages
    chat_container = st.container(height=350)
    with chat_container:
        if not global_data["messages"]:
            st.write("_No messages yet. Say hello!_")
        for msg in global_data["messages"]:
            time_str = msg["time"].strftime("%I:%M %p")
            header = f"**[{time_str}] {msg['emoji']} {msg['user']}:**"
            
            # If the message has text, show it
            if msg["text"]:
                st.markdown(f"{header} {msg['text']}")
            
            # If the message contains an image, show it
            if msg["image"]:
                st.write(header)
                st.image(msg["image"], width=250)

    # Inputs at the bottom: Text and Image Uploader
    with st.form("message_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            user_input = st.text_input("Type your message here...", label_visibility="collapsed")
        with col2:
            uploaded_file = st.file_uploader("Upload Pic", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
        
        submit_btn = st.form_submit_button("Send")

    if submit_btn:
        compressed_img_bytes = None
        
        # --- IMAGE COMPRESSION LOGIC ---
        if uploaded_file is not None:
            # 1. Open the uploaded file using PIL
            img = Image.open(uploaded_file)
            
            # 2. Resize it so it doesn't take too much RAM (max 400px wide)
            img.thumbnail((400, 400))
            
            # 3. Save it as a highly compressed JPEG in memory
            buffer = io.BytesIO()
            img.convert("RGB").save(buffer, format="JPEG", quality=60) # 60% quality uses tiny memory!
            compressed_img_bytes = buffer.getvalue()

        # Only send if there is text or an image
        if user_input or compressed_img_bytes:
            # Calculate India Standard Time (IST = UTC + 5:30)
            ist_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5, minutes=30)
            
            global_data["messages"].append({
                "user": st.session_state.username,
                "emoji": st.session_state.user_emoji,
                "text": user_input,
                "image": compressed_img_bytes, # Safely stores the tiny 50KB image
                "time": ist_time
            })
            
            # --- MEMORY PROTECTION: Keep only last 50 messages ---
            if len(global_data["messages"]) > MAX_MESSAGES:
                global_data["messages"].pop(0) # Remove the oldest message
                
            st.rerun()

    # Manual refresh button
    if st.button("🔄 Refresh"):
        st.rerun()
