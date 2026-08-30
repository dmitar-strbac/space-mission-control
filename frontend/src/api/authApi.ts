import type {
  AuthUser,
  LoginRequest,
  LoginResponse,
} from "../types/auth";
import { apiRequest } from "./apiClient";

export function login(request: LoginRequest): Promise<LoginResponse> {
  return apiRequest<LoginResponse>("/auth/login", {
    method: "POST",
    authenticated: false,
    body: JSON.stringify(request),
  });
}

export function getCurrentUser(): Promise<AuthUser> {
  return apiRequest<AuthUser>("/auth/me");
}
