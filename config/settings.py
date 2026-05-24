import os


GLASS_API_KEY = os.getenv("GLASS_API_KEY")
GLASS_API_BASE_URL = os.getenv("GLASS_API_BASE_URL", "https://glass.health/api/external/v2")
GLASS_API_VERSION = os.getenv("GLASS_API_VERSION", "glass-5.5")
GLASS_API_TIMEOUT_SECONDS = int(os.getenv("GLASS_API_TIMEOUT_SECONDS", "120"))
