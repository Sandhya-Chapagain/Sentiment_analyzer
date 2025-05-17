from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from app.database import Question, get_db, init_db


class Answer(BaseModel):
    id: int
    answer: str


class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    answer: str


app = FastAPI()

# Initialize the database with sample data
init_db()

# Dependency to get database session
db = next(get_db())


@app.get("/")
def read_root():
    return {"message": "Hello World! It's me Sandhya Chapagain. This is the assignment for the fusemachine AI Fellowship 2025. Welcome to the Quiz App!"}


@app.get("/quiz")
def read_quiz():
    questions = db.query(Question).all()

    ques_without_ans = [
        {
            "id": q.id,
            "question": q.question,
            "options": q.options
        }
        for q in questions
    ]

    return {
        "quiz": ques_without_ans,
        "message": "Quiz data retrieved successfully!"
    }


@app.post("/quiz")
def create_quiz(question: QuizQuestion):
    db = next(get_db())
    db_question = Question(**question.model_dump())
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return {
        "message": "Quiz question created successfully!",
        "question": db_question
    }


@app.post("/quiz/submit")
def submit_quiz(answers: List[Answer]):
    correct_answers = 0

    questions = db.query(Question).all()
    for answer in answers:
        question = next((q for q in questions if q.id == answer.id), None)
        if not question:
            raise HTTPException(
                status_code=400,
                detail=f"Question with id {answer.id} not found"
            )

        if question.answer.lower() == answer.answer.lower():
            correct_answers += 1

    total_questions = db.query(Question).count()
    return {
        "message": "Quiz submitted successfully!",
        "correct_answers": correct_answers,
        "total_questions": total_questions
    }
