import os

# Set a non-empty dummy key so gspread.api_key() doesn't raise at module import
# time when the real env var is absent (e.g. during local testing).
os.environ.setdefault("COMMUNITIES_GOOGLE_API_KEY", "fake_key_for_testing")
