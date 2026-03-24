import logging
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.crop_advisory import CropAdvisory

logger = logging.getLogger(__name__)


async def search_advisories(
    db: AsyncSession,
    query: str,
    language: str = "en",
    crop: str | None = None,
) -> list[dict]:
    """
    Search crop advisories in the knowledge base by keyword matching.
    Returns relevant advisories for grounding the LLM response.
    """
    query_lower = query.lower()
    stmt = select(CropAdvisory)

    if crop:
        stmt = stmt.where(CropAdvisory.crop.ilike(f"%{crop}%"))

    # Search across symptom fields
    stmt = stmt.where(
        or_(
            CropAdvisory.symptoms_te.ilike(f"%{query_lower}%"),
            CropAdvisory.symptoms_hi.ilike(f"%{query_lower}%"),
            CropAdvisory.symptoms_en.ilike(f"%{query_lower}%"),
            CropAdvisory.pest_disease.ilike(f"%{query_lower}%"),
        )
    )
    stmt = stmt.limit(5)

    result = await db.execute(stmt)
    advisories = result.scalars().all()

    formatted = []
    for adv in advisories:
        symptoms = getattr(adv, f"symptoms_{language}", adv.symptoms_en) or adv.symptoms_en or ""
        treatment = getattr(adv, f"treatment_{language}", adv.treatment) or adv.treatment
        formatted.append({
            "crop": adv.crop,
            "pest_disease": adv.pest_disease,
            "symptoms": symptoms,
            "treatment": treatment,
            "dosage": adv.dosage,
            "urgency": adv.urgency,
            "source": adv.source,
        })

    return formatted


def format_kb_context(advisories: list[dict]) -> str:
    """Format KB results into a context string for the LLM prompt."""
    if not advisories:
        return ""

    lines = ["--- Knowledge Base References ---"]
    for i, adv in enumerate(advisories, 1):
        lines.append(f"\n{i}. Crop: {adv['crop']} | Issue: {adv['pest_disease']}")
        lines.append(f"   Symptoms: {adv['symptoms']}")
        lines.append(f"   Treatment: {adv['treatment']}")
        if adv["dosage"]:
            lines.append(f"   Dosage: {adv['dosage']}")
        lines.append(f"   Urgency: {adv['urgency']}")
        if adv["source"]:
            lines.append(f"   Source: {adv['source']}")

    return "\n".join(lines)
