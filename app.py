# Import Libraries
import spacy
import streamlit as st
from collections import Counter
import streamlit.components.v1 as components
from streamlit_gsheets import GSheetsConnection

# Set app configuration
st.set_page_config(
    page_title='Data Analytics Interview Prep',
    page_icon="📊",
    layout='centered'
)

# Display the app title
st.markdown("""
    <div style="text-align:center;">
        <h1 style="color: #C07F00; font-family: sans-serif; font-size: 3em; margin-bottom: 30px;">
            Data Analytics Interview Prep
        </h1>
    </div>
""", unsafe_allow_html=True)

# Initialize session state
if 'index' not in st.session_state:
    st.session_state.index = 0

if 'user_response' not in st.session_state:
    st.session_state.user_response = ""

if 'submit_clicked' not in st.session_state:
    st.session_state['submit_clicked'] = False

# Load custom CSS style
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

# Define a function to Load keywords
@st.cache_resource
def load_keywords(filename):
    with open(filename, 'r') as file:
        keywords = [line.strip() for line in file.readlines()]
    return set(keywords)

# Load keywords from file
keywords = load_keywords('job_related_terms.txt')


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
            st.subheader(f'Question {index + 1}. {question}')
            text_to_speech_browser(f'Question {index + 1}. {question}')
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
            feedback = 'Outstanding work!'
        elif 0.8 <= similarity <= 0.95:
            feedback = 'Good effort, but there is room for improvement.'
        elif 0 < similarity < 0.8:
            feedback = 'Your response shows potential for further refinement. '
        elif similarity == 0:
            feedback = 'Please provide your answer to the question to receive feedback.'
        else:
            feedback = 'Your response appears to be quite different from the expected answer. ' \
                       'Lets take a look at the correct answer to help you understand the key.'

        return feedback

    except Exception as e:
        st.error(f"An error occurred while evaluating the response: {str(e)}")
        return 'An error occurred during evaluation.'

# Define key word and job related terms counter
def count_job_related_terms_and_frequent_words(user_response, keywords):
    user_response_lower = user_response.lower()
    unique_keywords = set(keyword.lower() for keyword in keywords)
    job_related_terms = set([keyword for keyword in unique_keywords if keyword in user_response_lower])
    doc = model(user_response_lower)
    word_freq = Counter([token.text for token in doc if token.is_alpha])
    frequent_words = {word for word, count in word_freq.items() if count >= 3}

    return len(job_related_terms), job_related_terms, frequent_words

# Define a function to show the correct answer and feedback
def show_feedback(index, category):
    try:
        if category != "All":
            filtered_df = df[df['category'].str.lower() == category.lower()]
        else:
            filtered_df = df

        if index < len(filtered_df):
            answer = filtered_df['answers'].iloc[index]
            user_response = st.session_state.get('user_response', '')

            feedback = evaluate_response(user_response, answer)
            job_related_terms_count, job_related_terms, frequent_words = count_job_related_terms_and_frequent_words\
                (user_response, keywords)

            keywords_feedback = f"You have used {job_related_terms_count} terms that are relevant to Data Analytics. "\
                                f"These are: {', '.join(job_related_terms) if job_related_terms else 'None'}." \
                                f" Additionally, the most used words in your" \
                                f"response are: {' '.join(frequent_words) if frequent_words else 'None.'}"

            if feedback == 'Please provide your answer to the question to receive feedback.':
                st.info(f'✍️ {feedback} ')
                text_to_speech_browser(f'{feedback} ')
            else:
                st.info(f'{feedback} {keywords_feedback}')
                text_to_speech_browser(f'{feedback} {keywords_feedback}')

                st.info(f'{answer} Ready for the next challenge? Click on the "Question" button to '
                        f'proceed to Question {index + 2}.')
                text_to_speech_browser(f'{answer} Ready for the next challenge? Click on the Question button to'\
                                       f' proceed to Question {index + 2}.')
        else:
            st.warning("No more answers in this category.")
    except Exception as e:
        st.error(f"An error occurred while showing the correct answer: {str(e)}")


