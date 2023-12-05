import os
import json
import psycopg2
from dotenv import load_dotenv

load_dotenv()


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
                         career_snapshot_milestones,
                         career_snapshot_key_numbers,
                         career_snapshot_roles,
                         skills_analysis_talents,
                         skills_analysis_skill_phasing_out,
                         skills_analysis_skill_trending,
                         strength_analysis_strengths):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO career_data (survey, parsed_resume, career_milestones, career_key_numbers,career_roles, skills_analisys_talents, skills_analysis_skill_phasing_out, skills_analysis_skill_trending, strength_analysis_strengths)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;
    """, (
        json.dumps(survey),
        parsed_cv_data,
        career_snapshot_milestones,
        career_snapshot_key_numbers,
        career_snapshot_roles,
        skills_analysis_talents,
        skills_analysis_skill_phasing_out,
        skills_analysis_skill_trending,
        strength_analysis_strengths
    )
                )

    cv_id = cur.fetchone()[0]
    conn.commit()

    cur.close()
    conn.close()

    return cv_id


def update_feedback(record_id, feedback_dict, like_column, comment_column):
    conn = get_db_connection()
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

