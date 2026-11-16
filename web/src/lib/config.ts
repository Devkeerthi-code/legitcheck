export const API_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/+$/, "");

export const MIN_TEXT = 20;
export const MAX_TEXT = 20_000;

/** Short messages lean on the rules; the API says so in model_note. Used for the input hint only. */
export const SHORT_MESSAGE_WORDS = 60;

export const LANGUAGES = [
  { value: "en", label: "English" },
  { value: "hi", label: "हिन्दी (Hindi)" },
  { value: "ta", label: "தமிழ் (Tamil)" },
  { value: "kn", label: "ಕನ್ನಡ (Kannada)" },
  { value: "te", label: "తెలుగు (Telugu)" },
] as const;
