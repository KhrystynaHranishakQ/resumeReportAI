from tika import parser
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import prompts
import time

load_dotenv()
client = OpenAI()
MODEL = "gpt-4-1106-preview"


def parse_file(file):
    # Tika can handle various file types, not just PDFs
    file_data = parser.from_file(file)
    text = file_data['content'].strip().replace('/n/n', '')
    return text


def prepare_career_snapshot(cv_text, obj, motivation):
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system",
             "content": prompts.career_snapshot_enhanced_part_1},
            {"role": "user", "content": prompts.cv_with_objective(cv_text, obj, motivation)}
        ]
    )
    report = completion.choices[0].message.content
    return report


def prepare_career_snapshot_part2(cv_text, obj, motivation):
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system",
             "content": prompts.career_snapshot_enhanced_part_2},
            {"role": "user", "content": prompts.cv_with_objective(cv_text, obj, motivation)}
        ]
    )
    report = completion.choices[0].message.content
    return report


def prepare_career_snapshot_part3(cv_text, survey_result):
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system",
             "content": prompts.career_snapshot_enhanced_part_3},
            {"role": "user", "content": prompts.cv_with_survey_result(cv_text, survey_result)}
        ]
    )
    report = completion.choices[0].message.content
    return report


def prepare_skills_analysis(system_prompt, cv_text, survey_result):
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system",
             "content": system_prompt},
            {"role": "user", "content": prompts.cv_with_survey_result(cv_text, survey_result)}
        ]
    )
    report = completion.choices[0].message.content
    return report


def prepare_strength_analysis(cv_text, survey_result):
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system",
             "content": prompts.strength_analysis},
            {"role": "user", "content": prompts.cv_with_survey_result(cv_text, survey_result)}
        ]
    )
    report = completion.choices[0].message.content
    return report


def set_state(i):
    st.session_state.stage = i


def validate_survey_responses(survey):

    is_valid = True
    for k in survey.keys():
        if survey[k] is None or not survey[k]:
            is_valid = False

    if is_valid:
        set_state(1)
        st.session_state.survey = survey
    else:
        set_state(-1)


def validate_uploads(upload_state):
    if upload_state:
        st.session_state.resume = upload_state
        set_state(2)
    else:
        set_state(-2)


