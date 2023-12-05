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

# Sidebar section with introductory information
with st.sidebar:
    st.info('🙋‍ :rainbow[**Hi,  Welcome to the Data Analytics Interview Prep! Click Question to start.**] ')
    st.info('This comprehensive resource is tailored to help you excel in your data analytics interviews. '
            'We\'ve curated a collection of 115 questions that primarily focus on data '
            'structures and algorithms – two essential pillars of data analytics. 🚀')

    st.divider()

    # Display creator information and links
    st.write("""
    Nov 2023 | [Efrem Assefa](https://www.linkedin.com/in/efrem-assefa-bbb286237)
            """)


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


# Load the dataset
df = load_dataset()


# Define a function to load the spaCy NLP model
@st.cache_resource()
def load_spacy():
    try:
        nlp = spacy.load('en_core_web_md')
        return nlp
    except Exception as e:
        st.error(f"An error occurred while loading the spaCy model: {str(e)}")
        return None


# Load the spaCy NLP model
model = load_spacy()


# Initialize the session state index if it doesn't exist
if 'index' not in st.session_state:
    st.session_state.index = 0


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
def display_question(index):
    try:
        question = df['questions'].iloc[index]
        st.subheader(question)
        text_to_speech_browser(question)
    except Exception as e:
        st.error(f"An error occurred while displaying the question: {str(e)}")


# Define a function to show the correct answer and feedback
def show_correct_answer(index):
    try:
        correct_answer = df['answers'].iloc[index]
        st.info(f'{correct_answer}')
        text_to_speech_browser(f' {correct_answer}')
            # f'{feedback} {answer}. To proceed to question # {index + 2}, click on the Question button.')

    except Exception as e:
        st.error(f"An error occurred while showing the correct answer: {str(e)}")


# Define the layout with three buttons for Question, Feedback, and Previous
col1, col2,  col3 = st.columns(3)
st.write('')
with col1:
    question_button = st.button('Question', type="primary", use_container_width=True)

with col2:
    feedback_button = st.button('Show answer', type="primary", use_container_width=True)

with col3:
    previous_button = st.button('Previous', type="primary", use_container_width=True)

# Handle button actions
if question_button:
    display_question(st.session_state.index)


if feedback_button:
    show_correct_answer(st.session_state.index)
    st.session_state.index += 1

if previous_button:
    if st.session_state.index > 0:
        st.session_state.index -= 1
        display_question(st.session_state.index)

