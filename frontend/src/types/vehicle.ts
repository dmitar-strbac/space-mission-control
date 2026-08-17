import type { MissionType } from "./mission";

export type VehicleType =
  | "CREW_CAPSULE"
  | "ORBITAL_VEHICLE"
  | "LUNAR_CAPABLE";

export type SpacecraftStatus =
  | "AVAILABLE"
  | "RESERVED"
  | "MAINTENANCE"
  | "UNAVAILABLE";

export interface Spacecraft {
  id: string;
  name: string;
  vehicle_type: VehicleType;
  supported_mission_types: MissionType[];

  dry_mass_kg: number;
  max_payload_kg: number;
  crew_capacity: number;

  engine_thrust_n: number;
  engine_specific_impulse_s: number;
  propellant_capacity_kg: number;

  oxygen_capacity_kg: number;
  battery_capacity_kwh: number;

  max_mission_duration_h: number;
  max_acceleration_g: number;

  status: SpacecraftStatus;
  fully_fueled_mass_kg: number;

  created_at: string;
  updated_at: string;
}

export interface SpacecraftListResponse {
  items: Spacecraft[];
  total: number;
  offset: number;
  limit: number;
}
