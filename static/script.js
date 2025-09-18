// Page switching
const homePage = document.getElementById("home");
const chatPage = document.getElementById("chat");
document.getElementById("start-chat").addEventListener("click", () => {
  homePage.classList.remove("active");
  chatPage.classList.add("active");
});
document.getElementById("back-home").addEventListener("click", () => {
  chatPage.classList.remove("active");
  homePage.classList.add("active");
});

// Scroll animations for sections
const sections = document.querySelectorAll("section.audience");
const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const index = [...sections].indexOf(entry.target);
      anime({
        targets: entry.target,
        opacity: [0, 1],
        translateX: index % 2 === 0 ? [-100, 0] : [100, 0],
        scale: [0.95, 1],
        easing: "easeOutExpo",
        duration: 1200
      });
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.2 });
sections.forEach(section => observer.observe(section));

// Chat logic
const chatWindow = document.getElementById("chat-window");
const queryForm = document.getElementById("query-form");
const queryInput = document.getElementById("query");

function addMessage(text, sender, citation = null) {
  const msg = document.createElement("div");
  msg.classList.add("message", sender);
  msg.textContent = text;
  if (citation) {
    const cite = document.createElement("div");
    cite.classList.add("citation");
    cite.textContent = `📖 Cited: ${citation}`;
    msg.appendChild(cite);
  }
  chatWindow.appendChild(msg);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

// Helper: format AI text with paragraphs, bold sections, and bullets
function formatAnswerText(text) {
  const container = document.createElement("div");
  const paragraphs = text.split(/\n{2,}/); // split double-newline paragraphs

  paragraphs.forEach(para => {
    const sections = para.match(/(Article|Section)\s*\d+/gi);
    if (sections && sections.length > 1) {
      const ul = document.createElement("ul");
      sections.forEach(sec => {
        const li = document.createElement("li");
        li.innerHTML = para.replace(sec, `<strong>${sec}</strong>`);
        li.style.marginBottom = "6px";
        ul.appendChild(li);
      });
      container.appendChild(ul);
    } else {
      const p = document.createElement("p");
      p.innerHTML = para.replace(/(Article|Section)\s*\d+/gi, match => `<strong>${match}</strong>`);
      p.style.textIndent = "20px";
      p.style.marginBottom = "12px";
      container.appendChild(p);
    }
  });

  return container;
}

async function typeMessage(text, sender, citation = null) {
  const msg = document.createElement("div");
  msg.classList.add("message", sender);
  chatWindow.appendChild(msg);

  // Append formatted AI text
  const formattedContainer = formatAnswerText(text);
  msg.appendChild(formattedContainer);

  if (citation) {
    const cite = document.createElement("div");
    cite.classList.add("citation");
    cite.textContent = `📖 Cited: ${citation}`;
    msg.appendChild(cite);
  }

  chatWindow.scrollTop = chatWindow.scrollHeight;
}

// Smooth scrolling utility for chat window
function scrollChatToBottom() {
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

// Handle form submit with FastAPI call
queryForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const query = queryInput.value.trim();
  if (!query) return;

  addMessage(query, "user");
  queryInput.value = "";

  // Show typing/loader message
  const typingMsg = document.createElement("div");
  typingMsg.classList.add("message", "agent");
  typingMsg.textContent = "⏳ Generating response...";
  chatWindow.appendChild(typingMsg);
  scrollChatToBottom();

  try {
    const formData = new FormData();
    formData.append("query", query);

    const res = await fetch("/ask", {
      method: "POST",
      body: formData
    });

    const data = await res.json();
    typingMsg.remove();

    // Display formatted answer
    await typeMessage(data.answer || "⚠️ No answer generated.", "agent", data.citation || null);

  } catch (error) {
    typingMsg.remove();
    addMessage("⚠️ Error connecting to the server.", "agent");
  }
});
