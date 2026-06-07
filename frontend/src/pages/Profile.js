import React, { useEffect, useState } from "react";
import { api } from "../api";

const ACTIVITY_OPTIONS = [
  { value: "sedentary",   label: "Sedentary",    desc: "Little or no exercise, desk job" },
  { value: "light",       label: "Light",        desc: "Light exercise 1–3 days/week" },
  { value: "moderate",    label: "Moderate",     desc: "Moderate exercise 3–5 days/week" },
  { value: "active",      label: "Active",       desc: "Hard exercise 6–7 days/week" },
  { value: "very_active", label: "Very Active",  desc: "Physical job or twice-daily training" },
];

const GOAL_OPTIONS = [
  { value: "lose",     label: "Lose weight",    desc: "−500 kcal/day deficit" },
  { value: "maintain", label: "Maintain weight", desc: "Eat at TDEE" },
  { value: "gain",     label: "Gain muscle",    desc: "+300 kcal/day surplus" },
];

const MACRO_COLORS = {
  calories: "#ff6b35",
  protein:  "#4ecdc4",
  carbs:    "#f9c846",
  fat:      "#e84393",
};

export default function Profile() {
  const [profile, setProfile]   = useState(null);
  const [targets, setTargets]   = useState(null);
  const [form, setForm]         = useState({});
  const [saving, setSaving]     = useState(false);
  const [saved, setSaved]       = useState(false);
  const [error, setError]       = useState("");

  /* ── Load current profile + targets ─────────────────────────── */
  useEffect(() => {
    Promise.all([api("/me"), api("/me/targets")])
      .then(([p, t]) => {
        setProfile(p);
        setTargets(t);
        setForm({
          gender:         p.gender         ?? "",
          age:            p.age            ?? "",
          weight:         p.weight         ?? "",
          height:         p.height         ?? "",
          activity_level: p.activity_level ?? "",
          goal_type:      p.goal_type      ?? "",
        });
      })
      .catch((err) => setError(err.message));
  }, []);

  /* ── Field change ────────────────────────────────────────────── */
  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
    setSaved(false);
  };

  /* ── Save profile ────────────────────────────────────────────── */
  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      const body = {
        gender:         form.gender         || null,
        age:            form.age            ? parseInt(form.age)        : null,
        weight:         form.weight         ? parseFloat(form.weight)   : null,
        height:         form.height         ? parseFloat(form.height)   : null,
        activity_level: form.activity_level || null,
        goal_type:      form.goal_type      || null,
      };
      const [updatedProfile, newTargets] = await Promise.all([
        api("/me", { method: "PUT", body: JSON.stringify(body) }),
        // Re-fetch targets after save
        api("/me/targets").catch(() => null),
      ]);
      // targets need to be re-fetched AFTER profile is saved
      const freshTargets = await api("/me/targets");
      setProfile(updatedProfile);
      setTargets(freshTargets);
      setSaved(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  if (!profile) {
    return <div className="loading">Loading profile…</div>;
  }

  const profileComplete = targets?.complete;

  return (
    <div className="profile-layout">

      {/* ── Left: form ─────────────────────────────────────────── */}
      <div className="profile-form-card">
        <h2 style={{ marginBottom: 4 }}>Your Profile</h2>
        <p className="profile-subtitle">
          Fill in your details so we can calculate personalised macro targets.
        </p>

        {error && <div className="error-msg">{error}</div>}
        {saved && <div className="success-msg">✅ Profile saved!</div>}

        <form onSubmit={handleSave}>

          {/* Gender */}
          <div className="form-group">
            <label>Biological sex</label>
            <div className="radio-group">
              {["male", "female"].map((g) => (
                <label key={g} className={`radio-btn ${form.gender === g ? "selected" : ""}`}>
                  <input
                    type="radio"
                    name="gender"
                    value={g}
                    checked={form.gender === g}
                    onChange={handleChange}
                  />
                  {g.charAt(0).toUpperCase() + g.slice(1)}
                </label>
              ))}
            </div>
            <div className="field-hint">Used for accurate BMR calculation (Mifflin-St Jeor)</div>
          </div>

          {/* Age / Weight / Height */}
          <div className="metrics-row">
            <div className="form-group">
              <label>Age</label>
              <div className="input-with-unit">
                <input
                  type="number" name="age" min="10" max="120"
                  value={form.age} onChange={handleChange}
                  placeholder="25"
                />
                <span className="unit-badge">yrs</span>
              </div>
            </div>
            <div className="form-group">
              <label>Weight</label>
              <div className="input-with-unit">
                <input
                  type="number" name="weight" min="30" max="300" step="0.1"
                  value={form.weight} onChange={handleChange}
                  placeholder="70"
                />
                <span className="unit-badge">kg</span>
              </div>
            </div>
            <div className="form-group">
              <label>Height</label>
              <div className="input-with-unit">
                <input
                  type="number" name="height" min="100" max="250" step="0.1"
                  value={form.height} onChange={handleChange}
                  placeholder="175"
                />
                <span className="unit-badge">cm</span>
              </div>
            </div>
          </div>

          {/* Activity level */}
          <div className="form-group">
            <label>Activity level</label>
            <div className="option-group">
              {ACTIVITY_OPTIONS.map((o) => (
                <label
                  key={o.value}
                  className={`option-btn ${form.activity_level === o.value ? "selected" : ""}`}
                >
                  <input
                    type="radio" name="activity_level" value={o.value}
                    checked={form.activity_level === o.value}
                    onChange={handleChange}
                  />
                  <span className="option-label">{o.label}</span>
                  <span className="option-desc">{o.desc}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Goal */}
          <div className="form-group">
            <label>Goal</label>
            <div className="option-group horizontal">
              {GOAL_OPTIONS.map((o) => (
                <label
                  key={o.value}
                  className={`option-btn ${form.goal_type === o.value ? "selected" : ""}`}
                >
                  <input
                    type="radio" name="goal_type" value={o.value}
                    checked={form.goal_type === o.value}
                    onChange={handleChange}
                  />
                  <span className="option-label">{o.label}</span>
                  <span className="option-desc">{o.desc}</span>
                </label>
              ))}
            </div>
          </div>

          <button className="btn-save" type="submit" disabled={saving}>
            {saving ? "Saving…" : "Save Profile"}
          </button>
        </form>
      </div>

      {/* ── Right: calculated targets ───────────────────────────── */}
      <div className="targets-card">
        <h3 style={{ marginBottom: 4 }}>Your Daily Targets</h3>
        <p className="profile-subtitle" style={{ marginBottom: 20 }}>
          {profileComplete
            ? "Calculated from your profile using Mifflin-St Jeor"
            : "Fill in your profile to get personalised targets"}
        </p>

        {!profileComplete && (
          <div className="targets-incomplete">
            ⚠️ Profile incomplete — showing default values.
            Fill in your age, weight and height to get accurate targets.
          </div>
        )}

        {/* BMR / TDEE explanation */}
        {profileComplete && targets && (
          <div className="tdee-breakdown">
            <div className="tdee-row">
              <span>BMR (base metabolic rate)</span>
              <strong>{targets.bmr} kcal</strong>
            </div>
            <div className="tdee-row">
              <span>TDEE (with activity)</span>
              <strong>{targets.tdee} kcal</strong>
            </div>
            <div className="tdee-row goal-row">
              <span>Daily target ({form.goal_type || "maintain"})</span>
              <strong>{targets.calories} kcal</strong>
            </div>
          </div>
        )}

        {/* Macro targets */}
        <div className="macro-targets-grid">
          {targets && [
            { key: "calories", label: "Calories", unit: "kcal", icon: "🔥" },
            { key: "protein",  label: "Protein",  unit: "g",    icon: "💪" },
            { key: "carbs",    label: "Carbs",    unit: "g",    icon: "🍞" },
            { key: "fat",      label: "Fat",      unit: "g",    icon: "🧈" },
          ].map(({ key, label, unit, icon }) => (
            <div
              key={key}
              className="macro-target-chip"
              style={{ borderColor: MACRO_COLORS[key] }}
            >
              <div className="chip-icon">{icon}</div>
              <div className="chip-value" style={{ color: MACRO_COLORS[key] }}>
                {targets[key]}
              </div>
              <div className="chip-label">{label}</div>
              <div className="chip-unit">{unit} / day</div>
            </div>
          ))}
        </div>

        {/* Formula note */}
        <div className="formula-note">
          <strong>How it's calculated:</strong><br />
          BMR uses the <em>Mifflin-St Jeor</em> equation.<br />
          Protein is set to 2 g per kg bodyweight.<br />
          Fat covers 25% of total calories.<br />
          Carbs fill the remaining calories.
        </div>
      </div>

    </div>
  );
}
