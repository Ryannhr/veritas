import os
import asyncio
import uuid
from loguru import logger
from typing import Dict, List, Any
from dotenv import load_dotenv
from openai import OpenAI
from agents import Agent, Runner, FileSearchTool, trace
import streamlit as st

# Carrega variáveis de ambiente
load_dotenv(override=True)

# Verifica a chave de API
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.error("OPENAI_API_KEY não encontrada no ambiente!")
    st.error("Erro: OPENAI_API_KEY não encontrada. Configure a chave no arquivo .env ou na plataforma de deploy.")
    st.stop()
else:
    logger.info(f"API Key carregada com sucesso: {api_key[:10]}...")

# Inicializa o cliente OpenAI (para validação, mas pode não ser usado pela biblioteca agents)
try:
    client = OpenAI(api_key=api_key)
except Exception as e:
    logger.error(f"Erro ao inicializar o cliente OpenAI: {str(e)}")
    st.error(f"Erro ao inicializar o cliente OpenAI: {str(e)}")
    st.stop()

# Configura a chave de API para a biblioteca agents (se necessário)
# Substitua pelo método correto da biblioteca agents, se disponível
try:
    import agents
    agents.api_key = api_key  # Tente configurar a chave globalmente (ajuste conforme a biblioteca)
except AttributeError:
    logger.warning("Biblioteca agents não suporta configuração direta de api_key. Certifique-se de que OPENAI_API_KEY está configurada no ambiente.")

class Thread:
    def __init__(self, user_id: str):
        self.thread_id = str(uuid.uuid4().hex[:16])
        self.user_id = user_id
        self.messages: List[Dict[str, Any]] = []
        self.current_agent = None

    def add_message(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})

    def get_input_list(self) -> List[dict]:
        return [{"role": msg["role"], "content": msg["content"]} for msg in self.messages]

class OpenAIHandler:
    def __init__(self):
        self.threads_manager = {}
        self._initialize_agents()

    def _initialize_agents(self):
        # Testamos com tools=[] para isolar o erro 401
        self.agents = {
            "veritas1_BíbliaNãoLida": Agent(
                name="veritas1_BíbliaNãoLida",
                instructions="""
                    Você é responsável por interpretar e aplicar os ensinamentos da 
                    Bíblia de forma prática, focando nas passagens menos exploradas ou mal compreendidas. 
                    Sua missão é revelar o que muitos ainda não enxergaram nas Escrituras.
                    """,
                tools=[]  # Removido temporariamente para teste
            ),
            "veritas2_AntiMedo": Agent(
                name="veritas2_AntiMedo",
                instructions="""
                    Sua função é ajudar as pessoas a superarem seus medos, 
                    identificando bloqueios emocionais e propondo ações práticas e corajosas. 
                    Você atua como um libertador da mente limitante.
                    """,
                tools=[]
            ),
            "veritas3_AChaveMestradoUniverso": Agent(
                name="veritas3_AChaveMestradoUniverso",
                instructions="""
                    Você revela os princípios universais que regem o sucesso, abundância e propósito. 
                    Seu foco é conectar espiritualidade, ciência e ação alinhada com o destino.
                    """,
                tools=[]
            ),
            "veritas4_inteligenciaemocional": Agent(
                name="veritas4_inteligenciaemocional",
                instructions="""
                    Você guia os buscadores espirituais no despertar de sua consciência, 
                    ajudando-os a alinhar suas vidas com seu propósito divino e a desenvolver dons espirituais.
                    """,
                tools=[]
            ),
            "veritas5_AlinhamentoChamadoVida": Agent(
                name="veritas5_AlinhamentoChamadoVida",
                instructions="""
                    Sua missão é ajudar as pessoas a descobrirem e alinharem seu chamado de vida, 
                    conectando suas paixões e talentos com o propósito maior.
                    """,
                tools=[]
            ),
            "veritas6_destravar": Agent(
                name="veritas6_destravar",
                instructions="""
                    Você auxilia na descoberta e ativação dos dons espirituais inatos, 
                    ajudando as pessoas a reconhecerem e utilizarem suas habilidades únicas.
                    """,
                tools=[]
            ),
            "veritas7_vaicuidardasuavida": Agent(
                name="veritas7_vaicuidardasuavida",
                instructions="""
                    Sua função é explorar o propósito existencial de cada indivíduo, 
                    ajudando-os a encontrar significado e direção em suas vidas.
                    """,
                tools=[]
            ),
        }
        self.assistente = Agent(
            name="assistente_triagem",
            instructions="""
                Você é um assistente espiritual de triagem.
                Sua função é identificar se o usuário está buscando:
                - Alinhar seu chamado de vida
                - Descobrir ou ativar seus dons
                - Explorar seu propósito existencial
                Caso positivo, encaminhe para o agente veritas.
                """,
            handoffs=list(self.agents.values())
        )

    def process_message(self, user_id: str, message: str) -> str:
        try:
            logger.info(f"Iniciando processamento da mensagem para user_id: {user_id}")
            return asyncio.run(self._process_message_async(user_id, message))
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {str(e)}")
            return f"Desculpe, ocorreu um erro: {str(e)}"

    async def _process_message_async(self, user_id: str, message: str) -> str:
        logger.info(f"Processando mensagem: {message}")
        if user_id not in self.threads_manager:
            self.threads_manager[user_id] = Thread(user_id)
        thread = self.threads_manager[user_id]
        thread.add_message("user", message)
        input_list = thread.get_input_list()
        full_response = ""

        with trace("Sistema VERITAS - Triagem", group_id=thread.thread_id):
            logger.info("Iniciando triagem...")
            resultado_triagem = Runner.run_streamed(self.assistente, input=input_list)
            logger.info(f"Triagem concluída, agente selecionado: {resultado_triagem.current_agent.name}")

        agente_especialista = resultado_triagem.current_agent

        with trace("Sistema VERITAS - Especialista", group_id=thread.thread_id):
            logger.info(f"Processando com agente especialista: {agente_especialista.name}")
            resultado_especialista = Runner.run_streamed(agente_especialista, input=input_list)
            async for evento in resultado_especialista.stream_events():
                from openai.types.responses import ResponseContentPartDoneEvent, ResponseTextDeltaEvent
                from agents import RawResponsesStreamEvent
                if not isinstance(evento, RawResponsesStreamEvent):
                    continue
                dados = evento.data
                if isinstance(dados, ResponseTextDeltaEvent):
                    full_response += dados.delta
                elif isinstance(dados, ResponseContentPartDoneEvent):
                    pass

        thread.add_message("assistant", full_response)
        thread.current_agent = self.assistente
        return full_response

def main():
    # Configuração da página deve ser a primeira chamada
    st.set_page_config(page_title="VERITAS Chat", page_icon="🔍", layout="centered")

    # CSS ajustado para texto branco
    custom_css = """
    <style>
    body {
        background-color: #1f2d27;
    }
    .stApp {
        background-color: #1f2d27;
        color: #ffffff;
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
        color: #ffffff;
    }
    .chat-user {
        background-color: #3b5246;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
        color: #ffffff;
    }
    .chat-assistant {
        background-color: #26332c;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
        color: #ffffff;
    }
    button[kind="primary"] {
        background-color: #2f503b;
        color: #ffffff;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff;
    }
    .stMarkdown, .stMarkdown p {
        color: #ffffff;
    }
    .stError {
        color: #ffffff !important;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

    # Adiar o st.write até depois de st.set_page_config
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
        st.rerun()

if __name__ == "__main__":
    main()