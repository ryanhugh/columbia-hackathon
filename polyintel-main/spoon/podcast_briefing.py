import os
import json
import time
from typing import Dict, Any
from integrations.de_search import DeSearchClient
from integrations.sudoapp import SudoClient
from spoon.audio import generate_briefing

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class PodcastBriefingGenerator:
    def __init__(self):
        self.de_search = DeSearchClient()
        self.sudo = SudoClient()
        
        # Initialize OpenAI client if available
        self.openai_client = None
        if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    async def generate_podcast_briefing(self, query: str, category: str = "crypto", duration: str = "PAST_24_HOURS") -> Dict[str, Any]:
        """Generate a comprehensive podcast-style briefing"""
        
        # Step 1: Get raw DeSearch data
        print(f"🔍 Fetching DeSearch data for: {query}")
        raw_data = await self.de_search.search_multi(query, category, duration)
        
        if raw_data.get("status") != "success":
            return {"error": "Failed to fetch DeSearch data"}
        
        # Step 2: Create comprehensive analysis prompt
        analysis_prompt = self._create_analysis_prompt(query, raw_data)
        
        # Step 3: Get deep analysis from Sudo/OpenAI
        print("🧠 Generating comprehensive analysis...")
        analysis_text = await self._generate_ai_analysis(query, raw_data, analysis_prompt)
        
        # Step 4: Create podcast script
        podcast_script = self._create_podcast_script(query, analysis_text, raw_data)
        
        # Step 5: Generate audio
        print("🎙️ Generating podcast audio...")
        audio_filename = f"podcast_briefing_{query.replace(' ', '_')}_{int(time.time())}.mp3"
        audio_path = generate_briefing(podcast_script, audio_filename)
        
        return {
            "status": "success",
            "query": query,
            "audio_file": audio_filename,
            "audio_path": audio_path,
            "script": podcast_script,
            "raw_data": raw_data,
            "analysis": analysis_text,
            "duration": duration,
            "category": category
        }
    
    def _create_analysis_prompt(self, query: str, raw_data: Dict) -> str:
        """Create a trader-focused analysis prompt"""
        
        tweets = raw_data.get("key_content", {}).get("tweets", [])
        posts = raw_data.get("key_content", {}).get("posts", [])
        news = raw_data.get("key_content", {}).get("news", [])
        sentiment_score = raw_data.get("sentiment_score", 0)
        
        # Extract high-engagement content
        viral_tweets = [t for t in tweets if t.get("likes", 0) > 200]
        hot_posts = [p for p in posts if p.get("upvotes", 0) > 1000]
        
        prompt = f"""
        You're a crypto trader who lives in prediction markets. Analyze this social data like you're talking to your trading group chat.

        QUERY: "{query}" (this is what people are betting on)
        SENTIMENT SCORE: {sentiment_score:.2f} (what the crowd thinks)

        VIRAL CONTENT (what's getting engagement):
        Tweets: {json.dumps(viral_tweets[:3], indent=2)}
        Reddit: {json.dumps(hot_posts[:2], indent=2)}

        FULL DATA DUMP:
        Tweets ({len(tweets)}): {json.dumps(tweets[:5], indent=2)}
        Reddit ({len(posts)}): {json.dumps(posts[:3], indent=2)}
        News ({len(news)}): {json.dumps(news[:3], indent=2)}

        Give me the TRADER'S PERSPECTIVE:
        1. What's the crowd getting wrong that I can fade?
        2. Any obvious FUD or hopium I should ignore?
        3. What's the smart money probably thinking?
        4. How does this sentiment translate to prediction market odds?
        5. Any red flags that scream "contrarian play"?
        6. What's the timeline on this - days, weeks, months?

        Talk like someone who's actually traded through bull and bear markets. Don't give me generic finance speak.
        """
        return prompt.strip()
    
    def _create_fallback_analysis(self, query: str, raw_data: Dict) -> str:
        """Create a basic analysis if AI service fails"""
        
        sentiment_score = raw_data.get("sentiment_score", 0)
        tweets = raw_data.get("key_content", {}).get("tweets", [])
        posts = raw_data.get("key_content", {}).get("posts", [])
        news = raw_data.get("key_content", {}).get("news", [])
        
        analysis = f"""
Based on the social media analysis for "{query}":

**Sentiment Score**: {sentiment_score:.2f} out of 1.0

**Key Findings**:
- {len(tweets)} Twitter posts analyzed
- {len(posts)} Reddit discussions reviewed  
- {len(news)} news articles examined

**Social Media Trends**:
The data shows {'positive' if sentiment_score > 0.5 else 'negative' if sentiment_score < -0.1 else 'neutral'} sentiment across platforms.

**Market Implications**:
This sentiment level suggests {'bullish momentum' if sentiment_score > 0.5 else 'bearish pressure' if sentiment_score < -0.1 else 'market uncertainty'}.

**Trading Considerations**:
Monitor for sentiment shifts and confirm with technical analysis before making trading decisions.
        """.strip()
        return analysis
    
    async def _generate_ai_analysis(self, query: str, raw_data: Dict, analysis_prompt: str) -> str:
        """Generate AI analysis using Sudo or OpenAI"""
        
        # Prefer Sudo first
        try:
            print("🔧 Using Sudo for analysis...")
            messages = [
                {"role": "system", "content": "You are a professional financial analyst and podcast host. Create engaging, comprehensive market analysis that helps traders understand current trends and sentiment."},
                {"role": "user", "content": analysis_prompt}
            ]
            analysis_result = await self.sudo.chat_completions("gpt-4o", messages, store=False)
            if not analysis_result.get("error"):
                analysis_text = analysis_result.get("choices", [{}])[0].get("message", {}).get("content", "")
                if analysis_text:
                    return analysis_text
        except Exception as e:
            print(f"Sudo failed: {e}")

        # Fallback to OpenAI if available
        if self.openai_client:
            try:
                print("🤖 Using OpenAI for analysis...")
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a professional financial analyst and podcast host. Create engaging, comprehensive market analysis that helps traders understand current trends and sentiment."},
                        {"role": "user", "content": analysis_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1500
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"OpenAI failed: {e}")
        
        # Final fallback to basic analysis
        print("📊 Using fallback analysis...")
        return self._create_fallback_analysis(query, raw_data)

    def _create_podcast_script(self, query: str, analysis: str, raw_data: Dict) -> str:
        """Create a dynamic, engaging podcast script for prediction market traders"""
        
        sentiment_score = raw_data.get("sentiment_score", 0)
        total_items = raw_data.get("metrics", {}).get("total_items", 0)
        
        # Get actual data points with engagement
        tweets = raw_data.get("key_content", {}).get("tweets", [])
        posts = raw_data.get("key_content", {}).get("posts", [])
        
        # Extract viral content with variety
        viral_content = []
        
        # Top tweets with different engagement levels
        top_tweets = sorted([t for t in tweets if t.get("likes", 0) > 50], key=lambda x: x.get("likes", 0), reverse=True)[:3]
        for i, tweet in enumerate(top_tweets):
            likes = tweet.get("likes", 0)
            text = tweet.get("text", "")
            if len(text) > 30:  # Substantial content
                if likes > 1000:
                    reaction = "went absolutely viral" if i == 0 else "got serious traction"
                elif likes > 500:
                    reaction = "picked up steam" if i == 0 else "started gaining momentum"
                else:
                    reaction = "caught some eyes" if i == 0 else "got people talking"
                viral_content.append(f"""One tweet with {likes} likes {reaction}: \"{text}\"""")
        
        # Top Reddit posts
        top_posts = sorted([p for p in posts if p.get("upvotes", 0) > 100], key=lambda x: x.get("upvotes", 0), reverse=True)[:2]
        for post in top_posts:
            upvotes = post.get("upvotes", 0)
            text = post.get("text", "")
            subreddit = post.get("subreddit", "")
            if len(text) > 40:
                if upvotes > 2000:
                    reaction = "blew up on"
                elif upvotes > 1000:
                    reaction = "gained serious traction on"
                else:
                    reaction = "started trending on"
                viral_content.append(f"""A post {reaction} {subreddit} with {upvotes} upvotes: \"{text}\"""")
        
        # Determine sentiment with prediction market trader language
        if sentiment_score > 0.8:
            sentiment_desc = "maximum bullish"
            market_mood = "degen mode: activated"
            prediction_take = "The crowd's euphoric - might be time to consider the fade trade"
        elif sentiment_score > 0.6:
            sentiment_desc = "solidly bullish"
            market_mood = "apes are feeling good"
            prediction_take = "Momentum's building, but watch for the flip"
        elif sentiment_score > 0.3:
            sentiment_desc = "leaning bullish"
            market_mood = "cautiously optimistic"
            prediction_take = "Could go either way - perfect for scalping"
        elif sentiment_score > 0.1:
            sentiment_desc = "slightly positive"
            market_mood = "waiting for a catalyst"
            prediction_take = "Chop city - maybe sit this one out"
        elif sentiment_score > -0.2:
            sentiment_desc = "mixed signals"
            market_mood = "confusion in the ranks"
            prediction_take = "When in doubt, zoom out"
        elif sentiment_score > -0.5:
            sentiment_desc = "bears waking up"
            market_mood = "fear setting in"
            prediction_take = "Blood in the streets? Might be shopping time"
        else:
            sentiment_desc = "maximum pain"
            market_mood = "doomer hours"
            prediction_take = "Extreme fear often signals opportunity"
        
        # Dynamic intro variations
        intros = [
            f"""What's up degens! Welcome back to the Crypto Sentiment Show - where we separate the signal from the noise in prediction markets.

I'm your AI host who's been deep in the trenches of crypto Twitter, Reddit trenches, and news feeds to bring you what's actually moving markets on {query}.""",
            
            f"""Yo what's good prediction market fam! Your AI sentiment scout here with the real talk on {query}.

I've been monitoring the social pulse so you don't have to - let's see what the crowd's cooking up today.""",
            
            f"""Eyy degens! Time for your daily dose of market sentiment straight from the crypto streets.

Your AI analyst here, fresh off scanning {total_items} data points on {query} - let's see if the crowd's onto something or if we're looking at a classic fade setup."""
        ]
        
        intro = intros[hash(query) % len(intros)]
        
        # Dynamic hot takes section
        hot_takes_section = ""
        if viral_content:
            hot_takes_section = f"""
Let's talk about what's actually catching fire in the timeline:
"""
            for content in viral_content[:2]:  # Limit to avoid repetition
                hot_takes_section += f"""
{content}
"""
        
        # Dynamic data presentation
        data_variations = [
            f"""So here's what the numbers are telling us - I've processed {total_items} pieces of content, and the sentiment meter is reading {sentiment_score:.2f}. Translation: {sentiment_desc}.

Basically, {market_mood}.""",
            
            f"""The data doesn't lie - {total_items} social signals later, and we're looking at {sentiment_score:.2f} on the sentiment scale. That's {sentiment_desc} territory.

{market_mood} vibes confirmed.""",
            
            f"""After crunching {total_items} data points, the crowd sentiment comes in at {sentiment_score:.2f}. In trader terms: {sentiment_desc}.

{market_mood} - you love to see it (or fade it)."""
        ]
        
        data_overview = data_variations[hash(query) % len(data_variations)]
        
        # Enhanced market insights for prediction markets
        market_insights_variations = [
            f"""Now here's where it gets spicy for you prediction market players:

{analysis}

{prediction_take}

This is the kind of sentiment data that can give you an edge before the crowd catches on. Are you riding the wave or betting against the herd?""",
            
            f"""For all my prediction market degens out there:

{analysis}

{prediction_take}

Remember, in prediction markets you're not just betting on outcomes - you're betting on what the crowd will do next. This sentiment data? It's your crystal ball into crowd psychology.""",
            
            f"""Let's break this down for the prediction market crew:

{analysis}

{prediction_take}

The beauty of sentiment analysis is it shows you the crowd's hand before they play their cards. Use it wisely, but don't forget - sometimes the best trade is the one everyone else is sleeping on."""
        ]
        
        market_insights = market_insights_variations[hash(query + analysis) % len(market_insights_variations)]
        
        # Dynamic closings
        closings = [
            f"""Alright fam, that's the sentiment breakdown on {query}.

Quick hits: {sentiment_desc} at {sentiment_score:.2f}, based on {total_items} data points the crowd processed while you were probably living your life.

Use this intel wisely - combine it with your own research, don't bet the farm on vibes alone, and remember: sometimes the best trade is no trade.

Catch you on the next one. May your predictions be right and your gas fees be low. 🫡""",
            
            f"""That's a wrap on today's {query} sentiment scan.

TL;DR: {sentiment_desc} sentiment, score of {sentiment_score:.2f}, {total_items} data points analyzed. The crowd has spoken.

Trade smart, stay safe, and don't let FOMO be your portfolio manager. This has been your AI sentiment scout signing off.

See you in the next briefing! 📊""",
            
            f"""And that's the sentiment story on {query} for today.

Final score: {sentiment_desc} vibes at {sentiment_score:.2f}. The hive mind processed {total_items} signals - make of that what you will.

Stay based, trade carefully, and remember - I'm just the messenger bringing you the crowd's pulse. What you do with it is your call.

Peace out, degens! ✌️"""
        ]
        
        closing = closings[hash(query + str(sentiment_score)) % len(closings)]
        
        # Combine with better flow
        sections = [intro]
        if hot_takes_section:
            sections.append(hot_takes_section)
        sections.extend([data_overview, market_insights, closing])
        
        return "\n\n".join(sections)
