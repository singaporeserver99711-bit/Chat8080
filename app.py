import streamlit as st
import datetime
from PIL import Image
import io

# 1. Page Configuration
st.set_page_config(page_title="Pro Python Chat", page_icon="💬", layout="wide")

ADMIN_PASSWORD = "1234$#@!1234$#@!"   # Secret password to clear the entire chat
MAX_MESSAGES = 50               # Automatically deletes oldest messages to save RAM
HEARTBEAT_TIMEOUT = 60          # Seconds before an inactive user is considered offline

# 2. Setup Global/Shared Store using Streamlit's Cache
@st.cache_resource
def get_global_data():
    return {
        "messages": [],         # List of chat messages
        "active_users": {}      # Dictionary of {username: last_active_datetime}
    }

global_data = get_global_data()

# Helper function to automatically remove "ghost" inactive users
def cleanup_inactive_users():
    now = datetime.datetime.now(datetime.timezone.utc)
    inactive_users = []
    for user, last_seen in global_data["active_users"].items():
        if (now - last_seen).total_seconds() > HEARTBEAT_TIMEOUT:
            inactive_users.append(user)
    
    for user in inactive_users:
        global_data["active_users"].pop(user, None)

# Initialize session state variables
if "username" not in st.session_state:
    st.session_state.username = ""
if "user_emoji" not in st.session_state:
    st.session_state.user_emoji = "👤"

# Always clean up dead sessions first
cleanup_inactive_users()

# Check for the secret admin back-door in the URL query parameters
# Access via: your-app.streamlit.app/?admin=true
is_admin_mode = st.query_params.get("admin") == "true"

# --- SCREEN 1: NICKNAME & PROFILE EMOJI SETUP ---
if not st.session_state.username:
    st.title("💬 Welcome to the Chatroom!")
    st.write("Set up your profile to join the conversation instantly.")
    
    # Let them pick a cool avatar emoji
    emoji_choice = st.selectbox("Choose your profile avatar:", 
        ["👤", "🙍‍♂️", "🙎‍♀️", "🧑‍🦰", "🤖", "👱", "🥷", "🧙", "💫", "😎", "🚀", "⚡"]
    )
    username_input = st.text_input("Enter your nickname to join:")
    
    if st.button("Join Chat"):
        username_clean = username_input.strip()
        if username_clean:
            if username_clean in global_data["active_users"]:
                st.error("This nickname is already in use! Try another one, or wait 1 minute if you recently closed your tab.")
            else:
                st.session_state.username = username_clean
                st.session_state.user_emoji = emoji_choice
                global_data["active_users"][username_clean] = datetime.datetime.now(datetime.timezone.utc)
                st.rerun()

# --- SCREEN 2: THE CHATROOM ---
else:
    # Update active user's heartbeat
    global_data["active_users"][st.session_state.username] = datetime.datetime.now(datetime.timezone.utc)

    # Sidebar showing active users and actions
    with st.sidebar:
        st.title("👥 Chat Lounge")
        st.write(f"Logged in as: **{st.session_state.user_emoji} {st.session_state.username}**")
        
        st.subheader("🟢 Online Now:")
        for user in global_data["active_users"].keys():
            st.write(f"• {user}")
        
        st.write("---")
        if st.button("🚪 Leave Chat"):
            global_data["active_users"].pop(st.session_state.username, None)
            st.session_state.username = ""
            st.rerun()
            
        # SECRET ADMIN INTERFACE - ONLY appears if "?admin=true" is in the browser URL!
        if is_admin_mode:
            st.write("---")
            st.subheader("🛠️ Secret Admin Panel")
            admin_key = st.text_input("Admin Password:", type="password")
            if st.button("🚨 Clear All Chat"):
                if admin_key == ADMIN_PASSWORD:
                    global_data["messages"] = []
                    st.success("Chat wiped clean!")
                    st.rerun()
                else:
                    st.error("Invalid Admin Pass!")

    # Main Chat Interface
    st.title("💬 Real-Time Chat")
    
    # Display Existing Messages
    chat_container = st.container(height=380)
    with chat_container:
        if not global_data["messages"]:
            st.write("_No messages yet. Say hello!_")
        for msg in global_data["messages"]:
            time_str = msg["time"].strftime("%I:%M %p")
            header = f"**[{time_str}] {msg['emoji']} {msg['user']}:**"
            
            if msg["text"]:
                st.markdown(f"{header} {msg['text']}")
            
            if msg["image"]:
                st.write(header)
                st.image(msg["image"], width=250)

    # Re-arranged Layout: Upload on the far left, input in middle, send button on right
    with st.form("message_form", clear_on_submit=True):
        col_upload, col_input, col_send = st.columns([1.2, 4, 1])
        
        with col_upload:
            uploaded_file = st.file_uploader("📷 Pic", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
        with col_input:
            user_input = st.text_input("Type your message here...", label_visibility="collapsed")
        with col_send:
            submit_btn = st.form_submit_button("Send 🚀", use_container_width=True)

    if submit_btn:
        compressed_img_bytes = None
        
        if uploaded_file is not None:
            img = Image.open(uploaded_file)
            img.thumbnail((400, 400))
            buffer = io.BytesIO()
            img.convert("RGB").save(buffer, format="JPEG", quality=60)
            compressed_img_bytes = buffer.getvalue()

        if user_input or compressed_img_bytes:
            ist_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5, minutes=30)
            
            global_data["messages"].append({
                "user": st.session_state.username,
                "emoji": st.session_state.user_emoji,
                "text": user_input,
                "image": compressed_img_bytes,
                "time": ist_time
            })
            
            if len(global_data["messages"]) > MAX_MESSAGES:
                global_data["messages"].pop(0)
                
            st.rerun()

    if st.button("🔄 Refresh Messages"):
        st.rerun()
