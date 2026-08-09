from datetime import datetime

def generate_markdown_dossier(data: dict) -> str:
    """
    Generates a structured biological field dossier in GitHub-flavored Markdown.
    """
    common_name = data.get("common_name", "Unknown Species")
    scientific_name = data.get("scientific_name", "Unknown")
    category = data.get("category", "General")
    confidence = data.get("confidence")
    iucn = data.get("iucn_status") or {}
    taxonomy = data.get("taxonomy") or {}
    regions = data.get("regions") or []
    synonyms = data.get("synonyms") or []
    wikipedia = data.get("wikipedia") or {}
    model_scores = data.get("model_scores") or []

    lines = []
    lines.append(f"# Biological Specimen Field Dossier: {common_name}")
    lines.append(f"**Scientific Name:** *{scientific_name}*  ")
    lines.append(f"**Broad Category:** {category}  ")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}  ")
    lines.append(f"**Source Engine:** FaunaFlora AI Multi-Stage Biological Pipeline\n")

    lines.append("---\n")

    # 1. Conservation Status
    lines.append("## 🛡️ IUCN Red List Conservation Status")
    if iucn and (iucn.get("code") or iucn.get("category")):
        code = iucn.get("code", "N/A")
        cat = iucn.get("category", "Unknown")
        url = iucn.get("iucn_url")
        lines.append(f"- **Threat Rating:** **{cat} ({code})**")
        if url:
            lines.append(f"- **Official IUCN Assessment:** [View Assessment]({url})")
    else:
        lines.append("- *Status not assessed or data deficient.*")
    lines.append("")

    # 2. Biological Taxonomy
    lines.append("## 🧬 Biological Taxonomy (GBIF)")
    if taxonomy and isinstance(taxonomy, dict) and any(taxonomy.values()):
        lines.append("| Taxonomic Rank | Classification |")
        lines.append("| :--- | :--- |")
        for rank in ["kingdom", "phylum", "class", "order", "family", "genus", "species"]:
            val = taxonomy.get(rank)
            if val:
                lines.append(f"| **{rank.capitalize()}** | *{val}* |")
    else:
        lines.append("- *Taxonomy data not available.*")
    lines.append("")

    # 3. Model Inference Scores (if present)
    if model_scores:
        lines.append("## 🎯 ML Model Candidate Predictions")
        lines.append("| Candidate Species | Confidence Score |")
        lines.append("| :--- | :--- |")
        for item in model_scores[:5]:
            lbl = item.get("label", "")
            score = float(item.get("score", 0.0))
            lines.append(f"| {lbl} | {score*100:.1f}% |")
        lines.append("")

    # 4. Wikipedia Summary & Sections
    lines.append("## 📖 Natural History & Encyclopedic Knowledge")
    summary = wikipedia.get("summary")
    if summary and summary != "Not available":
        lines.append(f"### Summary\n{summary}\n")
    
    sections = wikipedia.get("sections") or {}
    if sections:
        for heading, content in sections.items():
            lines.append(f"### {heading}\n{content}\n")
    
    if wikipedia.get("url"):
        lines.append(f"**Reference:** [Read full Wikipedia article]({wikipedia['url']})\n")

    # 5. Recorded Occurrence Regions & Synonyms
    if regions:
        lines.append("## 🌍 Recorded Occurrence Regions")
        lines.append(", ".join(regions))
        lines.append("")

    if synonyms:
        lines.append("## 🏷️ Scientific Synonyms")
        for syn in synonyms[:10]:
            lines.append(f"- *{syn}*")
        lines.append("")

    lines.append("---\n*Report compiled autonomously by FaunaFlora AI Intelligence System.*")
    return "\n".join(lines)
