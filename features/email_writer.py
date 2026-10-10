import os
import datetime
import subprocess
import logging
from typing import Tuple, Dict

from config import NOTES_DIR
from voice.text_to_speech import speak

logger = logging.getLogger("JARVIS.EmailWriter")

EMAIL_TEMPLATES: Dict[str, Dict[str, str]] = {
    "sick_leave": {
        "subject": "Application for Sick Leave",
        "body": (
            "To,\n"
            "The Class Teacher / Department Coordinator,\n"
            "[Department Name],\n"
            "[College / Institution Name]\n\n"
            "Date: [Current Date]\n\n"
            "Subject: Application for Sick Leave\n\n"
            "Respected Sir/Madam,\n\n"
            "I am writing to inform you that I am unwell and suffering from [Fever/Illness] since [Start Date]. "
            "My doctor has advised me to rest for [Number of Days] days. Therefore, I will not be able to attend classes from [Start Date] to [End Date].\n\n"
            "I request you to kindly grant me leave for the mentioned period. I will ensure to cover the missed academic work upon my return. "
            "Medical certificate is attached herewith for your reference.\n\n"
            "Thanking you.\n\n"
            "Yours sincerely,\n"
            "[Your Full Name]\n"
            "Roll No: [Your Roll / ID Number]\n"
            "Branch / Semester: [Your Branch & Semester]\n"
            "Contact No: [Your Phone Number]\n"
        )
    },
    "hod_leave": {
        "subject": "Permission Request for Absence / Leave",
        "body": (
            "To,\n"
            "The Head of Department (HOD),\n"
            "[Department Name],\n"
            "[College / Institution Name]\n\n"
            "Date: [Current Date]\n\n"
            "Subject: Permission Request for Leave of Absence\n\n"
            "Respected Sir/Madam,\n\n"
            "I am writing to formally request leave from [Start Date] to [End Date] due to [Reason: Personal Reason / Family Event / Medical Emergency]. "
            "I have informed my class coordinator and ensured that my coursework and lab submissions will be completed.\n\n"
            "I request you to kindly approve my leave application.\n\n"
            "Thanking you.\n\n"
            "Yours obediently,\n"
            "[Your Full Name]\n"
            "Roll No: [Your Roll / ID Number]\n"
            "Department: [Your Department]\n"
        )
    },
    "seminar_permission": {
        "subject": "Request for Permission to Attend Seminar / Workshop",
        "body": (
            "To,\n"
            "The Head of Department / Seminar Coordinator,\n"
            "[Department Name],\n"
            "[College / Institution Name]\n\n"
            "Date: [Current Date]\n\n"
            "Subject: Request for Permission to Attend Seminar / Workshop\n\n"
            "Respected Sir/Madam,\n\n"
            "I would like to seek permission to attend a seminar/workshop titled '[Seminar/Workshop Title]' scheduled to be held on [Event Date] at [Venue / Organization]. "
            "Attending this event will greatly enhance my academic knowledge and practical skills in [Subject / Domain].\n\n"
            "I request you to kindly grant me permission to attend the seminar and mark my attendance accordingly.\n\n"
            "Thanking you.\n\n"
            "Yours faithfully,\n"
            "[Your Full Name]\n"
            "Roll No: [Your Roll / ID Number]\n"
            "Department / Semester: [Your Department]\n"
        )
    },
    "assignment_extension": {
        "subject": "Request for Extension of Assignment Submission Date",
        "body": (
            "To,\n"
            "The Course Instructor / Professor,\n"
            "[Subject Name],\n"
            "[Department Name]\n\n"
            "Date: [Current Date]\n\n"
            "Subject: Request for Extension of Assignment Submission Date for [Subject / Course Name]\n\n"
            "Respected Professor,\n\n"
            "I am writing to request a short extension for submitting the assignment on '[Assignment Topic]'. "
            "Due to [Reason: Unavoidable Health Issue / Technical Difficulty / Overlapping Exams], I require additional time to complete the work with appropriate quality.\n\n"
            "I request you to kindly extend my submission deadline to [Proposed Submission Date]. I assure you that I will submit the completed assignment on or before the requested date.\n\n"
            "Thanking you for your understanding.\n\n"
            "Yours sincerely,\n"
            "[Your Full Name]\n"
            "Roll No: [Your Roll / ID Number]\n"
            "Course: [Course / Subject Name]\n"
        )
    },
    "general_college": {
        "subject": "Formal Application / Request to College Authority",
        "body": (
            "To,\n"
            "The Concerned Authority / Principal,\n"
            "[College / Institution Name]\n\n"
            "Date: [Current Date]\n\n"
            "Subject: Application Regarding [Purpose / Request]\n\n"
            "Respected Sir/Madam,\n\n"
            "I am writing to formally request your approval regarding [Brief Details of Request]. "
            "I have attached the necessary supporting documentation for your review.\n\n"
            "I request you to kindly consider my application and do the needful at the earliest.\n\n"
            "Thanking you.\n\n"
            "Yours sincerely,\n"
            "[Your Full Name]\n"
            "Roll No: [Your Roll / ID Number]\n"
            "Department: [Your Department]\n"
        )
    }
}

def generate_email_draft(prompt_topic: str, speaker_role: str = "Boss") -> Tuple[bool, str]:
    """
    Generate formal email draft based on topic, fill placeholders,
    save to draft file, and open in Windows Notepad.
    NEVER sends the email.
    """
    clean_topic = prompt_topic.lower().strip() if prompt_topic else ""
    logger.info(f"Generating email draft for topic: '{clean_topic}'")

    # Select appropriate template
    if "sick" in clean_topic or "fever" in clean_topic or "medical" in clean_topic:
        template_key = "sick_leave"
        topic_desc = "sick leave"
    elif "hod" in clean_topic or "leave request" in clean_topic:
        template_key = "hod_leave"
        topic_desc = "leave request to HOD"
    elif "seminar" in clean_topic or "workshop" in clean_topic or "conference" in clean_topic:
        template_key = "seminar_permission"
        topic_desc = "seminar permission"
    elif "assignment" in clean_topic or "extension" in clean_topic or "project" in clean_topic:
        template_key = "assignment_extension"
        topic_desc = "assignment extension"
    else:
        template_key = "general_college"
        topic_desc = "college request"

    template = EMAIL_TEMPLATES[template_key]
    today_str = datetime.datetime.now().strftime("%d %B %Y")
    
    body_formatted = template["body"].replace("[Current Date]", today_str)
    
    draft_content = (
        f"==================================================\n"
        f"SUBJECT: {template['subject']}\n"
        f"==================================================\n\n"
        f"{body_formatted}\n"
        f"==================================================\n"
        f"[NOTE: Draft generated by JARVIS. Edit placeholders before sending.]\n"
    )

    try:
        NOTES_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"email_draft_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        draft_filepath = NOTES_DIR / filename

        with open(draft_filepath, "w", encoding="utf-8") as f:
            f.write(draft_content)

        logger.info(f"Email draft saved to {draft_filepath}. Opening Notepad...")
        
        # Open in Notepad safely
        if os.name == "nt":
            subprocess.Popen(["notepad.exe", str(draft_filepath)])
        else:
            subprocess.Popen(["xdg-open", str(draft_filepath)])

        msg = f"I have generated your email draft for {topic_desc} and opened it in Notepad, {speaker_role}."
        speak(msg)
        return True, msg

    except Exception as e:
        logger.error(f"Error generating email draft: {e}")
        msg = f"Sorry {speaker_role}, I encountered an error while generating your email draft."
        speak(msg)
        return False, msg
