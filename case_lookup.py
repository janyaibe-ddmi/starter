import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class CaseLookupError(RuntimeError):
    """Raised when the case-search service returns an unusable response."""


def search_case_numbers(
    base_url: str,
    claim_number: str,
    *,
    client_id: str,
    nonce: str,
    id_token: str,
    csrf_token: str,
    timeout: float = 20,
) -> list[str]:
    """Search cases by claim number using the documented case-search API."""
    normalized_claim_number = claim_number.strip()
    if not normalized_claim_number:
        raise ValueError("claim_number is required")

    request = Request(
        url=f"{base_url.rstrip('/')}/api/v1/case/claim/search",
        data=json.dumps(
            {"caseClaimSearchRequest": {"claimNumber": normalized_claim_number}}
        ).encode("utf-8"),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "client_id": client_id,
            "nonce": nonce,
            "id_token": id_token,
            "x_csrf_token": csrf_token,
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            result = json.load(response)
    except HTTPError as error:
        raise CaseLookupError(
            f"Case search failed with HTTP status {error.code}"
        ) from error
    except URLError as error:
        raise CaseLookupError("Could not reach the case-search service") from error

    if not isinstance(result, dict):
        raise CaseLookupError("The case-search response must be a JSON object")

    cases = result.get("cases", [])
    if not isinstance(cases, list):
        raise CaseLookupError("The 'cases' response field must be a list")

    return [
        str(case["caseNumber"])
        for case in cases
        if isinstance(case, dict) and case.get("caseNumber") is not None
    ]
