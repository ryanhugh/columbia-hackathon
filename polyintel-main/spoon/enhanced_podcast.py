import os
import json
import time
from typing import Dict, Any, List
from integrations.de_search import DeSearchClient
from integrations.sudoapp import SudoClient
from spoon.audio import generate_briefing

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class EnhancedPodcastBriefingGenerator:
    def __init__(self):
        self.de_search = DeSearchClient()
        self.sudo = SudoClient()
        
        # Initialize OpenAI client if available
        self.openai_client = None
        if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def generate_enhanced_podcast(self, query: str, category: str = "crypto", duration: str = "PAST_24_HOURS") -> Dict[str, Any]:
        """Generate an enhanced podcast with multiple voices and dynamic segments"""
        
        # Step 1: Get raw DeSearch data
        print(f"🔍 Fetching DeSearch data for: {query}")
        raw_data = await self.de_search.search_multi(query, category, duration)
        
        if raw_data.get("status") != "success":
            return {"error": "Failed to fetch DeSearch data"}
        
        # Step 2: Create comprehensive analysis
        analysis_prompt = self._create_trader_analysis_prompt(query, raw_data)
        analysis_text = await self._generate_ai_analysis(query, raw_data, analysis_prompt)
        
        # Step 3: Create dynamic podcast segments
        segments = self._create_dynamic_segments(query, analysis_text, raw_data)
        
        # Step 4: Generate audio for each segment with different settings
        print("🎙️ Generating enhanced podcast audio...")
        audio_files = []
        
        for i, segment in enumerate(segments):
            filename = f"podcast_segment_{i}_{query.replace(' ', '_')}_{int(time.time())}.mp3"
            audio_path = self._generate_segment_audio(segment, filename)
            if audio_path:
                audio_files.append(audio_path)
        
        # Step 5: Combine segments (simple concatenation for now)
        combined_audio = self._combine_audio_segments(audio_files, query)
        
        return {
            "status": "success",
            "query": query,
            "audio_file": combined_audio,
            "audio_url": f"/polyflow/audio/{combined_audio}",
            "segments": segments,
            "segment_files": audio_files,
            "analysis": analysis_text,
            "sentiment_score": raw_data.get("sentiment_score", 0),
            "data_sources": raw_data.get("metrics", {})
        }
    
    def _create_trader_analysis_prompt(self, query: str, raw_data: Dict) -> str:
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

        Give me the TRADER'S PERSPECTIVE:
        1. What's the crowd getting wrong that I can fade?
        2. Any obvious FUD or hopium I should ignore?
        3. What's the smart money probably thinking?
        4. How does this sentiment translate to prediction market odds?
        5. Any red flags that scream "contrarian play"?
        6. What's the timeline on this - days, weeks, months?

        Talk like someone who's actually traded through bull and bear markets.
        """
        return prompt.strip()
    
    async def _generate_ai_analysis(self, query: str, raw_data: Dict, analysis_prompt: str) -> str:
        """Generate AI analysis using Sudo or OpenAI"""
        
        # Try OpenAI first if available
        if self.openai_client:
            try:
                print("🤖 Using OpenAI for analysis...")
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You're a crypto trader who specializes in prediction markets. Give raw, unfiltered analysis that traders can actually use."},
                        {"role": "user", "content": analysis_prompt}
                    ],
                    temperature=0.8,
                    max_tokens=1200
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"OpenAI failed: {e}, falling back to Sudo...")
        
        # Try Sudo as fallback
        try:
            print("🔧 Using Sudo for analysis...")
            messages = [
                {"role": "system", "content": "You're a crypto trader who specializes in prediction markets. Give raw, unfiltered analysis that traders can actually use."},
                {"role": "user", "content": analysis_prompt}
            ]
            
            analysis_result = await self.sudo.chat_completions("gpt-4o", messages, store=False)
            
            if not analysis_result.get("error"):
                analysis_text = analysis_result.get("choices", [{}])[0].get("message", {}).get("content", "")
                if analysis_text:
                    return analysis_text
                    
        except Exception as e:
            print(f"Sudo failed: {e}")
        
        # Final fallback
        return self._create_fallback_analysis(query, raw_data)
    
    def _create_fallback_analysis(self, query: str, raw_data: Dict) -> str:
        """Create a basic analysis if AI service fails"""
        
        sentiment_score = raw_data.get("sentiment_score", 0)
        total_items = raw_data.get("metrics", {}).get("total_items", 0)
        
        return f"""
Quick take on {query}:

Sentiment reading: {sentiment_score:.2f} - that's {'bullish' if sentiment_score > 0.3 else 'bearish' if sentiment_score < -0.1 else 'neutral'}

