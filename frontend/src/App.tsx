import { useState } from "react";
import Login from "./components/login";
import ChatWindow from "./components/ChatWindow";
import "./index.css";

function App() {
  // Check for existing session
  const [isAuthenticated, setIsAuthenticated] = useState(
    !!localStorage.getItem("access_token")
  );

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setIsAuthenticated(false);
  };

  return (
    <div className="app-root">
      {!isAuthenticated ? (
        <Login onLoginSuccess={() => setIsAuthenticated(true)} />
      ) : (
        <ChatWindow onLogout={handleLogout} />
      )}
    </div>
  );
}

export default App;