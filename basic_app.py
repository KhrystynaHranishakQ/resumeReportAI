import streamlit as st
import concurrent.futures
import database_module
import prompts
import utils
import survey_questions


def set_state_stage(i):
    st.session_state.stage = i


def validate_survey_responses(survey):
    is_valid = True
    for k in survey.keys():
        if survey[k] is None or not survey[k]:
            is_valid = False

    if is_valid:
        set_state_stage(1)
        st.session_state.survey = survey
    else:
        set_state_stage(-1)


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
        like_1 = st.button(label="YES :+1:", key=like_button_key, on_click=set_state_stage, args=[2])
    with col2:
        dislike_1 = st.button(label="NO :-1:", key=dislike_button_key, on_click=set_state_stage, args=[2])
    comment_snapshot = st.text_input("Please leave more detailed feedback to help us make response more accurate",
                                     key=comment_key,
                                     on_change=set_state_stage, args=[2])
    if like_1:
        response["like"] = True
    if dislike_1:
        response["dislike"] = True
    if comment_snapshot:
        response["comment"] = comment_snapshot

    return response


def main():

    gpt_response = utils.GPTResults()

    if 'stage' not in st.session_state:
        st.session_state.stage = 0
    if 'record_id' not in st.session_state:
        st.session_state.record_id = None
    if 'survey' not in st.session_state:
        st.session_state.survey = {}
    if 'resume' not in st.session_state:
        st.session_state.resume = None
    if 'gpt_responses' not in st.session_state:
        st.session_state.gpt_responses = gpt_response

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
        st.button('Start Over', on_click=set_state_stage, args=[0])

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
            print(st.session_state.resume)
            print(st.session_state.survey)

            user_prompt_cv_with_survey = utils.get_cv_with_survey_result(st.session_state.resume,
                                                                         st.session_state.survey)
            user_prompt_cv = utils.get_cv(st.session_state.resume)

            # Parallel execution of calls to GPT
            print('Parallel execution is started...')
            tasks = {
                'milestones': (prompts.career_snapshot_milestones, user_prompt_cv_with_survey, 'milestones'),
                'key_numbers': (prompts.career_snapshot_key_numbers, user_prompt_cv_with_survey, 'key_numbers'),
                'roles': (prompts.career_snapshot_roles, user_prompt_cv_with_survey, 'roles'),

                'talents': (prompts.skills_analysis_talents, user_prompt_cv_with_survey, 'talents'),
                'skill_phasing_out': (prompts.skills_analysis_skill_phasing_out, user_prompt_cv_with_survey, 'skill_phasing_out'),
                'skill_trending': (prompts.skills_analysis_skill_trending, user_prompt_cv_with_survey, 'skill_trending'),

                'strengths': (prompts.strength_analysis_strengths, user_prompt_cv, 'strengths'),
                'higher_positions': (prompts.strength_analysis_higher_positions, user_prompt_cv, 'higher_positions'),
                'optimal_positions': (prompts.strength_analysis_optimal_positions, user_prompt_cv_with_survey, 'optimal_positions')
            }
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_to_id = {executor.submit(utils.get_gpt_response, task[0], task[1]): task_id for task_id, task in
                                tasks.items()}

                for future in concurrent.futures.as_completed(future_to_id):
                    task_id = future_to_id[future]
                    attribute_name = tasks[task_id][2]
                    try:
                        data = future.result()
                        setattr(gpt_response, attribute_name, data)
                        print(f'{task_id}: Done')
                    except Exception as exc:
                        print(f'{task_id} generated an exception: {exc}')
            print('Parallel execution is finished.')
            st.session_state.gpt_responses = gpt_response
            print(gpt_response.optimal_positions)
            # save to db
            st.session_state.record_id = database_module.insert_analysis_data(st.session_state.survey,
                                                                              st.session_state.resume,
                                                                              st.session_state.gpt_responses)
            set_state_stage(2)
    # visualization
    if st.session_state.stage >= 2:
        st.title(":violet[Career Report]")

        st.markdown("# Snapshot of Your Career Journey")
        st.markdown(st.session_state.gpt_responses.milestones)
        milestone_feedback = get_feedback('yes_1',
                                          'no_1', 'comment_1')
        # save feedback to db
        database_module.update_feedback(st.session_state.record_id,
                                        milestone_feedback,
                                        'career_milestones_like',
                                        'career_milestones_comment')
        st.markdown(st.session_state.gpt_responses.key_numbers)
        key_numbers_feedback = get_feedback('yes_2',
                                            'no_2', 'comment_2')
        # save feedback to db
        database_module.update_feedback(st.session_state.record_id,
                                        key_numbers_feedback,
                                        'career_key_numbers_like',
                                        'career_key_numbers_comment')

        st.markdown(st.session_state.gpt_responses.roles)
        roles_feedback = get_feedback('yes_3',
                                      'no_3', 'comment_3')
        # save feedback to db
        database_module.update_feedback(st.session_state.record_id,
                                        roles_feedback,
                                        'career_roles_like',
                                        'career_roles_comment')

        st.markdown("# Analyzing Your Skills")
        st.markdown(st.session_state.gpt_responses.talents)
        talents_feedback = get_feedback('yes_4',
                                      'no_4', 'comment_4')
        # save feedback to db
        database_module.update_feedback(st.session_state.record_id,
                                        talents_feedback,
                                        'skills_analisys_talents_like',
                                        'skills_analisys_talents_comment')

        st.markdown(st.session_state.gpt_responses.skill_phasing_out)
        skill_phasing_out_feedback = get_feedback('yes_5',
                                        'no_5', 'comment_5')
        # save feedback to db
        database_module.update_feedback(st.session_state.record_id,
                                        skill_phasing_out_feedback,
                                        'skills_analysis_skill_phasing_out_like',
                                        'skills_analysis_skill_phasing_out_comment')

        st.markdown(st.session_state.gpt_responses.skill_trending)
        skill_trending_feedback = get_feedback('yes_6',
                                                'no_6', 'comment_6')
        # save feedback to db
        database_module.update_feedback(st.session_state.record_id,
                                        skill_trending_feedback,
                                        'skills_analysis_skill_trending_like',
                                        'skills_analysis_skill_trending_comment')

        st.markdown("# Your Strengths and Ideal Roles")
        st.markdown(st.session_state.gpt_responses.strengths)
        strength_analysis_feedback = get_feedback('yes_7',
                                                  'no_7', 'comment_7')
        # save feedback to db
        database_module.update_feedback(st.session_state.record_id,
                                        strength_analysis_feedback,
                                        'strength_analysis_strengths_like',
                                        'strength_analysis_strengths_comment')

        st.markdown(st.session_state.gpt_responses.higher_positions)
        higher_positions_feedback = get_feedback('yes_8',
                                                  'no_8', 'comment_8')
        # save feedback to db
        database_module.update_feedback(st.session_state.record_id,
                                        higher_positions_feedback,
                                        'strength_analysis_higher_position_like',
                                        'strength_analysis_higher_position_comment')

        st.markdown(st.session_state.gpt_responses.optimal_positions)
        optimal_positions_feedback = get_feedback('yes_9',
                                                 'no_9', 'comment_9')
        # save feedback to db
        database_module.update_feedback(st.session_state.record_id,
                                        optimal_positions_feedback,
                                        'strength_analysis_optimal_position_like',
                                        'strength_analysis_optimal_position_comment')

        st.button('Start Over', on_click=set_state_stage, args=[0])


if __name__ == "__main__":
    main()
