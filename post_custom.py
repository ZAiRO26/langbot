import asyncio
import json
from linkedin_official_client import LinkedInOfficialClient


def load_access_token() -> str:
    try:
        with open("linkedin_token.json", "r") as f:
            data = json.load(f)
            return data.get("access_token")
    except Exception:
        return None


async def main():
    token = load_access_token()
    if not token:
        print("❌ No access token found. Run linkedin_oauth.py first.")
        return

    client = LinkedInOfficialClient(token)

    # Compose the 500-word post content
    content = (
        "🚀 How to Successfully Transition from IT (or Any Corporate Role) to AI Product Manager: A Practical Guide for 2025\n\n"
        "Thinking about moving from hands-on IT, software engineering, data, or operations into AI Product Management? 2025 is the perfect time. AI is shifting from experiments to repeatable products, and companies need builders who understand both technology and outcomes. Here’s a clear, practical path you can start today.\n\n"
        "1) Translate experience into product language\n"
        "– Map what you’ve shipped to outcomes: reliability, user adoption, cost savings, SLA improvements.\n"
        "– Turn projects into problem statements: user need → constraints → solution → measurable impact.\n"
        "– Practice writing one-pagers: the problem, users, success metrics, risks, and launch plan.\n\n"
        "2) Build AI literacy that matters to PMs\n"
        "– Understand LLMs, embeddings, retrieval, fine-tuning, evaluation, and guardrails.\n"
        "– Know the difference between model performance and product performance (latency, cost per query, reliability, safety).\n"
        "– Learn how AI is delivered: data pipelines, prompt orchestration, vector stores, and human-in-the-loop feedback.\n\n"
        "3) Ship small but real AI artifacts\n"
        "– Build a micro-portfolio: a retrieval-augmented chatbot, classifier, or content assistant with clear metrics.\n"
        "– Document decisions like a PM: user story, constraints, trade-offs, offline/online evaluation, and rollout plan.\n"
        "– Show responsible AI thinking: privacy, hallucination mitigation, abuse prevention, and transparency.\n\n"
        "4) Master AI PM core skills\n"
        "– Discovery: interview users and stakeholders to validate the problem before picking a model.\n"
        "– Prioritization: ship thin slices; start with a dependable baseline, then add AI where it truly moves the metric.\n"
        "– Metrics: track not only accuracy, but coverage, cost per output, time-to-completion, and intervention rate.\n\n"
        "5) Position your story for hiring in 2025\n"
        "– Create a results-first portfolio site (screenshots, demos, PRDs, dashboards).\n"
        "– Replace buzzwords with measurable outcomes: ‘reduced review time by 37%’ beats ‘built an AI bot’.\n"
        "– Network with AI PMs and engineers; contribute to open-source or internal guilds to stay current.\n\n"
        "Starter project ideas you can ship in weeks:\n"
        "– A support-assist tool that drafts answers and flags uncertainty.\n"
        "– A meeting notes summarizer with owner/action extraction.\n"
        "– A policy checker that evaluates text against company guidelines with a risk score.\n\n"
        "Tagging Abhinav Nigam for inspiring this transition conversation and for the hard work he’s doing from a coding perspective — thank you!\n"
        "Profile: https://www.linkedin.com/in/abhinavnigam2207/\n\n"
        "If you’re making the leap in 2025, focus on user value, rigorous evaluation, and safe, reliable delivery. The best AI PMs are bridge-builders: they align users, data, models, and operations into a product that earns trust. Let’s build thoughtfully."
    )

    # Two relevant images (royalty-free sources)
    image_urls = [
        "https://picsum.photos/seed/ai/1200/800",
        "https://picsum.photos/seed/product/1200/800",
    ]

    # Post with images
    print("🔄 Posting content with images…")
    ok = await client.post_content_with_images(content, image_urls, visibility="PUBLIC")
    if ok:
        print("✅ Post published successfully!")
    else:
        print("❌ Failed to publish post.")


if __name__ == "__main__":
    asyncio.run(main())