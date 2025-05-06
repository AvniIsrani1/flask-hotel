import pytest
from HOTEL.services.response import format_response
from HOTEL.AImodels.csv_retriever import setup_csv_retrieval, get_answer_from_csv
from HOTEL.AImodels.ai_model import load_ai_model, generate_ai_response


class TestFormatResponse:
    def test_none_input(self):
        assert format_response(None, "Where is the pool?") is None

    def test_empty_input(self):
        assert format_response("", "What time is check-in?") is None

    def test_description_colon_format(self):
        answer = "description: Check-in time starts at 3 PM."
        assert format_response(answer, "What time is check-in?") == "Check-in time starts at 3 PM."

    def test_category_subcategory_format(self):
        answer = "Hotel Info: Check-in time is 3 PM."
        assert format_response(answer, "Tell me about check-in.") == "Check-in time is 3 PM."

    def test_csv_three_part_format(self):
        answer = "Check-in, Lobby, Check-in starts at 3 PM"
        assert format_response(answer, "Check-in info") == "Check-in starts at 3 PM"

    def test_fallback_plain_response(self):
        answer = "Please visit the front desk for assistance."
        assert format_response(answer, "Where to get help?") == "Please visit the front desk for assistance."


class TestIntegratedResponse:
    def test_csv_then_ai_fallback(self):
        question = "Where is the nearest boat dock?"
        db, df = setup_csv_retrieval()
        answer = get_answer_from_csv(db, df, question)

        if not answer:
            ai_model = load_ai_model()
            answer = generate_ai_response(ai_model, question)

        formatted = format_response(answer, question)

        assert formatted is not None
        assert isinstance(formatted, str)
        assert len(formatted) > 0

    def test_ai_fallback_direct_response(self):
        """
        Test that the AI fallback generates a valid Ocean Vista response
        when called directly (independent of CSV).
        """
        question = "Tell me about celebrity sightings in Malibu."
        ai_model = load_ai_model()
        ai_response = generate_ai_response(ai_model, question)

        formatted = format_response(ai_response, question)

        assert formatted is not None
        assert isinstance(formatted, str)
        assert formatted.startswith("Ocean Vista:") or "Ocean Vista" in formatted

