import re
import json
import os

class ResumeParser:
    def __init__(self):
        self.skills_keywords = self.load_skills_keywords()
        
    def load_skills_keywords(self):
        # Load from JSON file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(current_dir, 'data', 'common_keywords.json'), 'r') as f:
            return json.load(f)
    
    def parse(self, text):
        text = text.lower()
        
        return {
            'skills': self.extract_skills(text),
            'experience': self.extract_experience(text),
            'education': self.extract_education(text),
            'keywords': self.extract_all_keywords(text)
        }
    
    def extract_skills(self, text):
        skills = []
        
        # Look for skills section
        skills_section = re.search(r'skills?[:\s]*([^\\n]+(?:\\n[^\\n]+)*)', text, re.IGNORECASE)
        if skills_section:
            skills_text = skills_section.group(1)
            # Extract individual skills
            skills_raw = re.findall(r'[a-zA-Z+#\.]+(?:\s+[a-zA-Z+#\.]+)*', skills_text)
            skills.extend([s.strip() for s in skills_raw if len(s.strip()) > 2])
        
        # Also look for common technical skills throughout
        tech_skills = [
            'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'aws', 
            'docker', 'kubernetes', 'git', 'agile', 'machine learning', 'ai',
            'typescript', 'angular', 'vue', 'mongodb', 'postgresql', 'redis',
            'jenkins', 'ci/cd', 'terraform', 'azure', 'gcp', 'html', 'css'
        ]
        
        for skill in tech_skills:
            if skill in text and skill not in skills:
                skills.append(skill)
        
        return list(set(skills))  # Remove duplicates
    
    def extract_experience(self, text):
        # Extract years of experience
        years_pattern = r'(\d+)[\+]?\s*(?:years?|yrs?)\s*(?:of)?\s*experience'
        years_match = re.search(years_pattern, text, re.IGNORECASE)
        
        if years_match:
            return {
                'years': int(years_match.group(1)),
                'text': years_match.group(0)
            }
        
        # Look for experience in work history
        work_sections = re.findall(r'(?:work|experience|employment).*?(?=education|skills|projects|$)', text, re.IGNORECASE | re.DOTALL)
        if work_sections:
            # Count years from date ranges
            date_ranges = re.findall(r'(\d{4})\s*[-–]\s*(\d{4}|present)', text, re.IGNORECASE)
            total_years = 0
            for start, end in date_ranges:
                end_year = 2024 if end.lower() == 'present' else int(end)
                total_years += end_year - int(start)
            
            if total_years > 0:
                return {
                    'years': total_years,
                    'text': f'{total_years} years of work experience'
                }
        
        return {
            'years': 0,
            'text': 'Experience not clearly specified'
        }
    
    def extract_education(self, text):
        education = []
        
        # Common degree patterns
        degrees = re.findall(r'(?:bachelor|master|phd|b\.s\.|m\.s\.|b\.a\.|m\.a\.|mba|b\.tech|m\.tech)[^,\.\n]*', text, re.IGNORECASE)
        education.extend(degrees)
        
        return education
    
    def extract_all_keywords(self, text):
        # Extract all meaningful keywords
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        # Filter common words
        stop_words = {'the', 'and', 'for', 'with', 'from', 'have', 'been', 'this', 'that', 'will', 'can', 'but'}
        keywords = [w for w in words if w not in stop_words]
        return list(set(keywords))


class JDParser:
    def parse(self, text):
        text = text.lower()
        
        return {
            'required_skills': self.extract_required_skills(text),
            'required_experience': self.extract_required_experience(text),
            'education_requirements': self.extract_education_requirements(text),
            'keywords': self.extract_important_keywords(text)
        }
    
    def extract_required_skills(self, text):
        skills = []
        
        # Look for requirements/qualifications section
        req_section = re.search(r'(?:requirements?|qualifications?|skills?)[:\s]*([^\\n]+(?:\\n[^\\n]+)*)', text, re.IGNORECASE)
        
        if req_section:
            req_text = req_section.group(1)
            # Extract skills from bullet points or comma-separated lists
            skills_raw = re.findall(r'[a-zA-Z+#\.]+(?:\s+[a-zA-Z+#\.]+)*', req_text)
            skills.extend([s.strip() for s in skills_raw if len(s.strip()) > 2])
        
        # Look for must-have skills
        must_have = re.findall(r'(?:must have|required|mandatory)[:\s]*([^\.]+)', text, re.IGNORECASE)
        for section in must_have:
            skills_in_section = re.findall(r'[a-zA-Z+#\.]+(?:\s+[a-zA-Z+#\.]+)*', section)
            skills.extend([s.strip() for s in skills_in_section if len(s.strip()) > 2])
        
        # Common technical skills
        tech_skills = re.findall(r'\b(?:python|java|javascript|react|node\.js|sql|aws|docker|kubernetes|git|agile|machine learning|ai|typescript|angular|vue|mongodb|postgresql|redis|jenkins|ci/cd|terraform|azure|gcp|html|css)\b', text, re.IGNORECASE)
        skills.extend(tech_skills)
        
        return list(set([s.lower() for s in skills]))
    
    def extract_required_experience(self, text):
        # Look for experience requirements
        exp_patterns = [
            r'(\d+)[\+]?\s*(?:to|\-|–)?\s*(\d+)?\s*(?:years?|yrs?)\s*(?:of)?\s*experience',
            r'(\d+)[\+]?\s*(?:years?|yrs?)\s*(?:of)?\s*experience',
            r'experience[:\s]*(\d+)[\+]?\s*(?:years?|yrs?)',
        ]
        
        for pattern in exp_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if match.lastindex == 2 and match.group(2):  # Range
                    return {
                        'min_years': int(match.group(1)),
                        'max_years': int(match.group(2)),
                        'text': match.group(0)
                    }
                else:
                    years = int(match.group(1))
                    return {
                        'min_years': years,
                        'max_years': years + 2,  # Assume some flexibility
                        'text': match.group(0)
                    }
        
        return {
            'min_years': 0,
            'max_years': 0,
            'text': 'No specific experience requirement found'
        }
    
    def extract_education_requirements(self, text):
        education = []
        
        # Look for degree requirements
        degrees = re.findall(r'(?:bachelor|master|phd|b\.s\.|m\.s\.|b\.a\.|m\.a\.|mba|b\.tech|m\.tech)[^,\.\n]*', text, re.IGNORECASE)
        education.extend(degrees)
        
        return education
    
    def extract_important_keywords(self, text):
        # Extract important technical and business keywords
        # Remove common words and extract meaningful terms
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Keywords that are typically important in JDs
        important_terms = []
        
        # Technical terms
        tech_terms = re.findall(r'\b(?:api|sdk|framework|database|cloud|server|frontend|backend|fullstack|mobile|web|software|application|platform|system|architecture|design|development|deployment|integration|testing|debugging|optimization|performance|security|scalability)\b', text, re.IGNORECASE)
        important_terms.extend(tech_terms)
        
        # Soft skills
        soft_skills = re.findall(r'\b(?:leadership|communication|team|collaboration|problem-solving|analytical|creative|innovative|strategic|detail-oriented|organized|motivated|proactive)\b', text, re.IGNORECASE)
        important_terms.extend(soft_skills)
        
        return list(set([term.lower() for term in important_terms]))
