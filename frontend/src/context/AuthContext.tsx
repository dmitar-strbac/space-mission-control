import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type PropsWithChildren,
} from "react";

import {
  clearStoredAccessToken,
  getStoredAccessToken,
  storeAccessToken,
} from "../api/apiClient";
import {
  getCurrentUser,
  login as loginRequest,
} from "../api/authApi";
import type {
  AuthUser,
  LoginRequest,
} from "../types/auth";
import {
  AuthContext,
  type AuthContextValue,
} from "./auth-context";


export function AuthProvider({ children }: PropsWithChildren) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const logout = useCallback(() => {
    clearStoredAccessToken();
    setUser(null);
  }, []);

  useEffect(() => {
    const restoreSession = async () => {
      const token = getStoredAccessToken();

      if (!token) {
        setIsLoading(false);
        return;
      }

      try {
        const currentUser = await getCurrentUser();
        setUser(currentUser);
      } catch {
        logout();
      } finally {
        setIsLoading(false);
      }
    };

    void restoreSession();
  }, [logout]);

  const login = useCallback(async (credentials: LoginRequest) => {
    const response = await loginRequest(credentials);

    storeAccessToken(response.access_token);

    try {
      const currentUser = await getCurrentUser();
      setUser(currentUser);
    } catch (error) {
      clearStoredAccessToken();
      throw error;
    }
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: user !== null,
      isLoading,
      login,
      logout,
    }),
    [user, isLoading, login, logout],
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
