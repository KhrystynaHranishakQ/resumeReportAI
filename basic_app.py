import streamlit as st

import database_module
import prompts
import utils
import survey_questions


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


def get_feedback(like_button_key,
                 dislike_button_key,
                 comment_key):
    response = {"like": None,
                "dislike": None,
                "comment": None
                }
    st.info("Do you like the response?")
    col1, col2 = st.columns(2)
    with col1:
        like_1 = st.button(label="YES :+1:", key=like_button_key, on_click=set_state, args=[2])
    with col2:
        dislike_1 = st.button(label="NO :-1:", key=dislike_button_key, on_click=set_state, args=[2])
    comment_snapshot = st.text_input("Please leave more detailed feedback to help us make response more accurate",
                                     key=comment_key,
                                     on_change=set_state, args=[2])
    if like_1:
        response["like"] = True
    if dislike_1:
        response["dislike"] = True
    if comment_snapshot:
        response["comment"] = comment_snapshot

    return response


def main():
    if 'stage' not in st.session_state:
        st.session_state.stage = 0
    if 'record_id' not in st.session_state:
        st.session_state.record_id = None
    if 'survey' not in st.session_state:
        st.session_state.survey = {}
    if 'upload_file' not in st.session_state:
        st.session_state.resume = None
    if 'career_snapshot_milestones' not in st.session_state:
        st.session_state.career_snapshot_milestones = None
    if 'career_snapshot_key_numbers' not in st.session_state:
        st.session_state.career_snapshot_key_numbers = None
    if 'career_snapshot_roles' not in st.session_state:
        st.session_state.career_snapshot_roles = None
    if 'skills_analysis_talents' not in st.session_state:
        st.session_state.skills_analysis_talents = None
    if 'skills_analysis_skill_phasing_out' not in st.session_state:
        st.session_state.skills_analysis_skill_phasing_out = None
    if 'skills_analysis_skill_trending' not in st.session_state:
        st.session_state.skills_analysis_skill_trending = None
    if 'strength_analysis_strengths' not in st.session_state:
        st.session_state.strength_analysis_strengths = None

    if st.session_state.stage == 0:
        st.title(":violet[Career Consultation Survey]")
        survey = {}
        st.subheader("Your Career Goals")
        survey["goal"] = st.radio(survey_questions.q1,
                                  survey_questions.q1_answers,
                                  index=None)

        st.subheader("Motivation Factors")
        survey["motivation"] = st.radio(survey_questions.q2,
                                        survey_questions.q2_answers,
                                        index=None)

        st.subheader("Skills and Strengths")
        survey["skills"] = st.multiselect(survey_questions.q3,
                                          survey_questions.q3_answers,
                                          default=None)

        st.subheader("Work Environment Preferences")
        survey["environment"] = st.radio(survey_questions.q4,
                                         survey_questions.q4_answers,
                                         index=None)

        st.subheader("Professional Development")
        survey["development"] = st.radio(survey_questions.q5,
                                         survey_questions.q5_answers,
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
            st.success(
                "Thank you for the response! The analysis is started. Please be patient this might take a little while.")
            st.session_state.resume = utils.parse_file(uploaded_file)

            # get career snapshot from GPT
            user_prompt = utils.get_cv_with_survey_result(st.session_state.resume, st.session_state.survey)
            st.session_state.career_snapshot_milestones = utils.get_gpt_response(prompts.career_snapshot_milestones,
                                                                                 user_prompt)
            print('Milestones: Done')
            st.session_state.career_snapshot_key_numbers = utils.get_gpt_response(prompts.career_snapshot_key_numbers,
                                                                                  user_prompt)
            print('Key numbers: Done')
            st.session_state.career_snapshot_roles = utils.get_gpt_response(prompts.career_snapshot_roles,
                                                                            user_prompt)
            print('Roles: Done')

            # get skill analysis from GPT
            st.session_state.skills_analysis_talents = utils.get_gpt_response(prompts.skills_analysis_talents,
                                                                              user_prompt)
            print('Talents: Done')
            st.session_state.skills_analysis_skill_phasing_out = utils.get_gpt_response(
                prompts.skills_analysis_skill_phasing_out,
                user_prompt)
            print('Skills phasing out: Done')
            st.session_state.skills_analysis_skill_trending = utils.get_gpt_response(
                prompts.skills_analysis_skill_trending,
                user_prompt)
            print('Skills trending: Done')

            # get strength analysis from GPT
            st.session_state.strength_analysis_strengths = utils.get_gpt_response(
                prompts.strength_analysis_strengths,
                utils.get_cv(st.session_state.resume))
            print('Strengths: Done')

            # save to db
            st.session_state.record_id = database_module.insert_analysis_data(st.session_state.survey,
                                                                              st.session_state.resume,
                                                                              st.session_state.career_snapshot_milestones,
                                                                              st.session_state.career_snapshot_key_numbers,
                                                                              st.session_state.career_snapshot_roles,
                                                                              st.session_state.skills_analysis_talents,
                                                                              st.session_state.skills_analysis_skill_phasing_out,
                                                                              st.session_state.skills_analysis_skill_trending,
                                                                              st.session_state.strength_analysis_strengths)
            set_state(2)
    # visualization
    if st.session_state.stage >= 2:
        st.title(":violet[Career Report]")

        st.markdown("# Snapshot of Your Career Journey")
        st.markdown(st.session_state.career_snapshot_milestones)
        milestone_feedback = get_feedback('yes_1',
                                          'no_1', 'comment_1')
        # save feedback to db
        database_module.update_feedback(st.session_state.record_id,
                                        milestone_feedback,
                                        'career_milestones_like',
                                        'career_milestones_comment')
        st.markdown(st.session_state.career_snapshot_key_numbers)
        key_numbers_feedback = get_feedback('yes_2',
                                            'no_2', 'comment_2')
        # save feedback to db
        database_module.update_feedback(st.session_state.record_id,
                                        key_numbers_feedback,
                                        'career_key_numbers_like',
                                        'career_key_numbers_comment')

        st.markdown(st.session_state.career_snapshot_roles)
        roles_feedback = get_feedback('yes_3',
                                      'no_3', 'comment_3')
        # save feedback to db
        database_module.update_feedback(st.session_state.record_id,
                                        roles_feedback,
                                        'career_roles_like',
                                        'career_roles_comment')

        st.markdown("# Analyzing Your Skills")
        st.markdown(st.session_state.skills_analysis_talents)
        talents_feedback = get_feedback('yes_4',
                                      'no_4', 'comment_4')
        # save feedback to db
        database_module.update_feedback(st.session_state.record_id,
                                        talents_feedback,
                                        'skills_analisys_talents_like',
                                        'skills_analisys_talents_comment')

        st.markdown(st.session_state.skills_analysis_skill_phasing_out)
        skill_phasing_out_feedback = get_feedback('yes_5',
                                        'no_5', 'comment_5')
        # save feedback to db
        database_module.update_feedback(st.session_state.record_id,
                                        skill_phasing_out_feedback,
                                        'skills_analysis_skill_phasing_out_like',
                                        'skills_analysis_skill_phasing_out_comment')

        st.markdown(st.session_state.skills_analysis_skill_trending)
        skill_trending_feedback = get_feedback('yes_6',
                                                'no_6', 'comment_6')
        # save feedback to db
        database_module.update_feedback(st.session_state.record_id,
                                        skill_trending_feedback,
                                        'skills_analysis_skill_trending_like',
                                        'skills_analysis_skill_trending_comment')

        st.markdown("# Your Strengths and Ideal Roles")
        st.markdown(st.session_state.strength_analysis_strengths)
        strength_analysis_feedback = get_feedback('yes_7',
                                                  'no_7', 'comment_7')
        # save feedback to db
        database_module.update_feedback(st.session_state.record_id,
                                        strength_analysis_feedback,
                                        'strength_analysis_strengths_like',
                                        'strength_analysis_strengths_comment')

        st.button('Start Over', on_click=set_state, args=[0])


if __name__ == "__main__":
    main()
