import math

import pytest

from services.writing_service import SCORE_NAMES, evaluate_offline, word_count


EMAIL_TASK = {
    "id": "email-trip", "kind": "Email", "title": "A day out",
    "prompt": "Reply to Alex about a day out.",
    "points": ["Suggest Saturday", "Explain travelling by train", "Offer sandwiches"],
    "keywords": [["Saturday"], ["train"], ["sandwich", "sandwiches"]], "starter": "",
}
EMAIL_TEXT = """Hi Alex,

Thanks for your email. Saturday is a good day for our trip because I do not have
any classes then. I think we should take the train to the lake. It is comfortable
and we can talk during the journey. My brother went there last week and said
the water was really beautiful. We could walk around the lake first and then
take some pictures for our friends. I can bring sandwiches for lunch. Would you
like cheese or chicken? Please tell me what you prefer and when you can arrive
at the station.

Best wishes,
Sam"""
ARTICLE_TASK = {
    "id": "article-park", "kind": "Article", "title": "Your favourite place",
    "points": ["Name a place", "Explain an activity"], "keywords": [["park"], ["walk"]],
    "starter": "",
}
ARTICLE_TEXT = """My favourite park

Have you ever wanted a quiet place to relax after school? My favourite place
is the park near my house. There are tall trees and a small lake, so it is
always a pleasant place to spend an afternoon. I usually walk there with my
friends because we can talk and get some exercise at the same time.

Last weekend we took a picnic and watched the birds near the water. I think
you would enjoy this park too. It is free to visit and there is something
interesting to see in every season. Why not come next Saturday?"""
STORY_TASK = {
    "id": "story-key", "kind": "Story", "title": "The lost key",
    "points": ["Describe finding a key", "Describe the ending"],
    "keywords": [["key"], ["home", "happy"]], "starter": "When I opened the door, I saw a key.",
}
STORY_TEXT = """When I opened the door, I saw a key.

At first I thought it belonged to my brother, but he was away on holiday.
I picked it up and went into the kitchen. My mother was making lunch and
looked surprised when I showed it to her. She told me that our neighbour
had lost his key that morning, so we decided to take it to him together.

He was waiting outside his home when we arrived. He smiled and thanked us
because he could finally open his door. In the end he invited us inside
for some cake, and everybody was happy."""


@pytest.mark.parametrize("task,text", [(EMAIL_TASK, EMAIL_TEXT), (ARTICLE_TASK, ARTICLE_TEXT), (STORY_TASK, STORY_TEXT)])
def test_all_kinds_return_honest_actionable_feedback(task, text):
    feedback = evaluate_offline(text, task)
    assert feedback["provider"] == "offline"
    assert 80 <= feedback["word_count"] <= 120
    assert set(feedback["scores"]) == set(SCORE_NAMES)
    assert all(math.isfinite(score) and 0 <= score <= 5 for score in feedback["scores"].values())
    assert feedback["total"] == pytest.approx(sum(feedback["scores"].values()))
    assert feedback["missing_points"] == []
    assert feedback["strengths"] and feedback["improvements"] and feedback["useful_phrases"]
    assert feedback["improved_version"] == ""
    assert "cannot verify meaning" in feedback["disclaimer"]
    assert "does not prove" in feedback["disclaimer"]


@pytest.mark.parametrize("task", [EMAIL_TASK, ARTICLE_TASK, STORY_TASK])
@pytest.mark.parametrize("text", ["", "   \n ", "...!?---"])
def test_empty_responses_have_zero_scores_and_missing_points(task, text):
    feedback = evaluate_offline(text, task)
    assert feedback["word_count"] == 0
    assert feedback["total"] == 0
    assert set(feedback["scores"].values()) == {0.0}
    assert feedback["missing_points"] == task["points"]
    assert feedback["improvements"]


def test_short_response_cannot_score_high_for_matching_clues():
    feedback = evaluate_offline("Hi Alex, Saturday train sandwiches. Best wishes, Sam", EMAIL_TASK)
    assert max(feedback["scores"].values()) <= 1
    assert feedback["total"] <= 4
    assert any("Add useful detail" in item for item in feedback["improvements"])


def test_missing_task_point_reduces_content_and_names_the_point():
    complete = evaluate_offline(EMAIL_TEXT, EMAIL_TASK)
    incomplete = evaluate_offline(EMAIL_TEXT.replace("sandwiches", "something"), EMAIL_TASK)
    assert incomplete["missing_points"] == ["Offer sandwiches"]
    assert incomplete["scores"]["Content"] < complete["scores"]["Content"]
    assert any("Offer sandwiches" in item for item in incomplete["improvements"])


def test_keyword_matching_accepts_simple_inflection_and_avoids_substrings():
    task = dict(EMAIL_TASK, points=["Say you are visiting"], keywords=[["visit"]])
    assert evaluate_offline(EMAIL_TEXT + " I am visiting.", task)["missing_points"] == []
    assert evaluate_offline(EMAIL_TEXT + " I am a revisitor.", task)["missing_points"] == task["points"]


def test_no_keyword_checklist_requires_manual_content_review():
    task = dict(ARTICLE_TASK, keywords=[])
    feedback = evaluate_offline(ARTICLE_TEXT, task)
    assert feedback["missing_points"] == []
    assert any("no keyword checklist" in item for item in feedback["improvements"])
    assert not any("Keyword clues were found" in item for item in feedback["strengths"])


def test_email_format_feedback_identifies_missing_greeting_and_closing():
    text = EMAIL_TEXT.replace("Hi Alex,", "").replace("Best wishes,", "")
    feedback = evaluate_offline(text, EMAIL_TASK)
    assert any("Start your email" in item for item in feedback["improvements"])
    assert any("Finish with a friendly closing" in item for item in feedback["improvements"])


def test_article_format_feedback_identifies_missing_title():
    feedback = evaluate_offline(ARTICLE_TEXT.replace("My favourite park\n\n", ""), ARTICLE_TASK)
    assert any("title on its own line" in item for item in feedback["improvements"])


def test_story_requires_supplied_opening_and_not_merely_keyword_presence():
    feedback = evaluate_offline(STORY_TEXT.replace(STORY_TASK["starter"], "Yesterday I found a key."), STORY_TASK)
    assert feedback["missing_points"] == []
    assert any(STORY_TASK["starter"] in item for item in feedback["improvements"])
    assert feedback["scores"]["Communicative Achievement"] < evaluate_offline(STORY_TEXT, STORY_TASK)["scores"]["Communicative Achievement"]


def test_specific_surface_error_advice_is_given_without_claiming_full_grammar_check():
    feedback = evaluate_offline(EMAIL_TEXT + " i am agree and people is kind.", EMAIL_TASK)
    assert any("capital letter" in item for item in feedback["improvements"])
    assert "Use 'I agree', without am." in feedback["improvements"]
    assert "Use 'people are' because people is plural." in feedback["improvements"]
    assert "grammatical accuracy" in feedback["disclaimer"]


def test_word_count_handles_contractions_hyphens_unicode_and_punctuation():
    assert word_count("I'm well-known. Café! 100 ...") == 4


def test_invalid_kind_is_rejected():
    with pytest.raises(ValueError, match="Email, Article or Story"):
        evaluate_offline("Hello", {"kind": "Essay"})
