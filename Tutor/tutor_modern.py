import streamlit as st
from PIL import Image
import os, sys
import PyPDF2  # for extracting text from PDFs

# Adjust the root path and import your custom LLM service
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_path not in sys.path:
    sys.path.insert(0, root_path)
from llm_service.llm_generator import generate_llm_response

##############################################
# Placeholder Functions for Missing Dependencies
##############################################

def search_web_resources(query):
    """
    Placeholder for web search functionality.
    """
    return f"Search functionality is not implemented yet for query: '{query}'."

def analyze_formal_wear(image_file):
    """
    Placeholder for attire analysis.
    """
    return "Attire analysis functionality is not implemented yet."

def extract_text_from_pdf(pdf_file):
    """
    Extract text from an uploaded PDF file using PyPDF2.
    """
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

##############################################
# Helper Functions for Dynamic Topics & Lessons
##############################################

def generate_dynamic_topics():
    """
    Parse the user's topics from the profile and generate subtopics using LLM.
    Store the results in session state.
    """
    profile = st.session_state.profile
    topics_str = profile.get("topics", "")
    topics = [t.strip() for t in topics_str.split(",") if t.strip()]
    topics_data = {}
    for topic in topics:
        prompt = f"Generate 5 relevant subtopics for the learning topic: '{topic}'. Provide them as a comma-separated list."
        subtopics_str = generate_llm_response(prompt, provider="openai", model="gpt-4o", temperature=0.7)
        # Assume the response is a comma-separated list
        subtopics = [s.strip() for s in subtopics_str.split(",") if s.strip()]
        topics_data[topic] = subtopics
    st.session_state.dynamic_topics = topics_data

def generate_lesson_content(topic, subtopic):
    """
    Generate a lesson that matches the user's language tone and personality.
    The lesson prompt incorporates details such as the user's personality,
    hobby/tone sample, learning goals, and current level. 
    """
    profile = st.session_state.profile
    languages = profile.get('languages','N/A')
    prompt = (
        f"Based on the following user profile details:\n"
        f"Name: {profile.get('name', 'N/A')}\n"
        f"Personality: {profile.get('personality', 'N/A')}\n"
        f"Hobby/Tone Sample: {profile.get('tone_paragraph', 'N/A')}\n"
        f"Learning Goals: {profile.get('learning_goals', 'N/A')}\n"
        f"Current Level: {profile.get('level', 'N/A')}\n\n"
        f"languages: {profile.get('languages','N/A')}\n\n"
        f"Provide a comprehensive lesson on the topic '{topic}' specifically focusing on the subtopic '{subtopic}'. "
        "The lesson should match the user's language style, include real-life examples related to their hobby, "
        "and offer actionable recommendations to help the user feel comfortable and engaged in their learning journey."
        "Hobby is not the topic of interest, the topic/topics provided above are the topics to be looked at."
        "If in the personality type the user mentions he/she is fun loving then add small humour in the langauges provided."
        f"Always provide examples, idioms, proverbs in content strictly in all the languages {languages} provided to make it more relatable"
        ""
        
    )
    lesson_content = generate_llm_response(prompt, provider="openai", model="gpt-4o", temperature=0.7)
    # Save lesson in session state for later context (e.g., chatbot or interview)
    if "lessons" not in st.session_state:
        st.session_state.lessons = {}
    st.session_state.lessons[f"{topic} - {subtopic}"] = lesson_content
    return lesson_content

##############################################
# Interview Session Functions
##############################################

def initialize_interview():
    """
    Initialize an interview session:
    - Generate a list of interview questions based on the lesson content.
    - Store the difficulty and interviewer behavior.
    """
    profile = st.session_state.profile
    # Use the first generated lesson as context (if available)
    lesson_context = ""
    if "lessons" in st.session_state and st.session_state.lessons:
        lesson_context = list(st.session_state.lessons.values())[0]
    prompt = (
        f"Based on the following lesson content:\n{lesson_context}\n\n"
        f"Generate 3 interview questions for a candidate who has learned the above content. "
        "The questions should assess understanding and practical application. "
        "Return them as a numbered list."
    )
    questions_str = generate_llm_response(prompt, provider="openai", model="gpt-4o", temperature=0.7)
    # Parse questions (assuming they come as numbered lines)
    questions = [q.strip() for q in questions_str.split("\n") if q.strip()]
    st.session_state.interview_questions = questions
    st.session_state.current_question_index = 0
    st.session_state.interview_scores = []
    # Store interviewer settings using the widget values
    st.session_state.interviewer_settings = {
        "difficulty": st.session_state.get("interview_difficulty", "Medium"),
        "behavior": st.session_state.get("interview_behavior", "Medium")
    }

