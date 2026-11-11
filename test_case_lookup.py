import io
import json
import unittest
from unittest.mock import patch

from case_lookup import search_case_numbers


class CaseLookupTests(unittest.TestCase):
    def test_posts_claim_number_and_returns_case_numbers(self):
        response = io.BytesIO(
            b'{"cases":[{"caseNumber":456789},{"caseNumber":"987654"}]}'
        )

        with patch("case_lookup.urlopen", return_value=response) as urlopen:
            case_numbers = search_case_numbers(
                "https://sandbox.example",
                "  123456789  ",
                client_id="test-client",
                nonce="test-nonce",
                id_token="test-token",
                csrf_token="test-csrf",
            )

        self.assertEqual(case_numbers, ["456789", "987654"])
        request = urlopen.call_args.args[0]
        self.assertEqual(
            request.full_url,
            "https://sandbox.example/api/v1/case/claim/search",
        )
        self.assertEqual(request.method, "POST")
        self.assertEqual(
            json.loads(request.data),
            {"caseClaimSearchRequest": {"claimNumber": "123456789"}},
        )
        self.assertEqual(request.get_header("Client_id"), "test-client")
        self.assertEqual(request.get_header("Nonce"), "test-nonce")
        self.assertEqual(request.get_header("Id_token"), "test-token")
        self.assertEqual(request.get_header("X_csrf_token"), "test-csrf")

    def test_rejects_empty_claim_number_without_calling_api(self):
        with patch("case_lookup.urlopen") as urlopen:
            with self.assertRaises(ValueError):
                search_case_numbers(
                    "https://sandbox.example",
                    "   ",
                    client_id="test-client",
                    nonce="test-nonce",
                    id_token="test-token",
                    csrf_token="test-csrf",
                )

        urlopen.assert_not_called()


if __name__ == "__main__":
    unittest.main()
