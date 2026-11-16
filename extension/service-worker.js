// Holds the text from "Check with LegitCheck" in memory only, until the popup takes it.
// Nothing is written to storage; if the worker is shut down, the text is simply gone.

const MENU_ID = "legitcheck-check-selection";
const POPUP_PATH = "popup.html";

let pendingText = null;

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: MENU_ID,
    title: "Check with LegitCheck",
    contexts: ["selection"],
  });
});

async function openPopupSomehow() {
  try {
    if (chrome.action.openPopup) {
      await chrome.action.openPopup();
      return;
    }
  } catch {
    // openPopup can refuse (no focused window, older Chrome). Fall back to a small window.
  }
  await chrome.windows.create({
    url: chrome.runtime.getURL(`${POPUP_PATH}?window=1`),
    type: "popup",
    width: 380,
    height: 620,
  });
}

chrome.contextMenus.onClicked.addListener((info) => {
  if (info.menuItemId !== MENU_ID) return;
  pendingText = (info.selectionText || "").trim() || null;
  void openPopupSomehow();
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (sender.id !== chrome.runtime.id || message?.type !== "legitcheck:take-pending") return false;
  const text = pendingText;
  pendingText = null;
  sendResponse({ text });
  return false;
});
