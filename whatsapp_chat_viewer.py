import streamlit as st
import re
from datetime import datetime

st.set_page_config(page_title="WhatsApp Chat Viewer", layout="wide")
st.title("📱JC WhatsApp Chat Viewer")
st.markdown("---")
st.markdown("📌 Created by **JC**", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload your exported WhatsApp .txt file", type=["txt"])
if uploaded_file:
    chat_data = uploaded_file.read().decode("utf-8")

    # Clean special characters
    chat_data = chat_data.replace('\u202f', ' ').replace('\u200e', '')

    # Regex for both iPhone and Android formats
    iphone_pattern = re.compile(r"\[(\d{2}/\d{2}/\d{4}), (\d{1,2}:\d{2}:\d{2} [APMapm]{2})\] (.*?): (.*)", re.UNICODE)
    android_pattern = re.compile(r"(\d{2}/\d{2}/\d{4}), (\d{1,2}:\d{2} [apm]{2}) - (.*?): (.*)", re.IGNORECASE)

    iphone_matches = iphone_pattern.findall(chat_data)
    android_matches = android_pattern.findall(chat_data)

    parsed_messages = []

    # Process iPhone messages
    for date_str, time_str, sender, message in iphone_matches:
        try:
            dt = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %I:%M:%S %p")
            parsed_messages.append({"datetime": dt, "sender": sender.strip(), "message": message.strip()})
        except ValueError:
            continue

    # Process Android messages
    for date_str, time_str, sender, message in android_matches:
        try:
            dt = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %I:%M %p")
            parsed_messages.append({"datetime": dt, "sender": sender.strip(), "message": message.strip()})
        except ValueError:
            continue

    if not parsed_messages:
        st.error("No valid messages found. Please double-check the format of your .txt file.")
    else:
        # Get unique senders
        senders = sorted(set(m['sender'] for m in parsed_messages))

        # Select all checkbox
        select_all = st.checkbox("Select All Senders", value=True)

        # Multiselect with select all logic
        selected_senders = st.multiselect(
            "👤 Filter by sender(s):",
            options=senders,
            default=senders if select_all else []
        )

        # Filter messages
        filtered_messages = [m for m in parsed_messages if m['sender'] in selected_senders]

        # Display filtered messages
        for msg in filtered_messages:
            is_me = msg['sender'].lower() in ["you", "me", "🔄"]

            with st.chat_message("user" if is_me else "assistant"):
                st.markdown(f"**{msg['sender']}**")
                st.markdown(msg['message'])
                st.caption(msg['datetime'].strftime("%d %b %Y • %I:%M %p"))

        st.success(f"✅ Displaying {len(filtered_messages)} of {len(parsed_messages)} total messages.")

    st.markdown("---")
    st.markdown("📌 Created by **JC**", unsafe_allow_html=True)
else:
    st.info("Please upload your WhatsApp .txt file to begin.")
