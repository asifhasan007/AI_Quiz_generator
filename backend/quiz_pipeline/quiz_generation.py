import re
import google.generativeai as genai
from dotenv import load_dotenv
import os
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
def generate_quiz_with_gemini(key_points_text, num_mcq=5, num_tf=3):
    print("\n[3/4] Generating quiz using Google Gemini API...")
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found. Make sure it is set in your .env file.")
        return None
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        print(f"Error configuring Gemini API: {e}")
        return None

    prompt = f"""
    **CRITICAL RULE: Your entire output must ONLY contain the quiz questions. Do not include any headers, titles, or separators like "Multiple Choice Questions" or "--- TRUE/FALSE ---". The output must be a seamless list of questions.**

    Based on the key points below, generate a quiz with the following structure:
    1.  First, generate exactly {num_mcq} multiple-choice questions. After each questions must have four options (A. , B. , C. , D. ) and an answer line formatted as "ANSWER: [LETTER]".
    2.  Immediately after the last multiple-choice question, generate exactly {num_tf} True/False questions. Each must have an answer line formatted as "ANSWER: True" or "ANSWER: False".

    **KEY POINTS TO USE FOR THE QUIZ:**
    ---
    {key_points_text}
    ---
    """
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-lite')
        response = model.generate_content(prompt)
        quiz_text = response.text.strip()
        print("-> Successfully received quiz from Gemini.")
        print(quiz_text)
        return quiz_text.strip()

    except Exception as e:
        print(f"An error occurred while calling the Gemini API: {e}")
        return None

def parse_quiz_text(quiz_text):
    mcq_data = []
    tf_data = []

    if not isinstance(quiz_text, str) or not quiz_text.strip():
        print("Warning: Received empty or invalid text from the API.")
        return mcq_data, tf_data

    quiz_text = quiz_text.replace('\r\n', '\n').strip()
    quiz_text = re.sub(r'^.*(Multiple Choice Questions|---.*---):?\s*', '', quiz_text, flags=re.IGNORECASE | re.MULTILINE)
    quiz_text = quiz_text.strip()

    question_blocks = []
    current_block = []
    for line in quiz_text.split('\n'):
        stripped_line = line.strip()
        if not stripped_line:
            continue

        is_option = re.match(r'^[A-D]\.', stripped_line)
        is_answer = stripped_line.upper().startswith('ANSWER:')
        
        if not is_option and not is_answer:
            if current_block:
                question_blocks.append('\n'.join(current_block))
            current_block = [stripped_line]
        else:
            current_block.append(stripped_line)

    if current_block:
        question_blocks.append('\n'.join(current_block))

    for block in question_blocks:
        lines = [l.strip() for l in block.split('\n') if l.strip()]
        
        if len(lines) < 2:
            continue

        question = lines[0]
        answer_line = lines[-1]
        has_mcq_options = any(re.match(r'^[A-D]\.', line) for line in lines[1:-1])
        if has_mcq_options:
            options = [re.sub(r'^[A-D]\.\s*', '', opt) for opt in lines[1:-1] if re.match(r'^[A-D]\.', opt)]        
            if not options or not answer_line.upper().startswith("ANSWER:"):
                continue            
            try:
                answer_match = re.search(r'ANSWER:\s*([A-D])', answer_line, flags=re.IGNORECASE)
                if not answer_match:
                    continue
                
                answer_letter = answer_match.group(1).upper()
                answer_index = ord(answer_letter) - ord('A')

                if 0 <= answer_index < len(options):
                    answer_text = options[answer_index]
                    mcq_data.append({
                        "type": "Multiple Choice",
                        "question": question,
                        "options": options,
                        "answer": answer_text
                    })
            except (IndexError, TypeError):
                continue
        else:
            answer = None
            if "TRUE" in answer_line.upper():
                answer = "True"
            elif "FALSE" in answer_line.upper():
                answer = "False"
            
            if answer:
                tf_data.append({
                    "type": "True/False",
                    "question": question,
                    "answer": answer
                })

    print(f"-> Parsed {len(mcq_data)} MCQs and {len(tf_data)} True/False questions.")
    return mcq_data, tf_data