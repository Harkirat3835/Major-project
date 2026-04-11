import re
import logging
import nltk
import requests
from bs4 import BeautifulSoup
from readability import Document
from typing import Tuple, Dict, List, Any, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def safe_word_tokenize(text: str) -> List[str]:
    """Tokenize text with a regex fallback when NLTK data is unavailable."""
    try:
        return nltk.word_tokenize(text)
    except LookupError:
        return re.findall(r"[a-zA-Z']+", text)


def get_stop_words() -> set[str]:
    """Return English stopwords with an empty-set fallback."""
    try:
        return set(nltk.corpus.stopwords.words('english'))
    except LookupError:
        logger.warning('NLTK stopwords corpus not available. Continuing without stopword filtering.')
        return set()

class SimpleFakeNewsDetector:
    """Rule-based fake news detector with social and URL heuristics."""

    def __init__(self):
        self.lemmatizer = nltk.stem.WordNetLemmatizer()
        self.stop_words = get_stop_words()
        self.fake_keywords = {
            'shocking', 'unbelievable', 'amazing', 'incredible', 'breaking', 'exclusive',
            'conspiracy', 'hoax', 'fake news', 'deep state', 'illuminati', 'scandal',
            'outrageous', 'bombshell', 'urgent', 'crisis', 'emergency', 'panic',
            'viral', 'clickbait', 'alert', 'must see', "you won't believe"
        }
        self.real_keywords = {
            'according to', 'source:', 'reported by', 'citing', 'reuters', 'ap news',
            'bbc', 'cnn', 'washington post', 'new york times', 'study shows', 'researchers',
            'official', 'statement', 'press release', 'verified', 'confirmed'
        }

    def preprocess_text(self, text: str) -> str:
        """Basic text preprocessing for analysis."""
        if not text:
            return ""

        text = text.lower()
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)

        tokens = safe_word_tokenize(text)
        tokens = [word for word in tokens if word not in self.stop_words and len(word) > 2]

        return ' '.join(tokens)

    def predict(self, text: str, source_type: Optional[str] = None) -> Dict[str, Any]:
        """Make a prediction and score the contents."""
        if not text:
            return {'error': 'No text provided'}

        processed_text = self.preprocess_text(text)
        words = processed_text.split()
        text_lower = text.lower()

        fake_score = 0.0
        real_score = 0.0

        for keyword in self.fake_keywords:
            if keyword in text_lower:
                fake_score += 1

        for keyword in self.real_keywords:
            if keyword in text_lower:
                real_score += 1

        if len(words) < 50:
            fake_score += 0.7

        exclamation_count = text.count('!')
        question_count = text.count('?')

        if exclamation_count > 3:
            fake_score += 0.5
        if question_count > 3:
            fake_score += 0.5

        caps_words = [word for word in text.split() if word.isupper() and len(word) > 3]
        if len(caps_words) > 2:
            fake_score += 0.5

        if source_type == 'social_media':
            fake_score += 0.7
        elif source_type == 'url' and len(words) < 80:
            fake_score += 0.3

        total_score = fake_score + real_score
        if total_score == 0:
            fake_prob = 0.5
            real_prob = 0.5
        else:
            fake_prob = min(max(fake_score / total_score, 0.0), 1.0)
            real_prob = min(max(real_score / total_score, 0.0), 1.0)

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

    def is_social_media(self, text: str) -> bool:
        text_lower = text.lower()
        social_markers = ['@', '#', 'retweet', 'thread', 'followers', 'likes', 'share', 'tweet', 'viral', 'dm']
        if any(marker in text_lower for marker in social_markers):
            return True
        if len(text.split()) < 40 and any(keyword in text_lower for keyword in ['posted', 'shared', 'commented', 'tweeted']):
            return True
        return False

    def is_url(self, text: str) -> bool:
        parsed = urlparse(text.strip())
        return bool(parsed.scheme in ('http', 'https') and parsed.netloc)


# Global detector instance
detector = SimpleFakeNewsDetector()


