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
    Placeholder for basic search functionality.
    """
    return f"Basic search for '{query}' is not implemented."

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

def get_web_resources(query):
    """
    Dummy function to simulate retrieval of web resources.
    Returns a dictionary with PDFs, Articles, and Videos.
    """
    return {
         "PDFs": [f"PDF result {i} for query '{query}'" for i in range(1, 4)],
         "Articles": [f"Article result {i} for query '{query}'" for i in range(1, 4)],
         "Videos": [f"Video result {i} for query '{query}'" for i in range(1, 4)]
    }
    
def convert_audio_to_text(audio_file):
    """
    Dummy function to simulate converting audio to text.
    """
    # In a real implementation, this would call a speech-to-text service.
    return "Transcribed text from audio."

def analyze_video(video_file):
    """
    Dummy function to simulate video analysis.
    Extracts the audio, converts it to text, and analyzes tone.
    """
    # In a real implementation, you might extract audio,
    # process it with a speech-to-text and tone analysis API.
    return "Transcribed text from video with tone analysis."

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
    hobby/tone sample, learning goals, current level, and languages.
    """
    profile = st.session_state.profile
    languages = profile.get('languages','N/A')
    profile_assessment = profile.get('assessment','N/A')
    prompt = (
        f"Based on the following user profile details:\n"
        f"Name: {profile.get('name', 'N/A')}\n"
        f"Personality: {profile.get('personality', 'N/A')}\n"
        f"Hobby/Tone Sample: {profile.get('tone_paragraph', 'N/A')}\n"
        f"Learning Goals: {profile.get('learning_goals', 'N/A')}\n"
        f"Current Level: {profile.get('level', 'N/A')}\n"
        f"Languages: {languages}\n\n"
        f"Provide a comprehensive lesson on the topic '{topic}' specifically focusing on the subtopic '{subtopic}'. "
        "The lesson should match the user's language style, include real-life examples related to their hobby, "
        "and offer actionable recommendations to help the user feel comfortable and engaged in their learning journey. "
        "Note: The hobby is only for tone reference, while the topics to learn are those provided above. "
        "If the user mentions being fun loving, include small humour. Also, provide examples, idioms, and proverbs "
        "in all the specified languages to make the content relatable. Do not add idioms/proverbs/jokes solely for content; "
        "make it very relatable. In case English is not mentioned in the languages, provide the content in the first language provided. "
        "Provide detailed explanations and examples to help the user understand the topic better. "
        f"Based on the {profile_assessment}, highlight strengths and weaknesses while designing a learning curve appropriate for the user's age."
    )
    lesson_content = generate_llm_response(prompt, provider="openai", model="gpt-4o", temperature=0.7)
    # Append the new lesson to the list of lessons in session state.
    if "lessons" not in st.session_state:
        st.session_state.lessons = {}
    st.session_state.lessons[f"{topic} - {subtopic}"] = lesson_content
    return lesson_content

##############################################
# Interview Session Functions
##############################################

