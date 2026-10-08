import re

from src.agents.roles import can_call
from src.config.constants import (
    DEFAULT_ROLE, STARTER_QUESTIONS, SUGGESTION_COUNT, SUGGESTION_POOL, SUGGESTION_TOPIC_KEYWORDS,
)

TOPIC_REGEXES = {topic: re.compile(pattern, re.IGNORECASE) for topic, pattern in SUGGESTION_TOPIC_KEYWORDS.items()}


def topics_in(questions):
    found = []
    for question in questions:
        for topic, regex in TOPIC_REGEXES.items():
            if topic not in found and regex.search(question):
                found.append(topic)
    return found


def suggest_questions(role, answered_questions, count=SUGGESTION_COUNT):
    starters = STARTER_QUESTIONS.get(role, STARTER_QUESTIONS[DEFAULT_ROLE])
    if not answered_questions:
        return starters[:count]

    already_asked = {question.strip().lower() for question in answered_questions}
    history_topics = topics_in(answered_questions)
    pool = [item for item in SUGGESTION_POOL if can_call(role, item[2]) and item[3].lower() not in already_asked]
    start = len(answered_questions) % len(pool) if pool else 0
    pool = pool[start:] + pool[:start]

    suggestions, used_kinds, used_topics = [], set(), set()
    while pool and len(suggestions) < count:
        topic, kind, _tool, question = max(
            pool, key=lambda item: (item[1] not in used_kinds, item[0] not in used_topics, item[0] in history_topics),
        )
        suggestions.append(question)
        used_kinds.add(kind)
        used_topics.add(topic)
        pool = [item for item in pool if item[3] != question]

    for question in starters:
        if len(suggestions) >= count:
            break
        if question not in suggestions:
            suggestions.append(question)
    return suggestions
