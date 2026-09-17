import os

print("🦅 AlphaHawk Online")

token = os.getenv("TELEGRAM_TOKEN")

if token:
    print("Token Loaded")
else:
    print("Token Missing")

