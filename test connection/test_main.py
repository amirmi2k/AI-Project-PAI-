import unittest

from main import MASController


class MasControllerOfflineTest(unittest.TestCase):
    def test_network_input_uses_offline_heuristic_when_llm_unavailable(self):
        controller = MASController("Analyze network activity from IP 10.0.0.9 for The Entity breach.")
        controller._llm_is_available = lambda: False

        result = controller.route_and_execute()

        self.assertEqual(result["status"], "OFFLINE_ANALYSIS")
        self.assertIn("analysis_result", result)
        self.assertIn("confidence_score", result)
        self.assertIn("next_step", result)
        self.assertGreaterEqual(result["confidence_score"], 0.0)
        self.assertLessEqual(result["confidence_score"], 1.0)

    def test_voice_input_uses_offline_heuristic_when_llm_unavailable(self):
        controller = MASController("The intercepted voice sample shows unusual cadence and synthetic artifacts.")
        controller._llm_is_available = lambda: False

        result = controller.route_and_execute()

        self.assertEqual(result["status"], "OFFLINE_ANALYSIS")
        self.assertIn("analysis_result", result)
        self.assertIn("next_step", result)


if __name__ == "__main__":
    unittest.main()
