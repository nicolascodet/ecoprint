import openai
from typing import List, Dict
from datetime import datetime, timedelta
from app.core.config import get_settings

settings = get_settings()
openai.api_key = settings.OPENAI_API_KEY

class AIAnalyzer:
    def __init__(self):
        self.model = "gpt-4"  # or "gpt-3.5-turbo" for faster/cheaper analysis
        
    async def analyze_activities(self, activities: List[Dict]) -> Dict:
        """Analyze user activities and provide insights using ChatGPT."""
        
        # Format activities for the prompt
        activities_text = "\n".join([
            f"- {activity['activity_type']}: {activity['description']}, "
            f"Carbon Impact: {activity['carbon_impact']}kg CO2"
            for activity in activities
        ])
        
        prompt = f"""
        Analyze these user activities and their carbon impact:
        
        {activities_text}
        
        Provide:
        1. Main sources of carbon emissions
        2. Patterns in user behavior
        3. Specific suggestions for reducing carbon footprint
        4. Comparison to average carbon footprint
        5. Projected annual impact if behavior continues
        
        Format the response as JSON with these keys:
        - main_sources
        - patterns
        - suggestions
        - comparison
        - projection
        """
        
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[{
                    "role": "system",
                    "content": "You are an expert environmental analyst specializing in carbon footprint analysis."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return {
                "error": f"AI analysis failed: {str(e)}",
                "main_sources": [],
                "patterns": [],
                "suggestions": ["Unable to generate suggestions at this time"],
                "comparison": "Analysis unavailable",
                "projection": None
            }
    
    async def get_smart_suggestions(self, user_data: Dict) -> List[str]:
        """Generate personalized suggestions based on user's activity patterns."""
        
        total_impact = sum(a['carbon_impact'] for a in user_data['activities'])
        activity_types = set(a['activity_type'] for a in user_data['activities'])
        
        prompt = f"""
        Based on this user's data:
        - Total carbon impact: {total_impact}kg CO2
        - Activity types: {', '.join(activity_types)}
        
        Provide 3-5 specific, actionable suggestions to reduce their carbon footprint.
        Focus on their most impactful activities and consider realistic lifestyle changes.
        Format each suggestion as a separate string in a JSON array.
        """
        
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[{
                    "role": "system",
                    "content": "You are a helpful environmental advisor providing practical suggestions for reducing carbon footprint."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.8,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return ["Unable to generate suggestions at this time"] 