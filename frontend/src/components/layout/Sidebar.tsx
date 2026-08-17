import {
  Activity,
  Gauge,
  LayoutDashboard,
  Plus,
  RadioTower,
  Rocket,
} from "lucide-react";
import { NavLink } from "react-router-dom";

const primaryNavigation = [
  {
    label: "Overview",
    path: "/",
    icon: LayoutDashboard,
  },
  {
    label: "Missions",
    path: "/missions",
    icon: Rocket,
  },
  {
    label: "Create Mission",
    path: "/missions/new",
    icon: Plus,
  },
];

export function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="sidebar-brand-mark">
          <RadioTower size={22} />
        </div>

        <div>
          <span className="sidebar-brand-eyebrow">SPACE</span>
          <strong>MISSION CONTROL</strong>
        </div>
      </div>

      <nav className="sidebar-navigation">
        <span className="sidebar-section-label">
          Mission Operations
        </span>

        {primaryNavigation.map(({ label, path, icon: Icon }) => (
          <NavLink
            key={path}
            to={path}
            end={path === "/"}
            className={({ isActive }) =>
              `sidebar-link${isActive ? " active" : ""}`
            }
          >
            <Icon size={18} />
            <span>{label}</span>
          </NavLink>
        ))}

        <span className="sidebar-section-label sidebar-section-spaced">
          Live Systems
        </span>

        <button className="sidebar-link sidebar-link-disabled" disabled>
          <Gauge size={18} />
          <span>Mission Control</span>
          <small>SOON</small>
        </button>

        <button className="sidebar-link sidebar-link-disabled" disabled>
          <Activity size={18} />
          <span>Telemetry</span>
          <small>SOON</small>
        </button>
      </nav>

      <div className="sidebar-footer">
        <span className="status-indicator" />
        <div>
          <strong>Ground Network</strong>
          <span>Connected</span>
        </div>
      </div>
    </aside>
  );
}
