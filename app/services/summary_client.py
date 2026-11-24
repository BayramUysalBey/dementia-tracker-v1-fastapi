# Protocol: any class with an async summarize() counts as a SummaryClient.
from typing import Protocol


class SummaryClient(Protocol):
    """Anything that can turn patient data into a summary text."""
    async def summarize(self, data: dict) -> str: ...


class FakeSummaryClient:
    """Used in tests and local development: no network, no cost, same answer every time."""
    async def summarize(self, data: dict) -> str:
        habits = len(data.get("habits", []))
        medications = len(data.get("medications", []))
        notes = len(data.get("notes", []))
        journals = len(data.get("journals", []))
        return f"Fake summary: {habits} habits, {medications} medications, {notes} notes, {journals} journals"


def get_summary_client() -> SummaryClient:
    """FastAPI dependency. The real provider will be returned here at the end."""
    return FakeSummaryClient()