def initialize_interview(subtopics, difficulty, behavior):
    """
    Initialize an interview session:
    - Generate a list of interview questions based on the lesson content.
    - Store the difficulty and interviewer behavior.
    """
    profile = st.session_state.profile
    lesson_context = ""
    if "lessons" in st.session_state and st.session_state.lessons:
        # For simplicity, use the first lesson as context.
        lesson_context = list(st.session_state.lessons.values())[0]
    prompt = (
        f"Based on the following subtopics:\n{subtopics}\n\n"
        "Generate 5 interview questions for a candidate based on the above topics. Does not matter the level of the  "
        "Return them as a numbered list."
        f"The questions should be of {difficulty} difficulty and the interviewer should be {behavior}. "
        "The questions should test the candidate's understanding of the topics, their ability to apply the concepts to real-world scenarios, "
        "The questions should be challenging but not overly complex based on the user's level and difficulty preference."
        "The questions should also test the candidate's problem-solving skills, creativity, and ability to think on their feet. "
    )
    questions_str = generate_llm_response(prompt, provider="openai", model="gpt-4o", temperature=0.7)
    # Parse questions by splitting on newlines and removing unwanted prefixes.
    questions = [q.strip() for q in questions_str.split("\n") if q.strip()]
    # Fallback if the generated list appears to be generic or empty.
    if not questions or any("Certainly!" in q for q in questions):
        questions = [
            "What is one key takeaway from the lesson?",
            "How would you apply the concepts learned to a real-world scenario?",
            "Can you explain a challenging aspect of the lesson in your own words?"
        ]
    st.session_state.interview_questions = questions
    st.session_state.current_question_index = 0
    st.session_state.interview_scores = []
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
    Summarize the interview session by calculating an overall score and highlighting strengths and weaknesses.
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
    avg_score = sum(scores) / len(scores) if scores else 0
    summary = f"Final Interview Score: {avg_score:.1f}/10\n\nFeedback Summary:\n"
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
            level = st.radio("What is your current level in learning topics", 
                             options=["Beginner", "Intermediate", "Advanced"])
            topics = st.text_input("What topics are you most interested in? (e.g., Chatbots, Data Science, etc.)")
            
            # New: Resume upload field
            resume_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"], key="resume_file")
            
            submitted = st.form_submit_button("Submit Profile")
            if submitted:
                profile_data = {
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
                # If a resume was uploaded, extract its text and store it.
                if resume_file is not None:
                    resume_text = extract_text_from_pdf(resume_file)
                    profile_data["resume_text"] = resume_text
                st.session_state.profile = profile_data
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
            "Topics of Interest": profile.get("topics", ""),
            "Resume Provided": "Yes" if profile.get("resume_text") else "No"
        })

        if "profile_analysis" not in st.session_state:
            prompt = (
                "Based on the following user profile details, provide a comprehensive assessment that includes:\n\n"
                "1. An evaluation of the user's personality type from their self-description.\n"
                "2. An analysis of their language style and tone as inferred from their writing sample.\n"
                "3. A discussion of their learning goals and current level, including actionable recommendations on which topics to focus on and steps to achieve their goals.\n"
                "4. If a resume is provided, a brief summary of the important points from the resume.\n\n"
                f"Name: {profile.get('name', 'N/A')}\n"
                f"Age: {profile.get('age', 'N/A')}\n"
                f"Personality Description: {profile.get('personality', 'N/A')}\n"
                f"Writing Sample (Tone & Language Style): {profile.get('tone_paragraph', 'N/A')}\n"
                f"Learning Goals: {profile.get('learning_goals', 'N/A')}\n"
                f"Current Level: {profile.get('level', 'N/A')}\n"
                f"Topics of Interest: {profile.get('topics', 'N/A')}\n"
            )
            if profile.get("resume_text"):
                prompt += f"Resume Content: {profile.get('resume_text')}\n\n"
            prompt += "Please provide a detailed, insightful analysis along with recommendations on how the user can reach their learning goals."
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
    query = st.text_input("Enter research terms:", key="web_search_query")
    if st.button("Search", key="web_search_button"):
        with st.spinner("Searching for web resources..."):
            resources = get_web_resources(query)
        st.markdown("### PDFs")
        for pdf in resources["PDFs"]:
            st.write(pdf)
        st.markdown("### Articles")
        for article in resources["Articles"]:
            st.write(article)
        st.markdown("### Videos")
        for video in resources["Videos"]:
            st.write(video)

