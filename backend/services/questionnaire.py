
"""
Question bank for the Social Media Privacy Risk Assessment Framework.

This module contains educational, self-reported questions only.
It never requests passwords, contact details, exact locations, private
messages, or access to social media accounts.
"""

from copy import deepcopy


RESPONSE_OPTIONS = {
    "visibility": ["PUBLIC", "FRIENDS", "PRIVATE", "NOT SURE"],
    "frequency": ["YES", "NO", "SOMETIMES", "NOT SURE"],
    "status": ["ENABLED", "DISABLED", "SOMETIMES", "NOT SURE"],
    "awareness": ["YES", "NO", "PARTIALLY", "NOT SURE"],
}


def _question(
    question_id,
    category,
    prompt,
    input_type,
    options,
    feature_key,
    help_text,
):
    """Create one consistently structured questionnaire item."""
    return {
        "id": question_id,
        "category": category,
        "prompt": prompt,
        "input_type": input_type,
        "options": list(options),
        "feature_key": feature_key,
        "help_text": help_text,
        "required": True,
    }


QUESTION_BANK = [
    # 1. Profile Visibility
    _question("Q001", "profile", "How visible is your main social media profile?", "single_select", RESPONSE_OPTIONS["visibility"], "profile_visibility", "Consider whether people outside your connections can view your profile."),
    _question("Q002", "profile", "Can people who are not connected to you view your profile photo?", "single_select", RESPONSE_OPTIONS["visibility"], "profile_photo_visibility", "Think about the visibility setting for your profile photo."),
    _question("Q003", "profile", "Can people outside your connections view your profile information?", "single_select", RESPONSE_OPTIONS["visibility"], "profile_information_visibility", "This includes general profile details, not the details themselves."),
    _question("Q004", "profile", "Do you review your profile visibility settings periodically?", "single_select", RESPONSE_OPTIONS["frequency"], "profile_settings_review", "Regular reviews can help you identify unexpected visibility changes."),
    _question("Q005", "profile", "Are your profile discovery settings restricted to your preferred audience?", "single_select", RESPONSE_OPTIONS["frequency"], "profile_discovery_control", "Consider whether strangers can easily discover your profile."),

    # 2. Personal Information
    _question("Q006", "personal_information", "Is your date-of-birth visibility restricted?", "single_select", RESPONSE_OPTIONS["visibility"], "dob_visibility", "Do not enter your actual date of birth."),
    _question("Q007", "personal_information", "Is your phone-number visibility restricted?", "single_select", RESPONSE_OPTIONS["visibility"], "phone_visibility", "Do not enter or share your phone number in this assessment."),
    _question("Q008", "personal_information", "Is your email-address visibility restricted?", "single_select", RESPONSE_OPTIONS["visibility"], "email_visibility", "Do not enter your email address."),
    _question("Q009", "personal_information", "Do you avoid publishing sensitive personal details on your profile?", "single_select", RESPONSE_OPTIONS["frequency"], "sensitive_profile_details", "Examples include financial, identity, or other sensitive personal details."),
    _question("Q010", "personal_information", "Do you check whether profile fields reveal more information than intended?", "single_select", RESPONSE_OPTIONS["frequency"], "profile_field_review", "Review the types of information displayed, not the actual values."),

    # 3. Location Privacy
    _question("Q011", "location", "Is location sharing disabled when you do not need it?", "single_select", RESPONSE_OPTIONS["status"], "location_sharing", "Consider location sharing within social media applications."),
    _question("Q012", "location", "Do you avoid publishing real-time location updates publicly?", "single_select", RESPONSE_OPTIONS["frequency"], "realtime_location_posts", "This question does not ask for your current or previous location."),
    _question("Q013", "location", "Do you review location permissions granted to social media apps?", "single_select", RESPONSE_OPTIONS["frequency"], "location_permission_review", "Check permissions through your device settings."),
    _question("Q014", "location", "Are location tags on your posts restricted to your intended audience?", "single_select", RESPONSE_OPTIONS["visibility"], "location_tag_visibility", "Think about the audience that can see location-related post tags."),
    _question("Q015", "location", "Do you avoid revealing routine locations through repeated public posts?", "single_select", RESPONSE_OPTIONS["frequency"], "routine_location_exposure", "Consider whether repeated posts could reveal predictable routines."),

    # 4. Posts and Content
    _question("Q016", "content", "What is the usual audience for your posts?", "single_select", RESPONSE_OPTIONS["visibility"], "post_visibility", "Consider your typical post audience rather than one specific post."),
    _question("Q017", "content", "Do you review the audience before publishing a post?", "single_select", RESPONSE_OPTIONS["frequency"], "post_audience_review", "Check the audience selector before sharing content."),
    _question("Q018", "content", "Do you avoid sharing sensitive documents or identity-related information in posts?", "single_select", RESPONSE_OPTIONS["frequency"], "sensitive_content_sharing", "Never upload an actual document for this assessment."),
    _question("Q019", "content", "Do you review older public posts for unnecessary personal exposure?", "single_select", RESPONSE_OPTIONS["frequency"], "old_post_review", "Consider reviewing older content and its audience settings."),
    _question("Q020", "content", "Do you consider possible privacy consequences before sharing photos or videos?", "single_select", RESPONSE_OPTIONS["frequency"], "media_sharing_awareness", "Consider background details and information that media may reveal."),

    # 5. Friends and Followers
    _question("Q021", "connections", "Can anyone send you a connection or follow request?", "single_select", RESPONSE_OPTIONS["frequency"], "open_connection_requests", "Consider whether connection requests are limited to known or approved people."),
    _question("Q022", "connections", "Do you review unfamiliar connection requests before accepting them?", "single_select", RESPONSE_OPTIONS["frequency"], "connection_request_review", "Avoid accepting requests automatically."),
    _question("Q023", "connections", "Do you periodically review your existing connections or followers?", "single_select", RESPONSE_OPTIONS["frequency"], "connection_list_review", "You do not need to provide names or account details."),
    _question("Q024", "connections", "Are your connections or followers lists restricted to your intended audience?", "single_select", RESPONSE_OPTIONS["visibility"], "connections_list_visibility", "Consider whether strangers can view your connections list."),
    _question("Q025", "connections", "Do you avoid accepting suspicious or impersonating accounts?", "single_select", RESPONSE_OPTIONS["frequency"], "suspicious_connection_avoidance", "Look for unusual requests or accounts pretending to be someone else."),

    # 6. Tagging and Mentions
    _question("Q026", "tagging", "Do you control who can tag you in posts?", "single_select", RESPONSE_OPTIONS["status"], "tagging_control", "Review tagging permissions in your account settings."),
    _question("Q027", "tagging", "Is tag review enabled before tagged posts appear on your profile?", "single_select", RESPONSE_OPTIONS["status"], "tag_review", "Some platforms allow you to approve tags before they appear."),
    _question("Q028", "tagging", "Can anyone mention your account in public posts?", "single_select", RESPONSE_OPTIONS["frequency"], "open_mentions", "Consider whether mention permissions are restricted."),
    _question("Q029", "tagging", "Do you review tags and mentions that appear on your profile?", "single_select", RESPONSE_OPTIONS["frequency"], "tag_mention_review", "Review unwanted or unexpected tags and mentions."),
    _question("Q030", "tagging", "Do you remove tags that reveal information you do not want to share?", "single_select", RESPONSE_OPTIONS["frequency"], "unwanted_tag_removal", "Consider tags that may reveal personal associations or activities."),

    # 7. Account Security
    _question("Q031", "account_security", "Do you use a strong, unique password for your social media accounts?", "single_select", RESPONSE_OPTIONS["frequency"], "strong_unique_password", "Never enter or share your actual password."),
    _question("Q032", "account_security", "Is multi-factor authentication enabled?", "single_select", RESPONSE_OPTIONS["status"], "multi_factor_authentication", "This may include an authenticator app, security key, or other second factor."),
    _question("Q033", "account_security", "Do you review active sessions and logged-in devices?", "single_select", RESPONSE_OPTIONS["frequency"], "active_session_review", "Review sessions through the platform's official security settings."),
    _question("Q034", "account_security", "Do you keep account recovery options up to date?", "single_select", RESPONSE_OPTIONS["frequency"], "recovery_options_review", "Do not enter recovery codes, phone numbers, or email addresses here."),
    _question("Q035", "account_security", "Do you avoid logging in through suspicious links or untrusted pages?", "single_select", RESPONSE_OPTIONS["frequency"], "suspicious_login_avoidance", "Access your account through the official app or website."),

    # 8. Third-Party Applications
    _question("Q036", "third_party_apps", "Do you review applications connected to your social media accounts?", "single_select", RESPONSE_OPTIONS["frequency"], "connected_apps_review", "Review connected apps through official account settings."),
    _question("Q037", "third_party_apps", "Do you remove third-party apps that you no longer use?", "single_select", RESPONSE_OPTIONS["frequency"], "unused_apps_removal", "Remove access that is no longer needed."),
    _question("Q038", "third_party_apps", "Do you check requested permissions before connecting a third-party application?", "single_select", RESPONSE_OPTIONS["frequency"], "app_permission_review", "Consider whether requested permissions are relevant to the service."),
    _question("Q039", "third_party_apps", "Do you avoid granting unnecessary account permissions to external applications?", "single_select", RESPONSE_OPTIONS["frequency"], "unnecessary_app_permissions", "Grant only permissions that are necessary and appropriate."),
    _question("Q040", "third_party_apps", "Do you verify that an application is trustworthy before connecting your account?", "single_select", RESPONSE_OPTIONS["frequency"], "app_trust_verification", "Consider the provider, reputation, and official source of the application."),

    # 9. Messaging and Social Engineering
    _question("Q041", "social_engineering", "Do you avoid opening unexpected links received through messages?", "single_select", RESPONSE_OPTIONS["frequency"], "unexpected_link_avoidance", "Be cautious of unfamiliar links, even when a message looks convincing."),
    _question("Q042", "social_engineering", "Do you verify unusual requests for money or information through another trusted channel?", "single_select", RESPONSE_OPTIONS["frequency"], "request_verification", "Impersonation scams may come from accounts that appear familiar."),
    _question("Q043", "social_engineering", "Do you avoid sharing verification codes or one-time passwords with others?", "single_select", RESPONSE_OPTIONS["frequency"], "verification_code_protection", "Never enter or share a real verification code in this assessment."),
    _question("Q044", "social_engineering", "Do you check the identity of unfamiliar people before responding to sensitive requests?", "single_select", RESPONSE_OPTIONS["frequency"], "sender_identity_verification", "Be cautious when someone requests personal or account information."),
    _question("Q045", "social_engineering", "Are your message privacy settings restricted to your preferred audience?", "single_select", RESPONSE_OPTIONS["visibility"], "message_privacy_settings", "Consider who can send you messages or message requests."),

    # 10. Digital Footprint
    _question("Q046", "digital_footprint", "Do you periodically review your public digital footprint?", "single_select", RESPONSE_OPTIONS["frequency"], "digital_footprint_review", "Review information that you have intentionally made publicly visible."),
    _question("Q047", "digital_footprint", "Do you avoid reusing the same public username across all online services?", "single_select", RESPONSE_OPTIONS["frequency"], "username_reuse", "Reusing identifiers can make it easier to link different public profiles."),
    _question("Q048", "digital_footprint", "Do you review old accounts that you no longer use?", "single_select", RESPONSE_OPTIONS["frequency"], "old_account_review", "Consider closing or securing unused accounts where appropriate."),
    _question("Q049", "digital_footprint", "Do you check whether your public content reveals more than you intended?", "single_select", RESPONSE_OPTIONS["frequency"], "public_content_exposure_review", "Consider information that can be inferred from public content."),
    _question("Q050", "digital_footprint", "Do you understand that deleted online content may still exist in copies or archives?", "single_select", RESPONSE_OPTIONS["awareness"], "deletion_awareness", "Deletion from one platform does not guarantee removal of every copy."),
]


def get_all_questions():
    """Return a copy of the complete question bank."""
    return deepcopy(QUESTION_BANK)


def get_questions_by_category(category):
    """Return questions for one category, or an empty list if unknown."""
    normalized_category = str(category).strip().lower()
    return [
        deepcopy(question)
        for question in QUESTION_BANK
        if question["category"] == normalized_category
    ]


def get_questionnaire_summary():
    """Return basic questionnaire metadata."""
    category_counts = {}

    for question in QUESTION_BANK:
        category = question["category"]
        category_counts[category] = category_counts.get(category, 0) + 1

    return {
        "questionnaire_name": "Social Media Privacy Risk Assessment",
        "total_questions": len(QUESTION_BANK),
        "total_categories": len(category_counts),
        "minimum_required_questions": 40,
        "category_counts": category_counts,
        "response_types": sorted(
            {question["input_type"] for question in QUESTION_BANK}
        ),
    }


def get_question_by_id(question_id):
    """Return one question by its ID, or None if it does not exist."""
    normalized_id = str(question_id).strip().upper()

    for question in QUESTION_BANK:
        if question["id"] == normalized_id:
            return deepcopy(question)

    return None