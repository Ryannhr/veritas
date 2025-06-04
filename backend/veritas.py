import os
import asyncio
import uuid
from loguru import logger
from typing import Dict, List, Any
from dotenv import load_dotenv
from openai import OpenAI
from agents import Agent, Runner, FileSearchTool, trace
import streamlit as st

def main():
    st.set_page_config(page_title="VERITAS Chat", page_icon="🔍", layout="centered")

    custom_css = """
    <style>
    body {
        background-color: #1f2d27;
    }
    .stApp {
        background-color: #1f2d27;
        color: #d1d5db;
    }
    .stTextInput > div > div > input {
        background-color: #2e3b35;
        color: #ffffff;
    }
    .stChatMessage {
        background-color: #2a3832;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
        color: #e0e0e0;
    }
    .chat-user {
        background-color: #3b5246;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
        color: #e6f4ea;
    }
    .chat-assistant {
        background-color: #26332c;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
        color: #d1f0d5;
    }
    button[kind="primary"] {
        background-color: #2f503b;
        color: white;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

    st.title("🌿 VERITAS Chat")
    st.markdown("**Descubra seu propósito com inteligência espiritual guiada.**")

    if "handler" not in st.session_state:
        try:
            st.session_state.handler = OpenAIHandler()
        except Exception as e:
            st.error(f"Erro ao inicializar o chatbot: {str(e)}")
            st.stop()

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "user_id" not in st.session_state:
        st.session_state.user_id = f"streamlit_user_{uuid.uuid4().hex[:8]}"

    for message in st.session_state.messages:
        role_class = "chat-user" if message["role"] == "user" else "chat-assistant"
        role_icon = "👤" if message["role"] == "user" else "🤖"
        st.markdown(f"""
        <div class="{role_class}">
            <strong>{role_icon}</strong> {message["content"]}
        </div>
        """, unsafe_allow_html=True)

    if prompt := st.chat_input("Digite algo como: 'Sinto que estou travado na vida espiritual'"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        role_class = "chat-user"
        st.markdown(f"""
        <div class="{role_class}">
            <strong>👤</strong> {prompt}
        </div>
        """, unsafe_allow_html=True)

        with st.spinner("Consultando os especialistas VERITAS..."):
            try:
                response = st.session_state.handler.process_message(st.session_state.user_id, prompt)
                st.session_state.messages.append({"role": "assistant", "content": response})
                role_class = "chat-assistant"
                st.markdown(f"""
                <div class="{role_class}">
                    <strong>🤖</strong> {response}
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                error_msg = f"Erro: {str(e)}"
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                st.markdown(f"""
                <div class="chat-assistant">
                    <strong>🤖</strong> {error_msg}
                </div>
                """, unsafe_allow_html=True)

    if st.button("🧹 Limpar Conversa"):
        st.session_state.messages = []
        st.experimental_rerun()
