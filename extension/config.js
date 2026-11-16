// The only file to edit when you deploy.
//
// API_URL:      where the LegitCheck API runs (no trailing slash).
// WEB_APP_URL:  where the web app runs; "Open full report" opens WEB_APP_URL + "#text=...".
//
// When you change API_URL to a deployed address (e.g. https://legitcheck-api.onrender.com),
// also replace "host_permissions" in manifest.json with that origin, e.g.
//   "host_permissions": ["https://legitcheck-api.onrender.com/*"]
// then reload the extension in chrome://extensions.
export const API_URL = "http://127.0.0.1:8000";
export const WEB_APP_URL = "http://localhost:3000/";

export const MIN_TEXT = 20;
export const MAX_TEXT = 20000;
