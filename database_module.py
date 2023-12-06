import os
import json
import psycopg2
# from dotenv import load_dotenv
#
# load_dotenv()


def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        return conn
    except Exception as e:
        print("I am unable to connect to the database", e)


def insert_analysis_data(survey,
                         parsed_cv_data,
                         gpt_responses):
    conn = get_db_connection()
    cv_id = None
    if conn:
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO career_data (survey, parsed_resume, career_milestones, career_key_numbers,career_roles, skills_analisys_talents, skills_analysis_skill_phasing_out, skills_analysis_skill_trending, strength_analysis_strengths, strength_analysis_higher_position, strength_analysis_optimal_position)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;
        """, (
            json.dumps(survey),
            parsed_cv_data,
            gpt_responses.milestones,
            gpt_responses.key_numbers,
            gpt_responses.roles,
            gpt_responses.talents,
            gpt_responses.skill_phasing_out,
            gpt_responses.skill_trending,
            gpt_responses.strengths,
            gpt_responses.higher_positions,
            gpt_responses.optimal_positions
        )
                    )

        cv_id = cur.fetchone()[0]
        conn.commit()

        cur.close()
        conn.close()
    else:
        raise ConnectionError()

    return cv_id


def update_feedback(record_id, feedback_dict, like_column, comment_column):
    conn = get_db_connection()
    if conn and record_id:
        cur = conn.cursor()

        if feedback_dict['like']:
            cur.execute(f"""
                UPDATE career_data 
                SET {like_column} = %s
                WHERE id = %s;
            """, (True, record_id))
        if feedback_dict['dislike']:
            cur.execute(f"""
                UPDATE career_data 
                SET {like_column} = %s
                WHERE id = %s;
            """, (False, record_id))
        if feedback_dict['comment']:
            cur.execute(f"""
                        UPDATE career_data 
                        SET {comment_column} = %s 
                        WHERE id = %s;
                    """, (feedback_dict['comment'], record_id))

        conn.commit()
        cur.close()
        conn.close()

