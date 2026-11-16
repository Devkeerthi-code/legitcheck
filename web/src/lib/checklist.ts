import type { ChecklistItem } from "./types";

/** Same list the API sends with every verdict, kept here so it still shows when the API is unreachable. */
export const OFFLINE_CHECKLIST: ChecklistItem[] = [
  {
    id: "careers_page",
    title: "Find the company's official careers page",
    detail: "Search for the company yourself instead of using links in the message, and check the role is listed there.",
  },
  {
    id: "never_pay",
    title: "Never pay to get a job",
    detail: "No registration, training, kit or 'refundable' deposit. Real employers pay you, not the other way round.",
  },
  {
    id: "email_domain",
    title: "Check the HR email domain",
    detail: "The sender's address should end in the company's own website domain, not gmail.com, yahoo.com or outlook.com.",
  },
  {
    id: "search_scam",
    title: 'Search the company name with "scam"',
    detail: "Look for other students' experiences and reviews before you reply or share anything.",
  },
  {
    id: "report",
    title: "Report fraud",
    detail: "If you've been asked for money or already paid, report it at cybercrime.gov.in or call the 1930 helpline as soon as possible.",
    link: "https://cybercrime.gov.in",
    link_label: "cybercrime.gov.in",
  },
];
