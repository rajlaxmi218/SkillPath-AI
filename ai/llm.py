import os
import json
import time
from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()

# Change the model in ONE place (or set GEMINI_MODEL in .env).
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

_client = None


class LLMError(Exception):
    """A Gemini call failed, even after retries."""


class LLMRateLimitError(LLMError):
    """Gemini quota or rate limit reached."""


class LLMFormatError(LLMError):
    """Gemini replied, but not in the JSON format we asked for."""


def _get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise LLMError("GEMINI_API_KEY is not set")
        _client = genai.Client(api_key=api_key)
    return _client


def generate_text(prompt, max_attempts=3):
    delay = 2
    last_error = None

    for attempt in range(1, max_attempts + 1):
        try:
            response = _get_client().models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )
        except errors.APIError as e:
            code = getattr(e, "code", None)
            if code == 429:
                raise LLMRateLimitError("Gemini rate limit or quota reached") from e
            retryable = code in (500, 503, 504)
            last_error = e
        except Exception as e:
            retryable = True
            last_error = e
        else:
            text = (response.text or "").strip()
            if text:
                return text
            retryable = True
            last_error = LLMError("Gemini returned an empty reply")

        print(f"[llm] attempt {attempt} failed: {last_error}")
        if not retryable:
            break
        if attempt < max_attempts:
            time.sleep(delay)
            delay *= 2

    raise LLMError("Gemini is unavailable right now") from last_error


def extract_json(text):
    starts = [i for i in (text.find("["), text.find("{")) if i != -1]
    ends = [i for i in (text.rfind("]"), text.rfind("}")) if i != -1]
    if not starts or not ends:
        raise LLMFormatError("No JSON found in Gemini reply")
    try:
        return json.loads(text[min(starts): max(ends) + 1])
    except json.JSONDecodeError as e:
        raise LLMFormatError("Gemini returned malformed JSON") from e


def generate_json(prompt, max_attempts=2):
    for attempt in range(1, max_attempts + 1):
        text = generate_text(prompt)
        try:
            return extract_json(text)
        except LLMFormatError as e:
            print(f"[llm] format attempt {attempt} failed: {e}")
            if attempt == max_attempts:
                raise