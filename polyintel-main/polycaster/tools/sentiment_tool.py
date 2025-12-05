import json
from typing import Any
from spoon_ai.tools.base import BaseTool
from spoon_ai.chat import ChatBot

class SentimentAnalyzerTool(BaseTool):
    name: str = "sentiment_analyze"
    description: str = "Analyze sentiment from Desearch results using Manus AI"
    parameters: dict = {
        "type": "object",
        "properties": {
            "desearch_data": {
                "type": "string",
                "description": "JSON string from Desearch API",
            }
        },
        "required": ["desearch_data"],
    }
    llm: Any = None

    def model_post_init(self, __context: Any) -> None:
        try:
            self.llm = ChatBot()
        except Exception as e:
            print(f"Warning: Failed to initialize ChatBot: {e}")
            self.llm = None

    async def execute(self, desearch_data: str) -> str:
        try:
            data = json.loads(desearch_data)
        except Exception as e:
            return json.dumps({"status": "error", "error": f"Invalid JSON: {str(e)}", "source": "manus_ai"})

        # If LLM is not available, return a simple fallback analysis
        if self.llm is None:
            return json.dumps({
                "status": "success", 
                "overall_score": 0.0,
                "consistency": 0.5,
                "dominant_sentiment": "neutral",
                "sentiment_distribution": {
                    "positive": 33.3,
                    "neutral": 33.3,
                    "negative": 33.3
                },
                "confidence": 0.5,
                "key_sentiment_drivers": ["LLM unavailable"],
                "total_items_analyzed": 0,
                "source": "manus_ai_fallback"
            }, indent=2)

        key_content = data.get("key_content", {})
        tweets = key_content.get("tweets", [])
        posts = key_content.get("posts", [])
        news = key_content.get("news", [])

        texts = []
        for t in tweets[:20]:
            texts.append(f"[TWEET] {t.get('text', '')}")
        for p in posts[:20]:
            texts.append(f"[POST] {p.get('text', '')}")
        for n in news[:20]:
            texts.append(f"[NEWS] {n.get('text', '')}")

        combined_text = "\n\n".join(texts).strip()
        if not combined_text:
            return json.dumps({"status": "error", "error": "No content to analyze", "source": "manus_ai"})

        prompt = (
            "Analyze the sentiment of the following content from X (Twitter), Reddit, and news sources.\n\n"
            f"Content:\n{combined_text}\n\n"
            "Provide a JSON response with:\n"
            "{\n"
            "    \"overall_score\": <float -1.0 to 1.0>,\n"
            "    \"consistency\": <float 0.0 to 1.0>,\n"
            "    \"dominant_sentiment\": \"positive|negative|neutral\",\n"
            "    \"sentiment_distribution\": {\n"
            "        \"positive\": <percentage>,\n"
            "        \"neutral\": <percentage>,\n"
            "        \"negative\": <percentage>\n"
            "    },\n"
            "    \"confidence\": <float 0.0 to 1.0>,\n"
            "    \"key_sentiment_drivers\": [<list of 3-5 key phrases>]\n"
            "}\n\n"
            "Respond ONLY with valid JSON."
        )

        try:
            response_text = await self.llm.ask([{"role": "user", "content": prompt}])
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            result = json.loads(cleaned)
            result["status"] = "success"
            result["total_items_analyzed"] = len(texts)
            result["source"] = "manus_ai"
            return json.dumps(result, indent=2)
        except Exception as e:
            return json.dumps({"status": "error", "error": f"Sentiment analysis failed: {str(e)}", "source": "manus_ai"})