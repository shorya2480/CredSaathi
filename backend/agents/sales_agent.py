from typing import Dict
import json
import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables once
load_dotenv()


def _get_api_key() -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GROQ_API_KEY in environment or .env")
    return api_key


class SalesAgent:
    """
    Interactive BFSI Sales Agent for CredSaathi (single-language, no detection)
    """

    def __init__(self) -> None:
        self.client = Groq(api_key=_get_api_key())
        # Initialize collected data
        self.data = {
            "loan_amount": None,
            "tenure_months": None,
            "loan_purpose": None,
            "sentiment": "neutral",
            "next_question": "Hi! How much loan are you looking for?",
        }
        # Optional short conversation history (last few user messages)
        self.history = []

    def _normalize_amount(self, value):
        """
        Normalize Indian-style amounts like '10 lakh', '5L', '500000' into an int.
        Returns an int or None if it cannot be parsed or is unreasonable.
        """
        if value is None:
            return None

        # Already numeric
        if isinstance(value, (int, float)):
            amount = int(value)
        else:
            text = str(value).lower().replace(",", "").strip()

            multiplier = 1
            if "lakh" in text or "lac" in text or "lacs" in text:
                multiplier = 100000
                text = (
                    text.replace("lakh", "")
                    .replace("lac", "")
                    .replace("lacs", "")
                    .strip()
                )
            elif text.endswith("l"):
                # e.g. '5l'
                multiplier = 100000
                text = text[:-1].strip()

            try:
                number = float(text)
                amount = int(number * multiplier)
            except ValueError:
                return None

        # Basic sanity check
        if amount <= 0 or amount > 10**9:
            return None

        return amount

    def _normalize_tenure(self, value):
        """
        Normalize tenure into months. Accepts numbers like 36 or strings like '3 years'.
        Returns an int or None.
        """
        if value is None:
            return None

        if isinstance(value, (int, float)):
            months = int(value)
        else:
            text = str(value).lower().strip()
            if "year" in text:
                # e.g. '3 years'
                parts = [p for p in text.split() if p.replace(".", "", 1).isdigit()]
                if not parts:
                    return None
                years = float(parts[0])
                months = int(years * 12)
            else:
                # assume directly months like '36'
                try:
                    months = int(text)
                except ValueError:
                    return None

        if months <= 0 or months > 240:
            return None

        return months

    def _process_message(self, user_message: str) -> Dict:
        """
        Process user input through Groq LLM and update structured data.
        Language detection has been removed.
        """
        # Track short history (for better context)
        self.history.append(user_message)
        recent_history = "\n".join(self.history[-3:])

        prompt = f"""
You are a BFSI Sales Agent for CredSaathi.

CURRENT_KNOWN_DATA:
- loan_amount: {self.data['loan_amount'] if self.data['loan_amount'] is not None else 'unknown'}
- tenure_months: {self.data['tenure_months'] if self.data['tenure_months'] is not None else 'unknown'}
- loan_purpose: {self.data['loan_purpose'] if self.data['loan_purpose'] is not None else 'unknown'}

RECENT_USER_MESSAGES:
{recent_history}

TASKS:
1. Extract loan details from the latest user message (and earlier context if needed).
2. Detect user sentiment (positive / neutral / confused / stressed).
3. Respond politely and professionally.
4. Suggest next question ONLY for fields that are still unknown.
5. Return ONLY valid JSON (no markdown, no explanation).

CONSTRAINTS:
- loan_purpose must be a legitimate financial purpose (e.g. education, medical, home renovation, travel, wedding, debt consolidation, business, etc.).
- If the user mentions illegal or harmful activity (robbery, scams, drugs, etc.), do NOT accept that as loan_purpose.
  - In that case, set "loan_purpose": null and
    "next_question": "We cannot provide loans for illegal purposes. Could you please share a valid purpose for your loan?"
- If loan_amount, tenure_months, and loan_purpose are all known (not null), do NOT ask any more questions.
  - In that case, keep "next_question" as an empty string "".
- Try to infer numbers from phrases like "10 lakh" or "5 lakh" (e.g. 10 lakh = 1000000, 5 lakh = 500000).

FIELDS TO EXTRACT:
- loan_amount (number or null)
- tenure_months (number or null)
- loan_purpose (string or null)
- sentiment (one of: positive, neutral, confused, stressed)
- next_question (what should be asked next, or "" if everything is already known)

LATEST_USER_MESSAGE:
"{user_message}"

JSON FORMAT:
{{
  "loan_amount": null,
  "tenure_months": null,
  "loan_purpose": null,
  "sentiment": "neutral",
  "next_question": ""
}}
"""
        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a professional BFSI sales AI."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
            )
            content = response.choices[0].message.content
            json_data = json.loads(content)
        except Exception:
            json_data = {
                "loan_amount": None,
                "tenure_months": None,
                "loan_purpose": None,
                "sentiment": "neutral",
                "next_question": "Could you please share your loan requirement details?"
            }

        # Update main data dict only if new info is available
        for key in self.data:
            if key in json_data and json_data[key] not in [None, ""]:
                self.data[key] = json_data[key]

        # Normalize numeric fields
        self.data["loan_amount"] = self._normalize_amount(self.data["loan_amount"])
        self.data["tenure_months"] = self._normalize_tenure(self.data["tenure_months"])

        # If normalization failed, keep them as None so we can re-ask
        if self.data["loan_amount"] is None and self.data["loan_purpose"] is not None:
            self.data["next_question"] = (
                "Please tell me the loan amount you are looking for "
                "(for example: 5 lakh or 200000)."
            )

        if (
            self.data["tenure_months"] is None
            and self.data["loan_amount"] is not None
            and self.data["loan_purpose"] is not None
        ):
            self.data["next_question"] = (
                "What tenure are you looking for (for example: 3 years or 36 months)?"
            )

        # If core fields are all collected, clear next_question so flow can move
        if (
            self.data["loan_amount"] is not None
            and self.data["tenure_months"] is not None
            and self.data["loan_purpose"] is not None
        ):
            # No more questions from SalesAgent; hand off to next agent
            self.data["next_question"] = ""

        return self.data

    def interactive_chat(self) -> Dict:
        """
        Full multi-turn conversation (single language, no detection)
        """
        print("Agent: Hello! I am your AI Loan Assistant. I will help you with your personal loan requirements.\n")
        # First question
        self.data["next_question"] = "Please tell me, what is the purpose of your loan?"

        while True:
            # Ask the current question
            print(f"Agent: {self.data['next_question']}")
            user_input = input("You: ")
            self._process_message(user_input)

            # If all core fields are collected, stop here
            if (
                self.data["loan_amount"] is not None
                and self.data["tenure_months"] is not None
                and self.data["loan_purpose"] is not None
            ):
                break

        print("\nAgent: Thank you! I have collected all your details.")
        return self.data


# ====== RUN INTERACTIVE CHAT ======
if __name__ == "__main__":
    agent = SalesAgent()
    # Run a local interactive session for debugging.
    # The collected dict is kept internal (for chaining to other agents),
    # not printed directly to the end user.
    final_data = agent.interactive_chat()
