const sendBtn = document.getElementById("sendBtn");
const voiceBtn = document.getElementById("voiceBtn");
const chatbox = document.getElementById("chatbox");
const userInput = document.getElementById("userInput");

function appendMessage(sender, text) {
  chatbox.innerHTML += `<p><b>${sender}:</b> ${text}</p>`;
  chatbox.scrollTop = chatbox.scrollHeight;
}

sendBtn.onclick = async () => {
  const query = userInput.value.trim();
  if (!query) return;
  appendMessage("You", query);
  userInput.value = "";

  const res = await fetch("/api/chatbot", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query })
  });
  const data = await res.json();
  appendMessage("Bot", data.response);
};

voiceBtn.onclick = () => {
  const rec = new(window.SpeechRecognition || window.webkitSpeechRecognition)();
  rec.lang = "en-US";
  rec.start();
  rec.onresult = async (event) => {
    const query = event.results[0][0].transcript;
    appendMessage("🎤 You", query);
    const res = await fetch("/api/chatbot", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query })
    });
    const data = await res.json();
    appendMessage("Bot", data.response);
  };
};