def evaluate_interview_answer(answer, question):
    """
    Evaluate the candidate's answer to an interview question.
    The evaluation should include a score (out of 10) and specific feedback.
    """
    prompt = (
        f"Interview Question: {question}\n\n"
        f"Candidate Answer: {answer}\n\n"
        "Evaluate the candidate's answer on a scale of 1 to 10. "
        "Provide a brief explanation of what was strong and what could be improved. "
        "Format the response as: 'Score: X. Feedback: ...'"
    )
    evaluation = generate_llm_response(prompt, provider="openai", model="gpt-4o", temperature=0.7)
    return evaluation

def finalize_interview():
    """
    Summarize the interview session by calculating an overall score and highlighting the candidate's strengths and weaknesses.
    """
    evaluations = st.session_state.interview_scores
    scores = []
    feedbacks = []
    for eval_text in evaluations:
        try:
            score_line = [line for line in eval_text.split("\n") if "Score:" in line][0]
            score = int(''.join(filter(str.isdigit, score_line)))
            scores.append(score)
            feedback_line = [line for line in eval_text.split("\n") if "Feedback:" in line][0]
            feedbacks.append(feedback_line)
        except Exception:
            pass
    if scores:
        avg_score = sum(scores) / len(scores)
    else:
        avg_score = 0
    summary = f"Final Interview Score: {avg_score:.1f}/10\n\n"
    summary += "Feedback Summary:\n"
    for fb in feedbacks:
        summary += f"- {fb}\n"
    return summary

##############################################
# Page Functions
##############################################

def page_landing():
    st.header("Welcome to InsightsLib Learn")
    st.write("Please complete the following survey so we can tailor your learning experience.")

    # If the profile hasn't been submitted, show the form.
    if "profile_completed" not in st.session_state:
        with st.form("profile_form"):
            st.subheader("Personal Details")
            name = st.text_input("What is your name?")
            age = st.number_input("What is your age?", min_value=0, max_value=100, step=1)
            country = st.text_input("Which country do you live in?")
            languages = st.text_input("Which languages are you comfortable in? (Separate by commas)")
            english_first = st.radio("Is English your first language?", options=["Yes", "No"])

            st.subheader("Personality Assessment")
            personality = st.text_area("How would you describe your personality?")
            tone_paragraph = st.text_area(
                "Write a short paragraph on your favorite hobby. This will help us understand your tone and language style."
            )

            st.subheader("Learning Goals Survey")
            learning_goals = st.text_area("What are your learning goals?")
            level = st.radio("What is your current level in learning Python & Generative AI?", 
                             options=["Beginner", "Intermediate", "Advanced"])
            topics = st.text_input("What topics are you most interested in? (e.g., Chatbots, Data Science, etc.)")
            
            submitted = st.form_submit_button("Submit Profile")
            if submitted:
                st.session_state.profile = {
                    "name": name,
                    "age": age,
                    "country": country,
                    "languages": languages,
                    "english_first": english_first,
                    "personality": personality,
                    "tone_paragraph": tone_paragraph,
                    "learning_goals": learning_goals,
                    "level": level,
                    "topics": topics
                }
                st.session_state.profile_completed = True
                st.success("Profile submitted successfully!")
                st.rerun()  # Force a rerun to display the assessment
    else:
        st.subheader("Your Submitted Profile")
        profile = st.session_state.profile
        st.write({
            "Name": profile.get("name", ""),
            "Age": profile.get("age", ""),
            "Country": profile.get("country", ""),
            "Languages": profile.get("languages", ""),
            "English First": profile.get("english_first", ""),
            "Personality": profile.get("personality", ""),
            "Tone Sample": profile.get("tone_paragraph", ""),
            "Learning Goals": profile.get("learning_goals", ""),
            "Current Level": profile.get("level", ""),
            "Topics of Interest": profile.get("topics", "")
        })

        if "profile_analysis" not in st.session_state:
            prompt = (
                "Based on the following user profile details, provide a comprehensive assessment that includes:\n\n"
                "1. An evaluation of the user's personality type from their self-description.\n"
                "2. An analysis of their language style and tone as inferred from their writing sample.\n"
                "3. A discussion of their learning goals and current level, including actionable recommendations on which topics to focus on and steps to achieve their goals.\n\n"
                "4. The hobby should not be included as topics to learn. It should only be included if the user explicitly mentions it in the topics."
                f"Name: {profile.get('name', 'N/A')}\n"
                f"Age: {profile.get('age', 'N/A')}\n"
                f"Personality Description: {profile.get('personality', 'N/A')}\n"
                f"Writing Sample (Tone & Language Style): {profile.get('tone_paragraph', 'N/A')}\n"
                f"Learning Goals: {profile.get('learning_goals', 'N/A')}\n"
                f"Current Level: {profile.get('level', 'N/A')}\n"
                f"Topics of Interest: {profile.get('topics', 'N/A')}\n\n"
                "Please provide a detailed, insightful analysis along with recommendations on how the user can reach their learning goals."
            )
            analysis = generate_llm_response(prompt,
                                             provider="openai",
                                             model="gpt-4o",
                                             temperature=0.7)
            st.session_state.profile_analysis = analysis
            st.session_state.profile["assessment"] = analysis

        st.subheader("Profile Assessment")
        st.write(st.session_state.profile_analysis)

        if st.button("Proceed to Tutor"):
            st.session_state.profile_analysis_done = True
            if "dynamic_topics" not in st.session_state:
                generate_dynamic_topics()
            st.success("Proceeding to tutor functionalities...")
            st.rerun()

