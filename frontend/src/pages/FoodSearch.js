import React, { useState } from "react";
import { api } from "../api";

export default function FoodSearch({ onLogged }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  /* Modal state for entering grams */
  const [selected, setSelected] = useState(null);
  const [grams, setGrams] = useState("100");
  const [logging, setLogging] = useState(false);

  /* ── Search ────────────────────────────────────────────────── */
  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setError("");
    setLoading(true);
    setResults([]);

    try {
      const data = await api(`/foods/search?q=${encodeURIComponent(query.trim())}`);
      setResults(data);
      if (data.length === 0) setError("No foods found — try a different query.");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  /* ── Log food ──────────────────────────────────────────────── */
  const handleLog = async () => {
    if (!selected) return;
    const g = parseFloat(grams);
    if (!g || g <= 0) return;

    setLogging(true);
    try {
      await api("/foods/log", {
        method: "POST",
        body: JSON.stringify({
          food_name: selected.name,
          grams: g,
          calories: selected.calories,
          protein: selected.protein,
          carbs: selected.carbs,
          fat: selected.fat,
        }),
      });
      setSelected(null);
      setGrams("100");
      onLogged();            // navigate to dashboard
    } catch (err) {
      setError(err.message);
    } finally {
      setLogging(false);
    }
  };

  /* ── Render ────────────────────────────────────────────────── */
  return (
    <>
      <h2 style={{ marginBottom: 16 }}>Search Food</h2>

      {/* Search bar */}
      <form className="search-bar" onSubmit={handleSearch}>
        <input
          placeholder="e.g. chicken breast, banana, rice…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          autoFocus
        />
        <button type="submit" disabled={loading}>
          {loading ? "Searching…" : "Search"}
        </button>
      </form>

      {error && <div className="error-msg" style={{ marginBottom: 16 }}>{error}</div>}

      {/* Results grid */}
      <div className="food-grid">
        {results.map((food) => (
          <div className="food-card" key={food.fdc_id}>
            <h4>{food.name}</h4>
            <div className="food-macros">
              <span>🔥 Calories</span>
              <span className="macro-val">{food.calories}</span>
              <span>💪 Protein</span>
              <span className="macro-val">{food.protein} g</span>
              <span>🍞 Carbs</span>
              <span className="macro-val">{food.carbs} g</span>
              <span>🧈 Fat</span>
              <span className="macro-val">{food.fat} g</span>
            </div>
            <div style={{ fontSize: "0.75rem", color: "#aaa", marginBottom: 8 }}>
              per 100 g
            </div>
            <button className="btn-add" onClick={() => { setSelected(food); setGrams("100"); }}>
              + Add Food
            </button>
          </div>
        ))}
      </div>

      {/* Grams modal */}
      {selected && (
        <div className="modal-overlay" onClick={() => setSelected(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>How many grams?</h3>
            <p>{selected.name}</p>
            <input
              type="number"
              min="1"
              value={grams}
              onChange={(e) => setGrams(e.target.value)}
              autoFocus
              onKeyDown={(e) => e.key === "Enter" && handleLog()}
            />
            <div className="modal-actions">
              <button className="btn-cancel" onClick={() => setSelected(null)}>
                Cancel
              </button>
              <button className="btn-confirm" onClick={handleLog} disabled={logging}>
                {logging ? "Saving…" : "Log Food"}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
