const STEPS = {
  input: {
    badge: "1",
    title: "User Input",
    description:
      "The user pastes raw transaction text — bank statements, SMS alerts, or expense summaries — into the Analysis page.",
    tech: "Natural Language",
    input: "Raw text",
    output: "text field",
  },
  parse: {
    badge: "2",
    title: "Parser Agent",
    description:
      "The Groq LLM (llama-3.3-70b) extracts structured transactions with amount, category, and merchant from unstructured text.",
    tech: "Groq LLM",
    input: "Raw text",
    output: "transactions[]",
  },
  breakdown: {
    badge: "3",
    title: "Breakdown Node",
    description:
      "Aggregates parsed transactions by category to produce a spending breakdown used for allocation and RAG queries.",
    tech: "Python Analytics",
    input: "transactions[]",
    output: "breakdown{}",
  },
  profile: {
    badge: "4a",
    title: "Profile Agent",
    description:
      "Fetches the saved user profile from MongoDB — income, age, risk appetite, and financial goals.",
    tech: "MongoDB",
    input: "User ID",
    output: "profile{}",
  },
  history: {
    badge: "4b",
    title: "History Agent",
    description:
      "Retrieves all past transactions from MongoDB and computes historical spending patterns by category.",
    tech: "MongoDB",
    input: "transactions collection",
    output: "history{}",
  },
  rag: {
    badge: "4c",
    title: "RAG Agent",
    description:
      "Queries the ChromaDB knowledge base using spending categories to retrieve relevant financial tips and advice.",
    tech: "ChromaDB + Embeddings",
    input: "category keywords",
    output: "rag_context[]",
  },
  join: {
    badge: "5",
    title: "Join Node",
    description:
      "Merges parallel branch outputs (profile, history, RAG) with parse and breakdown data into a unified state.",
    tech: "LangGraph",
    input: "Parallel states",
    output: "merged state",
  },
  allocation: {
    badge: "6",
    title: "Allocation Agent",
    description:
      "Rule-based engine computes asset allocation percentages based on risk appetite, age, goals, and savings capacity.",
    tech: "Rule Engine",
    input: "profile + breakdown",
    output: "allocation{}",
  },
  advisor: {
    badge: "7",
    title: "AI Advisor",
    description:
      "The Groq LLM synthesizes all context — profile, history, breakdown, allocation, and RAG knowledge — into personalized financial advice. Traced via Langfuse.",
    tech: "Groq LLM + Langfuse",
    input: "Full state",
    output: "final_advice",
  },
};

function showStep(stepId) {
  const step = STEPS[stepId];
  if (!step) return;

  document.getElementById("stepBadge").textContent = step.badge;
  document.getElementById("stepTitle").textContent = step.title;
  document.getElementById("stepDescription").textContent = step.description;
  document.getElementById("stepTech").textContent = step.tech;
  document.getElementById("stepInput").textContent = step.input;
  document.getElementById("stepOutput").textContent = step.output;

  document.querySelectorAll(".workflow-step").forEach((el) => {
    el.classList.toggle("active", el.dataset.step === stepId);
  });
}

document.querySelectorAll(".workflow-step").forEach((el) => {
  el.addEventListener("click", () => showStep(el.dataset.step));
});

showStep("input");