def page_web_resource_search():
    st.header("Web Resource Search")
    query = st.text_input("Enter a topic to search for resources:", key="web_search_query")
    if st.button("Search", key="web_search_button"):
        with st.spinner("Searching for resources..."):
            search_results = search_web_resources(query)
        st.markdown("**Search Results:**")
        st.write(search_results)

def page_dynamic_lessons():
    st.header("Dynamic Lessons")
    # Display existing dynamic topics and allow user to add new ones.
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        # Display existing topics if available
        dynamic_topics = st.session_state.get("dynamic_topics", {})
        if dynamic_topics:
            selected_topic = st.selectbox("Select a Topic", list(dynamic_topics.keys()), key="selected_topic")
            subtopics = dynamic_topics.get(selected_topic, [])
            if subtopics:
                selected_subtopic = st.selectbox("Select a Subtopic", subtopics, key="selected_subtopic")
            else:
                selected_subtopic = ""
        else:
            st.info("No topics available from your profile. Please add topics below.")
            selected_topic, selected_subtopic = None, None

        if st.button("Get Lesson", key="lesson_button") and selected_topic and selected_subtopic:
            with st.spinner("Generating lesson content..."):
                lesson_content = generate_lesson_content(selected_topic, selected_subtopic)
            st.markdown("**Lesson Content:**")
            st.write(lesson_content)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Section to add additional topics
        st.subheader("Add Additional Topics")
        additional_topics = st.text_input("Enter additional topics (comma-separated)", key="additional_topics")
        if st.button("Add Topics"):
            if additional_topics:
                new_topics = [t.strip() for t in additional_topics.split(",") if t.strip()]
                dynamic_topics = st.session_state.get("dynamic_topics", {})
                for topic in new_topics:
                    if topic not in dynamic_topics:
                        prompt = f"Generate 5 relevant subtopics for the learning topic: '{topic}'. Provide them as a comma-separated list."
                        subtopics_str = generate_llm_response(prompt, provider="openai", model="gpt-4o", temperature=0.7)
                        subtopics = [s.strip() for s in subtopics_str.split(",") if s.strip()]
                        dynamic_topics[topic] = subtopics
                st.session_state.dynamic_topics = dynamic_topics
                st.success("Additional topics added.")
                st.rerun()
            else:
                st.error("Please enter at least one topic.")

def page_interview_assessment():
    st.header("Interview & Assessment")
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Interview Settings")
        # Use local variables for widget selections; these values are automatically stored in st.session_state
        difficulty = st.selectbox("Select Interview Difficulty", ["Easy", "Medium", "Hard"], key="interview_difficulty")
        behavior = st.selectbox("Select Interviewer Behavior", ["Aggressive", "Polite", "Medium"], key="interview_behavior")
        
        if st.button("Start Interview", key="start_interview"):
            initialize_interview()
            st.success("Interview session started!")
            st.rerun()

        if "interview_questions" in st.session_state:
            current_idx = st.session_state.current_question_index
            questions = st.session_state.interview_questions
            if current_idx < len(questions):
                st.subheader(f"Question {current_idx+1}:")
                current_question = questions[current_idx]
                st.write(current_question)
                user_answer = st.text_area("Your Answer:", key=f"interview_answer_{current_idx}")
                if st.button("Submit Answer", key=f"submit_interview_{current_idx}"):
                    with st.spinner("Evaluating your answer..."):
                        evaluation = evaluate_interview_answer(user_answer, current_question)
                    st.session_state.interview_scores.append(evaluation)
                    st.write("**Evaluation & Feedback:**")
                    st.write(evaluation)
                    st.session_state.current_question_index += 1
                    st.rerun()
            else:
                st.subheader("Interview Completed!")
                final_summary = finalize_interview()
                st.write(final_summary)
        st.markdown("</div>", unsafe_allow_html=True)

