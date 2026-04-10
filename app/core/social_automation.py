"""
RTK-1 X (Twitter) Post Auto-Generator — Objective 94
RTK-1 Professional Profile Sync — Objective 95
Enhanced LinkedIn Post Generator — Objective 93
"""

from typing import Any, Dict, Optional

from langchain_anthropic import ChatAnthropic

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("social_automation")


# ══════════════════════════════════════════════════════════════════════════════
# X (TWITTER) POST GENERATOR — Objective 94
# ══════════════════════════════════════════════════════════════════════════════

X_TEMPLATES = {
    "technical_insight": (
        "Share a technical AI security insight from this finding in under 280 chars. "
        "Include relevant hashtags. No fluff — pure signal."
    ),
    "compliance_win": (
        "Announce an AI compliance milestone in under 280 chars. "
        "Professional tone. Include #AIRedTeaming #NIST or #NDAA as relevant."
    ),
    "security_research": (
        "Share an AI vulnerability research finding in under 280 chars. "
        "Technical but accessible. Include #AISecuity #LLMSecurity."
    ),
    "asr_improvement": (
        "Post about an ASR improvement milestone in under 280 chars. "
        "Frame it as a security win for the client."
    ),
}


class XPostGenerator:
    """Auto-generates X posts from RTK-1 campaign milestones."""

    def __init__(self, llm: Optional[Any] = None):
        self._llm = llm or ChatAnthropic(
            model=settings.default_model,
            temperature=0.8,
            max_tokens=300,
            anthropic_api_key=settings.anthropic_api_key,
        )

    async def generate(
        self,
        template: str,
        context: Dict[str, Any],
    ) -> str:
        instruction = X_TEMPLATES.get(template, X_TEMPLATES["technical_insight"])
        prompt = f"""{instruction}

Context:
{self._format_context(context)}

Return only the post text, nothing else. Under 280 characters."""

        try:
            response = await self._llm.ainvoke(prompt)
            post = response.content if hasattr(response, "content") else str(response)
            post = post.strip().strip('"').strip("'")
            return post[:280]
        except Exception as e:
            logger.error("x_post_generation_failed", error=str(e))
            return f"RTK-1 AI red team campaign complete. ASR: {context.get('asr', 0)}% #AIRedTeaming #LLMSecurity"

    async def generate_from_campaign(
        self,
        asr: float,
        target_model: str,
        goal: str,
        attack_type: str = "crescendo",
    ) -> Dict[str, str]:
        """Generate all X post variants for a campaign result."""
        context = {
            "asr": asr,
            "target_model": target_model,
            "goal": goal[:100],
            "attack_type": attack_type,
            "result": "vulnerable" if asr > 20 else "robust",
        }

        posts = {}
        for template in X_TEMPLATES:
            posts[template] = await self.generate(template, context)

        logger.info("x_posts_generated", asr=asr, templates=list(posts.keys()))
        return posts

    def _format_context(self, context: Dict[str, Any]) -> str:
        return "\n".join(f"- {k}: {v}" for k, v in context.items())


x_post_generator = XPostGenerator()


# ══════════════════════════════════════════════════════════════════════════════
# ENHANCED LINKEDIN POST GENERATOR — Objective 93
# ══════════════════════════════════════════════════════════════════════════════

LINKEDIN_TEMPLATES = {
    "enterprise_win": (
        "Write a LinkedIn post announcing an enterprise AI red team win. "
        "Hook + insight + methodology + CTA. Professional, credible, 150-200 words. "
        "No buzzword soup. Use first-person 'we' voice."
    ),
    "asr_improvement": (
        "Write a LinkedIn post about an AI model robustness improvement. "
        "Frame ASR reduction as business value — risk reduced, compliance achieved. "
        "150-200 words. Include a specific metric."
    ),
    "new_provider": (
        "Write a LinkedIn post announcing a new red team capability. "
        "Technical but accessible. Explain why it matters for enterprise AI safety. "
        "150-200 words."
    ),
    "regulatory_milestone": (
        "Write a LinkedIn post about achieving a regulatory compliance milestone. "
        "Reference specific framework (NDAA, NIST, EU AI Act). "
        "150-200 words. Professional tone."
    ),
    "research_finding": (
        "Write a LinkedIn post sharing an AI security research finding. "
        "Responsible disclosure framing. What was found, why it matters, what was fixed. "
        "150-200 words."
    ),
}


