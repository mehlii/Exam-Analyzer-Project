"""Demo mode fixed exam data and AI feedback (English).

When `DEMO_MODE=1` (default ON), `upload_view` uses this module: regardless of
which file the user uploads, a fixed Beril Yildiz 8th grade practice exam result
and detailed study guide are displayed.

Exam: 8th Grade Practice Exam — 90 questions
(Turkish 20, Mathematics 20, Science 20, History 10, English 10, Religious 10).
Wrong answers: Turkish 8, Mathematics 7, Science 5, History 3, English 4, Religious 4.
"""

from datetime import date

DEMO_STUDENT_NAME = "Beril Yildiz"
DEMO_EXAM_DATE = date(2026, 5, 1)
DEMO_EXAM_NAME = "8th Grade Practice Exam"

# (Subject, Total, Correct, Wrong, Percent)
DEMO_SCORES = [
    ("Turkish", 20, 12, 8, 60.0),
    ("Mathematics", 20, 13, 7, 65.0),
    ("Science", 20, 15, 5, 75.0),
    ("Turkish History and Reforms", 10, 7, 3, 70.0),
    ("English", 10, 6, 4, 60.0),
    ("Religious Studies and Ethics", 10, 6, 4, 60.0),
]

DEMO_AVERAGE = round(sum(s[4] for s in DEMO_SCORES) / len(DEMO_SCORES), 2)
DEMO_MAX = max(s[4] for s in DEMO_SCORES)
DEMO_MIN = min(s[4] for s in DEMO_SCORES)

DEMO_PREDICTED = 412.5
DEMO_R2 = 0.81

