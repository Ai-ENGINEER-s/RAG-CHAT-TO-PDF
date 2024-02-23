import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_community.llms import HuggingFaceHub
from htmlTemplates import css, bot_template, user_template
import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_community.llms import HuggingFaceHub
from htmlTemplates import css, bot_template, user_template

# Fonction pour obtenir le texte à partir de PDFs
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

# Fonction pour découper le texte en chunks
def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

# Fonction pour créer le vecteur de stockage
def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

# Fonction pour créer la chaîne de conversation
def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain

# Fonction pour gérer l'interaction utilisateur
def handle_userinput(user_question):
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)

# Fonction pour sauvegarder une conversation
def save_conversation(conversation_id, conversation):
    st.session_state.conversations[conversation_id] = conversation

# Fonction pour charger une conversation sauvegardée
def load_conversation(conversation_id):
    return st.session_state.conversations.get(conversation_id, None)

# Fonction pour afficher les conversations précédentes dans la barre latérale
def display_saved_conversations():
    st.sidebar.subheader("Saved Conversations")
    if st.session_state.conversations:
        for conv_id, _ in st.session_state.conversations.items():
            if st.sidebar.button(f"Conversation {conv_id}", key=f"conv_button_{conv_id}"):
                st.session_state.conversation = load_conversation(conv_id)

# Contenu de la page
st.set_page_config(page_title="Chat with multiple PDFs", page_icon=":books:")
st.write(css, unsafe_allow_html=True)

# Vérification de la session
if "conversation" not in st.session_state:
    st.session_state.conversation = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = None
if "conversations" not in st.session_state:
    st.session_state.conversations = {}

# Nouvelle session
if st.button("Start a New Session"):
    st.session_state.conversation = None
    st.session_state.chat_history = None
    st.write("A new session has started. You can upload documents and ask questions.")

# Section des documents à charger
with st.sidebar:
    st.subheader("Your documents")
    pdf_docs = st.file_uploader(
        "Upload your PDFs here and click on 'Process'", accept_multiple_files=True)
    if st.button("Process"):
        if pdf_docs is None or len(pdf_docs) == 0:
            st.write("Please upload documents before processing.")
            st.stop()

        with st.spinner("Processing"):
            # Obtenir le texte des PDF
            raw_text = get_pdf_text(pdf_docs)

            # Découper le texte en chunks
            text_chunks = get_text_chunks(raw_text)

            # Créer le vecteur de stockage
            vectorstore = get_vectorstore(text_chunks)

            # Créer la chaîne de conversation
            st.session_state.conversation = get_conversation_chain(vectorstore)

            # Sauvegarder la nouvelle conversation
            save_conversation(len(st.session_state.conversations) + 1, st.session_state.conversation)

# Section pour poser une question
st.header("Chat with multiple PDF")
user_question = st.text_input("Ask a question about your documents:")

# Bouton "Send" avec icône d'envoi
if st.button("Send 📤", key="send_button"):
    if user_question:
        if st.session_state.conversation:
            handle_userinput(user_question)
        else:
            st.write("Please upload documents before making a request.")
            st.stop()

# Afficher les conversations sauvegardées dans la barre latérale
display_saved_conversations()