def extract_text_from_url(url: str) -> str:
    """Fetch readable text from a web URL for analysis."""
    if not url or not isinstance(url, str):
        raise ValueError('URL must be a valid string')

    if not url.lower().startswith(('http://', 'https://')):
        url = f'https://{url.strip()}'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }

    response = requests.get(url, headers=headers, timeout=12)
    response.raise_for_status()

    document = Document(response.text)
    article_html = document.summary()
    soup = BeautifulSoup(article_html, 'html.parser')
    paragraphs = [p.get_text(separator=' ', strip=True) for p in soup.find_all('p') if p.get_text(strip=True)]

    if not paragraphs:
        body = BeautifulSoup(response.text, 'html.parser').body
        paragraphs = [p.get_text(separator=' ', strip=True) for p in body.find_all('p') if p.get_text(strip=True)]

    if not paragraphs:
        raise ValueError('Unable to extract preview text from the provided URL')

    article_text = ' '.join(paragraphs)
    return article_text[:100000]


def classify_input_source(text: str) -> str:
    """Classify the type of input content."""
    if detector.is_url(text):
        return 'url'
    if detector.is_social_media(text):
        return 'social_media'
    return 'article'


def load_model() -> Tuple[Any, Any]:
    """Return the fake news detector instance."""
    return detector, None


def predict_news(model: Any, vectorizer: Any, text: str, source_type: str = 'article') -> Dict[str, Any]:
    """Run a prediction with contextual source awareness."""
    return detector.predict(text, source_type=source_type)


def analyze_fake_indicators(text: str, source_type: str = 'article') -> List[str]:
    """Analyze a text block for fake news signals."""
    reasons = []
    text_lower = text.lower()

    sensational_words = [
        'shocking', 'unbelievable', 'incredible', 'amazing', 'outrageous', 'scandalous',
        'bombshell', 'breaking', 'exclusive', 'urgent', 'alert', 'must see'
    ]
    found_sensational = [word for word in sensational_words if word in text_lower]
    if found_sensational:
        reasons.append(f"Contains sensational language: {', '.join(found_sensational[:3])}")

    conspiracy_words = [
        'conspiracy', 'cover-up', 'deep state', 'illuminati', 'new world order',
        'shadow government', 'hoax', 'false flag'
    ]
    if any(word in text_lower for word in conspiracy_words):
        reasons.append('Contains conspiracy theory language')

    emotional_words = ['terrifying', 'horrifying', 'devastating', 'catastrophic', 'crisis', 'emergency', 'panic', 'outrage']
    if any(word in text_lower for word in emotional_words):
        reasons.append('Uses emotional manipulation tactics')

    source_indicators = [
        'according to', 'source:', 'reported by', 'citing', 'reuters', 'ap news',
        'bbc', 'cnn', 'washington post', 'new york times', 'official', 'confirmed'
    ]
    if not any(indicator in text_lower for indicator in source_indicators):
        reasons.append('Lacks credible source citations')

    informal_indicators = ['omg', 'lol', 'wtf', 'tbh', 'idk', 'brb', 'yolo', 'smh']
    if any(indicator in text_lower for indicator in informal_indicators):
        reasons.append('Contains informal or slang language unusual for news')

    caps_words = [word for word in text.split() if word.isupper() and len(word) > 3]
    if len(caps_words) > 2:
        reasons.append(f'Excessive uppercase emphasis: {", ".join(caps_words[:2])}')

    if text.count('?') > 3:
        reasons.append('Contains excessive questioning and clickbait-style phrasing')
    if text.count('!') > 5:
        reasons.append('Contains excessive exclamation marks')

    if len(text.split()) < 50:
        reasons.append('Message is unusually short for a detailed news report')

    if source_type == 'social_media':
        reasons.append('Social media content can spread rapidly and may lack verification')
    elif source_type == 'url':
        reasons.append('Content was extracted from a URL and analyzed for source credibility')

    word_counts = {}
    for word in text_lower.split():
        normalized = word.strip('.,!?"\'')
        if len(normalized) > 3:
            word_counts[normalized] = word_counts.get(normalized, 0) + 1
    repeated_words = [word for word, count in word_counts.items() if count > 3]
    if repeated_words:
        reasons.append(f'Contains repetitive emphasis: {", ".join(repeated_words[:2])}')

    return reasons[:5]


def clean_text(text: str) -> str:
    """Clean and normalize input text."""
    if not isinstance(text, str):
        raise ValueError('Text must be a string')

    text = text.lower()
    text = re.sub(r'http\S+|www\S+|https\S+', ' ', text)
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    return text
