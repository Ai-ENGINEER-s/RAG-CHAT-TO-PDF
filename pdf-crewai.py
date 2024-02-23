
from crewai import Agent, Task, Crew
import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI

st.set_page_config(page_title="Chat with multiple PDFs", page_icon=":books:", layout="centered")

dotenv_path = r"C:\devpy\syncflow\pdf\pdf-back\.env.example"
load_dotenv(dotenv_path)
st.markdown("""
<style>
body {
    font-family: Arial, sans-serif;
}

.css-1rs6os.edgvbvh3{
   visibility:hidden         
}
.css-10pw50.egzxvld1{
           visibility:hidden
}
.container {
    display: flex;
    flex-direction: column;
    height: 100vh;
    padding: 20px;
    overflow-y: auto;
}

.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding-bottom: 70px; /* Espace pour le champ de saisie utilisateur */
}

.chat-message {
    margin-bottom: 10px;
    display: flex;
    align-items: flex-start;
}

.user .avatar img,
.bot .avatar img {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    margin-right: 10px;
}

.message {
    padding: 10px 15px;
    border-radius: 10px;
    max-width: 70%;
    word-wrap: break-word;
    color: black;
}

.user .message {
    background-color: #DCF8C6;
}

.bot .message {
    background-color: #E5E5EA;
}

.input-container {
    padding-top: 20px;
    padding-bottom: 20px;
    position: fixed;
    bottom: 0;
    width: 100%;
    background-color: white;
    z-index: 1;
    border-top: 1px solid #ccc;
}

.user-question {
    position: fixed;
    bottom: 0;
    width: 100%;
    padding: 10px;
    background-color: white;
    border-top: 1px solid #ccc;
    z-index: 2;
    overflow-y: hidden;
            
}

</style>
""", unsafe_allow_html=True)



# Définir les templates HTML
bot_template = '''
<div class="chat-message bot">
    <div class="avatar">
        <img src="https://digitar.be/wp-content/uploads/2017/11/logo-white-transp.png" style="max-height: 78px; max-width: 78px; border-radius: 50%; object-fit: cover;">
    </div>
    <div class="message">{{MSG}}</div>
</div>
'''

user_template = '''
<div class="chat-message user">
    <div class="avatar">
        <img src="https://cdn.pixabay.com/photo/2017/07/18/23/23/user-2517433_960_720.png">
    </div>    
    <div class="message">{{MSG}}</div>
</div>
'''
import os
import openai
from crewai import Agent, Task, Crew

# Configuration de la clé d'API OpenAI

# Définition de la fonction pour poser une question au modèle RAG
def poser_question(question):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt="Question: " + question + "\nAnswer:",
        temperature=0.7,
        max_tokens=300
    )
    return response.choices[0].text.strip()

# Création d'un agent CrewAI
researcher = Agent(
    role='Asker of resume document ',
    goal='just ask question resume this document',
    backstory="""you are resumer""",
    verbose=True,
    allow_delegation=False,
)

# Création d'une tâche pour l'agent
task1 = Task(
    description="""resume ce document """,
    agent=researcher
)

# Création d'un équipage avec un seul agent et une seule tâche
crew = Crew(
    agents=[researcher],
    tasks=[task1],
    verbose=2,
)


# Fonction pour récupérer le texte des documents PDF
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

# Fonction pour diviser le texte en morceaux
def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

# Fonction pour créer le vecteur store
def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore
def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    # llm = HuggingFaceHub(repo_id="google/flan-t5-xxl", model_kwargs={"temperature":0.5, "max_length":512})

    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain


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


def main():
    load_dotenv()

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    st.header("Chat with multiple PDFs :books:")
    user_question = crew.kickoff()
    if user_question:
        if st.session_state.conversation is not None:  # Vérifiez si conversation est initialisée
            handle_userinput(user_question)

    with st.sidebar:
        st.subheader("Your documents")
        pdf_docs = st.file_uploader(
            "Upload your PDFs here and click on 'Process'", accept_multiple_files=True)
        if st.button("Process"):
            with st.spinner("Processing"):
                # get pdf text
                raw_text = get_pdf_text(pdf_docs)

                # get the text chunks
                text_chunks = get_text_chunks(raw_text)

                # create vector store
                vectorstore = get_vectorstore(text_chunks)

                # create conversation chain
                st.session_state.conversation = get_conversation_chain(
                    vectorstore)

if __name__ == '__main__':
    main()




# # Fonction pour gérer l'entrée de l'utilisateur et les réponses de l'agent CrewAI
# def handle_userinput(user_question):
#     response = st.session_state.conversation({'question': user_question})
#     st.session_state.chat_history = response['chat_history']

#     for i, message in enumerate(st.session_state.chat_history):
#         if i % 2 == 0:
#             st.write(user_template.replace(
#                 "{{MSG}}", message.content), unsafe_allow_html=True)
#         else:
#             st.write(bot_template.replace(
#                 "{{MSG}}", message.content), unsafe_allow_html=True)

# def main():
#     st.header("Chat with multiple PDFs :books:")
#     user_question = crew.kickoff()
#     print("Résultat de l'équipage :", user_question)

    
#     if user_question:
#         handle_userinput( user_question)

#     with st.sidebar:
#         st.subheader("Your documents")
#         pdf_docs = st.file_uploader(
#             "Upload your PDFs here and click on 'Process'", accept_multiple_files=True)
#         if st.button("Process"):
#             with st.spinner("Processing"):
#                 # get pdf text
#                 raw_text = get_pdf_text(pdf_docs)
#                 # get the text chunks
#                 text_chunks = get_text_chunks(raw_text)
#                 # create vector store
#                 vectorstore = get_vectorstore(text_chunks)
#                 # create conversation chain
#                 st.session_state.conversation = get_conversation_chain(
#                     vectorstore)

# if __name__ == '__main__':
#     main()





# # Fonction principale pour exécuter l'équipage
