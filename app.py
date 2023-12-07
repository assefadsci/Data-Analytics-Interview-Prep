# Import Libraries
import spacy
import streamlit as st
import streamlit.components.v1 as components
from streamlit_gsheets import GSheetsConnection

# Set the configuration for the Streamlit app
st.set_page_config(
    page_title='Data Analytics Interview Prep',
    page_icon="📊",
    layout='centered'
)

# Display the app title
st.title('📈 :rainbow[Data Analytics Interview Prep]')
st.subheader('')

# Initialize session state
if 'index' not in st.session_state:
    st.session_state.index = 0

if 'user_response' not in st.session_state:
    st.session_state.user_response = ""

if 'submit_clicked' not in st.session_state:
    st.session_state['submit_clicked'] = False

# Load custom CSS style for the app
@st.cache_data
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")

# Define a function to load the dataset from Google Sheets
@st.cache_data()
def load_dataset():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        dataset = conn.read(usecols=[1, 2, 4])
        return dataset
    except Exception as e:
        st.error(f"An error occurred while loading the dataset: {str(e)}")
        return None

# Define a function to load the spaCy NLP model
@st.cache_resource()
def load_spacy():
    try:
        nlp = spacy.load('en_core_web_md')
        return nlp
    except Exception as e:
        st.error(f"An error occurred while loading the spaCy model: {str(e)}")
        return None

# Load the dataset and spaCy NLP model
df = load_dataset()
model = load_spacy()

# Define a function for text-to-speech output in the browser
def text_to_speech_browser(text, rate=1):
    js = f"""
    <script>
    var msg = new SpeechSynthesisUtterance();
    msg.text = "{text}";
    msg.rate = {rate}; 
    window.speechSynthesis.speak(msg);
    </script>
    """
    components.html(js, height=0, width=0)

# Define a function to display a question
def display_question(index, category):
    st.session_state.user_response = ""
    try:
        # Filter the dataset based on the selected category
        if category != "All":
            filtered_df = df[df['category'].str.lower() == category.lower()]
        else:
            filtered_df = df

        if index < len(filtered_df):
            question = filtered_df['questions'].iloc[index]
            st.subheader(question)
            text_to_speech_browser(question)
        else:
            st.warning("No more questions in this category.")
    except Exception as e:
        st.error(f"An error occurred while displaying the question: {str(e)}")

# Define a function to evaluate user responses against correct answers
def evaluate_response(user_response, correct_answer):
    try:
        doc1 = model(user_response)
        doc2 = model(correct_answer)

        if doc1.has_vector and doc2.has_vector:
            similarity = doc1.similarity(doc2)
        else:
            similarity = 0.0

        if similarity > 0.95:
            feedback = 'Excellent!'
        elif 0.8 <= similarity <= 0.95:
            feedback = 'Good effort, but there is room for improvement.'
        elif 0 < similarity < 0.8:
            feedback = 'Let us work on this together. It appears there is room for improvement in your response. ' \
                       'Keep practicing, you are on the right track.'
        elif similarity == 0:
            feedback = 'Please provide your answer to the question to receive feedback.'
        else:
            feedback = 'Your response appears to be quite different from the expected answer. ' \
                       'Lets take a look at the correct answer to help you understand the key.'

        return feedback

    except Exception as e:
        st.error(f"An error occurred while evaluating the response: {str(e)}")
        return 'An error occurred during evaluation.'

# Define a function to show the correct answer and feedback
def show_feedback(index, category):
    try:
        # Filter the dataset based on the selected category
        if category != "All":
            filtered_df = df[df['category'].str.lower() == category.lower()]
        else:
            filtered_df = df

        if index < len(filtered_df):
            answer = filtered_df['answers'].iloc[index]
            user_response = st.session_state.get('user_response', '')
            # st.write(user_response)
            feedback = evaluate_response(user_response, answer)

            if feedback == 'Please provide your answer to the question to receive feedback.':
                st.info(f'{feedback} Click on "Previous", to revisit the question.')
                text_to_speech_browser(f'{feedback} Click on previous, to revisit the question.')
            else:
                st.info(f'{feedback} {answer}')
                text_to_speech_browser(f'{feedback} {answer}')
        else:
            st.warning("No more answers in this category.")
    except Exception as e:
        st.error(f"An error occurred while showing the correct answer: {str(e)}")

# Sidebar section with introductory information
st.sidebar.info('🙋‍ :rainbow[**Welcome to the Data Analytics Interview Prep!**] 🎉🎉')
category = st.sidebar.selectbox(":red[**SELECT A CATEGORY:**]", ["All", "Behavioral", "Conceptual", "Technical"])
st.sidebar.info(':rainbow[**Start your preparation by clicking the "Question" button below. Cheers!**] ✨🎈')

# Sidebar buttons
if st.sidebar.button('Question', type="primary"):
    st.session_state['display'] = 'question'
    st.session_state.submit_clicked = False
if st.sidebar.button('Answer', type="primary"):
    st.session_state['display'] = 'answer'
    st.session_state.submit_clicked = False
if st.sidebar.button('Feedback', type="primary"):
    st.session_state['display'] = 'feedback'
if st.sidebar.button('Previous', type="primary"):
    if st.session_state.index > 0:
        st.session_state.index -= 1
        st.session_state['display'] = 'question'
        st.session_state.submit_clicked = False
st.sidebar.divider()
st.sidebar.write("Nov 2023 | [Efrem Assefa](https://www.linkedin.com/in/efrem-assefa-bbb286237)")

# Load initial image and text
if 'display' not in st.session_state:
    st.image('img.png', caption='Welcome to Data Analytics Interview Prep!', width=700)

# Displaying results on the main page
if 'display' in st.session_state:
    if st.session_state['display'] == 'question':
        display_question(st.session_state.index, category)
    elif st.session_state['display'] == 'answer':
        with st.form('answer_form'):
            st.session_state.user_response = st.text_area(':rainbow[**Type your answer below:**]', height=100)
            submit_btn = st.form_submit_button('Submit Answer', type="primary")
            if submit_btn:
                st.session_state.submit_clicked = True
    elif st.session_state['display'] == 'feedback':
        show_feedback(st.session_state.index, category)
        st.session_state.index += 1

# Handle submit button action
if st.session_state.submit_clicked:
    st.success('✅ Answer submitted! 🎆🎉')
    st.session_state.submit_clicked = False