Based on {total_items} social signals, here's what stands out:
- Crowd is feeling {'confident' if sentiment_score > 0.3 else 'fearful' if sentiment_score < -0.1 else 'indecisive'}
- This could signal {'momentum building' if abs(sentiment_score) > 0.5 else 'chop ahead'}

For prediction markets: Watch for sentiment shifts before major moves. The crowd often gets it wrong at extremes.
        """.strip()
    
    def _create_dynamic_segments(self, query: str, analysis: str, raw_data: Dict) -> List[Dict[str, Any]]:
        """Create dynamic podcast segments with different styles"""
        
        sentiment_score = raw_data.get("sentiment_score", 0)
        total_items = raw_data.get("metrics", {}).get("total_items", 0)
        
        # Get viral content
        tweets = raw_data.get("key_content", {}).get("tweets", [])
        posts = raw_data.get("key_content", {}).get("posts", [])
        
        viral_tweets = sorted([t for t in tweets if t.get("likes", 0) > 100], key=lambda x: x.get("likes", 0), reverse=True)[:2]
        hot_posts = sorted([p for p in posts if p.get("upvotes", 0) > 500], key=lambda x: x.get("upvotes", 0), reverse=True)[:1]
        
        # Determine market mood
        if sentiment_score > 0.7:
            mood, prediction_take = "euphoria", "Time to consider fading the euphoria"
        elif sentiment_score > 0.4:
            mood, prediction_take = "optimism", "Momentum building but watch for reversals"
        elif sentiment_score > 0.1:
            mood, prediction_take = "caution", "Chop city - perfect for range plays"
        elif sentiment_score > -0.2:
            mood, prediction_take = "uncertainty", "Mixed signals - sit tight or scalp"
        else:
            mood, prediction_take = "fear", "Extreme fear often signals opportunity"
        
        segments = []
        
        # Segment 1: High-energy intro
        intro_scripts = [
            f"""YO! What's good prediction market fam! Your AI sentiment scout here with the REAL intel on {query}.

I've been monitoring the social pulse so you can stay ahead of the crowd. Let's see what the hive mind is cooking up today!""",
            
            f"""What's up degens! Welcome to the Crypto Sentiment Show - where we separate signal from noise in prediction markets.

Your AI host here, fresh off analyzing {total_items} data points on {query}. Let's dive into the social sentiment that's actually moving markets!""",
            
            f"""Eyy fam! Time for your daily dose of market sentiment straight from the crypto trenches.

I'm your AI analyst, scanning the social sphere on {query}. Let's see if the crowd's onto something or if we're looking at a classic fade setup!"""
        ]
        
        segments.append({
            "type": "intro",
            "script": intro_scripts[hash(query) % len(intro_scripts)],
            "voice_settings": {
                "stability": 0.3,  # More energy/variation
                "similarity_boost": 0.8,
                "style": 0.4,
                "use_speaker_boost": True
            }
        })
        
        # Segment 2: Viral content breakdown
        if viral_tweets or hot_posts:
            viral_script = "Here's what's catching fire in the timeline:"
            
            for tweet in viral_tweets:
                likes = tweet.get("likes", 0)
                text = tweet.get("text", "")
                if likes > 1000:
                    reaction = "absolutely exploded"
                elif likes > 500:
                    reaction = "gained serious traction"
                else:
                    reaction = "started picking up steam"
                viral_script += f"""

One tweet with {likes} likes {reaction}: \"{text}\"""
            
            for post in hot_posts:
                upvotes = post.get("upvotes", 0)
                text = post.get("text", "")
                subreddit = post.get("subreddit", "")
                viral_script += f"""

Reddit post on {subreddit} with {upvotes} upvotes: \"{text}\"""
            
            segments.append({
                "type": "viral_content",
                "script": viral_script,
                "voice_settings": {
                    "stability": 0.4,
                    "similarity_boost": 0.75,
                    "style": 0.3,
                    "use_speaker_boost": True
                }
            })
        
        # Segment 3: Data analysis
        data_scripts = [
            f"""So here's what the data's telling us: I've processed {total_items} social signals, and sentiment is reading {sentiment_score:.2f}.

