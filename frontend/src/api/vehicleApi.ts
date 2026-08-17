import type {
  Spacecraft,
  SpacecraftListResponse,
} from "../types/vehicle";
import { apiRequest } from "./apiClient";

export function getSpacecraft(
  limit = 100,
  offset = 0,
): Promise<SpacecraftListResponse> {
  return apiRequest<SpacecraftListResponse>(
    `/api/vehicle/spacecraft?limit=${limit}&offset=${offset}`,
  );
}

export function getSpacecraftById(
  spacecraftId: string,
): Promise<Spacecraft> {
  return apiRequest<Spacecraft>(
    `/api/vehicle/spacecraft/${spacecraftId}`,
  );
}
