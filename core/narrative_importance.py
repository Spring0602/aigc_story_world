from schemas import CandidateFuture


class NarrativeImportance:
    def score(self, future: CandidateFuture) -> float:
        score = 0.45
        if future.expected_state_changes:
            score += 0.18
        if future.risks:
            score += 0.12
        if "秘密" in future.summary or "secret" in future.future_id:
            score += 0.09
        return min(1.0, round(score, 2))
