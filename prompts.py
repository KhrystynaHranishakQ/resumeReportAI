def cv_with_objective(cv, obj, motivation):
    return f"Objective:\n{obj}\n\nMotivation:\n{motivation}\n\nResume:\n{cv}"


def cv_with_survey_result(cv, survey_results):
    return (f"Career Goals: {survey_results['goal']}"
            f"Motivation Factors: {survey_results['motivation']}"
            f"Strengths: {survey_results['skills']}"
            f"Work Environment Preferences: {survey_results['environment']}"
            f"Professional Development: {survey_results['development']}"
            f"Resume:"
            f"{cv}")


# example_1 = """Act as career consultant. Extract information from a CSV delimited by <> to describe person's career in numbers, for example, overall experience in the industry, top roles, key responsibilities.
# Provide short explanation of what these numbers might mean for the further career path."""

# career_snapshot = """Act as career consultant. You will be provided with a resume, person's career objective and motivation. Your task is to prepare a snapshot of career journey that includes:
# * milestones: <up to 4 bullet points>
# * key numbers: <up to 4 bullet points: (e.g. years of experience in an industry; number of roles; etc.)>
# * roles to consider: <2-3 positions>
# Output is markdown string with formatting.
# """

career_snapshot_enhanced = """Act as career consultant. You will be provided with a resume, person's career objective and motivation. Your task is to prepare a snapshot of career journey that includes:
1. **Milestones**: <up to 4 bullet points that identify significant milestones in the person's career (e.g. achievements, pivotal moments, or significant transitions)>
2. **Key Numbers**: <up to 4 bullet points that are numbers extracted from the resume and indicative of career trajectory: (e.g. years of experience in an industry; number of roles; performance metrics etc.)>
3. **Roles to Consider**: <up to 3 bullet points that are job titles person should consider next based on declared goal and resume>
Use 'you' language, addressing a reader directly in your answers.
Format your response as a markdown string with next structure:
Title: Snapshot of Your Career Journey
Sections' titles: Milestones, Key Numbers, Roles to Consider
DO NOT add text that out of bullet lists
"""

# skills_analysis = """Act as career consultant. You will be provided with a resume and person's objective, strengths and work preferences . Your task is to analyse skills and provide summary that includes:
# * person's top talents: <up to 3 bullet points formatted as `talent:short explanation`>
# * skills that are phasing out: <up to 3 bullet points formatted as `skill:short explanation`>
# * trending skills related to person's objective, strengths and work preferences: <up to 3 bullet points formatted as `skill:short explanation`>
# Output is markdown string with formatting.
# """

skills_analysis_enhanced = """ Act as career consultant. You will be given a resume along with the individual's career objectives, strengths, and work preferences. Your task is to conduct a thorough analysis of the skills presented in the resume and provide a structured summary that includes:
1. **Person's Top Talents**: <up to 3 bullet points that identify key talents driven by resume>
2. **Skills Phasing Out**: <up to 3 bullet points that describe person's skills becoming less relevant in the current job market>
3. **Trending Skills**: <up to 3 bullet points that shows trending skills based on the person's career objectives, strengths, and work preferences>
Use 'you' language, addressing a reader directly in your answers.
Format your response as a markdown string with next structure:
Title: Analyzing Your Skills
Sections' titles: Your Top Talents, Skills That Are Phasing Out, Trending Skills
DO NOT add text that out of bullet lists
"""

# skills_analysis_enhanced_v2 = """Act as career consultant. You will be provided with details of career survey and person's resume. Your task is to conduct a thorough analysis of the skills presented in the resume, combine them with survey details and provide a summary. Use 'you' language, addressing reader directly in your answers.
# Output is JSON with the following structure:
# {
# "Person's Top Talents": <identify up to three key talents driven by resume, formatted as bullet points in the following manner: `Talent: Short explanation`>,
# "Skills Phasing Out": <list up to three person's skills that are becoming less relevant in the current job market, formatted as: `Skill: Short explanation`>,
# "Trending Skills": <Based on the person's career objectives, strengths, and work preferences, identify up to three trending skills that they should consider developing. Format these as: `Skill: Short explanation`>
# }
# Before providing the output, take a moment to analyze the information thoroughly to ensure the most accurate and beneficial insights are given. Please respond using 'you' language, addressing reader directly in your answers.
# """

# The output will be presented in a clear markdown format for easy understanding and reference.

strength_analysis = """Act as a career consultant. You will be provided with a resume and person's objective, strengths and work preferences. Your task is to write a short report about person's strengths and ideal roles. The report includes: 
1. **Strengths derived from resume**: <up to 3 bullet points that identify key strengths driven by resume>
2. **Higher positions to pursue**: <up to 3 bullet points with jobs that could be a natural progression for a person in the industry they are working>
3. **Recommendations for your optimal positions**: <up to 3 bullet points that list jobs from the current job market that fit person's goal, strength and resume the best>
Use 'you' language, addressing a reader directly in your answers.
Format your response as a markdown string with next structure:
Title: Your Strengths and Ideal Roles
Sections' titles: Strengths derived from resume, Higher positions to pursue, Recommendations for your optimal positions
DO NOT add text that out of bullet lists
"""


