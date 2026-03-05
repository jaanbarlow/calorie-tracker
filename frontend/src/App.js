import React, { useState } from "react";
import Login from "./pages/Login";
import Register from "./pages/Register";
import FoodSearch from "./pages/FoodSearch";
import Dashboard from "./pages/Dashboard";
import "./App.css";

export default function App() {
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [page, setPage] = useState(token ? "dashboard" : "login");

  /* ── Auth helpers ──────────────────────────────────────────── */
  const handleLogin = (jwt) => {
    localStorage.setItem("token", jwt);
    setToken(jwt);
    setPage("dashboard");
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setPage("login");
  };

  /* ── Render ────────────────────────────────────────────────── */
  if (!token) {
    return (
      <div className="auth-wrapper">
        {page === "login" ? (
          <Login onLogin={handleLogin} goToRegister={() => setPage("register")} />
        ) : (
          <Register onLogin={handleLogin} goToLogin={() => setPage("login")} />
        )}
      </div>
    );
  }

  return (
    <div className="app">
      {/* ── Navbar ──────────────────────────────────────────── */}
      <nav className="navbar">
        <span className="navbar-brand" onClick={() => setPage("dashboard")}>
          🔥 Calorie Tracker
        </span>
        <div className="navbar-links">
          <button
            className={`nav-btn ${page === "dashboard" ? "active" : ""}`}
            onClick={() => setPage("dashboard")}
          >
            Dashboard
          </button>
          <button
            className={`nav-btn ${page === "search" ? "active" : ""}`}
            onClick={() => setPage("search")}
          >
            Search Food
          </button>
          <button className="nav-btn logout" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </nav>

      {/* ── Page content ───────────────────────────────────── */}
      <main className="main-content">
        {page === "dashboard" && <Dashboard />}
        {page === "search" && <FoodSearch onLogged={() => setPage("dashboard")} />}
      </main>
    </div>
  );
}
