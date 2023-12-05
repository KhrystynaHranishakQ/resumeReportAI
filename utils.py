from tika import parser
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

MODEL = "gpt-4-1106-preview"
client = OpenAI()


def parse_file(file):
    # Tika can handle various file types, not just PDFs
    file_data = parser.from_file(file)
    text = file_data['content'].strip().replace('/n/n', '')
    return text


def get_gpt_response(system_message, user_message):

    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system",
             "content": system_message},
            {"role": "user", "content": user_message}
        ]
    )
    report = completion.choices[0].message.content
    return report


def get_cv_with_survey_result(cv, survey_results):
    return (f"Responses from a person to a career survey"
            f'"""'
            f"Career goals: {survey_results['goal']}"
            f"Motivation factors: {survey_results['motivation']}"
            f"Strengths: {survey_results['skills']}"
            f"Work environment preferences: {survey_results['environment']}"
            f"Professional development preferences: {survey_results['development']}"
            f'"""'
            f"Resume:"
            f'"""{cv}"""')


def get_cv(cv):
    return (
            f'"""'
            f"Resume:"
            f'"""{cv}"""')
