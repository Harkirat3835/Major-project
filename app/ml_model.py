import os
import pickle
import re
import logging
import numpy as np
import nltk
from typing import Tuple, Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# Download NLTK data if not present
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

class SimpleFakeNewsDetector:
    """Simplified fake news detector that works without scikit-learn"""

    def __init__(self):
        self.lemmatizer = nltk.stem.WordNetLemmatizer()
        self.stop_words = set(nltk.corpus.stopwords.words('english'))
        self.fake_keywords = {
            'shocking', 'unbelievable', 'amazing', 'incredible', 'breaking', 'exclusive',
            'conspiracy', 'hoax', 'fake news', 'deep state', 'illuminati', 'scandal',
            'outrageous', 'bombshell', 'urgent', 'crisis', 'emergency', 'panic'
        }
        self.real_keywords = {
            'according to', 'source:', 'reported by', 'citing', 'reuters', 'ap news',
            'bbc', 'cnn', 'washington post', 'new york times', 'study shows', 'researchers'
        }

    def preprocess_text(self, text: str) -> str:
        """Basic text preprocessing"""
        if not text:
            return ""

        # Convert to lowercase
        text = text.lower()

        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)

        # Remove special characters and numbers
        text = re.sub(r'[^a-zA-Z\s]', '', text)

        # Tokenize and basic cleaning
        tokens = nltk.word_tokenize(text)
        tokens = [word for word in tokens if word not in self.stop_words and len(word) > 2]

        return ' '.join(tokens)

    def predict(self, text: str) -> Dict[str, Any]:
        """Simple rule-based prediction"""
        if not text:
            return {'error': 'No text provided'}

        processed_text = self.preprocess_text(text)
        words = processed_text.split()
        text_lower = text.lower()

        # Count fake and real indicators
        fake_score = 0
        real_score = 0

        # Keyword-based scoring
        for keyword in self.fake_keywords:
            if keyword in text_lower:
                fake_score += 1

        for keyword in self.real_keywords:
            if keyword in text_lower:
                real_score += 1

        # Length-based scoring (very short articles might be suspicious)
        if len(words) < 50:
            fake_score += 0.5

        # Punctuation-based scoring
        exclamation_count = text.count('!')
        question_count = text.count('?')

        if exclamation_count > 3:
            fake_score += 0.5
        if question_count > 3:
            fake_score += 0.5

        # All caps words
        caps_words = [word for word in text.split() if word.isupper() and len(word) > 3]
        if len(caps_words) > 2:
            fake_score += 0.5

        # Calculate probabilities
        total_score = fake_score + real_score
        if total_score == 0:
            fake_prob = 0.5
            real_prob = 0.5
        else:
            fake_prob = fake_score / total_score
            real_prob = real_score / total_score

        # Determine prediction
        prediction = 'Fake' if fake_prob > real_prob else 'Real'
        confidence = max(fake_prob, real_prob) * 100

        return {
            'prediction': prediction,
            'confidence': round(confidence, 2),
            'probabilities': {
                'real': round(real_prob * 100, 2),
                'fake': round(fake_prob * 100, 2)
            }
        }

# Global detector instance
detector = SimpleFakeNewsDetector()

def load_model() -> Tuple[Any, Any]:
    """Return the simple detector (no actual model loading needed)"""
    return detector, None

def predict_news(model: Any, vectorizer: Any, text: str) -> Dict[str, Any]:
    """Make prediction using the simple detector"""
    return detector.predict(text)

def analyze_fake_indicators(text: str) -> List[str]:
    """Analyze text for indicators that suggest fake news"""
    reasons = []
    text_lower = text.lower()

    # Check for sensational language
    sensational_words = ['shocking', 'unbelievable', 'incredible', 'amazing', 'outrageous', 'scandalous', 'bombshell', 'breaking', 'exclusive', 'urgent']
    found_sensational = [word for word in sensational_words if word in text_lower]
    if found_sensational:
        reasons.append(f"Contains sensational words: {', '.join(found_sensational[:3])}")

    # Check for conspiracy keywords
    conspiracy_words = ['conspiracy', 'cover-up', 'deep state', 'illuminati', 'new world order', 'shadow government', 'hoax', 'false flag']
    if any(word in text_lower for word in conspiracy_words):
        reasons.append("Contains conspiracy theory language")

    # Check for emotional manipulation
    emotional_words = ['terrifying', 'horrifying', 'devastating', 'catastrophic', 'crisis', 'emergency', 'panic', 'outrage']
    if any(word in text_lower for word in emotional_words):
        reasons.append("Uses emotional manipulation tactics")

    # Check for lack of sources
    source_indicators = ['according to', 'source:', 'reported by', 'citing', 'reuters', 'ap news', 'bbc', 'cnn', 'washington post', 'new york times']
    has_sources = any(indicator in text_lower for indicator in source_indicators)
    if not has_sources:
        reasons.append("Lacks credible source citations")

    # Check for poor grammar or informal language
    informal_indicators = ['omg', 'lol', 'wtf', 'tbh', 'idk', 'brb', 'yolo', 'smh']
    if any(indicator in text_lower for indicator in informal_indicators):
        reasons.append("Contains informal or slang language unusual for news")

    # Check for all caps words (shouting)
    words = text.split()
    caps_words = [word for word in words if word.isupper() and len(word) > 3]
    if len(caps_words) > 2:
        reasons.append(f"Contains excessive use of capital letters: {', '.join(caps_words[:2])}")

    # Check for question marks (may indicate doubt or clickbait)
    question_count = text.count('?')
    if question_count > 3:
        reasons.append(f"Contains excessive questioning ({question_count} question marks)")

    # Check for exclamation marks
    exclamation_count = text.count('!')
    if exclamation_count > 5:
        reasons.append(f"Contains excessive exclamation marks ({exclamation_count})")

    # Check for text length (very short articles may be suspicious)
    word_count = len(text.split())
    if word_count < 50:
        reasons.append(f"Article is unusually short ({word_count} words) for a news piece")

    # Check for repeated words (emphasis)
    word_counts = {}
    for word in text_lower.split():
        word = word.strip('.,!?')
        if len(word) > 3:
            word_counts[word] = word_counts.get(word, 0) + 1

    repeated_words = [word for word, count in word_counts.items() if count > 3]
    if repeated_words:
        reasons.append(f"Contains excessive repetition: {', '.join(repeated_words[:2])}")

    # Check for clickbait patterns
    clickbait_patterns = ['you won\'t believe', 'this will blow your mind', 'what happened next', 'watch this', 'must see']
    if any(pattern in text_lower for pattern in clickbait_patterns):
        reasons.append("Contains clickbait language patterns")

    # Check for biased language
    biased_words = ['liberal', 'conservative', 'left-wing', 'right-wing', 'fake news', 'mainstream media', 'deep state']
    if any(word in text_lower for word in biased_words):
        reasons.append("Contains politically biased language")

    return reasons[:5]  # Limit to top 5 reasons


def clean_text(text: str) -> str:
    """Clean and normalize input text."""
    if not isinstance(text, str):
        raise ValueError('Text must be a string')

    text = text.lower()
    text = re.sub(r'http\S+|www\S+|https\S+', ' ', text)
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    return text