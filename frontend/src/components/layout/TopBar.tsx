import {
  Bell,
  ChevronDown,
  LogOut,
  ShieldCheck,
} from "lucide-react";

import { useAuth } from "../../hooks/useAuth";

export function TopBar() {
  const { user, logout } = useAuth();

  return (
    <header className="topbar">
      <div className="topbar-system-status">
        <span className="system-status-dot" />
        <span>Mission Control Online</span>
      </div>

      <div className="topbar-actions">
        <button
          className="topbar-icon-button"
          type="button"
          aria-label="Notifications"
        >
          <Bell size={18} />
        </button>

        <div className="operator-profile">
          <div className="operator-avatar">
            <ShieldCheck size={18} />
          </div>

          <div className="operator-details">
            <strong>{user?.username ?? "Operator"}</strong>
            <span>{user?.role ?? "OBSERVER"}</span>
          </div>

          <ChevronDown size={16} />
        </div>

        <button
          className="topbar-icon-button"
          type="button"
          aria-label="Log out"
          onClick={logout}
        >
          <LogOut size={18} />
        </button>
      </div>
    </header>
  );
}