Translation: we're in {mood} territory. {prediction_take}""",
            
            f"""The numbers don't lie - {total_items} pieces of content analyzed, sentiment score of {sentiment_score:.2f}.

That's {mood} vibes confirmed. Here's my take: {prediction_take}""",
            
            f"""After crunching {total_items} data points, here's the verdict: {sentiment_score:.2f} sentiment score puts us in {mood} mode.

{prediction_take}"""
        ]
        
        segments.append({
            "type": "data_analysis",
            "script": data_scripts[hash(query + str(sentiment_score)) % len(data_scripts)],
            "voice_settings": {
                "stability": 0.6,  # More stable for data
                "similarity_boost": 0.8,
                "style": 0.2,
                "use_speaker_boost": True
            }
        })
        
        # Segment 4: Deep analysis
        analysis_scripts = [
            f"""Now for the deep dive:

{analysis}

This is the kind of intel that can give you an edge in prediction markets. The question is: are you riding the sentiment wave or betting against the herd?""",
            
            f"""Let's break this down for the prediction market crew:

{analysis}

Remember, you're not just betting on outcomes - you're betting on what the crowd will do next. This sentiment data? It's your window into crowd psychology.""",
            
            f"""Here's where it gets interesting:

{analysis}

The beauty of sentiment analysis is seeing the crowd's hand before they play it. Use it wisely, but don't forget - sometimes the best trade is the one everyone else is sleeping on."""
        ]
        
        segments.append({
            "type": "deep_analysis",
            "script": analysis_scripts[hash(analysis) % len(analysis_scripts)],
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.3,
                "use_speaker_boost": True
            }
        })
        
        # Segment 5: Closing
        closings = [
            f"""Alright fam, that's the sentiment breakdown on {query}.

Sentiment: {mood} vibes at {sentiment_score:.2f}. Use this intel wisely - combine with your own research, don't bet the farm on vibes alone.

Catch you on the next one. May your trades be right and your gas fees be low!""",
            
            f"""That's a wrap on today's {query} sentiment scan.

{mood} sentiment confirmed. {total_items} data points processed. The crowd has spoken - now it's your move.

Trade smart, stay safe. This has been your AI sentiment scout signing off!""",
            
            f"""And that's the sentiment story on {query} for today.

{mood} mood at {sentiment_score:.2f}. The hive mind processed {total_items} signals - make of that what you will.

Stay based, trade carefully. Peace out, degens!"""
        ]
        
        segments.append({
            "type": "closing",
            "script": closings[hash(query + str(sentiment_score)) % len(closings)],
            "voice_settings": {
                "stability": 0.4,
                "similarity_boost": 0.8,
                "style": 0.3,
                "use_speaker_boost": True
            }
        })
        
        return segments
    
    def _generate_segment_audio(self, segment: Dict[str, Any], filename: str) -> str:
        """Generate audio for a single segment with custom settings"""
        try:
            # Use custom voice settings for each segment
            api_key = self._get_elevenlabs_key()
            if not api_key:
                return None
            
            client = ElevenLabs(api_key=api_key)
            
            # Use different voices for different segment types
            voice_id = self._get_voice_for_segment(segment["type"])
            
            audio_stream = client.text_to_speech.convert(
                text=segment["script"],
                voice_id=voice_id,
                model_id="eleven_multilingual_v2",
                voice_settings=segment["voice_settings"]
            )
            
            with open(filename, "wb") as f:
                for chunk in audio_stream:
                    f.write(chunk)
            
            return filename
        except Exception as e:
            print(f"Error generating segment audio: {e}")
            return None
    
    def _get_voice_for_segment(self, segment_type: str) -> str:
        """Get appropriate voice for different segment types"""
        voices = {
            "intro": "JBFqnCBsd6RMkjVDRZzb",  # Energetic male
            "viral_content": "21m00Tcm4TlvDq8ikWAM",  # Engaging female
            "data_analysis": "AZnzlk1XvdvUeBnXmlld",  # Professional male
            "deep_analysis": "JBFqnCBsd6RMkjVDRZzb",  # Analytical male
            "closing": "21m00Tcm4TlvDq8ikWAM"  # Friendly female
        }
        return voices.get(segment_type, "JBFqnCBsd6RMkjVDRZzb")
    
    def _get_elevenlabs_key(self) -> str:
        """Get ElevenLabs API key"""
        for k in ["ELEVENLABS_API_KEY", "ELEVEN_LABS_API_KEY", "ELEVEN_API_KEY", "ELEVENLABS_KEY"]:
            v = os.getenv(k, "")
            if v:
                return v
        return ""
    
    def _combine_audio_segments(self, segment_files: List[str], query: str) -> str:
        """Combine audio segments into final podcast"""
        if not segment_files:
            return None
        
        # For now, just return the first segment file
        # In a real implementation, you'd combine them properly
        final_filename = f"enhanced_podcast_{query.replace(' ', '_')}_{int(time.time())}.mp3"
        
        if segment_files:
            # Copy first file as final (placeholder for actual combining)
            import shutil
            shutil.copy(segment_files[0], final_filename)
            return final_filename
        
        return None