// DOM Elements
const resumeTextarea = document.getElementById('resume');
const jdTextarea = document.getElementById('jobDescription');
const analyzeBtn = document.getElementById('analyzeBtn');
const btnText = document.getElementById('btnText');
const loader = document.getElementById('loader');
const resultsSection = document.getElementById('results');

// Character count
resumeTextarea.addEventListener('input', (e) => {
    document.getElementById('resumeCharCount').textContent = `${e.target.value.length} characters`;
});

jdTextarea.addEventListener('input', (e) => {
    document.getElementById('jdCharCount').textContent = `${e.target.value.length} characters`;
});

// Analyze button click
analyzeBtn.addEventListener('click', async () => {
    const resumeText = resumeTextarea.value.trim();
    const jdText = jdTextarea.value.trim();

    // Validation
    if (!resumeText || !jdText) {
        alert('Please paste both resume and job description');
        return;
    }

    if (resumeText.length < 100 || jdText.length < 100) {
        alert('Please paste complete resume and job description (minimum 100 characters each)');
        return;
    }

    // Show loading state
    analyzeBtn.classList.add('loading');
    btnText.textContent = 'Analyzing...';
    resultsSection.classList.add('hidden');

    try {
        // Call API
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                resume: resumeText,
                jobDescription: jdText
            })
        });

        if (!response.ok) {
            throw new Error('Analysis failed');
        }

        const data = await response.json();
        displayResults(data);

    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred during analysis. Please try again.');
    } finally {
        // Reset button
        analyzeBtn.classList.remove('loading');
        btnText.textContent = 'Analyze Match';
    }
});

// Display results
function displayResults(data) {
    // Show results section
    resultsSection.classList.remove('hidden');

    // Overall score
    const scorePercentage = document.getElementById('scorePercentage');
    const scoreCircle = document.getElementById('scoreCircle');
    const scoreMessage = document.getElementById('scoreMessage');
    
    scorePercentage.textContent = data.overallScore;
    const offset = 565.48 - (565.48 * data.overallScore) / 100;
    scoreCircle.style.strokeDashoffset = offset;
    
    // Score color based on percentage
    if (data.overallScore >= 80) {
        scoreCircle.style.stroke = '#10b981';
        scoreMessage.textContent = 'Excellent match! Your resume aligns very well with this job.';
    } else if (data.overallScore >= 60) {
        scoreCircle.style.stroke = '#f59e0b';
        scoreMessage.textContent = 'Good match! Consider adding missing skills to improve.';
    } else {
        scoreCircle.style.stroke = '#ef4444';
        scoreMessage.textContent = 'Low match. Significant improvements needed.';
    }

    // Skills analysis
    displaySkills(data.skillsAnalysis);

    // Experience analysis
    displayExperience(data.experienceAnalysis);

    // Keywords analysis
    displayKeywords(data.keywordsAnalysis);

    // Suggestions
    displaySuggestions(data.suggestions);

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function displaySkills(skills) {
    const matchedContainer = document.getElementById('matchedSkills');
    const missingContainer = document.getElementById('missingSkills');

    // Clear previous results
    matchedContainer.innerHTML = '';
    missingContainer.innerHTML = '';

    // Display matched skills
    skills.matched.forEach(skill => {
        const tag = document.createElement('span');
        tag.className = 'skill-tag matched';
        tag.textContent = skill;
        matchedContainer.appendChild(tag);
    });

    // Display missing skills
    skills.missing.forEach(skill => {
        const tag = document.createElement('span');
        tag.className = 'skill-tag missing';
        tag.textContent = skill;
        missingContainer.appendChild(tag);
    });
}

function displayExperience(experience) {
    const container = document.getElementById('experienceAnalysis');
    container.innerHTML = `
        <p><strong>Required:</strong> ${experience.required}</p>
        <p><strong>Your Experience:</strong> ${experience.found}</p>
        <p><strong>Match Level:</strong> ${experience.matchLevel}</p>
        ${experience.suggestion ? `<p style="color: var(--warning-color); margin-top: 0.5rem;">${experience.suggestion}</p>` : ''}
    `;
}

function displayKeywords(keywords) {
    document.getElementById('foundKeywords').textContent = keywords.found.length;
    document.getElementById('missingKeywords').textContent = keywords.missing.length;

    const keywordsList = document.getElementById('keywordsList');
    keywordsList.innerHTML = '';

    if (keywords.missing.length > 0) {
        const missingDiv = document.createElement('div');
        missingDiv.innerHTML = '<h4 style="margin: 1rem 0 0.5rem;">Important missing keywords:</h4>';
        keywords.missing.slice(0, 10).forEach(keyword => {
            const item = document.createElement('span');
            item.className = 'skill-tag missing';
            item.style.marginRight = '0.5rem';
            item.style.marginBottom = '0.5rem';
            item.style.display = 'inline-block';
            item.textContent = keyword;
            missingDiv.appendChild(item);
        });
        keywordsList.appendChild(missingDiv);
    }
}

function displaySuggestions(suggestions) {
    const container = document.getElementById('suggestions');
    container.innerHTML = '';

    suggestions.forEach(suggestion => {
        const item = document.createElement('div');
        item.className = 'suggestion-item';
        item.innerHTML = `
            <span class="suggestion-priority ${suggestion.priority}">${suggestion.priority.toUpperCase()}</span>
            <p class="suggestion-text">${suggestion.text}</p>
            <p class="suggestion-tip">${suggestion.tip}</p>
        `;
        container.appendChild(item);
    });
}
