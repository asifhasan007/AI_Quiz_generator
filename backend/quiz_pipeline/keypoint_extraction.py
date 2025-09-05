import spacy
from transformers import pipeline
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer, util
def extract_keypoints_improved(transcribed_text, num_key_points=20):
    try:
        question_generator = pipeline("text2text-generation", model="mrm8488/t5-base-finetuned-question-generation-ap")
        answer_extractor = pipeline("question-answering", model="deepset/roberta-large-squad2")
        fact_synthesizer = pipeline("text2text-generation", model="google/flan-t5-large")

        kw_model = KeyBERT()
        similarity_model = SentenceTransformer('all-MiniLM-L6-v2')
        
    except Exception as e:
        print(f"Error loading AI models: {e}")
        return []
    nlp = spacy.load('en_core_web_sm')
    
    # clean and preprocess text
    cleaned_text = re.sub(r'\s+', ' ', transcribed_text).strip()
    doc = nlp(cleaned_text)
    
    # extract key phrases 
    keybert_keywords = kw_model.extract_keywords(
        cleaned_text, 
        keyphrase_ngram_range=(1, 3), 
        stop_words='english',
        top_n=30
    )
    
    # important noun phrases
    important_phrases = []
    for chunk in doc.noun_chunks:
        if len(chunk.text.split()) >= 2 and len(chunk.text) < 25:
            important_phrases.append(chunk.text.lower())
    
    # larger meaningful chunks
    sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.split()) > 5]

    # score sentences by TF-IDF
    vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    tfidf_matrix = vectorizer.fit_transform(sentences)
    sentence_scores = np.array(tfidf_matrix.sum(axis=1)).flatten()
    
    # top sentences
    top_sentence_indices = sentence_scores.argsort()[-min(30, len(sentences)):][::-1]
    important_sentences = [sentences[i] for i in top_sentence_indices]
    
    # generate questions from important only
    generated_questions = []
    print(f"--> Generating questions from {len(important_sentences)} important sentences...")
    
    for sentence in important_sentences[:15]:  
        try:
            if len(sentence.split()) > 10:  
                results = question_generator(
                    f"generate question: {sentence}",
                    max_length=64,
                    num_beams=5,
                    num_return_sequences=2,
                    early_stopping=True
                )
                generated_questions.extend([res['generated_text'].strip() for res in results])
        except Exception:
            continue
    
    # generate questions from key phrases
    for keyword, score in keybert_keywords[:10]:
        if score > 0.3:
            try:
                results = question_generator(
                    f"generate question about {keyword[0]}",
                    max_length=64,
                    num_beams=3,
                    num_return_sequences=1
                )
                generated_questions.extend([res['generated_text'].strip() for res in results])
            except Exception:
                continue
    
    # answer Extraction with higher threshold
    final_key_points = []
    seen_points = set()
    print(f"--> Extracting answers from {len(generated_questions)} questions...")

    question_priority = []
    for question in set(generated_questions):
        score = 0
        for keyword, kw_score in keybert_keywords:
            if keyword.lower() in question.lower():
                score += kw_score
        question_priority.append((question, score))
    
    # sort by importance
    question_priority.sort(key=lambda x: x[1], reverse=True)
    
    for question, _ in question_priority[:min(30, len(question_priority))]:
        try:
            qa_result = answer_extractor(question=question, context=cleaned_text)

            if qa_result['score'] > 0.55 and len(qa_result['answer'].split()) > 2:
                answer = qa_result['answer']
            
                # fact synthesis prompt
                prompt = f"""
                Create a clear, factual statement based on this information:
                Question: {question}
                Answer: {answer}

                Factual statement:
                """
                
                synthesis_result = fact_synthesizer(
                    prompt, 
                    max_length=120,
                    num_beams=3,
                    temperature=0.3
                )
                
                if synthesis_result:
                    fact = synthesis_result[0]['generated_text'].strip()
                    fact = fact.rstrip('?').strip()                    
                    if len(fact) > 15 and fact not in seen_points:
                        is_redundant = False
                        if final_key_points:
                            fact_embedding = similarity_model.encode([fact])
                            existing_embeddings = similarity_model.encode(final_key_points)
                            similarities = util.cos_sim(fact_embedding, existing_embeddings)[0]
                            if any(sim > 0.85 for sim in similarities):
                                is_redundant = True
                        
                        if not is_redundant:
                            final_key_points.append(fact)
                            seen_points.add(fact)
                            
                            if len(final_key_points) >= num_key_points:
                                break
                                
        except Exception as e:
            continue

    if len(final_key_points) < num_key_points:
        for sentence in important_sentences:
            if len(sentence.split()) > 8 and sentence not in seen_points:
                final_key_points.append(sentence)
                seen_points.add(sentence)
                if len(final_key_points) >= num_key_points:
                    break
    
    print(f"-> Successfully extracted {len(final_key_points)} key points.")
    return final_key_points[:num_key_points]