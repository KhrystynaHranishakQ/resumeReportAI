import os

from tika import parser
from openai import OpenAI
# from dotenv import load_dotenv
#
# load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4-1106-preview"
client = OpenAI()


class GPTResults:
    def __init__(self):
        self.milestones = None
        self.key_numbers = None
        self.roles = None
        self.talents = None
        self.skill_phasing_out = None
        self.skill_trending = None
        self.strengths = None
        self.higher_positions = None
        self.optimal_positions = None


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
