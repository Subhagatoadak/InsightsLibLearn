import streamlit as st
from PIL import Image
from transformers import pipeline
import os, sys

# Adjust the root path and import your custom LLM service
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_path not in sys.path:
    sys.path.insert(0, root_path)
from llm_service.llm_generator import generate_llm_response

##############################################
# Landing Page: User Profile, Assessment & Survey
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
        # Display the submitted profile (optional)
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

        # Generate and display the assessment if not already done.
        if "profile_analysis" not in st.session_state:
            prompt = (
                "Based on the following user profile details, provide a comprehensive assessment that includes:\n\n"
                "1. An evaluation of the user's personality type from their self-description.\n"
                "2. An analysis of their language style and tone as inferred from their writing sample.\n"
                "3. A discussion of their learning goals and current level, including actionable recommendations on which topics to focus on and steps to achieve their goals.\n\n"
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
            # Save the complete assessment with the profile.
            st.session_state.profile["assessment"] = analysis

        st.subheader("Profile Assessment")
        st.write(st.session_state.profile_analysis)

        if st.button("Proceed to Tutor"):
            st.session_state.profile_analysis_done = True
            st.success("Proceeding to tutor functionalities...")
            st.rerun()

##############################################
# Tutor Functionalities Page Functions
##############################################

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
        st.markdown('</div>', unsafe_allow_html=True)

def page_web_resource_search():
    st.header("Web Resource Search")
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        query = st.text_input("Enter a topic to search for resources:", key="web_search_query")
        if st.button("Search", key="web_search_button"):
            with st.spinner("Searching for resources..."):
                search_results = search_web_resources(query)
            st.markdown("**Search Results:**")
            st.write(search_results)
        st.markdown('</div>', unsafe_allow_html=True)

def page_genai_tutor_lessons():
    st.header("GenAI Tutor Lessons")
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        lesson_topic = st.selectbox("Select a lesson topic", [
            "Introduction to Python",
            "Advanced Python Concepts",
            "Introduction to Generative AI",
            "Prompt Engineering",
            "Building Chatbots with Python"
        ], key="lesson_topic")
        if st.button("Get Lesson", key="lesson_button"):
            with st.spinner("Generating lesson content..."):
                lesson_prompt = (
                    f"Provide a comprehensive lesson on {lesson_topic} that includes clear explanations, "
                    "code examples, and practical exercises. Write in a friendly and engaging tone."
                )
                lesson_content = generate_llm_response(lesson_prompt, provider="openai",
                                                       model="gpt-4o", temperature=0.7)
            st.markdown("**Lesson Content:**")
            st.write(lesson_content)
        st.markdown('</div>', unsafe_allow_html=True)

def page_interview_assessment():
    st.header("Interview & Assessment")
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Practice Interview")
        interview_question = st.text_area("Interview Question (or use a default one):",
                                          value="Describe a challenging project you have worked on and how you overcame difficulties.",
                                          key="interview_question")
        if st.button("Generate Interview Question", key="interview_generate"):
            st.info("Use the above question for your practice interview.")
        st.markdown("### Your Answer")
        user_answer = st.text_area("Type your answer here:", key="interview_answer")
        if st.button("Assess My Answer", key="interview_assess"):
            if user_answer.strip() == "":
                st.error("Please provide an answer before assessment.")
            else:
                with st.spinner("Evaluating your answer..."):
                    evaluation = assess_answer(user_answer)
                st.markdown("**Evaluation & Improvement Tips:**")
                st.write(evaluation)
        st.markdown('</div>', unsafe_allow_html=True)

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
        st.markdown('</div>', unsafe_allow_html=True)

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

    # If the profile hasn't been submitted or the analysis not approved,
    # show the landing page. Once both are done, show tutor functionalities.
    if ("profile_completed" not in st.session_state or not st.session_state.profile_completed) or \
       ("profile_analysis_done" not in st.session_state or not st.session_state.profile_analysis_done):
        page_landing()
    else:
        st.title("GenAI Tutor: Learn Python & Generative AI")
        st.markdown("<hr>", unsafe_allow_html=True)

        # Tutor functionalities using tabs (pills)
        tabs = st.tabs(["Chatbot", "Web Resource Search", "GenAI Tutor Lessons", "Interview & Assessment", "Attire Analysis"])
        with tabs[0]:
            page_chatbot()
        with tabs[1]:
            page_web_resource_search()
        with tabs[2]:
            page_genai_tutor_lessons()
        with tabs[3]:
            page_interview_assessment()
        with tabs[4]:
            page_attire_analysis()

if __name__ == "__main__":
    main()
