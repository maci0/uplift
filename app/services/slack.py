import httpx
import logging

logger = logging.getLogger(__name__)

_client = httpx.AsyncClient(timeout=10.0)


async def send_to_slack(endpoint: str, channel: str, name: str, email: str, message: str) -> bool:
    """Send a feedback message to Slack webhook."""
    if not endpoint:
        logger.info("Slack endpoint not configured, skipping notification")
        return False

    payload = {
        "channel": channel,
        "username": "Feedback-BOT",
        "text": f"{message} - <mailto:{email}|{name}>",
        "icon_emoji": ":rocket:",
    }

    try:
        response = await _client.post(endpoint, json=payload)
        if not response.is_success:
            logger.warning(
                "Slack webhook returned status=%d channel=%s", response.status_code, channel
            )
        return response.is_success
    except Exception:
        logger.exception("Failed to send Slack notification channel=%s", channel)
        return False
