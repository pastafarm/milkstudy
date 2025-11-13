# PDF Quiz Bot

An intelligent quiz bot that extracts information from PDF textbooks and continuously quizzes you with AI-generated questions. Perfect for studying and retaining information from academic materials.

## Features

- **PDF Text Extraction**: Automatically extracts and processes text from any PDF textbook
- **AI-Powered Question Generation**: Uses OpenAI's GPT models to generate intelligent, contextual questions
- **Multiple Question Types**:
  - Multiple Choice (A/B/C/D)
  - True/False
  - Short Answer (with AI-based evaluation)
  - Fill-in-the-Blank
- **Adaptive Learning**: Questions are generated from different sections of your textbook
- **Real-time Feedback**: Immediate explanations for correct and incorrect answers
- **Progress Tracking**: Track your performance by question type and overall accuracy
- **Continuous Mode**: Keep quizzing until you decide to stop
- **Interactive CLI**: Beautiful colored terminal interface

## Requirements

- Python 3.7+
- OpenAI API key
- PDF textbook or study materials

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd milkstudy
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up your OpenAI API key:

Create a `.env` file in the project directory:
```bash
OPENAI_API_KEY=your-api-key-here
```

Or set it as an environment variable:
```bash
export OPENAI_API_KEY=your-api-key-here
```

## Usage

### Basic Usage

Run the quiz bot with a specific PDF:
```bash
python quiz_bot.py "path/to/your/textbook.pdf"
```

Or simply run it without arguments to select from PDFs in the current directory:
```bash
python quiz_bot.py
```

### Interactive Mode

When you start the quiz bot, you'll be prompted to:

1. **Select a PDF** (if not specified in command line)
2. **Choose difficulty level**:
   - Easy
   - Medium (default)
   - Hard
   - Custom (set your own parameters)
3. **Set questions per batch** (default: 5)

### During the Quiz

- **Answer questions**: Type your answer and press Enter
- **Skip a question**: Type `skip`
- **End the session**: Type `quit` or `exit`
- **Continue or stop**: After each batch, decide whether to continue

### Example Session

```
==============================================================
  PDF QUIZ BOT - Interactive Learning Assistant
==============================================================

Available PDF files:
  1. Consumer Behavior, 8e.pdf
  2. Quiz 3 Study Guide.pdf

Select a PDF (1-2): 1

Initializing Quiz Bot...
Extracting text from PDF: Consumer Behavior, 8e.pdf
Successfully loaded 789 pages
Created 394 text segments for quizzing

Quiz Settings:
1. Easy (5 questions/batch)
2. Medium (5 questions/batch) - Default
3. Hard (5 questions/batch)
4. Custom

Select difficulty (1-4, default 2): 2

 Quiz Session Started
Difficulty: Medium
Questions per batch: 5
Type 'quit' or 'exit' anytime to end the session
Type 'skip' to skip a question

==================================================
Batch 1
==================================================
Generating questions... (this may take a moment)

 Question 1/5
Type: Multiple Choice

What is the primary factor in consumer decision-making?

  A) Price
  B) Brand loyalty
  C) Product quality
  D) All of the above

Your answer (A/B/C/D or 'skip'): D

✓ Correct!
Explanation: Consumer decision-making is influenced by multiple factors...
```

## Project Structure

```
milkstudy/
├── quiz_bot.py           # Main application entry point
├── pdf_extractor.py      # PDF text extraction module
├── quiz_generator.py     # AI question generation module
├── requirements.txt      # Python dependencies
├── .env                  # API keys (create this file)
└── README.md            # This file
```

## Modules

### pdf_extractor.py

Handles PDF text extraction and processing:
- Extracts text from PDF files
- Splits content into manageable chunks
- Cleans and normalizes text
- Provides page-specific text retrieval
- Supports keyword searching

### quiz_generator.py

Generates and validates quiz questions using AI:
- Creates multiple choice questions
- Generates true/false statements
- Produces short answer questions
- Creates fill-in-the-blank questions
- Validates user answers
- Uses AI to evaluate short answer responses

### quiz_bot.py

Main interactive quiz application:
- Manages quiz sessions
- Displays questions with colored output
- Tracks user progress and statistics
- Provides real-time feedback
- Supports continuous learning mode

## Configuration

### Difficulty Levels

- **Easy**: Simpler questions focusing on basic concepts
- **Medium**: Balanced questions covering main topics
- **Hard**: Complex questions requiring deep understanding

### Customization

You can customize the quiz experience by modifying:

- `questions_per_batch`: Number of questions in each batch
- `chunk_size`: Size of text chunks for question generation (in pdf_extractor.py)
- `difficulty`: Question difficulty level
- Question types: Enable/disable specific question types

## Statistics Tracking

The bot tracks:
- Total questions asked
- Correct/incorrect answers
- Accuracy percentage
- Performance by question type

Statistics are displayed after each batch and at the end of your session.

## Tips for Best Results

1. **Use quality PDFs**: The bot works best with text-based PDFs (not scanned images)
2. **Study in batches**: Take breaks between batches for better retention
3. **Review explanations**: Always read the explanations, even when you're correct
4. **Mix question types**: Different question types test different aspects of understanding
5. **Adjust difficulty**: Start with easy and progress to harder questions

## Troubleshooting

### "No text could be extracted from the PDF"
- Ensure your PDF contains actual text (not just images)
- Try a different PDF or use OCR to convert image-based PDFs

### "OpenAI API key not found"
- Make sure you've created a `.env` file with your API key
- Or set the `OPENAI_API_KEY` environment variable

### Questions seem off-topic
- The bot generates questions from text chunks. Some chunks might be from headers, footers, or less relevant sections
- Continue to the next batch for better questions

### API errors
- Check your OpenAI API key is valid
- Ensure you have available credits in your OpenAI account
- Check your internet connection

## Cost Considerations

This bot uses OpenAI's API, which incurs costs based on usage:
- The bot uses `gpt-4o-mini` model for cost efficiency
- Approximate cost: $0.01-0.03 per batch of 5 questions (varies by text length)
- Monitor your usage in the OpenAI dashboard

## Future Enhancements

Potential improvements:
- [ ] Support for multiple PDFs simultaneously
- [ ] Question history and review mode
- [ ] Spaced repetition scheduling
- [ ] Export quiz results to CSV/JSON
- [ ] Web interface
- [ ] Support for other document formats (DOCX, TXT, etc.)
- [ ] Offline mode with pre-generated questions
- [ ] Voice input/output support

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Built with OpenAI's GPT models
- Uses PyPDF2 for PDF processing
- Colorama for terminal styling

## Support

If you encounter any issues or have questions:
1. Check the Troubleshooting section
2. Review the OpenAI API documentation
3. Open an issue in the repository

---

Happy studying! 📚✨