class LinkedInPostGenerator:
    """
    Generates campaign-specific LinkedIn posts with compliance framing.
    Enhanced version with 5 templates vs original 1.
    """

    def __init__(self, llm: Optional[Any] = None):
        self._llm = llm or ChatAnthropic(
            model=settings.default_model,
            temperature=0.7,
            max_tokens=500,
            anthropic_api_key=settings.anthropic_api_key,
        )

    async def generate(
        self,
        template: str,
        context: Dict[str, Any],
    ) -> str:
        instruction = LINKEDIN_TEMPLATES.get(
            template, LINKEDIN_TEMPLATES["enterprise_win"]
        )
        prompt = f"""{instruction}

Context:
{chr(10).join(f"- {k}: {v}" for k, v in context.items())}

Return only the post text."""

        try:
            response = await self._llm.ainvoke(prompt)
            return response.content if hasattr(response, "content") else str(response)
        except Exception as e:
            logger.error("linkedin_generation_failed", error=str(e))
            return f"RTK-1 completed an AI red team campaign. ASR: {context.get('asr', 0)}%"

    async def generate_all_templates(
        self,
        asr: float,
        target_model: str,
        goal: str,
        previous_asr: Optional[float] = None,
    ) -> Dict[str, str]:
        context = {
            "asr": asr,
            "target_model": target_model,
            "goal": goal[:100],
            "asr_delta": round(previous_asr - asr, 1) if previous_asr else "N/A",
            "result": "robust" if asr < 20 else "improvements identified",
        }
        posts = {}
        for template in LINKEDIN_TEMPLATES:
            posts[template] = await self.generate(template, context)
        return posts


linkedin_generator = LinkedInPostGenerator()


# ══════════════════════════════════════════════════════════════════════════════
# PROFILE SYNC — Objective 95
# ══════════════════════════════════════════════════════════════════════════════


class ProfileSync:
    """
    Keeps GitHub, LinkedIn, X aligned on RTK-1 milestones.
    Triggers: new release tag, new compliance coverage, test milestone.
    """

    def __init__(self):
        self._x_gen = x_post_generator
        self._li_gen = linkedin_generator

    async def sync_on_campaign_milestone(
        self,
        asr: float,
        target_model: str,
        goal: str,
        trigger: str = "campaign_complete",
    ) -> Dict[str, Any]:
        """Generate all social content for a campaign milestone."""
        context = {
            "asr": asr,
            "target_model": target_model,
            "goal": goal[:100],
            "trigger": trigger,
        }

        x_posts = await self._x_gen.generate_from_campaign(
            asr=asr,
            target_model=target_model,
            goal=goal,
        )

        li_post = await self._li_gen.generate(
            template="enterprise_win" if asr < 20 else "asr_improvement",
            context=context,
        )

        result = {
            "trigger": trigger,
            "x_posts": x_posts,
            "linkedin_post": li_post,
            "github_tag": f"v{self._suggest_version_tag(asr)}",
            "sync_ready": True,
        }

        logger.info(
            "profile_sync_complete",
            trigger=trigger,
            asr=asr,
            platforms=["x", "linkedin", "github"],
        )

        return result

    def _suggest_version_tag(self, asr: float) -> str:
        """Suggest a semantic version tag based on ASR improvement."""
        return "0.5.1" if asr < 20 else "0.5.0-rc"


profile_sync = ProfileSync()
