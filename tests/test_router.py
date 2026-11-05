"""
Real (non-mocked) unit tests for the keyword router in
providers/mistral/session.py.

test_router_mock.py only checks that a *mocked* Mistral client returns
whatever value it was told to return -- it does not exercise route() at
all. These tests call the real route() function with realistic
teacher/student prompts (including the exact examples from
doc/quickstart.md) and check that they land on the agent a human would
expect.
"""

import os
import sys
from pathlib import Path

# A syntactically valid placeholder key is enough: route() does not call
# the Mistral API, so no network access or real credentials are needed.
os.environ.setdefault("MISTRAL_API_KEY", "test-key-not-used-by-these-tests")

project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from providers.mistral.session import route


def test_review_request_routes_to_critical_reviewer():
    assert route("Simulate a peer review of this methods section: ...") == "critical-reviewer"
    assert route("Can you give me a critique of section 2?") == "critical-reviewer"


def test_writing_request_routes_to_writing_coach():
    assert route("Help me write the introduction") == "writing-coach"
    assert route("Review this abstract: some text") == "writing-coach"


def test_vocabulary_request_routes_to_lexical_expert():
    assert route("Build a domain glossary for cardiology at B2 level") == "lexical-expert"
    assert route("What's a more academic word for 'big'?") == "lexical-expert"


def test_grammar_request_routes_to_language_tutor():
    assert route("I keep mixing up the past simple and present perfect tense") == "language-tutor"


def test_assessment_request_routes_to_assessment():
    # This is the exact wording used as example task #3 in doc/quickstart.md
    assert route("Assess this introduction using the IMRAD rubric") == "assessment"
    assert route("Can you grade my poster on the IMRAD rubric?") == "assessment"


def test_communication_request_routes_to_communication_coach():
    assert route("I need feedback on my conference poster slides") == "communication-coach"


def test_unrelated_input_returns_none():
    assert route("What's the weather like today?") is None
