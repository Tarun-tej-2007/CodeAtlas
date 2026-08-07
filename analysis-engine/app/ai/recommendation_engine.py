"""AI Recommendation Engine parsing raw LLM responses into structured recommendations."""

import json
import re
import uuid
from typing import Any, Dict, List, Optional, Tuple

from app.ai.enums import RecommendationCategory, RecommendationPriority
from app.ai.exceptions import AIValidationError
from app.ai.interfaces import RecommendationGenerator
from app.ai.models import AIAnalysis, AIContext, AIRecommendation, AIRequest, PromptContext

# Priority ordering mapping for deterministic sorting
PRIORITY_ORDER = {
    RecommendationPriority.CRITICAL: 0,
    RecommendationPriority.HIGH: 1,
    RecommendationPriority.MEDIUM: 2,
    RecommendationPriority.LOW: 3,
}


class RecommendationGeneratorService(RecommendationGenerator):
    """Concrete RecommendationGenerator service implementing robust raw response parsing."""

    def __init__(self) -> None:
        """Initializes the recommendation generator service."""
        pass

    def generate_recommendations(
        self,
        request: AIRequest,
        raw_completion: str,
        analysis: Optional[AIAnalysis] = None,
        prompt_context: Optional[PromptContext] = None,
        ai_context: Optional[AIContext] = None,
    ) -> Tuple[AIRecommendation, ...]:
        """Translates raw LLM response text into structured, sorted, normalized recommendations.

        Args:
            request: The AIRequest configuration.
            raw_completion: The raw string response from LLM provider APIs.
            analysis: Optional AIAnalysis run metadata.
            prompt_context: Optional PromptContext payload.
            ai_context: Optional AIContext baseline facts.

        Returns:
            An immutable tuple of normalized, sorted AIRecommendation instances.

        Raises:
            AIValidationError: If input validation fails.
        """
        # Fail-fast validation
        if request is None:
            raise AIValidationError("request must not be None.")
        if raw_completion is None:
            raise AIValidationError("raw_completion must not be None.")

        from app.ai.cache import execution_cache, make_hashable
        cache = execution_cache.get()
        cache_key = None
        if cache is not None:
            cache_key = make_hashable((
                "generate_recommendations", request, raw_completion, analysis,
                prompt_context, ai_context
            ))
            if cache_key in cache:
                return cache[cache_key]

        # Pre-clean raw text
        cleaned_completion = raw_completion.strip()
        if not cleaned_completion:
            return ()

        parsed_items: List[Dict[str, Any]] = []

        # 1. Try direct JSON parsing
        try:
            parsed = json.loads(cleaned_completion)
            if isinstance(parsed, list):
                parsed_items = parsed
            elif isinstance(parsed, dict):
                # Search for list keys containing dictionaries
                for val in parsed.values():
                    if isinstance(val, list) and len(val) > 0 and isinstance(val[0], dict):
                        parsed_items = val
                        break
                else:
                    parsed_items = [parsed]
        except json.JSONDecodeError:
            # 2. Try extraction from markdown blocks
            markdown_block_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned_completion, re.IGNORECASE)
            if markdown_block_match:
                try:
                    inner_json = markdown_block_match.group(1).strip()
                    parsed = json.loads(inner_json)
                    if isinstance(parsed, list):
                        parsed_items = parsed
                    elif isinstance(parsed, dict):
                        for val in parsed.values():
                            if isinstance(val, list) and len(val) > 0 and isinstance(val[0], dict):
                                parsed_items = val
                                break
                        else:
                            parsed_items = [parsed]
                except json.JSONDecodeError:
                    pass

        # 3. Fallback to Regex block parsing if JSON parsing could not be completed
        if not parsed_items:
            # Parse blocks by headers like "Title:", "Recommendation:"
            blocks = re.split(r"(?:^|\n)\s*-*#*\s*(?:Recommendation|Item|Finding)\s*\d*\s*:?", cleaned_completion, flags=re.IGNORECASE)
            for block in blocks:
                if not block.strip():
                    continue
                # Extract fields
                item = {}
                title_match = re.search(r"(?:Title|Summary)\s*:\s*(.*)", block, re.IGNORECASE)
                desc_match = re.search(r"(?:Description|Detail|Details)\s*:\s*(.*)", block, re.IGNORECASE)
                cat_match = re.search(r"(?:Category|Type)\s*:\s*(.*)", block, re.IGNORECASE)
                pri_match = re.search(r"(?:Priority|Severity)\s*:\s*(.*)", block, re.IGNORECASE)
                fix_match = re.search(r"(?:Suggested Fix|Fix|Action|Remediation)\s*:\s*(.*)", block, re.IGNORECASE)
                effort_match = re.search(r"(?:Effort|Remediation Effort)\s*:\s*(.*)", block, re.IGNORECASE)
                conf_match = re.search(r"(?:Confidence|Confidence Score)\s*:\s*([\d\.]+)", block, re.IGNORECASE)
                reason_match = re.search(r"(?:Reasoning|Rationale)\s*:\s*(.*)", block, re.IGNORECASE)

                if title_match:
                    item["title"] = title_match.group(1).strip()
                if desc_match:
                    item["description"] = desc_match.group(1).strip()
                if cat_match:
                    item["category"] = cat_match.group(1).strip()
                if pri_match:
                    item["priority"] = pri_match.group(1).strip()
                if fix_match:
                    item["suggested_fix"] = fix_match.group(1).strip()
                if effort_match:
                    item["remediation_effort"] = effort_match.group(1).strip()
                if conf_match:
                    try:
                        item["confidence_score"] = float(conf_match.group(1).strip())
                    except ValueError:
                        pass
                if reason_match:
                    item["reasoning"] = reason_match.group(1).strip()

                if item.get("title") and item.get("description"):
                    parsed_items.append(item)

        # 4. Instantiate and validate recommendations
        recommendations: List[AIRecommendation] = []
        seen_keys = set()

        for item in parsed_items:
            if not isinstance(item, dict):
                continue

            title = item.get("title", "").strip()
            description = item.get("description", "").strip()
            category_raw = item.get("category", "").strip().lower()
            priority_raw = item.get("priority", "").strip().lower()

            if not title or not description:
                # Malformed entry, ignore gracefully
                continue

            # Map category
            category = None
            for cat_enum in RecommendationCategory:
                if cat_enum.value == category_raw:
                    category = cat_enum
                    break
            if not category:
                # Default fallback or skip if malformed
                continue

            # Map priority
            priority = None
            for pri_enum in RecommendationPriority:
                if pri_enum.value == priority_raw:
                    priority = pri_enum
                    break
            if not priority:
                # Default fallback or skip if malformed
                continue

            # Duplicate check
            dup_key = (title.lower(), category)
            if dup_key in seen_keys:
                continue
            seen_keys.add(dup_key)

            # Extract fields
            affected_files_raw = item.get("affected_files", ()) or ()
            if isinstance(affected_files_raw, str):
                affected_files_raw = (affected_files_raw,)
            affected_files = tuple(
                str(f).replace("\\", "/").strip() for f in affected_files_raw if str(f).strip()
            )

            affected_comp_raw = item.get("affected_components", ()) or ()
            if isinstance(affected_comp_raw, str):
                affected_comp_raw = (affected_comp_raw,)
            affected_components = tuple(
                str(c).strip() for c in affected_comp_raw if str(c).strip()
            )

            actions_raw = item.get("suggested_actions", ()) or ()
            if isinstance(actions_raw, str):
                actions_raw = (actions_raw,)
            suggested_actions = tuple(
                str(a).strip() for a in actions_raw if str(a).strip()
            )

            # Confidence score validation
            confidence_score = float(item.get("confidence_score", 1.0))
            if confidence_score < 0.0 or confidence_score > 1.0:
                confidence_score = 1.0

            rec_id = item.get("recommendation_id")
            if rec_id:
                try:
                    rec_uuid = uuid.UUID(str(rec_id))
                except ValueError:
                    rec_uuid = uuid.uuid4()
            else:
                rec_uuid = uuid.uuid4()

            recommendations.append(
                AIRecommendation(
                    recommendation_id=rec_uuid,
                    title=title,
                    description=description,
                    category=category,
                    priority=priority,
                    affected_files=affected_files,
                    suggested_fix=item.get("suggested_fix"),
                    remediation_effort=item.get("remediation_effort"),
                    confidence_score=confidence_score,
                    reasoning=item.get("reasoning"),
                    affected_components=affected_components,
                    suggested_actions=suggested_actions,
                )
            )

        # 5. Deterministic sorting: priority, category, title
        recommendations.sort(
            key=lambda r: (
                PRIORITY_ORDER.get(r.priority, 99),
                r.category.value,
                r.title.lower(),
            )
        )

        res = tuple(recommendations)

        if cache is not None and cache_key is not None:
            cache[cache_key] = res

        return res
