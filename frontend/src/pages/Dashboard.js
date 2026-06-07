import React, { useCallback, useEffect, useState } from "react";
import { api } from "../api";

const DEFAULT_TARGETS = { calories: 2000, protein: 150, carbs: 225, fat: 67 };

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [logs, setLogs]       = useState([]);
  const [targets, setTargets] = useState(DEFAULT_TARGETS);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      const [s, l, t] = await Promise.all([
        api("/foods/today"),
        api("/foods/logs"),
        api("/me/targets"),
      ]);
      setSummary(s);
      setLogs(l);
      setTargets(t);
    } catch {
      /* token might be stale — ignore for now */
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  if (loading) return <div className="loading">Loading dashboard…</div>;

  const pct = (val, target) => Math.min(100, Math.round((val / target) * 100));

  return (
    <>
      <h2 style={{ marginBottom: 16 }}>Today's Nutrition</h2>

      {/* ── Summary cards ──────────────────────────────────── */}
      <div className="summary-grid">
        <Card
          cls="cal"
          label="Calories"
          value={summary?.calories ?? 0}
          unit="kcal"
          target={targets.calories}
          pct={pct}
        />
        <Card
          cls="prot"
          label="Protein"
          value={summary?.protein ?? 0}
          unit="g"
          target={targets.protein}
          pct={pct}
        />
        <Card
          cls="carb"
          label="Carbs"
          value={summary?.carbs ?? 0}
          unit="g"
          target={targets.carbs}
          pct={pct}
        />
        <Card
          cls="fat"
          label="Fat"
          value={summary?.fat ?? 0}
          unit="g"
          target={targets.fat}
          pct={pct}
        />
      </div>

      {/* ── Food log table ─────────────────────────────────── */}
      <div className="log-section">
        <h3>Food Log</h3>

        {logs.length === 0 ? (
          <div className="empty-state">
            No foods logged yet today — go to <strong>Search Food</strong> to add some!
          </div>
        ) : (
          <table className="log-table">
            <thead>
              <tr>
                <th>Food</th>
                <th>Grams</th>
                <th>Cal</th>
                <th>Protein</th>
                <th>Carbs</th>
                <th>Fat</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log.id}>
                  <td>{log.food_name}</td>
                  <td>{log.grams} g</td>
                  <td>{log.calories}</td>
                  <td>{log.protein} g</td>
                  <td>{log.carbs} g</td>
                  <td>{log.fat} g</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}

/* ── Small helper component ──────────────────────────────────── */
function Card({ cls, label, value, unit, target, pct }) {
  return (
    <div className={`summary-card ${cls}`}>
      <div className="label">{label}</div>
      <div className="value">{Math.round(value)}</div>
      <div className="unit">
        / {target} {unit}
      </div>
      <div className="progress-track">
        <div
          className="progress-fill"
          style={{ width: `${pct(value, target)}%` }}
        />
      </div>
    </div>
  );
}
