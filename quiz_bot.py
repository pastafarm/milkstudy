#!/usr/bin/env python3
"""
PDF Quiz Bot - Interactive Quiz Application
Continuously quizzes users with questions generated from PDF textbooks.
"""

import os
import sys
import random
import time
from typing import List, Dict, Optional
from colorama import init, Fore, Back, Style

from pdf_extractor import PDFExtractor
from quiz_generator import QuizGenerator


# Initialize colorama for cross-platform colored output
init(autoreset=True)


class QuizBot:
    """Main quiz bot application."""

    def __init__(self, pdf_path: str, api_key: Optional[str] = None):
        """
        Initialize the quiz bot.

        Args:
            pdf_path: Path to the PDF file
            api_key: Optional OpenAI API key
        """
        self.pdf_path = pdf_path
        self.pdf_extractor = PDFExtractor(pdf_path)
        self.quiz_generator = QuizGenerator(api_key)

        self.text_chunks = []
        self.current_chunk_index = 0
        self.questions_cache = []

        # Statistics
        self.total_questions = 0
        self.correct_answers = 0
        self.questions_by_type = {
            'multiple_choice': {'total': 0, 'correct': 0},
            'true_false': {'total': 0, 'correct': 0},
            'short_answer': {'total': 0, 'correct': 0},
            'fill_blank': {'total': 0, 'correct': 0}
        }

    def initialize(self):
        """Initialize the bot by extracting text from PDF."""
        print(f"{Fore.CYAN}Initializing Quiz Bot...")
        print(f"{Fore.CYAN}Extracting text from PDF: {os.path.basename(self.pdf_path)}")

        try:
            self.text_chunks = self.pdf_extractor.get_text_chunks(chunk_size=2000, overlap=200)
            total_pages = self.pdf_extractor.get_total_pages()

            print(f"{Fore.GREEN}Successfully loaded {total_pages} pages")
            print(f"{Fore.GREEN}Created {len(self.text_chunks)} text segments for quizzing\n")

            if not self.text_chunks:
                raise ValueError("No text could be extracted from the PDF")

            return True

        except Exception as e:
            print(f"{Fore.RED}Error initializing: {str(e)}")
            return False

    def generate_questions_batch(self, num_questions: int = 5, difficulty: str = 'medium') -> List[Dict]:
        """
        Generate a batch of questions from the current text chunk.

        Args:
            num_questions: Number of questions to generate
            difficulty: Difficulty level

        Returns:
            List of questions
        """
        if self.current_chunk_index >= len(self.text_chunks):
            self.current_chunk_index = 0  # Loop back to start

        chunk = self.text_chunks[self.current_chunk_index]
        self.current_chunk_index += 1

        print(f"{Fore.YELLOW}Generating questions... (this may take a moment)")

        try:
            questions = self.quiz_generator.generate_questions(
                chunk,
                num_questions=num_questions,
                difficulty=difficulty
            )

            if not questions:
                print(f"{Fore.RED}Could not generate questions. Trying another section...")
                return self.generate_questions_batch(num_questions, difficulty)

            return questions

        except Exception as e:
            print(f"{Fore.RED}Error generating questions: {str(e)}")
            return []

    def display_question(self, question: Dict, question_num: int, total: int):
        """Display a question to the user."""
        print(f"\n{Back.BLUE}{Fore.WHITE} Question {question_num}/{total} {Style.RESET_ALL}")
        print(f"{Fore.CYAN}Type: {question['type'].replace('_', ' ').title()}")
        print(f"\n{Fore.WHITE}{Style.BRIGHT}{question['question']}\n")

        if question['type'] == 'multiple_choice':
            for option in question['options']:
                print(f"  {option}")
        elif question['type'] == 'true_false':
            print(f"  {Fore.GREEN}True (T) {Fore.RED}or False (F)?")
        elif question['type'] == 'fill_blank':
            print(f"  {Fore.YELLOW}Fill in the blank")

    def get_user_answer(self, question: Dict) -> str:
        """Get answer from user with appropriate prompt."""
        q_type = question['type']

        if q_type == 'multiple_choice':
            prompt = f"{Fore.YELLOW}Your answer (A/B/C/D or 'skip'): "
        elif q_type == 'true_false':
            prompt = f"{Fore.YELLOW}Your answer (T/F or 'skip'): "
        else:
            prompt = f"{Fore.YELLOW}Your answer (or 'skip'): "

        while True:
            try:
                answer = input(prompt).strip()
                if answer.lower() == 'quit' or answer.lower() == 'exit':
                    return 'QUIT'
                elif answer.lower() == 'skip':
                    return 'SKIP'
                elif answer:
                    return answer
                else:
                    print(f"{Fore.RED}Please enter an answer or 'skip'")
            except KeyboardInterrupt:
                return 'QUIT'

    def display_result(self, result: Dict):
        """Display the result of an answer."""
        if result['correct']:
            print(f"\n{Fore.GREEN}{Style.BRIGHT}✓ Correct!")
        else:
            print(f"\n{Fore.RED}{Style.BRIGHT}✗ Incorrect")

        if 'explanation' in result and result['explanation']:
            print(f"{Fore.CYAN}Explanation: {result['explanation']}")

        if 'correct_answer' in result:
            print(f"{Fore.WHITE}Correct answer: {Fore.GREEN}{result['correct_answer']}")

        if 'feedback' in result:
            print(f"{Fore.CYAN}Feedback: {result['feedback']}")
            if 'score' in result:
                print(f"{Fore.YELLOW}Score: {result['score']}/100")

    def update_statistics(self, question: Dict, result: Dict):
        """Update quiz statistics."""
        q_type = question['type']
        self.total_questions += 1
        self.questions_by_type[q_type]['total'] += 1

        if result['correct']:
            self.correct_answers += 1
            self.questions_by_type[q_type]['correct'] += 1

    def display_statistics(self):
        """Display current statistics."""
        if self.total_questions == 0:
            return

        percentage = (self.correct_answers / self.total_questions) * 100

        print(f"\n{Back.CYAN}{Fore.BLACK} Session Statistics {Style.RESET_ALL}")
        print(f"{Fore.WHITE}Total Questions: {self.total_questions}")
        print(f"{Fore.GREEN}Correct: {self.correct_answers}")
        print(f"{Fore.RED}Incorrect: {self.total_questions - self.correct_answers}")
        print(f"{Fore.YELLOW}Accuracy: {percentage:.1f}%\n")

        print(f"{Fore.CYAN}Breakdown by Type:")
        for q_type, stats in self.questions_by_type.items():
            if stats['total'] > 0:
                type_percentage = (stats['correct'] / stats['total']) * 100
                type_name = q_type.replace('_', ' ').title()
                print(f"  {type_name}: {stats['correct']}/{stats['total']} ({type_percentage:.1f}%)")

    def run_quiz_session(
        self,
        questions_per_batch: int = 5,
        continuous: bool = True,
        difficulty: str = 'medium'
    ):
        """
        Run a quiz session.

        Args:
            questions_per_batch: Number of questions per batch
            continuous: Whether to continue generating new questions
            difficulty: Difficulty level
        """
        print(f"\n{Back.GREEN}{Fore.BLACK} Quiz Session Started {Style.RESET_ALL}")
        print(f"{Fore.CYAN}Difficulty: {difficulty.title()}")
        print(f"{Fore.CYAN}Questions per batch: {questions_per_batch}")
        print(f"{Fore.YELLOW}Type 'quit' or 'exit' anytime to end the session")
        print(f"{Fore.YELLOW}Type 'skip' to skip a question\n")

        batch_num = 1

        try:
            while True:
                print(f"\n{Fore.MAGENTA}{'='*50}")
                print(f"{Fore.MAGENTA}Batch {batch_num}")
                print(f"{Fore.MAGENTA}{'='*50}")

                questions = self.generate_questions_batch(questions_per_batch, difficulty)

                if not questions:
                    print(f"{Fore.RED}Could not generate questions. Ending session.")
                    break

                for i, question in enumerate(questions, 1):
                    self.display_question(question, i, len(questions))

                    answer = self.get_user_answer(question)

                    if answer == 'QUIT':
                        print(f"\n{Fore.YELLOW}Ending quiz session...")
                        self.display_statistics()
                        return

                    if answer == 'SKIP':
                        print(f"{Fore.YELLOW}Skipped")
                        continue

                    result = self.quiz_generator.validate_answer(question, answer)
                    self.display_result(result)
                    self.update_statistics(question, result)

                    time.sleep(0.5)

                # Display stats after each batch
                self.display_statistics()

                if not continuous:
                    break

                # Ask if user wants to continue
                print(f"\n{Fore.YELLOW}Continue to next batch? (Y/n): ", end='')
                response = input().strip().lower()

                if response in ['n', 'no', 'quit', 'exit']:
                    print(f"\n{Fore.YELLOW}Ending quiz session...")
                    self.display_statistics()
                    break

                batch_num += 1

        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}Quiz session interrupted.")
            self.display_statistics()