def page_attire_analysis():
    st.header("Attire Analysis")
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("To analyze your attire, please allow access to your camera and take a picture below.")
        image_file = st.camera_input("Take a picture", key="attire_camera")
        if image_file is not None:
            with st.spinner("Analyzing image..."):
                result = analyze_formal_wear(image_file)
            st.markdown("**Analysis Result:**")
            st.write(result)
            st.image(Image.open(image_file), caption="Captured Image", use_column_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

def page_chatbot():
    st.header("Chatbot Interface")
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        prompt = st.text_input("Enter your question or topic:", key="chatbot_prompt")
        provider = st.selectbox("Choose LLM Provider", ["openai", "huggingface", "claude", "gemini"],
                                key="chatbot_provider")
        model = st.text_input("Model", value="gpt-4o", key="chatbot_model")
        temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7,
                                  step=0.1, key="chatbot_temperature")
        if st.button("Submit", key="chatbot_submit"):
            with st.spinner("Generating response..."):
                response = generate_llm_response(prompt, provider=provider,
                                                 model=model, temperature=temperature)
            st.markdown("**Response:**")
            st.write(response)
        st.markdown("</div>", unsafe_allow_html=True)

def page_pdf_chatbot():
    st.header("PDF Chatbot")
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        uploaded_pdf = st.file_uploader("Upload a PDF", type=["pdf"], key="uploaded_pdf")
        if uploaded_pdf:
            with st.spinner("Extracting text from PDF..."):
                pdf_text = extract_text_from_pdf(uploaded_pdf)
            st.session_state.pdf_text = pdf_text  # store extracted text in session state
            st.success("PDF uploaded successfully. You can now ask questions related to this PDF.")
        else:
            st.info("No PDF uploaded. You can chat with the default knowledge base.")
        query = st.text_input("Enter your question about the PDF or default knowledge base:", key="pdf_query")
        if st.button("Ask", key="pdf_ask"):
            with st.spinner("Generating answer..."):
                if "pdf_text" in st.session_state and st.session_state.pdf_text:
                    kb_text = st.session_state.pdf_text
                else:
                    kb_text = "This is the default knowledge base of the GenAI Tutor. It includes comprehensive lessons on Python, Generative AI, and more."
                prompt = f"Given the following text:\n\n{kb_text}\n\nAnswer the following question in detail:\n{query}"
                answer = generate_llm_response(prompt, provider="openai", model="gpt-4o", temperature=0.7)
            st.markdown("**Answer:**")
            st.write(answer)
        st.markdown("</div>", unsafe_allow_html=True)

##############################################
# Custom CSS Injection for Modern Dark Design (Black & Red)
##############################################

def inject_custom_css():
    st.markdown("""
    <!-- Import Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <style>
    body {
        background: linear-gradient(135deg, #1c1c1c, #000000);
        font-family: 'Roboto', sans-serif;
        color: #fff;
    }
    .css-18e3th9 {
        background: linear-gradient(135deg, #1c1c1c, #000000);
    }
    h1, h2, h3 {
        color: #fff;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }
    .stButton>button {
        background: linear-gradient(45deg, #ff4d4d, #cc0000);
        border: none;
        border-radius: 50px;
        color: white;
        padding: 10px 20px;
        font-size: 16px;
        font-weight: bold;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 15px rgba(204, 0, 0, 0.5);
    }
    .stTextInput>div>div>input {
        border: 2px solid #ff4d4d;
        border-radius: 8px;
        padding: 10px;
        background: #333;
        color: #fff;
    }
    .card {
        background: #262626;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

##############################################
# Main App Function
##############################################

def main():
    st.set_page_config(page_title="InsightsLib Learn", layout="wide")
    inject_custom_css()

    # If the profile hasn't been submitted or the analysis not approved, show the landing page.
    if ("profile_completed" not in st.session_state or not st.session_state.profile_completed) or \
       ("profile_analysis_done" not in st.session_state or not st.session_state.profile_analysis_done):
        page_landing()
    else:
        st.title("GenAI Tutor: Learn Python & Generative AI")
        st.markdown("<hr>", unsafe_allow_html=True)

        # Tutor functionalities using tabs
        tabs = st.tabs(["Dynamic Lessons","Web Resource Search", "PDF Chatbot",  "Interview & Assessment", "Attire Analysis"])
        with tabs[0]:
            page_dynamic_lessons()
            
        with tabs[1]:
            
            page_web_resource_search()
        with tabs[2]:
            page_pdf_chatbot()
        with tabs[3]:
            page_interview_assessment()
        with tabs[4]:
            page_attire_analysis()
            

if __name__ == "__main__":
    main()