def main():
    if 'stage' not in st.session_state:
        st.session_state.stage = 0
    if 'survey' not in st.session_state:
        st.session_state.survey = {}
    if 'upload_file' not in st.session_state:
        st.session_state.resume = None
    if 'snapshot_part1' not in st.session_state:
        st.session_state.snapshot_part1 = None
    if 'snapshot_part2' not in st.session_state:
        st.session_state.snapshot_part2 = None
    if 'snapshot_part3' not in st.session_state:
        st.session_state.snapshot_part3 = None
    if 'skills_part1' not in st.session_state:
        st.session_state.skills_part1 = None
    if 'skills_part2' not in st.session_state:
        st.session_state.skills_part2 = None
    if 'skills_part3' not in st.session_state:
        st.session_state.skills_part3 = None
    if 'strength' not in st.session_state:
        st.session_state.strength = None

    if st.session_state.stage == 0:
        st.title(":violet[Career Consultation Survey]")
        survey = {}
        st.subheader("Your Career Goals")
        survey["goal"] = st.radio(
            "What are your short-term and long-term career goals?",
            ('Gain a leadership position in my current field',
             'Switch to a different industry or career path',
             'Enhance my skills and expertise in my current role',
             'Achieve a better work-life balance'),
            index=None)

        st.subheader("Motivation Factors")
        survey["motivation"] = st.radio(
            "What motivates you the most in your professional life?",
            ('Achieving challenging goals and targets',
             'Working in a team and collaborating with others',
             'Learning new skills and personal development',
             'Recognition and rewards for my achievements'),
            index=None)

        st.subheader("Skills and Strengths")
        survey["skills"] = st.multiselect(
            "Which of the following do you consider to be your strongest skills or attributes? (Select up to three)",
            ['Technical skills related to my field',
             'Communication and interpersonal skills',
             'Problem-solving and analytical thinking',
             'Creativity and innovation',
             'Leadership and management abilities'],
            default=None)

        st.subheader("Work Environment Preferences")
        survey["environment"] = st.radio(
            "What type of work environment do you thrive in?",
            ('Fast-paced and constantly changing',
             'Structured with clear rules and expectations',
             'Collaborative and team-oriented',
             'Independent with the flexibility to manage my own tasks'),
            index=None)

        st.subheader("Professional Development")
        survey["development"] = st.radio(
            "How do you prefer to grow professionally?",
            ('Through formal education and training',
             'On-the-job learning and experiences',
             'Networking and mentorship opportunities',
             'Self-directed learning and research'),
            index=None)
        st.button('Submit', on_click=validate_survey_responses, args=[survey])

    if st.session_state.stage == -1:
        st.title(":violet[Career Consultation Survey]")
        st.error('Please answer all questions')
        st.button('Start Over', on_click=set_state, args=[0])

    if st.session_state.stage == 1:
        st.title(":violet[Career Consultation Survey]")
        st.success("Thank you for the response! Please upload your resume")
        st.subheader("Upload Your CV")
        uploaded_file = st.file_uploader(" ",
                                         type=["pdf", "docx", "pptx", "xlsx", "txt", "html", "rtf", "jpg", "png", "mp3",
                                               "mp4"])
        if uploaded_file:
            st.success("Thank you for the response! Analysing...")
            st.session_state.resume = parse_file(uploaded_file)
            # get career snapshot from GPT
            st.session_state.snapshot_part1 = prepare_career_snapshot(st.session_state.resume, st.session_state.survey["goal"],
                                                                      st.session_state.survey["motivation"])
            st.session_state.snapshot_part2 = prepare_career_snapshot_part2(st.session_state.resume,
                                                                      st.session_state.survey["goal"],
                                                                      st.session_state.survey["motivation"])
            st.session_state.snapshot_part3 = prepare_career_snapshot_part3(st.session_state.resume,
                                                                            st.session_state.survey)
            # get skill analysis
            st.session_state.skills_part1 = prepare_skills_analysis(prompts.skills_analysis_enhanced_part_1,
                                                                    st.session_state.resume, st.session_state.survey)
            st.session_state.skills_part2 = prepare_skills_analysis(prompts.skills_analysis_enhanced_part_2,
                                                                    st.session_state.resume, st.session_state.survey)
            st.session_state.skills_part3 = prepare_skills_analysis(prompts.skills_analysis_enhanced_part_3_1,
                                                                    st.session_state.resume, st.session_state.survey)
            # get strength analysis
            #st.session_state.strength = prepare_strength_analysis(st.session_state.resume, st.session_state.survey)
            set_state(2)

    if st.session_state.stage >= 2:
        st.title(":violet[Career Report]")
        st.markdown("# Snapshot of Your Career Journey")
        st.markdown(st.session_state.snapshot_part1)
        st.markdown(st.session_state.snapshot_part2)
        st.markdown(st.session_state.snapshot_part3)
        st.info("Do you like the response?")
        col1, col2 = st.columns(2)
        with col1:
            like_1 = st.button(label="YES :+1:", key='snapshot_yes', on_click=set_state, args=[2])
        with col2:
            dislike_1 = st.button(label="NO :-1:", key='snapshot_no', on_click=set_state, args=[2])
            comment_snapshot = st.text_input("Please tell what exactly you dislike?", key='snapshot_comment', on_change=set_state, args=[2])
        if like_1:
            print('like')
        if dislike_1:
            print('dislike')
        if comment_snapshot:
            print(comment_snapshot)
        st.markdown("# Analyzing Your Skills")
        st.markdown(st.session_state.skills_part1)
        st.markdown(st.session_state.skills_part2)
        st.markdown(st.session_state.skills_part3)
        st.info("Do you like the response?")
        col1, col2 = st.columns(2)
        with col1:
            like_2 = st.button(label="YES :+1:", key='skills_yes', on_click=set_state, args=[2])
        with col2:
            dislike_2 = st.button(label="NO :-1:", key='skills_no', on_click=set_state, args=[2])
            comment_skills = st.text_input("Please tell what exactly you dislike?", key='skill_comment', on_change=set_state, args=[2])
        if like_2:
            print('like')
        if dislike_2:
            print('dislike')
        if comment_skills:
            print(comment_skills)

        st.markdown(st.session_state.strength)
        st.info("Do you like the response?")
        col1, col2 = st.columns(2)
        with col1:
            like_3 = st.button(label="YES :+1:", key='strength_yes', on_click=set_state, args=[2])
        with col2:
            dislike_3 = st.button(label="NO :-1:", key='strength_no', on_click=set_state, args=[2])
            comment_strength = st.text_input("Please tell what exactly you dislike?", key='strength_comment')
        if like_3:
            print('like')
        if dislike_3:
            print('dislike')
        if comment_strength:
            print(comment_strength)

        st.button('Start Over', on_click=set_state, args=[0])


if __name__ == "__main__":
    main()

