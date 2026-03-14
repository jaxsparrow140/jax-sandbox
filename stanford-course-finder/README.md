# Stanford Course Finder

A natural language interface for searching Stanford's course registry with AI-centric recommendations for GSB students.

## Features

- 🔍 **Natural Language Search** - Search courses using plain English queries
- 🤖 **AI Recommendations** - Get curated AI-centric course recommendations for GSB students
- 📚 **Schedule Management** - Add/remove courses to build your quarterly schedule
- 🎯 **GSB-Focused** - Prioritizes courses relevant to business students

## Installation

```bash
cd stanford-course-finder
python3 course_finder.py
```

## Usage

### Commands

- `search [query]` - Search for courses (e.g., "search machine learning")
- `recommend` - Get AI-centric course recommendations
- `add [subject] [number]` - Add course to schedule (e.g., "add CS 221")
- `remove [subject] [number]` - Remove course from schedule
- `schedule` - View your current schedule
- `help` - Show help message
- `quit` - Exit the app

### Examples

```
# Get AI course recommendations
recommend

# Search for AI business courses
search AI business

# Search for 3-unit CS courses
search CS 3 unit

# Add a course to your schedule
add CS 221

# View your schedule
schedule

# Remove a course
remove CS 221
```

## AI Course Recommendations

The app includes curated AI-centric courses perfect for GSB students:

### Top Recommendations:

1. **CS 231 - Generative AI** (AI Score: 0.99)
   - Deep dive into GANs, diffusion models, and LLMs
   - Applications in business and creativity

2. **MS 268 - AI Strategy and Innovation** (AI Score: 0.97)
   - Strategic implications of AI for business
   - Building AI-powered products and organizations

3. **CS 234 - Natural Language Processing with Deep Learning** (AI Score: 0.97)
   - Transformers, BERT, GPT models
   - Applications in business communication

4. **MS 292 - AI in Finance** (AI Score: 0.96)
   - ML applications in trading, risk assessment, portfolio optimization

5. **CS 230 - Applied Machine Learning** (AI Score: 0.96)
   - Hands-on ML implementation and deployment

## Course Data

The app includes Stanford courses from:
- Computer Science (CS)
- Management Science (MS) - GSB courses
- Statistics (STAT)

All courses are filtered and ranked by AI relevance for business students.

## Requirements

- Python 3.6+
- No external dependencies required

## License

MIT License - Feel free to modify and distribute.