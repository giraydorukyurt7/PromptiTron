"""API Enums - Copied from models.structured_models for API independence"""
from enum import Enum

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    FILL_BLANK = "fill_blank"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"

class SubjectType(str, Enum):
    MATEMATIK = "matematik"
    FIZIK = "fizik"
    KIMYA = "kimya"
    BIYOLOJI = "biyoloji"
    COGRAFYA = "cografya"
    TARIH = "tarih"
    FELSEFE = "felsefe"
    TURK_DILI_VE_EDEBIYATI = "turk_dili_ve_edebiyati"
    DIN_KULTURU = "din_kulturu"
    INKILAP_VE_ATATURKCULUK = "inkilap_ve_ataturkculuk"

class ExamType(str, Enum):
    TYT = "tyt"
    AYT = "ayt"
    YDT = "ydt"
    MSU = "msu"
    LGS = "lgs"