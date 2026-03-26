from .web_analyzer import WebAnalyzer
from .youtube_analyzer import YouTubeAnalyzer
from .document_analyzer import DocumentAnalyzer

class ContentAnalysis(WebAnalyzer, YouTubeAnalyzer, DocumentAnalyzer):
    pass