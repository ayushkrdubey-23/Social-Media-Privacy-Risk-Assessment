
"""
Central configuration for the Social Media Privacy
Risk Assessment Framework.

All risk scores represent assessed exposure.
A higher score means higher privacy or security risk.
"""

# =====================================================
# PROJECT INFORMATION
# =====================================================

PROJECT_NAME = "Social Media Privacy Risk Assessment Framework"

PROJECT_VERSION = "1.0.0"

PROJECT_TYPE = "Defensive Cybersecurity"

RISK_SCORE_MIN = 0

RISK_SCORE_MAX = 100


# =====================================================
# PRIVACY RISK CATEGORIES
# =====================================================

RISK_CATEGORIES = {
    "profile": {
        "name": "Profile Exposure",
        "weight": 10,
        "description": "Public profile visibility and discoverability."
    },

    "personal_information": {
        "name": "Personal Information",
        "weight": 15,
        "description": "Exposure of contact and identity-related information."
    },

    "location": {
        "name": "Location Exposure",
        "weight": 15,
        "description": "Location sharing, check-ins and travel disclosures."
    },

    "content": {
        "name": "Content Exposure",
        "weight": 10,
        "description": "Public posts and potentially sensitive content."
    },

    "connections": {
        "name": "Connection Risk",
        "weight": 10,
        "description": "Unknown followers and connection management."
    },

    "tagging": {
        "name": "Tagging Risk",
        "weight": 5,
        "description": "Tagging, mentions and approval controls."
    },

    "account_security": {
        "name": "Account Security",
        "weight": 15,
        "description": "Authentication and account protection practices."
    },

    "third_party_apps": {
        "name": "Third-Party Application Risk",
        "weight": 5,
        "description": "Connected applications and permission reviews."
    },

    "social_engineering": {
        "name": "Social Engineering",
        "weight": 10,
        "description": "Awareness of suspicious messages and manipulation."
    },

    "digital_footprint": {
        "name": "Digital Footprint",
        "weight": 5,
        "description": "Historical posts and privacy-review practices."
    }
}


# =====================================================
# RISK LEVEL THRESHOLDS
# =====================================================

RISK_LEVELS = {
    "LOW": {
        "min": 0,
        "max": 20,
        "description": "Relatively low assessed exposure."
    },

    "MODERATE": {
        "min": 21,
        "max": 40,
        "description": "Some privacy weaknesses require attention."
    },

    "HIGH": {
        "min": 41,
        "max": 70,
        "description": "Significant privacy or security weaknesses."
    },

    "CRITICAL": {
        "min": 71,
        "max": 100,
        "description": "Very high assessed exposure requiring priority action."
    }
}


# =====================================================
# RECOMMENDATION PRIORITIES
# =====================================================

RECOMMENDATION_PRIORITIES = [
    "IMMEDIATE",
    "IMPORTANT",
    "GOOD PRACTICE"
]


# =====================================================
# QUESTIONNAIRE CONFIGURATION
# =====================================================

QUESTIONNAIRE_CATEGORIES = [
    "Profile Visibility",
    "Personal Information",
    "Location Privacy",
    "Posts and Content",
    "Friends and Followers",
    "Tagging and Mentions",
    "Authentication and Account Security",
    "Third-Party Applications",
    "Messaging and Social Engineering",
    "Digital Footprint"
]

MINIMUM_QUESTION_COUNT = 40


# =====================================================
# ALLOWED QUESTIONNAIRE RESPONSES
# =====================================================

ALLOWED_RESPONSES = [
    "YES",
    "NO",
    "SOMETIMES",
    "NOT SURE",
    "PUBLIC",
    "FRIENDS",
    "PRIVATE"
]


# =====================================================
# PRIVACY-FIRST APPLICATION SETTINGS
# =====================================================

PRIVACY_SETTINGS = {
    "allow_real_profile_scraping": False,
    "allow_private_account_access": False,
    "allow_account_enumeration": False,
    "allow_real_person_tracking": False,
    "allow_sensitive_information_collection": False,
    "use_synthetic_dataset": True,
    "use_self_reported_assessments": True,
    "store_sensitive_responses": False
}


# =====================================================
# DATABASE CONFIGURATION
# =====================================================

DATABASE_CONFIG = {
    "engine": "SQLite",
    "store_passwords": False,
    "store_phone_numbers": False,
    "store_email_addresses": False,
    "store_home_addresses": False,
    "store_exact_locations": False,
    "store_private_messages": False
}


# =====================================================
# FRAMEWORK DISCLAIMERS
# =====================================================

FRAMEWORK_DISCLAIMER = (
    "This is an educational privacy-risk assessment framework. "
    "Its scores are based on self-reported responses and "
    "configurable educational assumptions. They do not guarantee "
    "whether an account will or will not be compromised."
)
