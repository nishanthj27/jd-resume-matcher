from http.server import BaseHTTPRequestHandler
import json
import re
from collections import Counter
import os
import sys

# Add utils to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.parser import ResumeParser, JDParser
from utils.matcher import SkillsMatcher, ExperienceMatcher, KeywordMatcher

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        try:
            # Parse request
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            resume_text = data.get('resume', '')
            jd_text = data.get('jobDescription', '')
            
            # Process texts
            result = self.analyze_match(resume_text, jd_text)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(result).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {'error': str(e)}
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def analyze_match(self, resume_text, jd_text):
        # Parse resume and JD
        resume_parser = ResumeParser()
        jd_parser = JDParser()
        
        resume_data = resume_parser.parse(resume_text)
        jd_data = jd_parser.parse(jd_text)
        
        # Match skills
        skills_matcher = SkillsMatcher()
        skills_analysis = skills_matcher.match(
            resume_data['skills'], 
            jd_data['required_skills']
        )
        
        # Match experience
        exp_matcher = ExperienceMatcher()
        experience_analysis = exp_matcher.match(
            resume_data['experience'], 
            jd_data['required_experience']
        )
        
        # Match keywords
        keyword_matcher = KeywordMatcher()
        keywords_analysis = keyword_matcher.match(
            resume_text, 
            jd_text
        )
        
        # Calculate overall score
        overall_score = self.calculate_overall_score(
            skills_analysis,
            experience_analysis,
            keywords_analysis
        )
        
        # Generate suggestions
        suggestions = self.generate_suggestions(
            skills_analysis,
            experience_analysis,
            keywords_analysis
        )
        
        return {
            'overallScore': overall_score,
            'skillsAnalysis': skills_analysis,
            'experienceAnalysis': experience_analysis,
            'keywordsAnalysis': keywords_analysis,
            'suggestions': suggestions
        }
    
    def calculate_overall_score(self, skills, experience, keywords):
        # Weighted scoring
        skills_score = skills['matchPercentage'] * 0.4
        exp_score = experience['matchPercentage'] * 0.3
        keywords_score = keywords['matchPercentage'] * 0.3
        
        return round(skills_score + exp_score + keywords_score)
    
    def generate_suggestions(self, skills, experience, keywords):
        suggestions = []
        
        # Skills suggestions
        if skills['missing']:
            for skill in skills['missing'][:3]:
                suggestions.append({
                    'priority': 'high',
                    'text': f"Add '{skill}' to your skills section",
                    'tip': f"This is a required skill. Use the exact keyword: {skill}"
                })
        
        # Experience suggestions
        if experience['matchPercentage'] < 80:
            suggestions.append({
                'priority': 'medium',
                'text': "Emphasize your relevant experience",
                'tip': experience.get('suggestion', 'Highlight years of experience in similar roles')
            })
        
        # Keyword suggestions
        if keywords['missing']:
            important_keywords = keywords['missing'][:5]
            suggestions.append({
                'priority': 'medium',
                'text': f"Include these keywords: {', '.join(important_keywords)}",
                'tip': "Naturally incorporate these terms in your experience descriptions"
            })
        
        # ATS suggestions
        suggestions.append({
            'priority': 'low',
            'text': "Ensure ATS compatibility",
            'tip': "Use standard section headers and avoid tables or graphics"
        })
        
        return suggestions[:5]  # Return top 5 suggestions