def main():
    """Main entry point for the quiz bot."""
    print(f"{Fore.CYAN}{Style.BRIGHT}")
    print("="*60)
    print("  PDF QUIZ BOT - Interactive Learning Assistant")
    print("="*60)
    print(Style.RESET_ALL)

    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print(f"{Fore.RED}Error: OPENAI_API_KEY environment variable not set")
        print(f"{Fore.YELLOW}Please create a .env file with your OpenAI API key:")
        print(f"{Fore.WHITE}  OPENAI_API_KEY=your-api-key-here")
        sys.exit(1)

    # Get PDF path from command line or use default
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        # Look for PDFs in current directory
        pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]

        if not pdf_files:
            print(f"{Fore.RED}No PDF files found in current directory")
            print(f"{Fore.YELLOW}Usage: python quiz_bot.py <path-to-pdf>")
            sys.exit(1)

        print(f"{Fore.CYAN}Available PDF files:")
        for i, pdf in enumerate(pdf_files, 1):
            print(f"  {i}. {pdf}")

        while True:
            try:
                choice = input(f"\n{Fore.YELLOW}Select a PDF (1-{len(pdf_files)}): ").strip()
                idx = int(choice) - 1
                if 0 <= idx < len(pdf_files):
                    pdf_path = pdf_files[idx]
                    break
                else:
                    print(f"{Fore.RED}Invalid selection")
            except (ValueError, KeyboardInterrupt):
                print(f"\n{Fore.RED}Invalid input")
                sys.exit(1)

    # Initialize bot
    bot = QuizBot(pdf_path)

    if not bot.initialize():
        sys.exit(1)

    # Quiz settings
    print(f"\n{Fore.CYAN}Quiz Settings:")
    print(f"{Fore.WHITE}1. Easy (5 questions/batch)")
    print(f"{Fore.WHITE}2. Medium (5 questions/batch) - Default")
    print(f"{Fore.WHITE}3. Hard (5 questions/batch)")
    print(f"{Fore.WHITE}4. Custom")

    try:
        choice = input(f"\n{Fore.YELLOW}Select difficulty (1-4, default 2): ").strip() or '2'

        if choice == '1':
            difficulty = 'easy'
            questions_per_batch = 5
        elif choice == '3':
            difficulty = 'hard'
            questions_per_batch = 5
        elif choice == '4':
            difficulty = input(f"{Fore.YELLOW}Difficulty (easy/medium/hard): ").strip() or 'medium'
            questions_per_batch = int(input(f"{Fore.YELLOW}Questions per batch: ").strip() or '5')
        else:
            difficulty = 'medium'
            questions_per_batch = 5

    except (ValueError, KeyboardInterrupt):
        print(f"\n{Fore.YELLOW}Using default settings (medium, 5 questions/batch)")
        difficulty = 'medium'
        questions_per_batch = 5

    # Start quiz
    bot.run_quiz_session(
        questions_per_batch=questions_per_batch,
        continuous=True,
        difficulty=difficulty
    )

    print(f"\n{Fore.GREEN}Thank you for using PDF Quiz Bot!")
    print(f"{Fore.CYAN}Keep learning! 📚")


if __name__ == "__main__":
    main()
