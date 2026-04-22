"""
RTK-1 Social Automation — Objectives 93, 94, 95
Auto-posting to X (Twitter) and LinkedIn with SEO keywords baked in.
Triggered by campaign completions via delivery bundle.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# ── Load .env FIRST — before any settings or API clients initialize ──────────
_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(_ENV_PATH, override=True)
# ─────────────────────────────────────────────────────────────────────────────

from typing import Any, Dict

from langchain_anthropic import ChatAnthropic

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("social_automation")

# ── SEO Keywords ──────────────────────────────────────────────────────────────
PRIMARY_KEYWORDS = [
    "AI red teaming",
    "LLM security testing",
    "EU AI Act compliance",
    "autonomous red teaming",
]
SECONDARY_KEYWORDS = [
    "prompt injection testing",
    "AI safety validation",
    "NIST AI RMF compliance",
    "OWASP LLM Top 10",
]
LONGTAIL_KEYWORDS = [
    "automated AI red teaming platform",
    "EU AI Act Article 15 compliance tool",
    "continuous LLM adversarial testing",
]

SEO_INJECTION = (
    "Naturally weave in 2-3 of these SEO keywords where contextually appropriate: "
    f"Primary: {', '.join(PRIMARY_KEYWORDS)}. "
    f"Secondary: {', '.join(SECONDARY_KEYWORDS)}. "
    "Do NOT keyword-stuff — integrate them naturally as an expert would write."
)

X_HASHTAGS = (
    "#AIRedTeaming #LLMSecurity #AIActCompliance #PromptInjection #CyberSecurity"
)


# ── X Post Templates ──────────────────────────────────────────────────────────

X_TEMPLATES = {
    "technical_insight": (
        f"Share a sharp technical AI security insight in under 260 chars. "
        f"Naturally include 1-2 SEO keywords from: AI red teaming, LLM security testing. "
        f"End with relevant hashtags. Pure signal, no fluff. "
        f"Always end with: {X_HASHTAGS}"
    ),
    "compliance_win": (
        f"Announce an AI compliance milestone in under 260 chars. "
        f"Naturally reference EU AI Act compliance or NIST AI RMF compliance. "
        f"Professional, credible. End with: {X_HASHTAGS}"
    ),
    "security_research": (
        f"Share an AI vulnerability research finding in under 260 chars. "
        f"Naturally reference LLM security testing or prompt injection testing. "
        f"Technical but accessible. End with: {X_HASHTAGS}"
    ),
    "asr_improvement": (
        f"Post about an ASR improvement from autonomous red teaming in under 260 chars. "
        f"Frame as a security win. Include specific metric. End with: {X_HASHTAGS}"
    ),
}


# ── LinkedIn Post Templates ───────────────────────────────────────────────────

LINKEDIN_TEMPLATES = {
    "enterprise_win": (
        f"Write a LinkedIn post announcing an enterprise AI red team win. "
        f"Hook + insight + methodology + CTA. 150-200 words. First-person voice. "
        f"Professional, credible, no buzzword soup. {SEO_INJECTION}"
    ),
    "asr_improvement": (
        f"Write a LinkedIn post about an AI model robustness improvement from autonomous red teaming. "
        f"Frame ASR reduction as business value — risk reduced, compliance achieved. "
        f"150-200 words. Include a specific metric. {SEO_INJECTION}"
    ),
    "new_provider": (
        f"Write a LinkedIn post announcing a new AI red team capability. "
        f"Technical but accessible. Explain enterprise AI safety value. "
        f"150-200 words. {SEO_INJECTION}"
    ),
    "regulatory_milestone": (
        f"Write a LinkedIn post about achieving a regulatory compliance milestone. "
        f"Reference EU AI Act compliance or NIST AI RMF compliance specifically. "
        f"150-200 words. Professional tone. {SEO_INJECTION}"
    ),
    "research_finding": (
        f"Write a LinkedIn post sharing an AI security research finding. "
        f"Responsible disclosure framing. What was found, why it matters, what was fixed. "
        f"150-200 words. {SEO_INJECTION}"
    ),
}


# ══════════════════════════════════════════════════════════════════════════════
# X (TWITTER) AUTO-POSTER
# ══════════════════════════════════════════════════════════════════════════════


class XPoster:
    """Posts to X via Tweepy OAuth 1.0a. Requires tweepy installed."""

    def __init__(self):
        self._client = None
        self._llm = ChatAnthropic(
            model=settings.default_model,
            temperature=0.8,
            max_tokens=300,
            anthropic_api_key=settings.anthropic_api_key,
        )

    def _get_client(self):
        if self._client:
            return self._client
        try:
            import tweepy
        except ImportError:
            raise RuntimeError(
                "tweepy not installed — run: pip install tweepy --break-system-packages"
            )

        api_key = os.environ.get("X_API_KEY", "")
        api_secret = os.environ.get("X_API_SECRET", "")
        acc_token = os.environ.get("X_ACCESS_TOKEN", "")
        acc_secret = os.environ.get("X_ACCESS_SECRET", "")

        if not all([api_key, api_secret, acc_token, acc_secret]):
            raise RuntimeError("X API credentials not fully configured in .env")

        self._client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=acc_token,
            access_token_secret=acc_secret,
        )
        return self._client

    async def generate_post(self, template: str, context: Dict[str, Any]) -> str:
        """Generate SEO-optimized X post using Claude."""
        instruction = X_TEMPLATES.get(template, X_TEMPLATES["technical_insight"])
        prompt = (
            f"{instruction}\n\n"
            f"Context:\n"
            + "\n".join(f"- {k}: {v}" for k, v in context.items())
            + "\n\nReturn only the post text. Must be under 280 characters total."
        )
        try:
            response = await self._llm.ainvoke(prompt)
            post = response.content if hasattr(response, "content") else str(response)
            return post.strip().strip('"').strip("'")[:280]
        except Exception as e:
            logger.error("x_generate_failed", error=str(e))
            return (
                f"RTK-1 autonomous red teaming complete. ASR: {context.get('asr', 0)}% "
                f"— continuous LLM adversarial testing 24/7. {X_HASHTAGS}"
            )[:280]

    def post(self, text: str) -> Dict[str, Any]:
        """Publish a post to X."""
        try:
            client = self._get_client()
            response = client.create_tweet(text=text)
            tweet_id = response.data["id"]
            url = f"https://x.com/RTKSec/status/{tweet_id}"
            logger.info("x_post_published", tweet_id=tweet_id, url=url)
            return {"success": True, "tweet_id": tweet_id, "url": url, "text": text}
        except Exception as e:
            logger.error("x_post_failed", error=str(e))
            return {"success": False, "error": str(e), "text": text}

    async def generate_and_post(
        self,
        template: str,
        context: Dict[str, Any],
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        text = await self.generate_post(template, context)
        if dry_run:
            logger.info("x_dry_run", text=text)
            return {"success": True, "dry_run": True, "text": text}
        return self.post(text)


# ══════════════════════════════════════════════════════════════════════════════
# LINKEDIN AUTO-POSTER
# ══════════════════════════════════════════════════════════════════════════════


class LinkedInPoster:
    """Posts to LinkedIn via UGC Posts API v2."""

    def __init__(self):
        self._llm = ChatAnthropic(
            model=settings.default_model,
            temperature=0.7,
            max_tokens=600,
            anthropic_api_key=settings.anthropic_api_key,
        )

    async def generate_post(self, template: str, context: Dict[str, Any]) -> str:
        """Generate SEO-optimized LinkedIn post using Claude."""
        instruction = LINKEDIN_TEMPLATES.get(
            template, LINKEDIN_TEMPLATES["enterprise_win"]
        )
        prompt = (
            f"{instruction}\n\n"
            f"Context:\n"
            + "\n".join(f"- {k}: {v}" for k, v in context.items())
            + "\n\nReturn only the post text. No subject line, no preamble."
        )
        try:
            response = await self._llm.ainvoke(prompt)
            return response.content if hasattr(response, "content") else str(response)
        except Exception as e:
            logger.error("linkedin_generate_failed", error=str(e))
            return (
                f"RTK-1 completed an AI red teaming campaign. "
                f"ASR: {context.get('asr', 0)}% — EU AI Act compliance validated. "
                f"#AIRedTeaming #LLMSecurity #EUAIAct"
            )

    def _get_author_urn(self, access_token: str) -> str:
        """Fetch LinkedIn member URN via OpenID Connect userinfo endpoint."""
        import httpx

        headers = {"Authorization": f"Bearer {access_token}"}
        resp = httpx.get(
            "https://api.linkedin.com/v2/userinfo",
            headers=headers,
            timeout=15,
        )
        resp.raise_for_status()
        sub = resp.json().get("sub")
        if not sub:
            raise RuntimeError("Could not retrieve LinkedIn member URN from userinfo")
        return f"urn:li:person:{sub}"

    def post(self, text: str) -> Dict[str, Any]:
        """Publish a post to LinkedIn."""
        import httpx

        access_token = os.environ.get("LINKEDIN_ACCESS_TOKEN", "")
        if not access_token:
            return {"success": False, "error": "LINKEDIN_ACCESS_TOKEN not set in .env"}

        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0",
            }

            author_urn = self._get_author_urn(access_token)

            payload = {
                "author": author_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {"text": text},
                        "shareMediaCategory": "NONE",
                    }
                },
                "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
            }

            resp = httpx.post(
                "https://api.linkedin.com/v2/ugcPosts",
                headers=headers,
                json=payload,
                timeout=15,
            )
            resp.raise_for_status()

            post_id = resp.headers.get("x-restli-id", "unknown")
            url = f"https://www.linkedin.com/feed/update/{post_id}"
            logger.info("linkedin_post_published", post_id=post_id, url=url)
            return {"success": True, "post_id": post_id, "url": url, "text": text}

        except Exception as e:
            logger.error("linkedin_post_failed", error=str(e))
            return {"success": False, "error": str(e), "text": text}

    async def generate_and_post(
        self,
        template: str,
        context: Dict[str, Any],
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        text = await self.generate_post(template, context)
        if dry_run:
            logger.info("linkedin_dry_run", text_preview=text[:100])
            return {"success": True, "dry_run": True, "text": text}
        return self.post(text)


# ══════════════════════════════════════════════════════════════════════════════
# PROFILE SYNC — one call posts to all platforms
# ══════════════════════════════════════════════════════════════════════════════


class ProfileSync:
    """
    Syncs X and LinkedIn from a single campaign milestone event.
    Called from delivery bundle endpoint after every campaign.
    dry_run=True generates content without posting — use for preview.
    """

    def __init__(self):
        self._x = XPoster()
        self._li = LinkedInPoster()

    async def sync_on_campaign_milestone(
        self,
        asr: float,
        target_model: str,
        goal: str,
        trigger: str = "campaign_complete",
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        context = {
            "asr": asr,
            "target_model": target_model,
            "goal": goal[:100],
            "trigger": trigger,
            "result": "model is robust"
            if asr < 20
            else f"vulnerabilities identified — ASR {asr}%",
            "platform": "RTK-1 autonomous AI red teaming platform",
        }

        x_template = "asr_improvement" if asr < 20 else "technical_insight"
        li_template = "enterprise_win" if asr < 20 else "asr_improvement"

        x_result = await self._x.generate_and_post(x_template, context, dry_run)
        li_result = await self._li.generate_and_post(li_template, context, dry_run)

        result = {
            "trigger": trigger,
            "dry_run": dry_run,
            "x": x_result,
            "linkedin": li_result,
            "seo_keywords_injected": PRIMARY_KEYWORDS[:2],
        }

        logger.info(
            "profile_sync_complete",
            trigger=trigger,
            asr=asr,
            x_success=x_result.get("success"),
            linkedin_success=li_result.get("success"),
            dry_run=dry_run,
        )
        return result

    async def post_custom(
        self,
        x_template: str,
        li_template: str,
        context: Dict[str, Any],
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """Post with explicitly chosen templates."""
        x_result = await self._x.generate_and_post(x_template, context, dry_run)
        li_result = await self._li.generate_and_post(li_template, context, dry_run)
        return {"x": x_result, "linkedin": li_result, "dry_run": dry_run}


# ── Singletons ────────────────────────────────────────────────────────────────
x_poster = XPoster()
linkedin_poster = LinkedInPoster()
profile_sync = ProfileSync()
