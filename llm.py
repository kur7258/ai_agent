from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import FewShotChatMessagePromptTemplate

from config import answer_examples
from dotenv import load_dotenv

load_dotenv()

store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


def get_retriever():
    embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    index_name = "tax-markdown-index"
    database = PineconeVectorStore.from_existing_index(index_name=index_name, embedding=embedding)
    retriever = database.as_retriever(search_kwargs={"k": 4})

    return retriever


def get_llm(model='gemini-2.0-flash'):
    llm = GoogleGenerativeAI(model=model)

    return llm


def get_dictionary_chain():
    dictionary = ['사람을 나타내는 표현 -> 거주자']

    prompt = ChatPromptTemplate.from_template(f'''
        사용자의 질문을 보고, 우리의 사전을 참고해서 사용자의 질문을 변경해주세요.
        만약 변경할 필요가 없다고 판단되면, 사용자의 질문을 변경하지 않아도 됩니다.
        그런 경우에는 질문만 리턴해주세요.
        사전: {dictionary}

        질문: {{question}}
    ''')

    dictionary_chain = prompt | get_llm() | StrOutputParser()

    return dictionary_chain

def get_rag_chain():
    retriever = get_retriever()
    llm = get_llm()  
    
    example_prompt = ChatPromptTemplate.from_messages(
        [
            ('human', '{input}'),
            ('ai', '{answer}')
        ]
    )
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt = example_prompt,
        examples = answer_examples
    )
    
    contextualize_q_system_prompt = (
        'Give a caht history and the latest user question '
        'which might reference context in the caht history, '
        'formulate a standalone question which can be understood '
        'wihtout the chat history. Do NOT answer the question, '
        'just reformulate it if needed and otherwise return it as is.'
    )

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ('system', contextualize_q_system_prompt),
            MessagesPlaceholder(variable_name='chat_history'),
            ('human', '{input}')
        ]
    )
    history_aware_retriever = create_history_aware_retriever(
        llm,
        retriever,
        contextualize_q_prompt
    )

    system_prompt = (
        "당신은 소득세법 전문가입니다. 사용자의 소득세법에 관한 질문에 답변해주세요"
        "아래에 제공된 문서를 활용해서 답변해주시고"
        "답변을 알 수 없다면 모른다고 답변해주세요"
        "답변을 제공할 때는 소득세법 (XX조)에 따르면 이라고 시작하면서 답변해주시고"
        "2-3 문장 정도의 짧은 내용의 답변을 원합니다"
        "\n\n"
        "{context}"
    )

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ('system', system_prompt),
            few_shot_prompt,
            MessagesPlaceholder(variable_name='chat_history'),
            ('human', '{input}')
        ]
    )
    question_answer_chain = create_stuff_documents_chain(
        llm,
        qa_prompt
    )

    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key='input',
        history_messages_key='chat_history',
        output_messages_key='answer'
    ).pick('answer')

    return conversational_rag_chain


def get_ai_response(user_message):
    rag_chain = get_rag_chain()
    dictionary_chain = get_dictionary_chain()

    tax_chain = {'input': dictionary_chain} | rag_chain
    ai_response = tax_chain.stream(
        {
            "question": user_message
        },
        config={
            "configurable": {"session_id": "123"}
        }
    )

    return ai_response