def page_dynamic_lessons():
    st.header("Dynamic Lessons")
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        dynamic_topics = st.session_state.get("dynamic_topics", {})
        if dynamic_topics:
            selected_topic = st.selectbox("Select a Topic", list(dynamic_topics.keys()), key="selected_topic")
            subtopics = dynamic_topics.get(selected_topic, [])
            if subtopics:
                st.session_state.subtopics = subtopics
                selected_subtopic = st.selectbox("Select a Subtopic", subtopics, key="selected_subtopic")
            else:
                selected_subtopic = ""
        else:
            st.info("No topics available from your profile. Please add topics below.")
            selected_topic, selected_subtopic = None, None

        if st.button("Get Lesson", key="lesson_button") and selected_topic and selected_subtopic:
            with st.spinner("Generating lesson content..."):
                lesson_content = generate_lesson_content(selected_topic, selected_subtopic)
            # Append the new lesson and display all lessons
            st.success("Lesson generated!")
            st.markdown("#### Generated Lessons")
            for key, content in st.session_state.lessons.items():
                st.markdown(f"**{key}**")
                st.write(content)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
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
        interview_difficulty = st.selectbox("Select Interview Difficulty", ["Easy", "Medium", "Hard"], key="interview_difficulty")
        interview_behavior = st.selectbox("Select Interviewer Behavior", ["Aggressive", "Polite", "Medium"], key="interview_behavior")
        
        if st.button("Start Interview", key="start_interview"):
            initialize_interview(st.session_state.subtopics, interview_difficulty, interview_behavior) 
            st.success("Interview session started!")
            st.rerun()

        if "interview_questions" in st.session_state:
            current_idx = st.session_state.current_question_index
            questions = st.session_state.interview_questions
            if current_idx < len(questions):
                st.subheader(f"Question {current_idx+1}:")
                current_question = questions[current_idx]
                st.write(current_question)
                # Allow user to select answer mode
                answer_mode = st.radio("Select Answer Mode", options=["Text", "Audio", "Video"], key=f"answer_mode_{current_idx}")
                if answer_mode == "Text":
                    user_answer = st.text_area("Your Answer:", key=f"interview_answer_text_{current_idx}")
                elif answer_mode == "Audio":
                    audio_file = st.file_uploader("Upload Audio Answer", type=["mp3", "wav"], key=f"interview_audio_{current_idx}")
                    if audio_file is not None:
                        user_answer = convert_audio_to_text(audio_file)
                    else:
                        user_answer = ""
                elif answer_mode == "Video":
                    video_file = st.file_uploader("Upload Video Answer", type=["mp4", "mov"], key=f"interview_video_{current_idx}")
                    if video_file is not None:
                        user_answer = analyze_video(video_file)
                    else:
                        user_answer = ""
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
            st.session_state.pdf_text = pdf_text
            st.success("PDF uploaded successfully. You can now ask questions related to this PDF.")
        else:
            st.info("No PDF uploaded. You can chat with the default knowledge base.")
        query = st.text_input("Enter your question about the PDF or default knowledge base:", key="pdf_query")
        if st.button("Ask", key="pdf_ask"):
            with st.spinner("Generating answer..."):
                if "pdf_text" in st.session_state and st.session_state.pdf_text:
                    kb_text = st.session_state.pdf_text
                else:
                    kb_text = ("This is the default knowledge base of the GenAI Tutor. It includes comprehensive lessons on Python, "
                               "Generative AI, and more.")
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

    # If the profile hasn't been submitted or analysis not approved, show the landing page.
    if ("profile_completed" not in st.session_state or not st.session_state.profile_completed) or \
       ("profile_analysis_done" not in st.session_state or not st.session_state.profile_analysis_done):
        page_landing()
    else:
        st.title("GenAI Tutor: Learn Python & Generative AI")
        st.markdown("<hr>", unsafe_allow_html=True)

        tabs = st.tabs(["Dynamic Lessons", "Web Resource Search", "PDF Chatbot", "Interview & Assessment"])
        with tabs[0]:
            page_dynamic_lessons()
        with tabs[1]:
            page_web_resource_search()
        with tabs[2]:
            page_pdf_chatbot()
        with tabs[3]:
            page_interview_assessment()
    

if __name__ == "__main__":
    main()