# Sidebar section with introductory information
st.sidebar.info('🙋‍ **Hi! Welcome to the Data Analytics Interview Prep!** 🎉🎉🎉')
st.sidebar.write("")
category = st.sidebar.selectbox("**Category:**", ["All", "Behavioral", "Conceptual", "Technical"])

# Sidebar buttons
if st.sidebar.button('Question', type="primary"):
    st.session_state['display'] = 'question'
    st.session_state.submit_clicked = False

if st.sidebar.button('Answer', type="primary"):
    st.session_state['display'] = 'answer'
    st.session_state.submit_clicked = False

st.sidebar.divider()
st.sidebar.write(":orange[Nov 2023 |] [Efrem Assefa](https://www.linkedin.com/in/efrem-assefa-bbb286237)")

# Load initial image and texts
if 'display' not in st.session_state:
    st.image('img.jpg', width=700)

    st.divider()
    st.markdown("""
        <div style="text-align:center;">
            <h1 style="color: #C07F00; font-style: sans-serif;font-size: 2em;margin-top: 40px; margin-bottom:40px;">
                How it works
            </h1>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
            <div style="background-color: #C07F00; padding: 10px; border-radius: 10px; margin-bottom: 10px;">
                <h1 style="color: #F5F5F5; text-align: center; font-style: sans-serif; font-size: 1em;">Select a Category</h1>
                <hr style="border: 1px solid #000000; margin-top: 1px; margin-bottom: 15px;" />
                <p style="color: #000000; margin-bottom: 70px;">Begin by choosing your desired category from the dropdown menu.</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div style="background-color: #C07F00; padding: 10px; border-radius: 10px; margin-bottom: 10px;">
                <h1 style="color: #F5F5F5; text-align: center; font-style: sans-serif; font-size: 1em;">Display a Question</h1>
                <hr style="border: 1px solid #000000; margin-top: 1px; margin-bottom: 15px;" />
                <p style="color: #000000; margin-bottom: 70px;">Click the "Question" button to view a new question from your selected category.</p>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
            <div style="background-color: #C07F00; padding: 10px; border-radius: 10px; margin-bottom: 10px;">
                <h1 style="color: #F5F5F5; text-align: center;font-style: sans-serif; font-size: 1em;">Submit Your Answer</h1>
                <hr style="border: 1px solid #000000;margin-top:1px; margin-bottom: 15px;" />
                <p style="color: #000000; margin-bottom: 20px;">After considering your response, click the "Answer" button.
                    A text box will appear for you to type in your answer.</p>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
            <div style="background-color: #C07F00; padding: 10px; border-radius: 10px; margin-bottom: 10px;">
                <h1 style="color: #F5F5F5; font-style: sans-serif; text-align: center; font-size: 1em;">Get Feedback</h1>
                <hr style="border: 1px solid #000000; margin-top: 1px; margin-bottom: 15px;" />
                <p style="color: #000000;margin-bottom: 20px;">Once you submit your answer, you'll immediately see
                    the correct answer along with personalized feedback.</p>
            </div>
        """, unsafe_allow_html=True)
    st.divider()
    st.markdown("""
            <div style="text-align:center;">
                <h1 style="font-style: sans-serif;font-size: 3em;margin-top: 70px; margin-bottom: 40px;">
                    ✨✨✨
                </h1>
            </div>
        """, unsafe_allow_html=True)


# Displaying results on the main page
if 'display' in st.session_state:
    if st.session_state['display'] == 'question':
        display_question(st.session_state.index, category)
        st.session_state.index += 1
    elif st.session_state['display'] == 'answer':
        st.session_state.user_response = st.text_area('**Type your answer below:**')
        submit_btn = st.button('Submit', type="primary")
        if submit_btn:
            st.session_state.submit_clicked = True
            st.write("")
            show_feedback(st.session_state.index - 1, category)





