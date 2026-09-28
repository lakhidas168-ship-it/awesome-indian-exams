import unittest

def calculate_score(answers, questions):
    score = 0
    for q in questions:
        ans = answers.get(q['id'])
        if ans == q['answer']:
            score += 1
        elif ans:
            score -= 0.25
    return score

class TestScoring(unittest.TestCase):
    def test_scoring(self):
        questions = [
            {'id': 'q1', 'answer': 'A'},
            {'id': 'q2', 'answer': 'B'}
        ]
        # Correct, Wrong
        answers = {'q1': 'A', 'q2': 'A'}
        self.assertEqual(calculate_score(answers, questions), 0.75)
        # Correct, Unanswered
        answers = {'q1': 'A'}
        self.assertEqual(calculate_score(answers, questions), 1.0)
        # Wrong, Wrong
        answers = {'q1': 'B', 'q2': 'A'}
        self.assertEqual(calculate_score(answers, questions), -0.5)

if __name__ == '__main__':
    unittest.main()
