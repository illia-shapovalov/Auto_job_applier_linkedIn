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
