import unittest

from cancellation import extract_cancellation_order_id


class ExtractCancellationOrderIdTests(unittest.TestCase):
    def test_extracts_clear_cancellation_requests(self):
        messages = {
            "cancel order 456": "456",
            "Please cancel order 123": "123",
            "Can you cancel my order #789?": "789",
            "Order 321, please cancel": "321",
        }

        for message, expected_order_id in messages.items():
            with self.subTest(message=message):
                self.assertEqual(extract_cancellation_order_id(message), expected_order_id)

    def test_rejects_negated_cancellation_requests(self):
        messages = [
            "Don't cancel order 123",
            "Do not cancel order 456",
            "I can't cancel order 789",
            "Cancel order 123, but don't do it",
        ]

        for message in messages:
            with self.subTest(message=message):
                self.assertIsNone(extract_cancellation_order_id(message))

    def test_rejects_uncertain_or_capability_questions(self):
        messages = [
            "Should I cancel order 123?",
            "Maybe cancel order 456",
            "I'm thinking about canceling order 789",
            "Can I cancel order 123?",
        ]

        for message in messages:
            with self.subTest(message=message):
                self.assertIsNone(extract_cancellation_order_id(message))


if __name__ == "__main__":
    unittest.main()
