import re
import google.generativeai as genai
from dotenv import load_dotenv
import os
def generate_quiz_with_gemini(key_points_text, num_mcq=5, num_tf=3):
    print("\n[3/4] Generating quiz using Google Gemini API...")
    # This line reads the .env file and loads the variables into the environment
    load_dotenv() 
    
    # This securely gets the API key from the environment.
    # It will return None if the key is not found.
    api_key = os.getenv("GEMINI_API_KEY") 
    
    if not api_key:
        print("Error: GEMINI_API_KEY not found. Make sure it is set in your .env file.")
        return None
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
    except Exception as e:
        print(f"Error configuring Gemini API: {e}")
        return None

    # The rest of the function remains exactly the same...
    # Inside your generate_quiz_with_gemini function, replace the old prompt with this one:

    prompt = f"""
    You are an expert quiz creator. Based on the key points provided, generate a quiz.

    **Formatting Rules:**
    1.  generate exactly {num_mcq} multiple-choice questions with four options (A, B, C, D) each.
    3.  The final line for each MCQ must be "ANSWER: <Letter>".
    4.  Next, create a second section with the exact header "--- TRUE/FALSE ---".
    5.  Under this header, generate exactly {num_tf} True/False questions.
    6.  The final line for each True/False question must be "ANSWER: True" or "ANSWER: False".
    7.  Do not add any other text, introductions, or conclusions.

    **KEY POINTS TO USE FOR THE QUIZ:**
    ---
    {key_points_text}
    ---
    """
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-lite')   #gemini-1.5-flash
        response = model.generate_content(prompt)
        quiz_text = response.text.strip()
        print("-> Successfully received quiz from Gemini.")
        return quiz_text

    except Exception as e:
        print(f"An error occurred while calling the Gemini API: {e}")
        return None

def parse_quiz_text(quiz_text):

    mcq_data = []
    tf_data = []

    if not isinstance(quiz_text, str) or not quiz_text.strip():
        print("Warning: Received empty or invalid text from the API.")
        return mcq_data, tf_data

    mcq_section_text = ""
    tf_section_text = ""
    
    # case-insensitive search for the headers
    tf_split = re.split(r'---\s*TRUE/FALSE\s*---', quiz_text, flags=re.IGNORECASE)
    
    if len(tf_split) == 2:
        mcq_section_text = tf_split[0]
        tf_section_text = tf_split[1]
    else:
        mcq_section_text = quiz_text

    mcq_blocks = re.split(r'\n\s*\n', mcq_section_text.strip())
    for block in mcq_blocks:
        lines = [line.strip() for line in block.strip().split('\n') if line.strip()]
        if len(lines) < 2 or "ANSWER:" not in lines[-1]:
            continue
            
        question_line = lines[0]
        answer_line = lines[-1]
        options = [line[3:] for line in lines[1:-1] if re.match(r"^[A-D]\.", line)]
        
        if len(options) == 4:
            try:
                answer_letter = answer_line.split("ANSWER:")[1].strip().upper()
                correct_answer_index = ord(answer_letter) - ord('A')
                correct_answer_text = options[correct_answer_index]
                mcq_data.append({
                    "type": "Multiple Choice", "question": question_line,
                    "options": options, "answer": correct_answer_text
                })
            except (IndexError, TypeError):
                continue


    tf_blocks = re.split(r'\n\s*\n', tf_section_text.strip())
    for block in tf_blocks:
        lines = [line.strip() for line in block.strip().split('\n') if line.strip()]
        if len(lines) < 2 or "ANSWER:" not in lines[-1]:
            continue
            
        question_line = lines[0]
        answer_line = lines[-1]
        answer = "True" if "True" in answer_line else "False"
        tf_data.append({"type": "True/False", "question": question_line, "answer": answer})

    print(f"-> Parsed {len(mcq_data)} MCQs and {len(tf_data)} True/False questions.")
    return mcq_data, tf_data
