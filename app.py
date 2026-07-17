import streamlit as st
import datetime

# 1. Page Configuration
st.set_page_config(page_title="Global Python Chat", page_icon="💬")
st.title("💬 Real-Time Global Chat")
st.write("Open this link on any device to join the conversation!")

# 2. Define a Global/Shared Store using Streamlit's Cache
# This persists data on the server across ALL users and devices
@st.cache_resource
def get_global_messages():
    return []  # Returns a shared, mutable list of messages

global_messages = get_global_messages()

# 3. Handle Username Setup
if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.username:
    # Ask for a nickname before entering chat
    username_input = st.text_input("Enter your nickname to join:", key="user_init")
    if st.button("Join Chat"):
        if username_input.strip():
            st.session_state.username = username_input.strip()
            st.rerun()
else:
    st.sidebar.write(f"Logged in as: **{st.session_state.username}**")
    if st.sidebar.button("Leave Chat"):
        st.session_state.username = ""
        st.rerun()

    # 4. Display Existing Messages
    chat_container = st.container(height=400)
    with chat_container:
        if not global_messages:
            st.write("_No messages yet. Say hello!_")
        for msg in global_messages:
            # Format: [HH:MM] Name: Message
            time_str = msg["time"].strftime("%H:%M")
            st.markdown(f"**[{time_str}] {msg['user']}:** {msg['text']}")

    # 5. Send Message Input
    user_input = st.chat_input("Type your message here...")
    if user_input:
        # Append message to the global shared list
        global_messages.append({
            "user": st.session_state.username,
            "text": user_input,
            "time": datetime.datetime.now()
        })
        # Instantly refresh the page to show the new message
        st.rerun()

    # 6. Simple Refresh Button (Since Streamlit updates on interaction)
    if st.button("🔄 Refresh Messages"):
        st.rerun()
