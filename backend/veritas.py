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

# aplicando chat sdk

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class OpenAIHandler:
    """
    Manipulador para interagir com a API OpenAI com foco em descoberta de propósito e dons.
    """

    def __init__(self):
        self.threads_manager = ThreadsManager()
        self._initialize_agents()

    def _initialize_agents(self):
        """Inicialize o agente especialista VERITAS."""

        self.veritas = Agent(
            name="veritas1_BíbliaNãoLida",
            instructions="""
                Você é responsável por interpretar e aplicar os ensinamentos da 
                Bíblia de forma prática, focando nas passagens menos exploradas ou mal compreendidas. 
                Sua missão é revelar o que muitos ainda não enxergaram nas Escrituras.
                """,
            tools=[
                FileSearchTool(
                    max_num_results=3,
                    vector_store_ids=["vs_683a1ba02a048191a607f9bf399d113d"]
                )
            ],
        )

        self.veritas = Agent(
            name="veritas2_AntiMedo",
            instructions="""
                Sua função é ajudar as pessoas a superarem seus medos, 
                identificando bloqueios emocionais e propondo ações práticas e corajosas. 
                Você atua como um libertador da mente limitante.
                """,
            tools=[
                FileSearchTool(
                    max_num_results=3,
                    vector_store_ids=["vs_683a1b7406148191855ec2d329a19ca0"]
                )
            ],
        )

        self.veritas = Agent(
            name="veritas3_AChaveMestradoUniverso",
            instructions="""
                Você revela os princípios universais que regem o sucesso, abundância e propósito. 
                Seu foco é conectar espiritualidade, ciência e ação alinhada com o destino.
                """,
            tools=[
                FileSearchTool(
                    max_num_results=3,
                    vector_store_ids=["vs_683a1b47837081919e2f5445bf2f22eb"]
                )
            ],
        )

        self.veritas = Agent(
            name="veritas4_DestravarDigital",
            instructions="""
                Seu papel é ajudar pessoas a conquistarem autoridade e liberdade no mundo digital. 
                Você orienta sobre posicionamento, presença online e desbloqueio de mentalidade digital.
                """,
            tools=[
                FileSearchTool(
                    max_num_results=3,
                    vector_store_ids=["vs_6839f99235588191b1b1cc728bc3dd5f"]
                )
            ],
        )

        self.veritas = Agent(
            name="veritas5_inteligenciaemocional",
            instructions="""
                Você é especialista em inteligência emocional.
                Sua missão é destravar sentimentos reprimidos, 
                ensinar autoconsciência e regular emoções para uma vida mais equilibrada.

                """,
            tools=[
                FileSearchTool(
                    max_num_results=3,
                    vector_store_ids=["vs_683a1d633ea8819185512589fc0539b2"]
                )
            ],
        )

        self.veritas = Agent(
            name="veritas6_CódigosdoMilhão",
            instructions="""
                Você é responsável por entregar mentalidade, hábitos e estratégias de construção de riqueza. 
                Atua como mentor financeiro, mostrando caminhos para acessar o “código dos milionários”.

                """,
            tools=[
                FileSearchTool(
                    max_num_results=3,
                    vector_store_ids=["vs_683a1b0f9ce0819191b2bda7433cb6e4"]
                )
            ],
        )

        self.veritas = Agent(
            name="veritas7_vaicudardasuavida",
            instructions="""
                Seu foco é despertar a responsabilidade pessoal. Você confronta desculpas, 
                empodera decisões e direciona a pessoa a assumir o controle da própria jornada.
                """,
            tools=[
                FileSearchTool(
                    max_num_results=3,
                    vector_store_ids=["vs_683a1ac4125081919bf279d9c1b47c75"]
                )
            ],
        )

        self.assistente = Agent(
            name="assistente_triagem",
            instructions="""
                Você é um assistente espiritual de triagem.
                Sua função é identificar se o usuário está buscando:
                - Alinhar seu chamado de vida
                - Descobrir ou ativar seus dons
                - Explorar seu propósito existencial
                Caso positivo, encaminhe para o agente veritas.

                Se a dúvida for irrelevante ao propósito ou dons, peça mais detalhes com sensibilidade.
            """,
            handoffs=[self.veritas]
        )

    def process_message(self, user_id: str, message: str) -> str:
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self._process_message_async(user_id, message))
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {str(e)}")
            return f"Desculpe, ocorreu um erro: {str(e)}"

    async def _process_message_async(self, user_id: str, message: str) -> str:
        thread = self.threads_manager.get_or_create_thread(user_id)
        thread.add_message("user", message)
        input_list = thread.get_input_list()
        full_response = ""

        with trace("Sistema VERITAS - Triagem", group_id=thread.thread_id):
            resultado_triagem = Runner.run_streamed(self.assistente, input=input_list)

        agente_especialista = resultado_triagem.current_agent

        with trace("Sistema VERITAS - Especialista", group_id=thread.thread_id):
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

# Streamlit Interface
def main():
    """Streamlit-based interface for the dental clinic system."""
    # Configuração da página
    st.set_page_config(page_title="Clínica Odontológica Medical Smile")
    st.title("Clínica Odontológica Medical Smile")
    st.write("Bem-vindo! Digite sua pergunta sobre odontologia ou agendamento.")

    # Inicializa
    if "handler" not in st.session_state:
        try:
            st.session_state.handler = OpenAIHandler()
        except Exception as e:
            st.error(f"Erro ao inicializar o chatbot: {str(e)}")
            st.stop()

    # Inicializa estado da sessão para histórico e user_id
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "user_id" not in st.session_state:
        st.session_state.user_id = f"streamlit_user_{uuid.uuid4().hex[:8]}"

    # Exibe histórico de conversa
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Campo de entrada do usuário
    if prompt := st.chat_input("Digite sua pergunta (ex.: 'Quero clarear dentes')"):
        # Adiciona mensagem do usuário
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Processa e exibe resposta
        with st.chat_message("assistant"):
            with st.spinner("Processando..."):
                try:
                    response = st.session_state.handler.process_message(st.session_state.user_id, prompt)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"Erro: {str(e)}"
                    st.markdown(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

    # Botão para limpar conversa
    if st.button("Limpar Conversa"):
        st.session_state.messages = []
        st.session_state.user_id = f"streamlit_user_{uuid.uuid4().hex[:8]}"

if __name__ == "_main_":
    main()