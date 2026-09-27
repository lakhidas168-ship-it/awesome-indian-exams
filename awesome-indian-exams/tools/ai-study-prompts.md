# AI study prompts

Paid apps sell AI mentors, doubt solving and answer evaluation. You can get most of it free with any free AI chat
(Gemini, ChatGPT, Claude, DeepSeek and others) and a good prompt. Copy a prompt, fill in the parts in `[brackets]`,
and paste it into the chat.

!!! warning "AI makes mistakes"
    AI can invent facts, numbers and dates with total confidence. Every prompt below asks it to name its source and
    to say when it is unsure. Check anything you will rely on against the official notification, NCERT or the
    official answer key. Never paste your Aadhaar, phone number or other personal details into a chat.

## 1. Doubt solver that sticks to the syllabus

```text
You are a patient tutor for the [EXAM] exam in India. Explain [TOPIC / PASTE YOUR DOUBT] at the level this exam
asks, in [English / Hindi / your language].
Rules:
- Base the explanation on the NCERT textbook or the exam's official syllabus. Name the book, class and chapter
  (or the syllabus section) you are using.
- If you are not sure about a fact, number or date, say "not sure, check the official source" instead of guessing.
- Use one simple everyday example.
- End with 3 exam-style practice questions, then their answers with one-line reasons.
```

## 2. UPSC Mains answer evaluator

```text
Act as a strict UPSC Civil Services Mains examiner. Evaluate my answer.
Question: [PASTE THE QUESTION]
Marks: [10 or 15]   Word limit: [150 or 250]
My answer: [PASTE YOUR ANSWER, or type it out if handwritten]

Score it out of the marks above and give feedback under these headings:
1. Demand of the question: did I address every part and follow the directive word (discuss, critically examine,
   analyse, comment, elaborate...)?
2. Introduction: relevant and short?
3. Body: structure, subheadings or points, and balance between dimensions (social, economic, political,
   environmental, ethical as relevant).
4. Substantiation: examples, data, reports, committees, judgments or constitutional articles. Mark anything I
   cited that you think is wrong, and say how to verify it.
5. Conclusion: forward-looking and balanced?
6. Word limit and presentation.
Then rewrite only my weakest paragraph to show the improvement. Do not write a full model answer.
```

## 3. Study plan from this list's modules

```text
I am preparing for [EXAM] on [EXAM DATE]. I can study [HOURS] hours a day. My strong areas: [..]. Weak areas: [..].
These are the shared modules the exam needs (from the Awesome Indian Exams study planner): [PASTE THE MODULE LIST].
Make a week-by-week plan:
- Weak modules first, while there is time. Previous-year questions of each module at the start of that module.
- One full mock every week from the halfway point, and the last 15% of the time for revision and mocks only.
- A daily routine that fits my hours, with one day a week lighter.
Keep it realistic; list what to drop first if I fall behind.
```

## 4. Previous-year paper analyst

```text
Here are questions from the official [EXAM] [YEAR] paper: [PASTE QUESTIONS, OR ATTACH THE OFFICIAL PDF].
For each question, give: subject, topic, and difficulty (easy / medium / hard).
Then give a table of topics by number of questions, and the 5 topics I should prepare first.
Do not solve the questions unless I ask. If a question's topic is ambiguous, say so.
```

## 5. Flashcard maker (in this list's deck format)

```text
Make 20 flashcards from the text below, one fact per card, for revision for [EXAM].
Output only JSON in this format:
{"id": "[deck-id]", "title": "[deck title]", "source": {"title": "[SOURCE NAME]", "url": "[OFFICIAL SOURCE URL]"},
 "cards": [{"id": "[short-unique-id]", "front": "question", "back": "answer"}]}
Only use facts that are in the text. Do not add anything from memory.
Text: [PASTE FROM NCERT, AN OFFICIAL REPORT OR YOUR OWN NOTES]
```

Check every card against the source before you use it.

## 6. Mistake coach after a mock

```text
I took a [EXAM] mock. Here are the questions I got wrong or skipped, with my answer and the correct answer:
[PASTE]
For each one, classify the reason: concept gap, silly mistake, time pressure, or guess. Then give me:
- the 3 concepts to revise first, with the NCERT chapter or syllabus topic for each;
- one rule to follow in the next mock (for example, when to skip or guess, given the negative marking).
```

## 7. Current affairs from an official release

```text
Here is an official Press Information Bureau release: [PASTE THE TEXT OR THE pib.gov.in LINK].
1. Summarise it in 5 bullet points for [EXAM] preparation.
2. Link it to the static syllabus: which topic of polity, economy, environment, science or history does it connect to?
3. Write 3 exam-style MCQs using only facts from this release, with answers.
```

## 8. Interview practice

```text
Act as a board for the [UPSC personality test / PSU interview / bank interview]. My background: [DEGREE, HOME
STATE, HOBBIES, WORK EXPERIENCE]. Ask me one question at a time, the way a real board would, and wait for my
answer. After 8 questions, give feedback on content, honesty, balance and composure.
```

Have a prompt that helped you? Share it in a pull request so every aspirant gets it.
