<div align="center">
  <h1>🚀 Multimodal Chat Facility</h1>
  <p>A production-grade full-stack gateway for Gemini and Groq AI providers.</p>
</div>

<hr />

<h2>📋 Project Overview</h2>
<p>
  This project implements a high-performance multimodal chatbot application. It serves as a unified 
  gateway for <b>Google Gemini</b> and <b>Groq</b>, supporting simultaneous text and image inputs 
  via a custom streaming interface. 
</p>

<h2>🛠️ Core Features</h2>
<ul>
  <li><b>Dual Provider Gateway:</b> Supports <code>gemini-2.0-flash</code> and <code>llama-3.2-vision</code>. </li>
  <li><b>Automatic Fallback:</b> Implements 5xx error handling to switch between providers mid-session. </li>
  <li><b>Secure Authentication:</b> Dual-layer system with JWT access and refresh rotation. </li>
  <li><b>Resource Management:</b> In-memory rate limiting and mid-call stream cancellation. </li>
  <li><b>Real-time UI:</b> Markdown rendering, optimistic media updates, and model selection. </li>
</ul>

<h2>🐛 Resolved Critical Bugs</h2>
<p>During development, the following architectural challenges were addressed:</p>
<ol>
  <li>
    <b>The "Double-Nesting" SSE Bug:</b> 
    Resolved a conflict where both the controller and router were wrapping data in SSE format, 
    causing JSON parsing failures on the frontend.
  </li>
  <li>
    <b>Provider Argument Mismatch:</b> 
    Fixed a crash in the <code>GroqProvider</code> where the streaming method was receiving 
    multimodal image data it wasn't signature-ready to handle.
  </li>
  <li>
    <b>Docker DNS Resolution:</b> 
    Corrected a <code>Temporary failure in name resolution</code> error by explicitly 
    configuring public DNS servers in the Docker container to reach Google API endpoints.
  </li>
</ol>

<h2>🏗️ Tech Stack</h2>
<ul>
  <li><b>Backend:</b> FastAPI (Python) </li>
  <li><b>Frontend:</b> React + Vite (TypeScript) </li>
  <li><b>Containerization:</b> Docker & Docker-Compose </li>
</ul>

<h2>🚀 Getting Started</h2>
<pre>
# Clone the repository
git clone https://github.com/your-username/repo.git
# Create a .env file with your GEMINI_API_KEY and GROQ_API_KEY
# Launch the entire stack
docker-compose up --build
</pre>
