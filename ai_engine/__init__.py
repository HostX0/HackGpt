from .advanced_engine import (
    AdvancedAIEngine,
    AnalysisResult,
    PatternRecognizer,
    VulnerabilityCorrelator,
    ContextManager,
)


def get_advanced_ai_engine():
    """Initialize and return the advanced AI engine"""
    return AdvancedAIEngine()


__all__ = [
    "AdvancedAIEngine",
    "AnalysisResult",
    "PatternRecognizer",
    "VulnerabilityCorrelator",
    "ContextManager",
    "get_advanced_ai_engine",
]
