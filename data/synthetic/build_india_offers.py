"""Writes india_offers.jsonl: SYNTHETIC Indian-style job/internship messages.

Every message, company, email and link here is invented for testing. Domains that imitate
real brands are deliberate examples of lookalike links. This set is NEVER used for training
(train.py asserts that). `split`: "dev" examples were used while writing the rules and in
unit tests; "holdout" examples were written afterwards and are only used for evaluation.

Run: python data/synthetic/build_india_offers.py
"""

from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).with_name("india_offers.jsonl")

# (split, label, category, text, email, url, expected_rules)
EXAMPLES: list[tuple[str, str, str, str, str, str, list[str]]] = [
    # ---------------- dev: scams ----------------
    (
        "dev",
        "scam",
        "registration_fee",
        "Dear Candidate, Congratulations! You have been shortlisted for the Work From Home Data Entry "
        "Internship at Nexora Talent Solutions. Stipend Rs 18,000 per month. To confirm your seat, pay "
        "the registration fee of Rs 1,999 to our UPI id nexora.hr@okaxis today. Offer valid only today.",
        "",
        "",
        ["payment_request", "pressure_to_decide"],
    ),
    (
        "dev",
        "scam",
        "security_deposit",
        "Greetings from Brightpath Infra Pvt Ltd. You are selected for the post of Office Assistant. "
        "A refundable security deposit of Rs 5,500 is required for your laptop and ID card. The amount "
        "will be returned with your first salary. Kindly transfer within 2 hours to block your joining date.",
        "",
        "",
        ["payment_request", "pressure_to_decide"],
    ),
    (
        "dev",
        "scam",
        "telegram_hr",
        "Hi, I am Priya from the HR team of Zentrix Digital. We saw your resume on a job portal. We "
        "have a part-time online job. Please contact our HR on Telegram @zentrix_hr_priya for details "
        "and your interview.",
        "",
        "",
        ["messaging_only_contact"],
    ),
    (
        "dev",
        "scam",
        "task_scam",
        "Earn Rs 3000 daily from your phone! Simple task: like YouTube videos and subscribe to channels. "
        "Rs 50 per like, paid instantly on UPI. No experience needed. Join our Telegram group t.me/earnwithlikes "
        "to start.",
        "",
        "",
        ["task_scam", "unrealistic_pay", "messaging_only_contact"],
    ),
    (
        "dev",
        "scam",
        "aadhaar_early",
        "Your profile is selected for Customer Support Executive at Vantara BPO Services. Before the "
        "interview please send your Aadhaar card, PAN card and bank account details on WhatsApp 98765 43210 "
        "for verification.",
        "",
        "",
        ["id_or_bank_request", "messaging_only_contact"],
    ),
    (
        "dev",
        "scam",
        "gmail_hr",
        "Offer Letter - Junior Analyst, Corvanta Technologies Pvt Ltd. Joining date 1st of next month. "
        "Kindly reply to this email to accept. Regards, HR Department, corvanta.hr.recruit@gmail.com",
        "corvanta.hr.recruit@gmail.com",
        "",
        ["personal_email"],
    ),
    (
        "dev",
        "scam",
        "lookalike_link",
        "Infosys Off-Campus Drive 2026 for freshers. Package 6.5 LPA. Register now at "
        "https://infosys-careers-hiring.in/apply before seats are filled. Limited seats.",
        "",
        "https://infosys-careers-hiring.in/apply",
        ["suspicious_link", "pressure_to_decide"],
    ),
    (
        "dev",
        "scam",
        "short_link",
        "Amazon is hiring work from home associates. Salary Rs 35,000 per week. Apply here: bit.ly/amzn-wfh-jobs "
        "Hurry, only 10 slots left!",
        "",
        "",
        ["suspicious_link", "unrealistic_pay", "pressure_to_decide"],
    ),
    (
        "dev",
        "scam",
        "training_fee",
        "Congratulations on clearing the online test for Kavex Software Solutions. As per company policy, "
        "selected candidates must complete a 15-day paid training. Training fees of Rs 12,500 must be paid "
        "before joining. The fee is fully refundable after 6 months of service.",
        "",
        "",
        ["payment_request"],
    ),
    (
        "dev",
        "scam",
        "otp",
        "Hello, this is from Skyline Staffing. To activate your salary account for the new job, please share "
        "the OTP you just received on your mobile. Do it immediately or your offer will be cancelled.",
        "",
        "",
        ["id_or_bank_request", "pressure_to_decide"],
    ),
    (
        "dev",
        "scam",
        "hinglish_fee",
        "Namaste! Aapka selection ho gaya hai Data Entry job ke liye at Ujjwal Services. Joining ke liye "
        "Rs 1500 registration fees jama karna hoga. Payment ke baad offer letter milega. WhatsApp karein 91234 56789.",
        "",
        "",
        ["payment_request", "messaging_only_contact"],
    ),
    (
        "dev",
        "scam",
        "hotel_reviews",
        "Part-time job: rate hotels on Google Maps and earn Rs 150 per review. Daily income Rs 4,000. For "
        "higher commission per task you can buy prepaid tasks. Contact our mentor on WhatsApp.",
        "",
        "",
        ["task_scam", "unrealistic_pay", "messaging_only_contact"],
    ),
    (
        "dev",
        "scam",
        "kit_fee",
        "Dear Applicant, your application for Field Sales Intern at Ruvan Agro Ventures is approved. "
        "Please pay the kit charges of Rs 799 for your welcome kit and certificate. Payment link: "
        "tinyurl.com/ruvan-kit",
        "",
        "",
        ["payment_request", "suspicious_link"],
    ),
    (
        "dev",
        "scam",
        "unrealistic",
        "Earn Rs 2 lakh per month working just 2 hours a day from home. No interview required, no "
        "experience needed, earn guaranteed income. Limited vacancies. Message on Telegram to join.",
        "",
        "",
        ["unrealistic_pay", "pressure_to_decide", "messaging_only_contact"],
    ),
    (
        "dev",
        "scam",
        "interview_fee",
        "Your interview with Halcyon Global Services is scheduled for tomorrow. An interview slot booking "
        "amount of Rs 499 is mandatory. Pay via Paytm to 9876501234 and send the screenshot to the HR.",
        "",
        "",
        ["payment_request"],
    ),
    (
        "dev",
        "scam",
        "bank_details",
        "Congratulations! You have been selected as a Remote Typing Associate at Lumora Works. Send your "
        "bank account number, IFSC and a cancelled cheque today so we can release your joining bonus.",
        "",
        "",
        ["id_or_bank_request"],
    ),
    (
        "dev",
        "scam",
        "lookalike_tcs",
        "TCS NextStep urgent recruitment. Candidates must upload documents at https://tcs-nextstep-portal.co/upload "
        "within 24 hours, otherwise the offer will be withdrawn.",
        "",
        "",
        ["suspicious_link", "pressure_to_decide"],
    ),
    (
        "dev",
        "scam",
        "yahoo_offer",
        "Dear Student, Orbix Learning Pvt Ltd is offering a paid internship in digital marketing. "
        "Stipend Rs 15,000 per month. Mail your CV to orbix.internships@yahoo.com. Note: a document "
        "verification fee of Rs 350 applies.",
        "orbix.internships@yahoo.com",
        "",
        ["personal_email", "payment_request"],
    ),
    (
        "dev",
        "scam",
        "ip_link",
        "Wipro freshers hiring 2026. Fill the form at http://103.45.67.89/wipro-form to get your offer "
        "letter. Process closes today.",
        "",
        "",
        ["suspicious_link"],
    ),
    (
        "dev",
        "scam",
        "reels",
        "Instagram reels liking job! Like posts and reels of brands and earn Rs 30 per like. Rs 900 to "
        "Rs 3,500 daily. Ping us on WhatsApp to get the task link.",
        "",
        "",
        ["task_scam", "unrealistic_pay", "messaging_only_contact"],
    ),
    (
        "dev",
        "scam",
        "deposit_upi",
        "Selected for Warehouse Supervisor at Tarang Logistics. Deposit Rs 2,000 as caution deposit. "
        "Send to UPI id tarang.jobs@ybl and WhatsApp the receipt.",
        "",
        "",
        ["payment_request", "messaging_only_contact"],
    ),
    (
        "dev",
        "scam",
        "pan_whatsapp",
        "Hi, HR Neha here from Fintrive Consulting. To process your offer, share your PAN card and Aadhaar "
        "photo on WhatsApp. Also reply with your date of birth.",
        "",
        "",
        ["id_or_bank_request", "messaging_only_contact"],
    ),
    (
        "dev",
        "scam",
        "certification_fee",
        "Congratulations, your internship at Qubitra Labs is confirmed! Interns receive a certificate "
        "after 1 month. Certification charges of Rs 1,200 are payable in advance. Seats are limited.",
        "",
        "",
        ["payment_request", "pressure_to_decide"],
    ),
    (
        "dev",
        "scam",
        "outlook_hr",
        "We are hiring for Accenture backend roles through our partner Velmora HR. Send your resume to "
        "accenture.hiring.velmora@outlook.com and pay the processing fee of Rs 999.",
        "",
        "",
        ["personal_email", "payment_request"],
    ),
    # ---------------- dev: genuine ----------------
    (
        "dev",
        "genuine",
        "internship",
        "Software Engineering Intern at Kestrel Analytics Pvt Ltd, Bengaluru (hybrid). Stipend Rs 25,000 per "
        "month. You'll work on data pipelines in Python with a mentor. There is no registration fee or deposit "
        "at any stage. Apply at https://kestrelanalytics.in/careers. Interviews happen on Google Meet.",
        "careers@kestrelanalytics.in",
        "https://kestrelanalytics.in/careers",
        [],
    ),
    (
        "dev",
        "genuine",
        "offer_letter",
        "Dear Ananya, we are pleased to offer you the role of Associate Product Designer at Meridian Labs. "
        "Your annual CTC will be Rs 7,20,000. Please review the attached offer letter and reply by 25th with "
        "any questions. On your first day, HR will help you complete payroll forms on the HR portal. Regards, "
        "Rohit, Talent Team, rohit.k@meridianlabs.co.in",
        "rohit.k@meridianlabs.co.in",
        "",
        [],
    ),
    (
        "dev",
        "genuine",
        "campus",
        "Campus placement notice: Ostrava Systems will visit on 12 March for the 2026 batch. Roles: Graduate "
        "Engineer Trainee. Eligibility: 60% throughout. Rounds: aptitude test, technical interview and HR "
        "interview. Register through the placement cell portal.",
        "",
        "",
        [],
    ),
    (
        "dev",
        "genuine",
        "startup",
        "Hiring a frontend intern (React) for 3 months at Patchwork Studio, Pune. Remote friendly. Stipend "
        "Rs 12,000 per month. Send your GitHub link to jobs@patchworkstudio.in. We reply to everyone within "
        "a week.",
        "jobs@patchworkstudio.in",
        "",
        [],
    ),
    (
        "dev",
        "genuine",
        "retail",
        "Store Associate (part-time) at Greenleaf Grocers, Koramangala. Weekend shifts, Rs 180 per hour. "
        "Walk in with your resume on Saturday between 10am and 1pm, or email hr@greenleafgrocers.in.",
        "",
        "",
        [],
    ),
    (
        "dev",
        "genuine",
        "research",
        "Summer research fellowship at the Institute for Coastal Studies. 8 weeks, monthly fellowship of "
        "Rs 10,000. Selection based on statement of purpose and a short interview. Last date to apply: 30 April.",
        "",
        "",
        [],
    ),
    (
        "dev",
        "genuine",
        "bank_after_joining",
        "Welcome to Arcadia Fintech! Before your start date you will get a link to our HR portal. After "
        "joining, you'll submit your PAN and bank account details there so payroll can be set up. Never share "
        "OTPs with anyone, including us.",
        "people@arcadiafintech.com",
        "",
        [],
    ),
    (
        "dev",
        "genuine",
        "whatsapp_plus_email",
        "Thanks for applying to Lattice Robotics. Your interview is on Thursday at 11am. The calendar invite "
        "comes from recruiting@latticerobotics.in. You can also WhatsApp me if you're running late. - Kavya, Recruiter",
        "recruiting@latticerobotics.in",
        "",
        [],
    ),
    (
        "dev",
        "genuine",
        "urgent_hiring",
        "Urgent hiring: Accounts Executive at Sharma & Rao Chartered Accountants, Chennai. 1-3 years experience "
        "with Tally and GST filing. Salary Rs 25,000 to Rs 32,000 per month. Send CV to careers@sharmarao.co.in.",
        "",
        "",
        [],
    ),
    (
        "dev",
        "genuine",
        "ngo",
        "Volunteer program coordinator (paid, 6 months) at Saathi Foundation. Monthly honorarium Rs 20,000. "
        "We never ask candidates for money. Apply via saathifoundation.org/careers.",
        "",
        "",
        [],
    ),
    (
        "dev",
        "genuine",
        "big_company_real_domain",
        "Thank you for your interest in Wipro. Your application ID is WP-48213. Track your status at "
        "https://careers.wipro.com. Wipro does not charge any fee at any stage of recruitment.",
        "",
        "https://careers.wipro.com",
        [],
    ),
    (
        "dev",
        "genuine",
        "teaching",
        "Part-time maths tutor needed for Class 10 students at Bright Minds Tuition Centre, Mysuru. Evening "
        "batches, Rs 400 per hour. Demo class before selection. Call the centre during working hours.",
        "",
        "",
        [],
    ),
    (
        "dev",
        "genuine",
        "delivery",
        "Delivery partner openings at QuickKart, Hyderabad. Flexible hours, weekly payout based on orders. "
        "You'll need a two-wheeler and a driving licence. Sign up in the QuickKart Partner app; there is no "
        "joining fee.",
        "",
        "",
        [],
    ),
    (
        "dev",
        "genuine",
        "design_freelance",
        "Freelance illustrator wanted for a children's book at Inkwell Press. Fixed fee Rs 60,000 for 20 "
        "illustrations, half in advance. Share your portfolio with editor@inkwellpress.in.",
        "",
        "",
        [],
    ),
    (
        "dev",
        "genuine",
        "mba_intern",
        "Marketing intern for 2 months at Coastline Foods, Kochi. Stipend Rs 15,000 per month plus travel. "
        "Two interview rounds with the brand manager. Email internships@coastlinefoods.in.",
        "",
        "",
        [],
    ),
    (
        "dev",
        "genuine",
        "govt",
        "The district library invites applications for a contract Library Assistant post. Consolidated pay "
        "as per government norms. Applications by post only. No application fee.",
        "",
        "",
        [],
    ),
    # ---------------- holdout: scams (not used to write the rules) ----------------
    (
        "holdout",
        "scam",
        "fee_variant",
        "Hello! You're shortlisted for an Online Survey Executive role with Prasthan Media. Stipend 22k/month. "
        "One small step left: onboarding charges Rs. 1,450 (adjusted in first stipend). Do it soon, we close "
        "the batch tonight.",
        "",
        "",
        ["payment_request"],
    ),
    (
        "holdout",
        "scam",
        "task_variant",
        "Hi dear, we need people for movie rating work. Each rating gives Rs 120. Most members make 5k+ daily. "
        "To unlock VIP tasks a recharge task of Rs 1,000 is needed. Message me here only.",
        "",
        "",
        ["task_scam"],
    ),
    (
        "holdout",
        "scam",
        "telegram_variant",
        "Your CV was forwarded by our partner. We'd like to offer you a remote role in Zylo Commerce. All "
        "communication happens on Telegram, add HR Rahul: t.me/zylo_rahul_hr",
        "",
        "",
        ["messaging_only_contact"],
    ),
    (
        "holdout",
        "scam",
        "id_variant",
        "Selected! For background verification kindly upload aadhar copy, PAN number and your passbook "
        "photo on this chat before interview.",
        "",
        "",
        ["id_or_bank_request"],
    ),
    (
        "holdout",
        "scam",
        "gmail_variant",
        "From: Talent Acquisition, Hexalore Technologies <hexalore.careers.in@gmail.com> Subject: Offer of "
        "employment - Trainee Engineer. Please confirm acceptance by return mail.",
        "",
        "",
        ["personal_email"],
    ),
    (
        "holdout",
        "scam",
        "lookalike_variant",
        "Flipkart seasonal hiring! Packers and pickers needed, Rs 28,000 per month. Register: "
        "https://flipkart-jobs-india.online/register",
        "",
        "",
        ["suspicious_link"],
    ),
    (
        "holdout",
        "scam",
        "deposit_variant",
        "Dear selected candidate, for hostel and training arrangements a refundable amount of Rs 4,000 "
        "must be deposited at the earliest. Bank details will be shared on WhatsApp.",
        "",
        "",
        ["payment_request"],
    ),
    (
        "holdout",
        "scam",
        "pay_variant",
        "Typing work from home. Earn $500 per week typing simple documents. No skills required. Payment "
        "every Friday.",
        "",
        "",
        ["unrealistic_pay"],
    ),
    (
        "holdout",
        "scam",
        "pressure_variant",
        "Final reminder: your offer from Orinth Solutions expires in 3 hours. Confirm immediately by paying "
        "the joining kit amount. Only 2 positions remaining.",
        "",
        "",
        ["pressure_to_decide", "payment_request"],
    ),
    (
        "holdout",
        "scam",
        "shortlink_variant",
        "HCL walk-in drive for freshers this week. Get your hall ticket from cutt.ly/hcl-walkin-2026",
        "",
        "",
        ["suspicious_link"],
    ),
    (
        "holdout",
        "scam",
        "upi_pin",
        "To receive your first stipend through our payroll system, enter your UPI PIN when the collect "
        "request appears. Zevora Interns Team.",
        "",
        "",
        ["id_or_bank_request"],
    ),
    (
        "holdout",
        "scam",
        "hinglish_variant",
        "Bhai part time kaam hai, ghar baithe 2000 roz kamao. Bas pehle 500 rupees bhejo registration ke liye. "
        "Telegram pe message karo.",
        "",
        "",
        ["payment_request", "messaging_only_contact"],
    ),
    (
        "holdout",
        "scam",
        "mixed",
        "Accenture-partner hiring: Customer Care (non-voice). CTC 4.2 LPA. Selected candidates pay a one-time "
        "laptop deposit. Contact: accenture.partner.desk@hotmail.com",
        "",
        "",
        ["personal_email", "payment_request"],
    ),
    (
        "holdout",
        "scam",
        "quiet",
        "Congratulations, you have been selected without interview for the Remote Assistant role at Kairo "
        "Systems. We will guide you on the next steps on WhatsApp.",
        "",
        "",
        ["messaging_only_contact"],
    ),
    # ---------------- holdout: genuine ----------------
    (
        "holdout",
        "genuine",
        "intern",
        "Data Science Intern, Riverstone Health (Chennai, on-site). 6 months, stipend Rs 30,000 per month. "
        "Apply through riverstonehealth.in/careers. Shortlisted candidates take a take-home task and two "
        "interviews.",
        "",
        "",
        [],
    ),
    (
        "holdout",
        "genuine",
        "offer",
        "Hi Arjun, following your interviews, we're happy to offer you the Junior Developer role at Tidewater "
        "Software. Offer letter attached; please read it and let us know by Friday next week. talent@tidewater.dev",
        "",
        "",
        [],
    ),
    (
        "holdout",
        "genuine",
        "ops",
        "Operations Executive at Banyan Couriers, Indore. Salary Rs 20,000-24,000 per month plus PF. Two "
        "rounds: written test and manager interview at our office. hr@banyancouriers.in",
        "",
        "",
        [],
    ),
    (
        "holdout",
        "genuine",
        "events",
        "Event volunteers (paid) for the city book fair, 3 days, Rs 800 per day plus meals. Register on the "
        "fair's official website. Volunteers never pay anything to take part.",
        "",
        "",
        [],
    ),
    (
        "holdout",
        "genuine",
        "remote",
        "Remote content writer (part-time) at Folio & Co. Rs 2 per word, around 10 articles a month. "
        "Paid writing test. Send samples to editors@folioandco.in.",
        "",
        "",
        [],
    ),
    (
        "holdout",
        "genuine",
        "lab",
        "Lab assistant (project) at the university biotechnology department. Fellowship as per DST norms. "
        "Walk-in interview on Monday at 10am with original certificates.",
        "",
        "",
        [],
    ),
    (
        "holdout",
        "genuine",
        "sales",
        "Inside Sales Associate at Northwind CRM, Gurugram. Fixed Rs 28,000 per month plus incentives. "
        "We'll schedule a call from our official number after you apply on our careers page.",
        "",
        "",
        [],
    ),
    (
        "holdout",
        "genuine",
        "documents_after",
        "Welcome aboard! On your first day at Pinecrest Engineering please bring your PAN card and a "
        "cancelled cheque for payroll. HR will collect them at the office.",
        "",
        "",
        [],
    ),
    (
        "holdout",
        "genuine",
        "hackathon",
        "Hackathon winners get a paid internship at Solace AI, Rs 40,000 per month for 3 months. Free to "
        "enter. Details on the official event page.",
        "",
        "",
        [],
    ),
    (
        "holdout",
        "genuine",
        "teacher",
        "Primary school teacher (English) at Little Oaks School, Mangaluru. B.Ed required. Salary as per "
        "school norms. Demo lesson and interview with the principal.",
        "",
        "",
        [],
    ),
]


def main() -> None:
    with OUT.open("w", encoding="utf-8", newline="\n") as handle:
        for i, (split, label, category, text, email, url, rules) in enumerate(EXAMPLES, 1):
            record = {
                "id": f"syn-{i:03d}",
                "synthetic": True,
                "split": split,
                "label": label,
                "category": category,
                "text": text,
                "email": email,
                "url": url,
                "expected_rules": rules,
            }
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"wrote {len(EXAMPLES)} synthetic examples to {OUT}")


if __name__ == "__main__":
    main()