DEMO_SUMMARY_JSON = {
    "average": DEMO_AVERAGE,
    "max_score": DEMO_MAX,
    "min_score": DEMO_MIN,
    "subject_averages": {s[0]: s[4] for s in DEMO_SCORES},
    "student_name": DEMO_STUDENT_NAME,
    "exam_name": DEMO_EXAM_NAME,
    "placement_score": 387.42,
    "net_total": 49.67,
    "rankings": {
        "class": 4,
        "school": 12,
        "district": 142,
        "city": 1850,
        "national": 18420,
    },
    "extraction_method": "demo",
    "ai_advice": {
        "source": "ai",
        "model": "gemini-2.5-flash-lite",
        "overall": (
            "Beril, on this practice exam your subject average is 65% — "
            "59 correct, 31 wrong, with a net of 49.67. Science (75%) is your "
            "strongest area; Turkish and English at 60% have the most room to "
            "grow. Mathematics with 7 wrong is the most critical point — if "
            "you tighten your algebra and geometry topics, your score can "
            "easily climb from 387 to 420+. You're 4th in your class — your "
            "potential is high; with planned study on the weak topics, you "
            "can break into the district top 50."
        ),
        "subjects": [
            {
                "subject": "Turkish",
                "commentary": (
                    "60% accuracy, 12 correct / 8 wrong. Your wrong answers "
                    "concentrate around paragraph comprehension and grammar. "
                    "Following a weekly plan on the topics below should push "
                    "your net to 16+ quickly."
                ),
                "weak_topics": [
                    "Paragraph Coherence",
                    "Word Meaning (Figurative/Technical)",
                    "Spelling Rules",
                    "Punctuation",
                    "Sentence Elements",
                    "Verbals",
                    "Expression Errors",
                    "Figures of Speech",
                ],
                "weak_topics_detailed": [
                    {
                        "topic": "Paragraph Coherence",
                        "study": (
                            "Solve 5 paragraph questions per day. For each "
                            "paragraph, identify the main idea, supporting "
                            "ideas, and best title. Pay special attention to "
                            "'find the sentence that breaks the flow' questions."
                        ),
                    },
                    {
                        "topic": "Word Meaning (Figurative/Technical)",
                        "study": (
                            "Learn the differences between literal, figurative, "
                            "technical, and connotative meanings. Use 10 new "
                            "words in sentences each day. Make flashcards for "
                            "idioms and proverbs; review morning and evening."
                        ),
                    },
                    {
                        "topic": "Spelling Rules",
                        "study": (
                            "Study the capitalization, compound words, and "
                            "common spelling sections of the official spelling "
                            "guide. Take a 20-question spelling test once a week."
                        ),
                    },
                    {
                        "topic": "Punctuation",
                        "study": (
                            "List the rules for commas, semicolons, and "
                            "apostrophes. For each question you miss, write "
                            "the rule in your notebook and review them all "
                            "at the weekend."
                        ),
                    },
                    {
                        "topic": "Sentence Elements",
                        "study": (
                            "Separate questions about predicates, subjects, "
                            "objects, indirect objects, and adverbials. In "
                            "every sentence, find the predicate first, then "
                            "ask who/what/whom/where in order."
                        ),
                    },
                    {
                        "topic": "Verbals",
                        "study": (
                            "Memorize the suffixes for noun-verbals, "
                            "adjective-verbals, and adverb-verbals. Write 5 "
                            "example sentences for each type."
                        ),
                    },
                    {
                        "topic": "Expression Errors",
                        "study": (
                            "Separate the types: redundant words, logical "
                            "errors, subject-verb disagreement. Solve 10 "
                            "questions of each type and underline the faulty word."
                        ),
                    },
                    {
                        "topic": "Figures of Speech",
                        "study": (
                            "Memorize definitions of simile, personification, "
                            "hyperbole, apostrophe, and antithesis. Reinforce "
                            "with poetry examples; take one figures-of-speech "
                            "test per week."
                        ),
                    },
                ],
                "priority": "high",
            },
            {
                "subject": "Mathematics",
                "commentary": (
                    "65% accuracy, 13 correct / 7 wrong. Your mistakes cluster "
                    "around algebra-based and geometry questions. Closing the "
                    "topic gaps in order will push your net to 16-17 — this "
                    "raises your overall score the most."
                ),
                "weak_topics": [
                    "Exponents",
                    "Square Roots",
                    "Data Analysis",
                    "Probability",
                    "Triangles and Pythagorean Theorem",
                    "Inequalities",
                    "Algebraic Expressions",
                ],
                "weak_topics_detailed": [
                    {
                        "topic": "Exponents",
                        "study": (
                            "Write a table of exponent rules (multiplication, "
                            "division, power of a power, negative exponents). "
                            "Solve 15 questions per day, focusing on negative "
                            "exponents and scientific notation."
                        ),
                    },
                    {
                        "topic": "Square Roots",
                        "study": (
                            "Memorize that addition/subtraction needs the same "
                            "root, and multiplication/division can be combined "
                            "under the root. Work through 20 solved examples, "
                            "then 30 practice problems."
                        ),
                    },
                    {
                        "topic": "Data Analysis",
                        "study": (
                            "Learn the definitions of mean, median, mode, and "
                            "range. Practice reading bar and pie charts — most "
                            "data questions ask you to read the chart first."
                        ),
                    },
                    {
                        "topic": "Probability",
                        "study": (
                            "Distinguish dependent vs. independent events. "
                            "Start with ball, dice, and card examples. Always "
                            "use P(A) = favorable / total; memorize the "
                            "multiplication and addition rules."
                        ),
                    },
                    {
                        "topic": "Triangles and Pythagorean Theorem",
                        "study": (
                            "Memorize the Pythagorean theorem (a² + b² = c²) "
                            "and special triples (3-4-5, 5-12-13, 8-15-17). "
                            "Also study angle-side relations and the triangle "
                            "inequality; do 10 questions per day."
                        ),
                    },
                    {
                        "topic": "Inequalities",
                        "study": (
                            "Always remember to flip the inequality sign when "
                            "multiplying by a negative. Show the solution on a "
                            "number line; practice double inequalities and "
                            "absolute-value inequalities."
                        ),
                    },
                    {
                        "topic": "Algebraic Expressions",
                        "study": (
                            "Memorize the identities ((a+b)², (a-b)², a²-b²). "
                            "Learn factoring techniques: common factor and "
                            "grouping. Solve 20 factoring problems daily."
                        ),
                    },
                ],
                "priority": "high",
            },
            {
                "subject": "Science",
                "commentary": (
                    "75% — your strongest subject! 15 correct / 5 wrong — "
                    "your topic command is solid. Just a few gaps; closing "
                    "them comfortably puts you at 18+ net."
                ),
                "weak_topics": [
                    "DNA and Genetic Code",
                    "Pressure",
                    "Acids and Bases",
                    "Seasons and Climate",
                    "Matter Cycles (Water Cycle)",
                ],
                "weak_topics_detailed": [
                    {
                        "topic": "DNA and Genetic Code",
                        "study": (
                            "Learn the relationships between DNA, RNA, gene, "
                            "chromosome, and nucleotide using a diagram. For "
                            "Mendelian genetics questions, draw Punnett "
                            "squares; separate dominant and recessive alleles."
                        ),
                    },
                    {
                        "topic": "Pressure",
                        "study": (
                            "Memorize the formulas for solid pressure (P=F/A), "
                            "liquid pressure (P=h·d·g), and gas pressure "
                            "separately. Practice unit conversions (Pascal, "
                            "N/m²) for each formula."
                        ),
                    },
                    {
                        "topic": "Acids and Bases",
                        "study": (
                            "Memorize everyday acid-base examples (lemon, "
                            "vinegar = acid; soap, detergent = base). Draw "
                            "the pH scale; reinforce neutralization reactions "
                            "with examples."
                        ),
                    },
                    {
                        "topic": "Seasons and Climate",
                        "study": (
                            "Diagram how Earth's axial tilt (23°27') and "
                            "orbit produce the seasons. Explain the equator-"
                            "to-pole temperature gradient using sunlight angle."
                        ),
                    },
                    {
                        "topic": "Matter Cycles (Water Cycle)",
                        "study": (
                            "Learn the sequence: evaporation → condensation "
                            "→ precipitation → runoff via a diagram. Compare "
                            "the carbon and nitrogen cycles too — cycle "
                            "diagrams are common on this exam."
                        ),
                    },
                ],
                "priority": "medium",
            },
            {
                "subject": "Turkish History and Reforms",
                "commentary": (
                    "70% — solid level. 7 correct / 3 wrong — focus especially "
                    "on treaty articles and the relationships between reforms."
                ),
                "weak_topics": [
                    "Treaty of Lausanne Articles",
                    "Abolition of the Sultanate",
                    "Republican Era Reforms",
                ],
                "weak_topics_detailed": [
                    {
                        "topic": "Treaty of Lausanne Articles",
                        "study": (
                            "Memorize Lausanne's resolved articles (borders, "
                            "capitulations, war reparations) and unresolved "
                            "ones (Straits, Hatay, Mosul, Foreign Schools) in "
                            "a two-column table. Write a one-sentence summary "
                            "for each article."
                        ),
                    },
                    {
                        "topic": "Abolition of the Sultanate",
                        "study": (
                            "Memorize the date (Nov 1, 1922) and reason "
                            "(double-delegation issue at Lausanne). Don't "
                            "confuse it with the abolition of the Caliphate "
                            "(Mar 3, 1924) — those are two separate events."
                        ),
                    },
                    {
                        "topic": "Republican Era Reforms",
                        "study": (
                            "Group reforms under 5 headings: political, "
                            "legal, education, economic, social-cultural. "
                            "Under each heading, write the date + event. "
                            "Review the chronological flow as flashcards."
                        ),
                    },
                ],
                "priority": "medium",
            },
            {
                "subject": "English",
                "commentary": (
                    "60% — improvable area. 6 correct / 4 wrong — you "
                    "struggle with vocabulary and reading questions. With 10 "
                    "new words and a short passage daily, you'll quickly "
                    "raise your net to 8+."
                ),
                "weak_topics": [
                    "Past Continuous Tense",
                    "Modal Verbs (must, should, have to)",
                    "Vocabulary — Tourism & Travel",
                    "Reading Comprehension",
                ],
                "weak_topics_detailed": [
                    {
                        "topic": "Past Continuous Tense",
                        "study": (
                            "Memorize the structure was/were + V-ing. Compare "
                            "with Past Simple: 'I was reading when she called.' "
                            "Form 10 sentences a day using when/while clauses."
                        ),
                    },
                    {
                        "topic": "Modal Verbs (must, should, have to)",
                        "study": (
                            "Distinguish must (obligation), should (advice), "
                            "have to (external obligation), can (ability), "
                            "may/might (possibility) with example sentences. "
                            "Practice their negative and question forms too."
                        ),
                    },
                    {
                        "topic": "Vocabulary — Tourism & Travel",
                        "study": (
                            "List exam-frequent travel words: booking, "
                            "accommodation, sightseeing, itinerary, luggage, "
                            "departure. Use each in a sentence; take a quiz "
                            "at the weekend."
                        ),
                    },
                    {
                        "topic": "Reading Comprehension",
                        "study": (
                            "Read one short passage (150-200 words) per day. "
                            "Read the questions first, then return to the "
                            "passage — underline keywords. Write unfamiliar "
                            "words in a notebook."
                        ),
                    },
                ],
                "priority": "high",
            },
            {
                "subject": "Religious Studies and Ethics",
                "commentary": (
                    "60% — improvable. 6 correct / 4 wrong. You have gaps "
                    "in conceptual topics and details about the Prophet's life."
                ),
                "weak_topics": [
                    "Fate and Predestination",
                    "Life of Prophet Muhammad (Farewell Sermon)",
                    "Zakat and Charity",
                    "Reason and Knowledge in the Quran",
                ],
                "weak_topics_detailed": [
                    {
                        "topic": "Fate and Predestination",
                        "study": (
                            "Distinguish fate (eternal divine knowledge) and "
                            "predestination (the realization of that "
                            "knowledge). Reinforce the will (free vs. divine "
                            "will) topic; learn causes and trust in God (tawakkul)."
                        ),
                    },
                    {
                        "topic": "Life of Prophet Muhammad (Farewell Sermon)",
                        "study": (
                            "Memorize the core messages of the Farewell "
                            "Sermon (equality, sanctity of life and property, "
                            "women's rights, ban on usury). Make flashcards "
                            "for the dates and outcomes of the battles of "
                            "Hijra, Badr, Uhud, and the Trench."
                        ),
                    },
                    {
                        "topic": "Zakat and Charity",
                        "study": (
                            "Memorize the difference between zakat "
                            "(obligatory, 2.5%, with a nisab threshold) and "
                            "voluntary charity (optional, no fixed amount or "
                            "time). List the 8 categories eligible for zakat."
                        ),
                    },
                    {
                        "topic": "Reason and Knowledge in the Quran",
                        "study": (
                            "Distinguish the definitions of reason, "
                            "knowledge, wisdom, and reflection. Memorize "
                            "examples from related verses (Surah Al-Alaq, "
                            "Al-Mujadila 11)."
                        ),
                    },
                ],
                "priority": "high",
            },
        ],
        "next_steps": [
            "Mathematics: 25 questions per day — exponents and square roots "
            "first, then geometry (triangles/Pythagoras). Aim for net 16-17 "
            "in 4 weeks.",
            "Spend 15 minutes per day on Turkish paragraph practice; do 2 "
            "paragraph tests (40 questions) per week. For spelling-"
            "punctuation, read one section of the official guide weekly.",
            "Make 10 vocabulary flashcards per day for English, review in "
            "the evening. Take 1 reading test (10 questions) at the weekend "
            "and log unfamiliar words.",
            "For Science and History, build concept maps: DNA-genetics, "
            "treaty articles, reforms. Take a subject mock each week and "
            "log your wrong topics in a study notebook.",
        ],
    },
}


def populate_demo_analysis(analysis):
    """Populates the given Analysis with fixed demo data and creates Score rows."""
    from analysis.models import Analysis as AnalysisModel, Score

    analysis.summary_json = DEMO_SUMMARY_JSON
    analysis.predicted_score = DEMO_PREDICTED
    analysis.r2_score = DEMO_R2
    analysis.student_name = DEMO_STUDENT_NAME
    analysis.status = AnalysisModel.Status.COMPLETED
    analysis.save()

    analysis.scores.all().delete()
    Score.objects.bulk_create([
        Score(
            analysis=analysis,
            subject=row[0],
            score=row[4],
            exam_date=DEMO_EXAM_DATE,
        )
        for row in DEMO_SCORES
    ])

    return analysis
