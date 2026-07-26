import "./App.css";

function App() {
  return (
    <main className="app-shell">
      <section className="status-card">
        <span className="status-badge">Development Foundation</span>

        <h1>Space Mission Control</h1>

        <p>
          The frontend application is running. Mission planning, simulation and
          telemetry features will be introduced in future milestones.
        </p>

        <div className="system-status">
          <span className="status-indicator" />
          <span>Frontend operational</span>
        </div>
      </section>
    </main>
  );
}

export default App;
