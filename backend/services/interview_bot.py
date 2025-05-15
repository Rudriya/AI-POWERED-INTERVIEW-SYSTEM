from transformers import pipeline

# ✅ Light model that works well for text-generation + instruction
qa_pipeline = pipeline("text2text-generation", model="google/flan-t5-base")

def generate_questions(topic="Python", count=3):
    prompt = f"List {count} beginner-level interview questions on the topic '{topic}'."
    result = qa_pipeline(prompt, max_length=256, do_sample=False)
    
    # Extract questions from generated text
    questions_raw = result[0]["generated_text"]
    questions = [q.strip("- ").strip() for q in questions_raw.strip().split("\n") if q.strip()]
    
    return questions[:count]

def evaluate_answer(question, answer):
    prompt = (
        f"Evaluate this answer to the interview question.\n\n"
        f"Question: {question}\nAnswer: {answer}\n\n"
        f"Give a score from 0 to 10 with brief feedback."
    )
    result = qa_pipeline(prompt, max_length=256, do_sample=False)
    return result[0]["generated_text"]
