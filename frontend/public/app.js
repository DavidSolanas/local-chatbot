document.addEventListener("DOMContentLoaded", function () {
  const chatWindow = document.getElementById("messages"); // match HTML
  const userInput = document.getElementById("prompt");    // match HTML
  const sendButton = document.getElementById("send");    // match HTML

  sendButton.addEventListener("click", sendMessage);
  userInput.addEventListener("keypress", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault(); // prevent newline
      sendMessage();
    }
  });

  function appendMessage(sender, message) {
    const messageElement = document.createElement("div");
    messageElement.classList.add("message", sender);
    messageElement.innerText = message;
    chatWindow.appendChild(messageElement);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    return messageElement;
  }

  async function sendMessage() {
    const userText = userInput.value.trim();
    if (!userText) return;

    // Append user message
    appendMessage("user", userText);
    userInput.value = "";

    // Append empty assistant message for streaming
    const assistantMessageElement = appendMessage("assistant", "");

    try {
      const response = await fetch("/api/chat/stream", {  // match backend route
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          message: userText,
          temperature: 0.7,
          max_new_tokens: 512,
          top_p: 0.95
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let done = false;

      while (!done) {
        const { value, done: streamDone } = await reader.read();
        done = streamDone;
        if (value) {
          const chunk = decoder.decode(value, { stream: true });
          assistantMessageElement.innerText += chunk;
          chatWindow.scrollTop = chatWindow.scrollHeight;
        }
      }
    } catch (error) {
      console.error("Error:", error);
      assistantMessageElement.innerText = "Error getting response. Please try again.";
    }
  }
});
