import json
from utils.openai_client import get_openai_client

def convert_txt_to_json():
    pass

def load_courses(filename: str):
    with open(filename, "r") as file:
        courses = file.read()
    
    return courses


def get_courses(user_prompt):
    
    client = get_openai_client()
    courses = load_courses(r"data/ece_curriculum_nitk.txt")

    system_prompt = f"""Your are a helpful assistant who selects the right courses based on requirements specified by the user. Given the user query select the matching courses from the list of available courses given below
                    
    Courses : {courses}
    
    Respond in json format as follows: 
    {{
        "matched_courses" : [<list of strings>] 
    }}  
    """

    messages = [
        {"role":"system", "content":system_prompt},
        {"role":"user", "content":user_prompt}
    ]
    
    response = client.chat.completions.create(
        messages=messages,
        temperature=0.1,
        model="gpt-3.5-turbo"
    )

    output = response.choices[0].message.content
    output = json.loads(output)

    return output['matched_courses']

if __name__ == '__main__':
    get_courses("Could you share courses related to VLSI?")