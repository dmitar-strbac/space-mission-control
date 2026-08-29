import {
  ArrowRight,
  CircleAlert,
  LockKeyhole,
  RadioTower,
  ShieldCheck,
  UserRound,
} from "lucide-react";
import { motion } from "motion/react";
import { useState, type FormEvent } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { ApiError } from "../api/apiClient";
import { useAuth } from "../hooks/useAuth";

export function LoginPage() {
  const navigate = useNavigate();
  const {
    login,
    isAuthenticated,
    isLoading: authLoading,
  } = useAuth();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!authLoading && isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    setError(null);
    setIsSubmitting(true);

    try {
      await login({
        username,
        password,
      });

      navigate("/", {
        replace: true,
      });
    } catch (requestError) {
      if (requestError instanceof ApiError) {
        setError("Access denied. Verify mission control credentials.");
      } else {
        setError("Mission control gateway is currently unavailable.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-starfield" />

      <div className="login-orbit login-orbit-primary" />
      <div className="login-orbit login-orbit-secondary" />

      <motion.section
        className="login-panel"
        initial={{
          opacity: 0,
          y: 18,
        }}
        animate={{
          opacity: 1,
          y: 0,
        }}
        transition={{
          duration: 0.55,
        }}
      >
        <div className="login-panel-accent login-panel-accent-left" />
        <div className="login-panel-accent login-panel-accent-right" />

        <div className="login-header-row">
          <div className="login-brand">
            <div className="login-brand-icon">
              <RadioTower size={25} />
            </div>

            <div>
              <span>SPACE</span>
              <strong>MISSION CONTROL</strong>
              <small>GROUND OPERATIONS NETWORK</small>
            </div>
          </div>

          <div className="login-signal-bars" aria-hidden="true">
            <span />
            <span />
            <span />
          </div>
        </div>

        <div className="login-copy">
          <span className="eyebrow">Authorized Access Terminal</span>
          <h1>MISSION CONTROL ACCESS</h1>
          <p>
            Authenticate to access mission planning, distributed preparation
            and flight operations.
          </p>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          <label>
            <span>OPERATOR ID</span>

            <div className="input-shell">
              <div className="input-icon-shell">
                <UserRound size={18} />
              </div>

              <input
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                placeholder="ENTER USERNAME"
                autoComplete="username"
                required
              />
            </div>
          </label>

          <label>
            <span>ACCESS CODE</span>

            <div className="input-shell">
              <div className="input-icon-shell">
                <LockKeyhole size={18} />
              </div>

              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="ENTER PASSWORD"
                autoComplete="current-password"
                required
              />
            </div>
          </label>

          {error && (
            <motion.div
              className="login-error"
              role="alert"
              initial={{
                opacity: 0,
                y: -5,
              }}
              animate={{
                opacity: 1,
                y: 0,
              }}
              transition={{
                duration: 0.2,
              }}
            >
              <div className="login-error-icon">
                <CircleAlert size={18} />
              </div>

              <div className="login-error-content">
                <span>AUTHENTICATION DENIED</span>
                <p>{error}</p>
              </div>
            </motion.div>
          )}

          <button
            className="primary-button login-submit"
            type="submit"
            disabled={isSubmitting}
          >
            <span>
              {isSubmitting
                ? "ESTABLISHING LINK..."
                : "ACCESS MISSION CONTROL"}
            </span>

            <ArrowRight size={19} />
          </button>
        </form>

        <div className="login-security-row">
          <div className="login-security">
            <span className="system-status-dot" />
            <span>SECURE GATEWAY CHANNEL AVAILABLE</span>
          </div>

          <div className="login-encryption">
            <ShieldCheck size={17} />
            <div>
              <span>ENCRYPTED CONNECTION</span>
              <small>TLS 1.3 · JWT AUTH</small>
            </div>
          </div>
        </div>
      </motion.section>

      <div className="login-footer">
        SPACE MISSION CONTROL · ORBITAL OPERATIONS PLATFORM
      </div>
    </div>
  );
}
