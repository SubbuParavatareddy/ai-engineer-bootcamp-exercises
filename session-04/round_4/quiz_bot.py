"""Quiz bot: ask the practice API five questions and print the answers.

Run it from the top folder of the repository:
    python session-04/round_4/quiz_bot.py
"""

import logging
import re
import time

from practice_api import ask, PracticeAPIError

MAX_RETRIES = 3
MAX_BACKOFF_SECONDS = 30

QUESTIONS = [
    "What is a token?",
    "What is a context window?",
    "What does temperature change?",
    "What is a system prompt?",
    "What is a stack trace?",
]

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def retry_delay(error: PracticeAPIError, retry_number: int) -> float:
    match = re.search(r"Try again in (\d+(?:\.\d+)?) seconds?", error.message)
    if match:
        return max(1.0, float(match.group(1)))
    return min(2 ** (retry_number - 1), MAX_BACKOFF_SECONDS)


for question in QUESTIONS:
    print(f"\nQ: {question}")
    for attempt in range(MAX_RETRIES + 1):
        try:
            answer = ask(question)
            print(f"A: {answer}")
            break
        except PracticeAPIError as error:
            if error.status_code != 429:
                logging.error("ask failed: question=%r error=%s", question, error)
                break
            if attempt == MAX_RETRIES:
                logging.error("ask failed after %d retries: question=%r error=%s", MAX_RETRIES, question, error)
                break
            delay = retry_delay(error, attempt + 1)
            logging.warning(
                "rate limited: question=%r retry=%d/%d wait=%.1fs",
                question,
                attempt + 1,
                MAX_RETRIES,
                delay,
            )
            time.sleep(delay)
        except Exception as error:
            logging.error("ask failed: question=%r error=%s", question, error)
            break
