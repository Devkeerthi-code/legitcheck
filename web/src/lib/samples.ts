/** FICTIONAL examples. Every company, person, email and link here is invented. */
export interface Sample {
  id: "scam" | "genuine";
  text: string;
  email: string;
  url: string;
}

export const SAMPLES: Record<Sample["id"], Sample> = {
  scam: {
    id: "scam",
    text: [
      "Dear Candidate,",
      "Congratulations! You are selected for a Work From Home internship at Zentrova Infotech (fictional). Stipend Rs 30,000/month. No interview required.",
      "To confirm your seat, pay the training fee of Rs 2,499 and send your Aadhaar and PAN card photos to HR today.",
      "For joining, message HR on Telegram @zentrova_hr.",
      "Pay here: bit.ly/ztv-join",
      "This offer is valid only today. Seats are limited.",
    ].join("\n"),
    email: "zentrova.careers.hr@gmail.com",
    url: "",
  },
  genuine: {
    id: "genuine",
    text: [
      "Hi Ananya,",
      "Thank you for interviewing with Meridian Labs (fictional) last Thursday. We are happy to offer you a 6-month Frontend Intern role, starting 6 January, with a monthly stipend of Rs 20,000.",
      "The offer letter is attached. Please review it and reply with any questions by Friday 20 December. If you accept, our HR team will send the onboarding forms through our HR portal.",
      "Regards,",
      "Rohit Menon, Talent team, Meridian Labs",
    ].join("\n"),
    email: "talent@meridianlabs.in",
    url: "https://meridianlabs.in/careers",
  },
};
