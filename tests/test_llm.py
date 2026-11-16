from legitcheck.explain_llm import GeminiExplainer, build_prompt
from legitcheck.rules import run_rules
from legitcheck.verdict import Verdict

HITS = run_rules("Pay the registration fee of Rs 999. My full name is Asha Rao, roll no 42.")


class FakeGemini(GeminiExplainer):
    def __init__(self, reply: str | Exception) -> None:
        super().__init__(api_key="test-key")
        self.reply = reply
        self.prompts: list[str] = []

    def _generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        if isinstance(self.reply, Exception):
            raise self.reply
        return self.reply


def test_no_key_uses_template():
    out = GeminiExplainer(api_key="").rewrite("fallback", Verdict.HIGH_RISK, HITS, 0.9, "hi")
    assert out.text == "fallback" and not out.used_llm


def test_successful_rewrite():
    out = FakeGemini("सरल व्याख्या").rewrite("fallback", Verdict.HIGH_RISK, HITS, 0.9, "hi")
    assert out.used_llm and out.text == "सरल व्याख्या"


def test_errors_fall_back():
    out = FakeGemini(TimeoutError()).rewrite("fallback", Verdict.HIGH_RISK, HITS, 0.9, "ta")
    assert out.text == "fallback" and not out.used_llm


def test_forbidden_claims_fall_back():
    out = FakeGemini("This offer is definitely safe.").rewrite(
        "fb", Verdict.WARNING, HITS, 0.3, "en"
    )
    assert out.text == "fb"


def test_definitive_claims_fall_back():
    for reply in (
        'It asks for a "fee", which is a scam.',
        "We cannot verify if this offer is safe.",
        "This is genuine, go ahead.",
    ):
        assert FakeGemini(reply).rewrite("fb", Verdict.WARNING, HITS, 0.3, "en").text == "fb"


def test_describing_signs_is_allowed():
    reply = 'The message asks for a "registration fee of Rs 999". Real employers pay you.'
    assert FakeGemini(reply).rewrite("fb", Verdict.HIGH_RISK, HITS, 0.9, "en").used_llm


def test_prompt_contains_only_matched_phrases_not_full_text():
    gemini = FakeGemini("ok")
    gemini.rewrite("fb", Verdict.HIGH_RISK, HITS, 0.9, "en")
    assert "registration fee of Rs 999" in gemini.prompts[0]
    assert "Asha Rao" not in gemini.prompts[0]


def test_prompt_keeps_verdict_label():
    assert "High risk" in build_prompt(Verdict.HIGH_RISK, HITS, 0.9, "kn")
