import asyncio
import argparse
import json
from typing import List, Optional

from ollama_client import OllamaOpenAIClient
from linkedin_official_client import LinkedInOfficialClient
from config import settings


def load_access_token() -> str:
    try:
        with open("linkedin_token.json", "r") as f:
            data = json.load(f)
            return data.get("access_token")
    except Exception:
        return None


def build_image_urls(
    topic: str,
    count: int,
    explicit_urls: Optional[List[str]] = None,
) -> List[str]:
    """Return curated image URLs.

    Priority:
    1) Use explicit URLs provided
    2) Fallback to Unsplash keyword-based featured images (more relevant than random)
    """

    if explicit_urls:
        # Ensure max count respected
        return explicit_urls[: max(1, min(count, 6))]

    keywords = [
        "ai,teamwork,office",
        "robot,collaboration,business",
        "future,work,technology",
        "upskilling,learning,workplace",
        "innovation,automation,career",
        "human,in,the,loop,ai",
    ]
    keywords = keywords[: max(1, min(count, 6))]
    # Unsplash keyword-based featured images (hotlinkable, 1200x675)
    return [f"https://source.unsplash.com/1200x675/?{kw}" for kw in keywords]


async def generate_content(topic: str) -> str:
    # Respect .env-configured Ollama settings
    client = OllamaOpenAIClient(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
    )
    context = (
        "Interactive LinkedIn post. Start with a strong hook. "
        "Discuss how AI reshapes careers and skills. Emphasize upskilling, adaptability, and how AI frees human creativity. "
        "Use short sections and bullets for skimmability. Include a brief CTA for comments. "
        "Add 4–6 relevant hashtags (no more than 6). Keep tone professional, warm, and specific."
    )
    return await client.generate_linkedin_post(topic=topic, context=context)


def read_text_file(path: Optional[str]) -> Optional[str]:
    if not path:
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return None


async def main():
    parser = argparse.ArgumentParser(description="Post a multi-image carousel to LinkedIn")
    parser.add_argument(
        "--topic",
        required=True,
        help="Topic of the LinkedIn post",
    )
    parser.add_argument(
        "--images",
        type=int,
        default=4,
        help="Number of images for the carousel (3–6 supported)",
    )
    parser.add_argument(
        "--visibility",
        default="PUBLIC",
        choices=["PUBLIC", "CONNECTIONS", "LOGGED_IN_MEMBERS"],
        help="LinkedIn post visibility",
    )
    parser.add_argument(
        "--content_file",
        default=None,
        help="Optional path to a text file with the post content (~500 words)",
    )
    parser.add_argument(
        "--images_urls",
        nargs="+",
        default=None,
        help="Optional list of image URLs to use (space-separated)",
    )
    args = parser.parse_args()

    token = load_access_token()
    if not token:
        print("❌ No access token found. Run linkedin_oauth.py first.")
        return

    client = LinkedInOfficialClient(token)

    # Optional: quick API check
    ok = await client.test_connection()
    if not ok:
        print("❌ LinkedIn API connection failed. Check token/permissions.")
        return

    # Content: use provided file or generate
    content = read_text_file(args.content_file)
    if content:
        print("📝 Using content from file")
    else:
        print("🔄 Generating interactive post content…")
        content = await generate_content(args.topic)

    # Images: use explicit URLs or curated keyword-based fallbacks
    images = build_image_urls(args.topic, args.images, explicit_urls=args.images_urls)

    print("\n📝 POST PREVIEW:\n" + "=" * 60)
    print(content)
    print("=" * 60)
    print("\n🖼️ Images:")
    for i, url in enumerate(images, 1):
        print(f"  {i}. {url}")

    print("\n🚀 Publishing carousel (multi-image) post…")
    success = await client.post_content_with_images(content, images, visibility=args.visibility)
    if success:
        print("✅ Post published successfully!")
    else:
        print("❌ Failed to publish post.")


if __name__ == "__main__":
    asyncio.run(main())