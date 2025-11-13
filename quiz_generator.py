"""
Quiz Question Generator Module
Generates various types of quiz questions from text content using AI.
"""

import os
import json
import random
from typing import List, Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv


class QuizGenerator:
    """Generates quiz questions from text content using OpenAI API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the quiz generator.

        Args:
            api_key: OpenAI API key (if not provided, loads from environment)
        """
        load_dotenv()
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')

        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable "
                "or pass it to the constructor."
            )

        self.client = OpenAI(api_key=self.api_key)
        self.question_types = ['multiple_choice', 'true_false', 'short_answer', 'fill_blank']

    def generate_questions(
        self,
        text_chunk: str,
        num_questions: int = 5,
        question_types: Optional[List[str]] = None,
        difficulty: str = 'medium'
    ) -> List[Dict]:
        """
        Generate quiz questions from a text chunk.

        Args:
            text_chunk: Text content to generate questions from
            num_questions: Number of questions to generate
            question_types: Types of questions to generate
            difficulty: Difficulty level ('easy', 'medium', 'hard')

        Returns:
            List of question dictionaries
        """
        if question_types is None:
            question_types = self.question_types

        questions = []
        questions_per_type = max(1, num_questions // len(question_types))

        for q_type in question_types:
            if len(questions) >= num_questions:
                break

            try:
                if q_type == 'multiple_choice':
                    qs = self._generate_multiple_choice(text_chunk, questions_per_type, difficulty)
                elif q_type == 'true_false':
                    qs = self._generate_true_false(text_chunk, questions_per_type, difficulty)
                elif q_type == 'short_answer':
                    qs = self._generate_short_answer(text_chunk, questions_per_type, difficulty)
                elif q_type == 'fill_blank':
                    qs = self._generate_fill_blank(text_chunk, questions_per_type, difficulty)
                else:
                    continue

                questions.extend(qs)
            except Exception as e:
                print(f"Error generating {q_type} questions: {str(e)}")
                continue

        # Shuffle and limit to requested number
        random.shuffle(questions)
        return questions[:num_questions]

    def _generate_multiple_choice(
        self,
        text: str,
        num_questions: int,
        difficulty: str
    ) -> List[Dict]:
        """Generate multiple choice questions."""
        prompt = f"""Based on the following text, generate {num_questions} multiple choice questions at {difficulty} difficulty level.

Text:
{text[:3000]}

Return your response as a JSON array with this exact format:
[
  {{
    "question": "What is...",
    "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
    "correct_answer": "A",
    "explanation": "Brief explanation of why this is correct"
  }}
]

Make sure the questions are diverse and test understanding of key concepts."""

        return self._call_openai_api(prompt, 'multiple_choice')

    def _generate_true_false(
        self,
        text: str,
        num_questions: int,
        difficulty: str
    ) -> List[Dict]:
        """Generate true/false questions."""
        prompt = f"""Based on the following text, generate {num_questions} true/false questions at {difficulty} difficulty level.

Text:
{text[:3000]}

Return your response as a JSON array with this exact format:
[
  {{
    "question": "Statement to evaluate...",
    "correct_answer": "True",
    "explanation": "Brief explanation of why this is true/false"
  }}
]

Include a mix of true and false statements."""

        return self._call_openai_api(prompt, 'true_false')

    def _generate_short_answer(
        self,
        text: str,
        num_questions: int,
        difficulty: str
    ) -> List[Dict]:
        """Generate short answer questions."""
        prompt = f"""Based on the following text, generate {num_questions} short answer questions at {difficulty} difficulty level.

Text:
{text[:3000]}

Return your response as a JSON array with this exact format:
[
  {{
    "question": "What...",
    "sample_answer": "Sample correct answer",
    "key_points": ["Key point 1", "Key point 2"]
  }}
]

Questions should require 1-3 sentence answers."""

        return self._call_openai_api(prompt, 'short_answer')

    def _generate_fill_blank(
        self,
        text: str,
        num_questions: int,
        difficulty: str
    ) -> List[Dict]:
        """Generate fill-in-the-blank questions."""
        prompt = f"""Based on the following text, generate {num_questions} fill-in-the-blank questions at {difficulty} difficulty level.

Text:
{text[:3000]}

Return your response as a JSON array with this exact format:
[
  {{
    "question": "The process of _____ involves...",
    "correct_answer": "the missing word or phrase",
    "explanation": "Brief explanation"
  }}
]

Use _____ to indicate the blank."""

        return self._call_openai_api(prompt, 'fill_blank')

    def _call_openai_api(self, prompt: str, question_type: str) -> List[Dict]:
        """
        Call OpenAI API and parse response.

        Args:
            prompt: The prompt to send
            question_type: Type of question being generated

        Returns:
            List of question dictionaries
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that generates educational quiz questions. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )

            content = response.choices[0].message.content.strip()

            # Try to extract JSON from the response
            # Sometimes the API wraps JSON in markdown code blocks
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
                content = content.strip()

            questions = json.loads(content)

            # Add question type to each question
            for q in questions:
                q['type'] = question_type

            return questions

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {str(e)}")
            print(f"Response content: {content}")
            return []
        except Exception as e:
            print(f"Error calling OpenAI API: {str(e)}")
            return []

    def validate_answer(
        self,
        question: Dict,
        user_answer: str
    ) -> Dict[str, any]:
        """
        Validate a user's answer to a question.

        Args:
            question: The question dictionary
            user_answer: The user's answer

        Returns:
            Dictionary with validation results
        """
        q_type = question['type']
        user_answer = user_answer.strip()

        if q_type == 'multiple_choice':
            correct = user_answer.upper() == question['correct_answer'].upper()
            return {
                'correct': correct,
                'user_answer': user_answer,
                'correct_answer': question['correct_answer'],
                'explanation': question.get('explanation', '')
            }

        elif q_type == 'true_false':
            correct = user_answer.lower() in ['true', 't', 'yes', 'y'] and question['correct_answer'].lower() == 'true' or \
                      user_answer.lower() in ['false', 'f', 'no', 'n'] and question['correct_answer'].lower() == 'false'
            return {
                'correct': correct,
                'user_answer': user_answer,
                'correct_answer': question['correct_answer'],
                'explanation': question.get('explanation', '')
            }

        elif q_type == 'short_answer':
            # For short answer, we use AI to evaluate
            return self._validate_short_answer(question, user_answer)

        elif q_type == 'fill_blank':
            correct_lower = question['correct_answer'].lower().strip()
            user_lower = user_answer.lower().strip()
            correct = correct_lower == user_lower or correct_lower in user_lower

            return {
                'correct': correct,
                'user_answer': user_answer,
                'correct_answer': question['correct_answer'],
                'explanation': question.get('explanation', '')
            }

        return {'correct': False, 'user_answer': user_answer}

    def _validate_short_answer(self, question: Dict, user_answer: str) -> Dict:
        """Use AI to validate short answer questions."""
        prompt = f"""Evaluate if this answer is correct for the given question.

Question: {question['question']}
Sample Answer: {question['sample_answer']}
Key Points: {', '.join(question.get('key_points', []))}
User Answer: {user_answer}

Respond with JSON in this format:
{{
  "correct": true/false,
  "score": 0-100,
  "feedback": "Brief feedback on the answer"
}}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an educational assistant evaluating student answers. Be fair but thorough."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )

            content = response.choices[0].message.content.strip()
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
                content = content.strip()

            result = json.loads(content)
            result['user_answer'] = user_answer
            result['sample_answer'] = question['sample_answer']
            return result

        except Exception as e:
            print(f"Error validating short answer: {str(e)}")
            return {
                'correct': False,
                'user_answer': user_answer,
                'sample_answer': question['sample_answer'],
                'feedback': 'Could not evaluate answer automatically.'
            }
