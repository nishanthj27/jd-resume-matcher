import json
import os
from collections import Counter

class SkillsMatcher:
    def __init__(self):
        self.synonyms = self.load_synonyms()
    
    def load_synonyms(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(current_dir, 'data', 'skills_synonyms.json'), 'r') as f:
            return json.load(f)
    
    def match(self, resume_skills, jd_skills):
        matched = []
        missing = []
        
        # Normalize skills
        resume_skills_lower = [s.lower() for s in resume_skills]
        
        for jd_skill in jd_skills:
            jd_skill_lower = jd_skill.lower()
            
            # Direct match
            if jd_skill_lower in resume_skills_lower:
                matched.append(jd_skill)
                continue
            
            # Synonym match
            found = False
            if jd_skill_lower in self.synonyms:
                for synonym in self.synonyms[jd_skill_lower]:
                    if synonym in resume_skills_lower:
                        matched.append(jd_skill)
                        found = True
                        break
            
            # Partial match (e.g., "python" matches "python programming")
            if not found:
                for resume_skill in resume_skills_lower:
                    if jd_skill_lower in resume_skill or resume_skill in jd_skill_lower:
                        matched.append(jd_skill)
                        found = True
                        break
            
            if not found:
                missing.append(jd_skill)
        
        match_percentage = (len(matched) / len(jd_skills) * 100) if jd_skills else 0
        
        return {
            'matched': matched,
            'missing': missing,
            'matchPercentage': round(match_percentage),
            'totalRequired': len(jd_skills),
            'totalMatched': len(matched)
        }


class ExperienceMatcher:
    def match(self, resume_experience, jd_experience):
        resume_years = resume_experience.get('years', 0)
        jd_min_years = jd_experience.get('min_years', 0)
        jd_max_years = jd_experience.get('max_years', 0)
        
        # Calculate match
        if resume_years >= jd_min_years:
            match_percentage = 100
            match_level = "Exceeds requirements"
            suggestion = None
        elif resume_years >= jd_min_years - 1:
            match_percentage = 80
            match_level = "Close to requirements"
            suggestion = f"Consider highlighting relevant projects to compensate for {jd_min_years - resume_years} year gap"
        elif resume_years >= jd_min_years - 2:
            match_percentage = 60
            match_level = "Below requirements"
            suggestion = f"You need {jd_min_years - resume_years} more years of experience. Focus on relevant achievements"
        else:
            match_percentage = 40
            match_level = "Significantly below requirements"
            suggestion = f"Gap of {jd_min_years - resume_years} years. Consider gaining more experience or applying for junior positions"
        
        return {
            'matchPercentage': match_percentage,
            'matchLevel': match_level,
            'required': f"{jd_min_years}+ years",
            'found': f"{resume_years} years",
            'suggestion': suggestion
        }


class KeywordMatcher:
    def match(self, resume_text, jd_text):
        # Extract meaningful keywords from JD
        jd_keywords = self.extract_keywords(jd_text)
        resume_keywords = self.extract_keywords(resume_text)
        
        # Convert to lowercase for matching
        jd_keywords_lower = set(k.lower() for k in jd_keywords)
        resume_keywords_lower = set(k.lower() for k in resume_keywords)
        
        # Find matches
        matched_keywords = jd_keywords_lower & resume_keywords_lower
        missing_keywords = jd_keywords_lower - resume_keywords_lower
        
        # Calculate percentage
        match_percentage = (len(matched_keywords) / len(jd_keywords_lower) * 100) if jd_keywords_lower else 0
        
        return {
            'found': list(matched_keywords),
            'missing': list(missing_keywords)[:20],  # Top 20 missing
            'matchPercentage': round(match_percentage),
            'totalKeywords': len(jd_keywords_lower),
            'matchedCount': len(matched_keywords)
        }
    
    def extract_keywords(self, text):
        import re
        
        # Remove common words
        stop_words = {
            'the', 'is', 'at', 'which', 'on', 'a', 'an', 'as', 'and', 'or', 'but',
            'in', 'with', 'to', 'for', 'of', 'from', 'by', 'about', 'into',
            'will', 'can', 'may', 'must', 'shall', 'should', 'could', 'would',
            'have', 'has', 'had', 'having', 'be', 'been', 'being', 'am', 'are', 'was', 'were',
            'do', 'does', 'did', 'doing', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'this', 'that', 'these', 'those', 'there', 'here', 'where', 'when', 'what',
            'who', 'why', 'how', 'all', 'each', 'every', 'some', 'any', 'many', 'much',
            'more', 'most', 'less', 'least', 'few', 'fewer', 'very', 'just', 'only'
        }
        
        # Extract words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Filter out stop words and get important keywords
        keywords = []
        for word in words:
            if word not in stop_words and len(word) > 2:
                keywords.append(word)
        
        # Count frequency and get top keywords
        word_freq = Counter(keywords)
        top_keywords = [word for word, count in word_freq.most_common(50) if count > 1]
        
        # Also include important technical terms that appear even once
        tech_terms = [
            'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue',
            'node', 'django', 'flask', 'spring', 'sql', 'nosql', 'mongodb', 'postgresql',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'github',
            'api', 'rest', 'graphql', 'microservices', 'agile', 'scrum', 'devops',
            'machine', 'learning', 'ai', 'data', 'analytics', 'cloud', 'security'
        ]
        
        for term in tech_terms:
            if term in text.lower() and term not in top_keywords:
                top_keywords.append(term)
        
        return top_keywords
