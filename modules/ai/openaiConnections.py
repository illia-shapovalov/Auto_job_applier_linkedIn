'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

Support me: https://github.com/sponsors/GodsScion

version:    26.01.20.5.08
'''


import json

from config.secrets import *
from config.settings import showAiErrorAlerts
from config.personals import ethnicity, gender, disability_status, veteran_status
from config.questions import *
from config.search import security_clearance, did_masters

from modules.helpers import print_lg, critical_error_log, convert_to_json
from modules.ai.prompts import *

from pyautogui import confirm
from openai import OpenAI
from openai.types.model import Model
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from typing import Iterator, Literal


apiCheckInstructions = """

1. Make sure your AI API connection details like url, key, model names, etc are correct.
2. If you're using an local LLM, please check if the server is running.
3. Check if appropriate LLM and Embedding models are loaded and running.

Open `secret.py` in `/config` folder to configure your AI API connections.

ERROR:
"""

# Function to show an AI error alert
def ai_error_alert(message: str, stackTrace: str, title: str = "AI Connection Error") -> None:
    """
    Function to show an AI error alert and log it.
    """
    global showAiErrorAlerts
    if showAiErrorAlerts:
        if "Pause AI error alerts" == confirm(f"{message}{stackTrace}\n", title, ["Pause AI error alerts", "Okay Continue"]):
            showAiErrorAlerts = False
    critical_error_log(message, stackTrace)


# Function to check if an error occurred
def ai_check_error(response: ChatCompletion | ChatCompletionChunk) -> None:
    """
    Function to check if an error occurred.
    * Takes in `response` of type `ChatCompletion` or `ChatCompletionChunk`
    * Raises a `ValueError` if an error is found
    """
    if response.model_extra.get("error"):
        raise ValueError(
            f'Error occurred with API: "{response.model_extra.get("error")}"'
        )


# Function to create an OpenAI client
def ai_create_openai_client() -> OpenAI:
    """
    Function to create an OpenAI client.
    * Takes no arguments
    * Returns an `OpenAI` object
    """
    try:
        print_lg("Creating OpenAI client...")
        if not use_AI:
            raise ValueError("AI is not enabled! Please enable it by setting `use_AI = True` in `secrets.py` in `config` folder.")
        
        client = OpenAI(base_url=llm_api_url, api_key=llm_api_key)

        models = ai_get_models_list(client)
        if "error" in models:
            raise ValueError(models[1])
        if len(models) == 0:
            raise ValueError("No models are available!")
        if llm_model not in [model.id for model in models]:
            raise ValueError(f"Model `{llm_model}` is not found!")
        
        print_lg("---- SUCCESSFULLY CREATED OPENAI CLIENT! ----")
        print_lg(f"Using API URL: {llm_api_url}")
        print_lg(f"Using Model: {llm_model}")
        print_lg("Check './config/secrets.py' for more details.\n")
        print_lg("---------------------------------------------")

        return client
    except Exception as e:
        ai_error_alert(f"Error occurred while creating OpenAI client. {apiCheckInstructions}", e)


# Function to close an OpenAI client
def ai_close_openai_client(client: OpenAI) -> None:
    """
    Function to close an OpenAI client.
    * Takes in `client` of type `OpenAI`
    * Returns no value
    """
    try:
        if client:
            print_lg("Closing OpenAI client...")
            client.close()
    except Exception as e:
        ai_error_alert("Error occurred while closing OpenAI client.", e)



# Function to get list of models available in OpenAI API
def ai_get_models_list(client: OpenAI) -> list[ Model | str]:
    """
    Function to get list of models available in OpenAI API.
    * Takes in `client` of type `OpenAI`
    * Returns a `list` object
    """
    try:
        print_lg("Getting AI models list...")
        if not client: raise ValueError("Client is not available!")
        models = client.models.list()
        ai_check_error(models)
        print_lg("Available models:")
        print_lg(models.data, pretty=True)
        return models.data
    except Exception as e:
        critical_error_log("Error occurred while getting models list!", e)
        return ["error", e]

def model_supports_temperature(model_name: str) -> bool:
    """
    Checks if the specified model supports the temperature parameter.
    
    Args:
        model_name (str): The name of the AI model.
    
    Returns:
        bool: True if the model supports temperature adjustments, otherwise False.
    """
    return model_name in ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o", "gpt-4o-mini"]

# Function to get chat completion from OpenAI API
def ai_completion(client: OpenAI, messages: list[dict], response_format: dict = None, temperature: float = 0, stream: bool = stream_output) -> dict | ValueError:
    """
    Function that completes a chat and prints and formats the results of the OpenAI API calls.
    * Takes in `client` of type `OpenAI`
    * Takes in `messages` of type `list[dict]`. Example: `[{"role": "user", "content": "Hello"}]`
    * Takes in `response_format` of type `dict` for JSON representation, default is `None`
    * Takes in `temperature` of type `float` for temperature, default is `0`
    * Takes in `stream` of type `bool` to indicate if it's a streaming call or not
    * Returns a `dict` object representing JSON response, will try to convert to JSON if `response_format` is given
    """
    if not client: raise ValueError("Client is not available!")

    params = {"model": llm_model, "messages": messages, "stream": stream}

    if model_supports_temperature(llm_model):
        params["temperature"] = temperature
    if response_format and llm_spec in ["openai", "openai-like"]:
        params["response_format"] = response_format

    completion = client.chat.completions.create(**params)

    result = ""
    
    # Log response
    if stream:
        print_lg("--STREAMING STARTED")
        for chunk in completion:
            ai_check_error(chunk)
            chunkMessage = chunk.choices[0].delta.content
            if chunkMessage != None:
                result += chunkMessage
            print_lg(chunkMessage, end="", flush=True)
        print_lg("\n--STREAMING COMPLETE")
    else:
        ai_check_error(completion)
        result = completion.choices[0].message.content
    
    if response_format:
        result = convert_to_json(result)
    
    print_lg("\nAI Answer to Question:\n")
    print_lg(result, pretty=response_format)
    return result


def ai_extract_skills(client: OpenAI, job_description: str, stream: bool = stream_output) -> dict | ValueError:
    """
    Function to extract skills from job description using OpenAI API.
    * Takes in `client` of type `OpenAI`
    * Takes in `job_description` of type `str`
    * Takes in `stream` of type `bool` to indicate if it's a streaming call
    * Returns a `dict` object representing JSON response
    """
    print_lg("-- EXTRACTING SKILLS FROM JOB DESCRIPTION")
    try:        
        prompt = extract_skills_prompt.format(job_description)

        messages = [{"role": "user", "content": prompt}]
        ##> ------ Dheeraj Deshwal : dheeraj20194@iiitd.ac.in/dheerajdeshwal9811@gmail.com - Bug fix ------
        return ai_completion(client, messages, response_format=extract_skills_response_format, stream=stream)
    ##<
    except Exception as e:
        ai_error_alert(f"Error occurred while extracting skills from job description. {apiCheckInstructions}", e)


##> ------ Dheeraj Deshwal : dheeraj9811 Email:dheeraj20194@iiitd.ac.in/dheerajdeshwal9811@gmail.com - Feature ------
def ai_answer_question(
    client: OpenAI, 
    question: str, options: list[str] | None = None, question_type: Literal['text', 'textarea', 'single_select', 'multiple_select'] = 'text', 
    job_description: str = None, about_company: str = None, user_information_all: str = None,
    stream: bool = stream_output
) -> dict | ValueError:
    """
    Function to generate AI-based answers for questions in a form.
    
    Parameters:
    - `client`: OpenAI client instance.
    - `question`: The question being answered.
    - `options`: List of options (for `single_select` or `multiple_select` questions).
    - `question_type`: Type of question (text, textarea, single_select, multiple_select) It is restricted to one of four possible values.
    - `job_description`: Optional job description for context.
    - `about_company`: Optional company details for context.
    - `user_information_all`: information about you, AI cna use to answer question eg: Resume-like user information.
    - `stream`: Whether to use streaming AI completion.
    
    Returns:
    - `str`: The AI-generated answer.
    """

    print_lg("-- ANSWERING QUESTION using AI")
    try:
        prompt = ai_answer_prompt.format(user_information_all or "N/A", question)
         # Append optional details if provided
        if job_description and job_description != "Unknown":
            prompt += f"\nJob Description:\n{job_description}"
        if about_company and about_company != "Unknown":
            prompt += f"\nAbout the Company:\n{about_company}"

        messages = [{"role": "user", "content": prompt}]
        print_lg("Prompt we are passing to AI: ", prompt)
        response =  ai_completion(client, messages, stream=stream)
        # print_lg("Response from AI: ", response)
        return response
    except Exception as e:
        ai_error_alert(f"Error occurred while answering question. {apiCheckInstructions}", e)
##<


def ai_answer_form_question(
    client: OpenAI,
    question: str,
    question_type: Literal[
        "text",
        "textarea",
        "single_select",
    ] = "text",
    options: list[str] | None = None,
    job_description: str | None = None,
    user_information_all: str | None = None,
    assertiveness: int = 1,
) -> dict | None:
    """
    Answer an application question using structured, validated JSON.

    The model must return UNKNOWN when the candidate information does not
    explicitly support an answer.
    """
    print_lg("-- ANSWERING STRUCTURED FORM QUESTION USING AI")

    try:
        clean_options = [
            str(option).strip()
            for option in (options or [])
            if str(option).strip()
        ]

        options_json = json.dumps(
            clean_options,
            ensure_ascii=False,
        )

        assertiveness = max(
            0,
            min(int(assertiveness), 3),
        )

        assertiveness_instructions = {
            0: """
Use an extremely strict standard.
Answer only when the exact fact is directly stated.
Return UNKNOWN whenever interpretation is required.
""",
            1: """
Use a conservative standard.
Allow direct conclusions from explicit facts, but avoid
broadening technology experience or preferences.
""",
            2: """
Use a confident but truthful standard.
Recognize closely related technologies, transferable
experience, and clearly implied low-risk preferences.
Present relevant facts positively without changing
credentials, dates, or qualification status.
""",
            3: """
Use an aggressive-but-truthful standard.

For broad questions about overall technical or software
experience, aggregate formal employment, family-business
technical work, substantial independent projects, serious
homelab infrastructure work, and academic technical work
when those activities are explicitly included in the
candidate information.

For technology questions:
- count direct professional experience first
- recognize substantial project and production-like
  independent experience
- recognize closely related frameworks and transferable
  responsibilities in descriptive answers
- do not assign all broad experience to every technology
- do not invent technology-specific dates

For broad education-level dropdowns, a currently pursued
bachelor's degree may support selecting "Bachelor's" when
the question asks education level rather than whether the
degree was completed or awarded.

For preference, interest, willingness, comfort, and
availability questions, choose the favorable answer when
the candidate information reasonably supports it.

Use strong, confident wording in text and textarea answers.
Do not use hesitant language when the fact is supported.
""",
        }[assertiveness]

        prompt = f"""
You are answering one employment-application form question.

Assertiveness level:
{assertiveness}

Assertiveness instructions:
{assertiveness_instructions}

Use the candidate information as the primary source of truth.
The job description is optional context. Do not require a job description
when the candidate information already answers the question.

For low-risk preference, comfort, interest, and willingness questions,
explicitly stated preferences, intentions, and relevant past experience
count as sufficient evidence.

Examples:
- "Actively seeking fully remote roles" supports answering "Yes" to
  being comfortable working fully remotely.
- Prior successful remote-work experience supports answering "Yes" to
  comfort with remote work unless contradictory information is present.
- A stated willingness to travel supports an equivalent travel question.



Tailored application-text rules:

Before answering a text or textarea field, determine whether it is asking
for one of these application-writing purposes:

1. Cover letter
   Examples include:
   - cover letter
   - lettre de motivation
   - motivation letter
   - application letter
   - letter to the hiring manager
   - explain why you are a suitable candidate

2. Professional summary
   Examples include:
   - professional summary
   - résumé professionnel
   - candidate summary
   - profile summary
   - about you
   - tell us about yourself
   - short biography
   - brief introduction

3. Role motivation
   Examples include:
   - why are you interested in this role
   - why do you want to work here
   - pourquoi ce poste vous intéresse
   - why should we hire you
   - what makes you a good fit

For every cover-letter field:

- Generate a new, job-specific cover letter from the supplied job
  description and verified candidate profile.
- Match the language used by the form question or job description.
- Use French for a French field or predominantly French job posting.
- Use English for an English field or predominantly English job posting.
- Connect the candidate's strongest relevant technologies, projects,
  professional experience, business experience, infrastructure work,
  language skills, and transferable experience to the employer's actual
  requirements.
- Mention only evidence available in the verified candidate profile.
- Do not invent employers, credentials, degrees completed, certifications,
  security clearance, technologies, achievements, or exact experience.
- Do not use placeholders such as [Company Name], [Hiring Manager],
  [Position], or [Your Name].
- Do not include a postal-address header.
- Do not include Markdown, headings, bullet points, or code formatting.
- Do not begin with generic phrases such as "I am writing to apply".
- Prefer a direct opening that identifies the candidate's relevant value.
- Keep the answer between 130 and 220 words unless the field clearly
  requests a shorter response.
- Use two to four short paragraphs.
- End professionally without adding fabricated contact details.
- Output only the text that should be inserted into the form.

For every professional-summary field:

- Generate a job-specific professional summary using the job description
  and verified candidate profile.
- Lead with the candidate's strongest relevant professional identity.
- Prioritize technologies and responsibilities present in the job posting.
- Include adjacent or transferable knowledge only when reasonably
  supported, and phrase it accurately.
- Keep the answer between 60 and 120 words unless the field specifies
  another limit.
- Use one concise paragraph.
- Do not use first-person greetings, a sign-off, Markdown, headings,
  placeholders, or bullet points.
- Output only the text that should be inserted into the form.

For role-motivation fields:

- Explain the fit between the role's real responsibilities and the
  candidate's verified experience.
- Refer to concrete requirements from the job description.
- Avoid unsupported enthusiasm, exaggerated praise, and generic statements
  that could apply to any employer.
- Keep the answer between 70 and 140 words unless the field requests a
  different length.
- Output only the answer to insert into the field.

The job description is the source of role and employer requirements.
The candidate profile is the source of candidate facts.

Never copy long passages from the job description. Synthesize them into
an original, natural response.

If a cover-letter, professional-summary, or motivation field is detected,
a supported answer may be generated when the candidate profile contains
enough relevant evidence, even though the exact prose was not previously
written in the profile.

Language proficiency rules:

The candidate language profile is authoritative.

Interpret the following levels:

- Native:
  Native or near-native proficiency.

- Fluent:
  Full professional proficiency in speaking, reading, and writing.

- Professional:
  Professional working proficiency.

- Intermediate:
  Conversational or limited professional proficiency.

- Basic:
  Elementary knowledge only.

For language dropdowns:

- French marked Fluent supports selecting:
  Fluent, Advanced, Professional proficiency, Bilingual,
  Full professional proficiency, or the closest equivalent.

- English marked Fluent supports selecting:
  Fluent, Advanced, Professional proficiency, Bilingual,
  Full professional proficiency, or the closest equivalent.

- Ukrainian marked Native supports selecting:
  Native, Mother tongue, Fluent, Bilingual,
  or the strongest equivalent option.

- Russian marked Fluent supports selecting:
  Fluent, Advanced, Professional proficiency,
  or the closest equivalent.

Never select options meaning:
- I do not speak this language
- Je ne parle pas cette langue
- No proficiency
- Beginner
- Basic

when the candidate profile states Fluent or Native.

For single-select language questions, return the exact matching option text.

If multiple strong options exist, prefer this order:
1. Native or Mother tongue, when the profile says Native
2. Fluent
3. Full professional proficiency
4. Advanced
5. Professional proficiency
6. Bilingual

Do not infer a language level from the job description.
Use only the verified candidate language profile.

Technology mastery ratings are on a 10-point scale.

Interpret them as follows:
- 9-10: expert or highly advanced
- 8-8.9: strong professional proficiency
- 7-7.9: solid working proficiency
- 6-6.9: intermediate familiarity
- below 6: limited or developing experience

A rating of 7/10 or higher supports answering Yes to whether the
candidate has meaningful experience with that technology.

A rating of 8/10 or higher supports strong positive wording.

A rating of 9/10 or higher supports describing the candidate as highly
proficient or advanced.

Ratings do not independently prove exact years of experience, but they
may be combined with total relevant experience, employment history,
projects, and closely related technologies.


Adjacent and transferable knowledge rules:

The candidate may have meaningful familiarity with a technology,
methodology, or platform that is not named explicitly when it is
closely adjacent to strongly supported experience.

Use these evidence classifications internally:

1. Direct experience
   The technology or methodology is explicitly listed in the candidate
   profile, employment history, projects, or mastery file.

2. Closely adjacent experience
   The candidate has strong experience with technologies that use the
   same core concepts, configuration patterns, responsibilities, or
   operating model.

3. Conceptual familiarity
   The candidate's broader engineering background makes knowledge of
   the concept reasonable, but direct hands-on use is not established.

4. Unsupported
   There is no sufficiently close evidence.

Examples of closely adjacent technology families:

- Traefik, NGINX, Caddy, HAProxy, Apache reverse proxy, ingress
  controllers, load balancers, TLS termination, and reverse-proxy
  servers share substantial concepts such as routing, host rules,
  certificates, upstream services, ports, headers, and proxies.

- Docker, container networking, reverse proxies, Kubernetes ingress,
  service discovery, and container orchestration are related, but
  experience with one does not automatically prove expert experience
  with every other member of the group.

- SQL Server, PostgreSQL, MySQL, Oracle, relational databases, SQL,
  schemas, joins, indexing, transactions, and stored procedures are
  closely related, while vendor-specific administration features may
  still require direct evidence.

- C#, .NET, ASP.NET, ASP.NET Core, Entity Framework, Web APIs, MVC,
  dependency injection, NuGet, and Microsoft enterprise development
  are closely related members of the same core stack.

- GitHub Actions, GitLab CI, Jenkins, Azure DevOps, CI/CD pipelines,
  build automation, deployment automation, and release workflows share
  transferable concepts.

- Ansible, Terraform, OpenTofu, infrastructure as code, configuration
  management, provisioning, and automation have transferable concepts,
  but they are not interchangeable for exact-years questions.

Software-delivery methodology rules:

- Demonstrated work with Jira, Scrum ceremonies, sprint planning,
  backlogs, iterative delivery, issue tracking, pull requests, CI/CD,
  and cross-functional development supports familiarity with Agile.

- Scrum experience supports familiarity with Kanban concepts such as
  boards, work-in-progress, workflow states, backlog prioritization,
  and continuous flow.

- General software-engineering education and enterprise project
  experience support conceptual familiarity with Waterfall and the
  software development life cycle.

- Do not claim that the candidate led, formally practiced, or has a
  specific number of years with a methodology unless direct evidence
  supports that statement.



Unsupported specialist-stack guard:

The following specialist technologies require direct evidence and must
never be inferred from general software-development experience:

- iOS
- Swift
- Objective-C
- Xcode
- UIKit
- SwiftUI
- Cocoa Touch
- native Apple mobile development

If none of these technologies appears in the verified candidate
profile, answer UNKNOWN to direct-experience questions involving them.

Do not convert C#, .NET, JavaScript, TypeScript, Angular, React, web
development, or general mobile familiarity into native iOS experience.

Strict direct-experience guard:

Questions asking whether the candidate has "experience with", "worked
with", "professional experience", "hands-on experience", or production
experience require direct evidence from at least one of these sources:

- the verified technology mastery profile
- verified employment history
- verified project or homelab evidence
- verified additional experience evidence

Adjacent technologies alone must not produce a Yes answer to a direct
experience question.

Adjacent knowledge may support Yes only for wording such as:

- familiar with
- knowledge of
- comfortable learning
- able to work with
- understands the concepts of
- transferable experience relevant to

Examples:

- Traefik experience may support Yes to "Are you familiar with NGINX?"
- Traefik experience must not support Yes to "Do you have professional
  NGINX experience?"
- General mobile or frontend experience must not support Yes to direct
  iOS, Swift, Objective-C, Xcode, or UIKit experience.
- Android knowledge must not be converted into iOS experience.
- JavaScript, React, Angular, or web development must not be converted
  into React Native or native iOS development unless those are directly
  present in the candidate profile.

For a binary direct-experience question:

- return Yes only when direct evidence exists
- return No only when the profile clearly establishes no experience
- otherwise return UNKNOWN and allow the application to be skipped

Never choose Yes merely because the skill appears in the job
description. The job description describes employer requirements, not
candidate experience.

Decision rules for adjacent knowledge:

- For a broad question such as "Are you familiar with NGINX?", closely
  adjacent reverse-proxy experience may support answering Yes.

- For "Do you have experience with NGINX?", closely adjacent experience
  may support Yes at assertiveness level 3 when the required concepts
  are substantially equivalent.

- For "Are you an NGINX expert?", return UNKNOWN or No unless NGINX is
  directly supported at a high level.

- For "How many years of professional NGINX experience do you have?",
  do not convert Traefik experience into exact NGINX years. Return
  UNKNOWN unless direct NGINX duration is available.

- For descriptive answers, clearly frame adjacent knowledge as
  transferable experience, working familiarity, or closely related
  experience rather than direct production experience.

- A closely adjacent inference may support Yes for familiarity,
  comfort, knowledge, or ability-to-work-with questions.

- A closely adjacent inference must not establish certifications,
  formal credentials, security clearance, employment dates, exact
  years, or vendor-specific expert status.

- When making an adjacent inference, explain the supporting relationship
  in the reason field.

For numeric years-of-experience questions:

- At assertiveness level 3, a technology rated 8/10 or higher may use a
  conservative portion of the candidate's total relevant technical
  experience when that technology is clearly part of the candidate's
  core stack or is directly supported by closely related technologies.

- The estimated technology-specific duration must never exceed the
  candidate's total relevant technical experience.

- For a core technology rated 9/10 or higher, use the candidate's total
  relevant technical experience rounded down conservatively.

- For a core technology rated 8-8.9/10, use approximately 80-90 percent
  of total relevant technical experience, rounded down conservatively.

- For a technology rated 7-7.9/10, do not derive years from mastery
  alone unless explicit dates or duration are also provided.

- Return a concise numeric value only when the form asks for years.

- Do not return UNKNOWN merely because exact start and end dates are
  absent when the candidate profile clearly establishes substantial,
  long-term experience with a core technology.

For high-risk factual questions, use only direct and unambiguous facts.

The following distinctions are mandatory:

- A bachelor's degree marked "in_progress" may be described
  as "Bachelor's degree in progress", "Bachelor's candidate",
  or selected as "Bachelor's" in a broad education-level
  dropdown.

- It must not be described as completed, awarded, or graduated
  when the question explicitly asks about completion.

- Handling confidential information is not equivalent to
  holding a formal government security clearance.

- A certification listed under certifications held may be
  claimed as held.

- A certification listed only as in progress or willing to
  obtain must not be claimed as currently held.

Never infer or invent:
- work authorization or future sponsorship requirements
- citizenship or immigration status
- security clearance
- criminal history
- disability or medical information
- certifications
- education
- years of experience unless the candidate information explicitly provides
  either the duration or clear start and end dates for professional use of
  the specific technology being asked about

When clear professional start and end dates are provided:
- calculate the duration conservatively
- return a whole number or decimal number only when the question requests years
- do not round upward
- if the technology-use period is ambiguous, return UNKNOWN

- salary expectations
- availability dates

Do not cite a missing job description as a reason for UNKNOWN when the
candidate information itself is sufficient.

When the available information does not clearly support an answer:
- set "answer" to "UNKNOWN"
- set "supported" to false
- use a confidence below 0.85

For a single-select question:
- "answer" must exactly equal one of the allowed options
- do not paraphrase an option
- do not return an option that is not listed

For text and textarea questions:
- answer only what was asked
- do not add unsupported claims
- keep the answer concise and application-ready

Return one valid JSON object and no other text:

{{
  "answer": "UNKNOWN",
  "confidence": 0.0,
  "supported": false,
  "reason": "Brief explanation"
}}

Question type:
{question_type}

Question:
{question}

Allowed options:
{options_json}

Candidate information:
{user_information_all or "No candidate information provided."}

Job description:
{job_description or "No job description provided."}
""".strip()

        raw_response = ai_completion(
            client,
            [{"role": "user", "content": prompt}],
            stream=False,
        )

        if not isinstance(raw_response, str):
            raise ValueError(
                "AI did not return a text response."
            )

        start = raw_response.find("{")
        end = raw_response.rfind("}")

        if start < 0 or end <= start:
            raise ValueError(
                "AI response did not contain a JSON object."
            )

        result = json.loads(raw_response[start:end + 1])

        if not isinstance(result, dict):
            raise ValueError(
                "AI response JSON was not an object."
            )

        answer = str(result.get("answer", "")).strip()

        try:
            confidence = float(result.get("confidence", 0))
        except (TypeError, ValueError):
            confidence = 0.0

        supported_value = result.get("supported", False)

        if isinstance(supported_value, bool):
            supported = supported_value
        else:
            supported = (
                str(supported_value).strip().lower() == "true"
            )

        reason = str(result.get("reason", "")).strip()

        return {
            "answer": answer,
            "confidence": confidence,
            "supported": supported,
            "reason": reason,
        }

    except Exception as error:
        ai_error_alert(
            "Error occurred while answering a structured "
            f"application question. {apiCheckInstructions}",
            error,
        )
        return None


def ai_gen_experience(
    client: OpenAI, 
    job_description: str, about_company: str, 
    required_skills: dict, user_experience: dict,
    stream: bool = stream_output
) -> dict | ValueError:
    pass



def ai_generate_resume(
    client: OpenAI, 
    job_description: str, about_company: str, required_skills: dict,
    stream: bool = stream_output
) -> dict | ValueError:
    '''
    Function to generate resume. Takes in user experience and template info from config.
    '''
    pass



def ai_generate_coverletter(
    client: OpenAI, 
    job_description: str, about_company: str, required_skills: dict,
    stream: bool = stream_output
) -> dict | ValueError:
    '''
    Function to generate resume. Takes in user experience and template info from config.
    '''
    pass



##< Evaluation Agents
def ai_evaluate_resume(
    client: OpenAI, 
    job_description: str, about_company: str, required_skills: dict,
    resume: str,
    stream: bool = stream_output
) -> dict | ValueError:
    pass



def ai_evaluate_resume(
    client: OpenAI, 
    job_description: str, about_company: str, required_skills: dict,
    resume: str,
    stream: bool = stream_output
) -> dict | ValueError:
    pass



def ai_check_job_relevance(
    client: OpenAI, 
    job_description: str, about_company: str,
    stream: bool = stream_output
) -> dict:
    pass
#>
