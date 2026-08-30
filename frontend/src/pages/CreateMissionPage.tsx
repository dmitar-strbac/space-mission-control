import {
  geoOrthographic,
  geoPath,
} from "d3-geo";

import { feature } from "topojson-client";

import worldLand from "world-atlas/land-110m.json";

import {
  useMutation,
  useQuery,
} from "@tanstack/react-query";
import {
  ArrowLeft,
  ArrowRight,
  BatteryCharging,
  Check,
  CheckCircle2,
  Clock3,
  Fuel,
  Gauge,
  Orbit,
  Rocket,
  Satellite,
  Users,
  Weight,
  Zap
} from "lucide-react";
import {
  useMemo,
  useState,
} from "react";
import {
  Link,
  useNavigate,
} from "react-router-dom";
import type {
  GeometryCollection,
  Topology,
} from "topojson-specification";

import { createMission } from "../api/missionApi";
import { getSpacecraft } from "../api/vehicleApi";
import { useAuth } from "../hooks/useAuth";
import type {
  MissionCreateRequest,
  MissionType,
} from "../types/mission";
import type { Spacecraft } from "../types/vehicle";
import {
  formatKilograms,
  formatKilonewtons,
  formatLabel,
  formatNumber,
} from "../utils/formatters";

type WizardStep =
  | "MISSION"
  | "VEHICLE"
  | "FLIGHT"
  | "OPERATIONS"
  | "REVIEW";

interface MissionFormState {
  name: string;
  missionType: MissionType;
  crewCount: number;
  vehicleId: string;
  initialAltitudeKm: number;
  targetAltitudeKm: number;
  minimumPropellantReservePercent: number;
  plannedLaunchTime: string;
  simulationSpeed: number;
}

const wizardSteps: Array<{
  id: WizardStep;
  label: string;
}> = [
  {
    id: "MISSION",
    label: "Mission",
  },
  {
    id: "VEHICLE",
    label: "Vehicle",
  },
  {
    id: "FLIGHT",
    label: "Flight Profile",
  },
  {
    id: "OPERATIONS",
    label: "Operations",
  },
  {
    id: "REVIEW",
    label: "Review",
  },
];

const simulationSpeeds = [
  {
    value: 1,
    label: "1×",
    description: "Real time",
  },
  {
    value: 10,
    label: "10×",
    description: "Accelerated",
  },
  {
    value: 60,
    label: "60×",
    description: "Mission demo",
  },
  {
    value: 300,
    label: "300×",
    description: "Rapid simulation",
  },
];

type WorldLandTopology =
  Topology<{
    land: GeometryCollection;
  }>;

const WORLD_LAND =
  worldLand as unknown as
    WorldLandTopology;

export function CreateMissionPage() {
  const navigate = useNavigate();
  const { user } = useAuth();

  const [currentStep, setCurrentStep] =
    useState<WizardStep>("MISSION");

  const [form, setForm] =
    useState<MissionFormState>({
      name: "",
      missionType: "LEO",
      crewCount: 0,
      vehicleId: "",
      initialAltitudeKm: 200,
      targetAltitudeKm: 400,
      minimumPropellantReservePercent: 10,
      plannedLaunchTime: "",
      simulationSpeed: 60,
    });

  const {
    data: spacecraftData,
    isLoading: spacecraftLoading,
  } = useQuery({
    queryKey: ["spacecraft"],
    queryFn: () => getSpacecraft(),
  });

  const createMutation = useMutation({
    mutationFn: createMission,
    onSuccess: (mission) => {
      navigate(`/missions/${mission.id}`);
    },
  });

  const spacecraft = spacecraftData?.items ?? [];

  const selectedSpacecraft =
    spacecraft.find(
      (item) => item.id === form.vehicleId,
    ) ?? null;

  const currentStepIndex = wizardSteps.findIndex(
    (step) => step.id === currentStep,
  );

  const availableSpacecraft = spacecraft.filter(
    (item) =>
      item.supported_mission_types.includes(
        form.missionType,
      ),
  );

  const canContinue = (() => {
    switch (currentStep) {
      case "MISSION":
        return (
          form.name.trim().length >= 3 &&
          form.crewCount >= 0
        );

      case "VEHICLE":
        return Boolean(form.vehicleId);

      case "FLIGHT":
        return (
          form.initialAltitudeKm >= 160 &&
          form.initialAltitudeKm <= 2000 &&
          form.targetAltitudeKm >= 160 &&
          form.targetAltitudeKm <= 2000 &&
          form.minimumPropellantReservePercent >= 0 &&
          form.minimumPropellantReservePercent < 100
        );

      case "OPERATIONS":
      case "REVIEW":
        return true;
    }
  })();

  const goNext = () => {
    if (
      currentStepIndex <
      wizardSteps.length - 1
    ) {
      setCurrentStep(
        wizardSteps[currentStepIndex + 1].id,
      );
    }
  };

  const goBack = () => {
    if (currentStepIndex > 0) {
      setCurrentStep(
        wizardSteps[currentStepIndex - 1].id,
      );
    }
  };

  const handleCreateMission = () => {
    const payload: MissionCreateRequest = {
      name: form.name.trim(),
      mission_type: form.missionType,
      vehicle_id: form.vehicleId || null,
      crew_count: form.crewCount,
      target_type: "EARTH_ORBIT",
      target_parameters: {
        initial_altitude_m:
          form.initialAltitudeKm * 1000,
        target_altitude_m:
          form.targetAltitudeKm * 1000,
        minimum_propellant_reserve_percent:
          form.minimumPropellantReservePercent,

        // UI convenience values
        initial_altitude_km:
          form.initialAltitudeKm,
        target_altitude_km:
          form.targetAltitudeKm,
      },
      planned_launch_time:
        form.plannedLaunchTime
          ? new Date(
              form.plannedLaunchTime,
            ).toISOString()
          : null,
      simulation_speed: form.simulationSpeed,
    };

    createMutation.mutate(payload);
  };

  if (user?.role === "OBSERVER") {
    return (
      <div className="content-error-state">
        <Rocket size={30} />
        <strong>Operator access required</strong>
        <p>
          Observer accounts can review missions but
          cannot create or modify mission definitions.
        </p>
      </div>
    );
  }

  return (
    <div className="create-mission-page">
      <Link className="back-link" to="/missions">
        <ArrowLeft size={15} />
        Mission Registry
      </Link>

      <section className="page-heading">
        <div>
          <span className="eyebrow">
            Mission Configuration
          </span>

          <h1>Create orbital mission</h1>

          <p>
            Define mission objectives, assign a spacecraft
            and configure the initial simulation profile.
          </p>
        </div>
      </section>

      <div className="mission-wizard">
        <nav className="wizard-navigation">
          {wizardSteps.map((step, index) => {
            const completed =
              index < currentStepIndex;

            const active =
              step.id === currentStep;

            return (
              <button
                className={`wizard-step ${
                  active ? "active" : ""
                } ${
                  completed ? "completed" : ""
                }`}
                key={step.id}
                type="button"
                onClick={() => {
                  if (index <= currentStepIndex) {
                    setCurrentStep(step.id);
                  }
                }}
              >
                <span className="wizard-step-number">
                  {completed ? (
                    <Check size={14} />
                  ) : (
                    String(index + 1).padStart(
                      2,
                      "0",
                    )
                  )}
                </span>

                <span>{step.label}</span>
              </button>
            );
          })}
        </nav>

        <section className="wizard-panel">
          {currentStep === "MISSION" && (
            <MissionStep
              form={form}
              setForm={setForm}
            />
          )}

          {currentStep === "VEHICLE" && (
            <VehicleStep
              spacecraft={availableSpacecraft}
              selectedId={form.vehicleId}
              crewCount={form.crewCount}
              loading={spacecraftLoading}
              onSelect={(vehicleId) =>
                setForm((current) => ({
                  ...current,
                  vehicleId,
                }))
              }
            />
          )}

          {currentStep === "FLIGHT" && (
            <FlightStep
              form={form}
              setForm={setForm}
            />
          )}

          {currentStep === "OPERATIONS" && (
            <OperationsStep
              form={form}
              setForm={setForm}
            />
          )}

          {currentStep === "REVIEW" && (
            <ReviewStep
              form={form}
              spacecraft={selectedSpacecraft}
            />
          )}

          {createMutation.isError && (
            <div className="wizard-error">
              Mission creation failed. Verify the
              configuration and API Gateway connection.
            </div>
          )}

          <div className="wizard-actions">
            <button
              className="secondary-button"
              type="button"
              onClick={goBack}
              disabled={currentStepIndex === 0}
            >
              <ArrowLeft size={16} />
              Back
            </button>

            {currentStep !== "REVIEW" ? (
              <button
                className="primary-button wizard-next"
                type="button"
                onClick={goNext}
                disabled={!canContinue}
              >
                Continue
                <ArrowRight size={16} />
              </button>
            ) : (
              <button
                className="primary-button wizard-next"
                type="button"
                onClick={handleCreateMission}
                disabled={
                  createMutation.isPending ||
                  !selectedSpacecraft
                }
              >
                {createMutation.isPending
                  ? "Creating mission..."
                  : "Create Mission"}

                <Rocket size={17} />
              </button>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}

interface MissionStepProps {
  form: MissionFormState;
  setForm: React.Dispatch<
    React.SetStateAction<MissionFormState>
  >;
}

function MissionStep({
  form,
  setForm,
}: MissionStepProps) {
  return (
    <div className="wizard-content">
      <WizardHeading
        eyebrow="01 · Mission Definition"
        title="Define mission objectives"
        description="Configure the identity and operational scope of the mission."
      />

      <div className="form-grid">
        <label className="form-field form-field-wide">
          <span>Mission Name</span>

          <input
            value={form.name}
            onChange={(event) =>
              setForm((current) => ({
                ...current,
                name: event.target.value,
              }))
            }
            placeholder="e.g. LEO Pathfinder 01"
          />
        </label>

        <label className="form-field">
          <span>Crew Count</span>

          <input
            min={0}
            type="number"
            value={form.crewCount}
            onChange={(event) =>
              setForm((current) => ({
                ...current,
                crewCount: Math.max(
                  0,
                  Number(event.target.value),
                ),
              }))
            }
          />
        </label>
      </div>

      <div className="mission-type-section">
        <span className="form-section-label">
          Mission Type
        </span>

        <div className="mission-type-grid">
          <button
            className="mission-type-card active"
            type="button"
          >
            <Orbit size={23} />

            <div>
              <strong>Low Earth Orbit</strong>
              <span>Core mission scope</span>
            </div>

            <CheckCircle2 size={18} />
          </button>

          <button
            className="mission-type-card disabled"
            type="button"
            disabled
          >
            <Satellite size={23} />

            <div>
              <strong>LEO Rendezvous</strong>
              <span>Extended scope</span>
            </div>

            <small>FUTURE</small>
          </button>

          <button
            className="mission-type-card disabled"
            type="button"
            disabled
          >
            <Rocket size={23} />

            <div>
              <strong>Lunar Mission</strong>
              <span>Advanced scope</span>
            </div>

            <small>FUTURE</small>
          </button>
        </div>
      </div>
    </div>
  );
}

interface VehicleStepProps {
  spacecraft: Spacecraft[];
  selectedId: string;
  crewCount: number;
  loading: boolean;
  onSelect: (vehicleId: string) => void;
}

function VehicleStep({
  spacecraft,
  selectedId,
  crewCount,
  loading,
  onSelect,
}: VehicleStepProps) {
  return (
    <div className="wizard-content">
      <WizardHeading
        eyebrow="02 · Spacecraft"
        title="Select mission vehicle"
        description="Choose a spacecraft compatible with the selected mission profile and crew requirements."
      />

      {loading ? (
        <div className="vehicle-loading">
          Loading spacecraft registry...
        </div>
      ) : (
        <div className="vehicle-selection-grid">
          {spacecraft.map((vehicle) => {
            const selected =
              selectedId === vehicle.id;

            const crewCompatible =
              crewCount <= vehicle.crew_capacity;

            const available =
              vehicle.status === "AVAILABLE";

            const selectable =
              available && crewCompatible;

            return (
              <button
                className={`vehicle-selection-card ${
                  selected ? "selected" : ""
                } ${
                  !selectable ? "unavailable" : ""
                }`}
                key={vehicle.id}
                type="button"
                disabled={!selectable}
                onClick={() =>
                  onSelect(vehicle.id)
                }
              >
                <div className="vehicle-card-heading">
                  <div className="vehicle-icon">
                    <Satellite size={23} />
                  </div>

                  <div>
                    <strong>{vehicle.name}</strong>
                    <span>
                      {formatLabel(
                        vehicle.vehicle_type,
                      )}
                    </span>
                  </div>

                  <span
                    className={`vehicle-availability ${vehicle.status.toLowerCase()}`}
                  >
                    {formatLabel(vehicle.status)}
                  </span>
                </div>

                <div className="vehicle-spec-grid">
                  <VehicleSpec
                    icon={<Users size={14} />}
                    label="Crew"
                    value={`${vehicle.crew_capacity}`}
                  />

                  <VehicleSpec
                    icon={<Weight size={14} />}
                    label="Mass"
                    value={formatKilograms(
                      vehicle.fully_fueled_mass_kg,
                    )}
                  />

                  <VehicleSpec
                    icon={<Fuel size={14} />}
                    label="Propellant"
                    value={formatKilograms(
                      vehicle.propellant_capacity_kg,
                    )}
                  />

                  <VehicleSpec
                    icon={<Zap size={14} />}
                    label="Thrust"
                    value={formatKilonewtons(
                      vehicle.engine_thrust_n,
                    )}
                  />
                </div>

                {!crewCompatible && (
                  <div className="vehicle-warning">
                    Crew capacity exceeded
                  </div>
                )}

                {selected && (
                  <div className="vehicle-selected">
                    <Check size={14} />
                    Selected for mission
                  </div>
                )}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

interface FlightStepProps {
  form: MissionFormState;
  setForm: React.Dispatch<
    React.SetStateAction<MissionFormState>
  >;
}

function FlightProfileEarth() {
  const SIZE = 130;
  const CENTER = SIZE / 2;
  const RADIUS = 43;

  const land =
    useMemo(
      () =>
        feature(
          WORLD_LAND,
          WORLD_LAND.objects.land,
        ),
      [],
    );

  const projection =
    useMemo(
      () =>
        geoOrthographic()
          .translate([
            CENTER,
            CENTER,
          ])
          .scale(RADIUS)
          .rotate([
            -12,
            -12,
            0,
          ])
          .clipAngle(90)
          .precision(0.5),
      [CENTER],
    );

  const landPath =
    useMemo(
      () =>
        geoPath(
          projection,
        )(land) ?? "",
      [
        projection,
        land,
      ],
    );

  return (
    <svg
      className="flight-profile-earth"
      viewBox={`0 0 ${SIZE} ${SIZE}`}
      aria-hidden="true"
    >
      <defs>
        <radialGradient
          id="flight-earth-ocean"
          cx="32%"
          cy="27%"
          r="76%"
        >
          <stop
            offset="0%"
            stopColor="#183e5b"
          />

          <stop
            offset="60%"
            stopColor="#0a243a"
          />

          <stop
            offset="100%"
            stopColor="#06131f"
          />
        </radialGradient>

        <radialGradient
          id="flight-earth-shadow"
          cx="26%"
          cy="22%"
          r="90%"
        >
          <stop
            offset="45%"
            stopColor="#020710"
            stopOpacity="0"
          />

          <stop
            offset="78%"
            stopColor="#020710"
            stopOpacity="0.42"
          />

          <stop
            offset="100%"
            stopColor="#020710"
            stopOpacity="0.82"
          />
        </radialGradient>

        <clipPath id="flight-earth-clip">
          <circle
            cx={CENTER}
            cy={CENTER}
            r={RADIUS}
          />
        </clipPath>
      </defs>

      <circle
        className="flight-profile-earth-halo"
        cx={CENTER}
        cy={CENTER}
        r={RADIUS + 3}
      />

      <circle
        className="flight-profile-earth-ocean"
        cx={CENTER}
        cy={CENTER}
        r={RADIUS}
        fill="url(#flight-earth-ocean)"
      />

      <g clipPath="url(#flight-earth-clip)">
        <path
          className="flight-profile-earth-land"
          d={landPath}
        />

        <circle
          cx={CENTER}
          cy={CENTER}
          r={RADIUS}
          fill="url(#flight-earth-shadow)"
        />
      </g>

      <circle
        className="flight-profile-earth-grid"
        cx={CENTER}
        cy={CENTER}
        r={RADIUS}
      />

      <path
        className="flight-profile-equator"
        d={
          `M ${CENTER - RADIUS} ${CENTER} ` +
          `Q ${CENTER} ${CENTER + 13} ` +
          `${CENTER + RADIUS} ${CENTER}`
        }
      />
    </svg>
  );
}

function FlightStep({
  form,
  setForm,
}: FlightStepProps) {
  return (
    <div className="wizard-content">
      <WizardHeading
        eyebrow="03 · Flight Profile"
        title="Configure target orbit"
        description="Define the target orbital altitude and desired mission start time."
      />

      <div className="flight-profile-layout">
        <div className="flight-profile-form">
          <label className="form-field">
            <span>Initial Orbit Altitude</span>

            <div className="flight-number-input">
              <input
                min={160}
                max={2000}
                type="number"
                value={form.initialAltitudeKm}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    initialAltitudeKm: Number(
                      event.target.value,
                    ),
                  }))
                }
              />

              <span className="flight-input-unit">
                KM
              </span>
            </div>

            <small>
              Starting Low Earth Orbit altitude.
            </small>
          </label>

          <label className="form-field">
            <span>Target Orbit Altitude</span>

            <div className="flight-number-input">
              <input
                min={160}
                max={2000}
                type="number"
                value={form.targetAltitudeKm}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    targetAltitudeKm: Number(
                      event.target.value,
                    ),
                  }))
                }
              />

              <span className="flight-input-unit">
                KM
              </span>
            </div>

            <small>
              Desired final Low Earth Orbit altitude.
            </small>
          </label>

          <label className="form-field">
            <span>Minimum Propellant Reserve</span>

            <div className="flight-number-input">
              <input
                min={0}
                max={99}
                type="number"
                value={
                  form.minimumPropellantReservePercent
                }
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    minimumPropellantReservePercent:
                      Number(event.target.value),
                  }))
                }
              />

              <span className="flight-input-unit">
                %
              </span>
            </div>

            <small>
              Required remaining fuel margin after
              planned maneuvers.
            </small>
          </label>

          <label className="form-field">
            <span>Planned Launch Time</span>

            <input
              type="datetime-local"
              value={form.plannedLaunchTime}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  plannedLaunchTime:
                    event.target.value,
                }))
              }
            />

            <small>
              Optional — may be scheduled later.
            </small>
          </label>
        </div>

        <div className="orbit-preview-card">
          <div className="orbit-preview">
            <div className="orbit-preview-earth">
              <FlightProfileEarth />
            </div>

            <div className="orbit-preview-ring">
              <div className="orbit-preview-spacecraft">
                <Satellite size={14} />
              </div>
            </div>
          </div>

          <div className="orbit-preview-data">
            <span>Initial → Target altitude</span>

            <strong>
              {formatNumber(
                form.initialAltitudeKm,
                0,
              )}{" "}
              →{" "}
              {formatNumber(
                form.targetAltitudeKm,
                0,
              )}{" "}
              km
            </strong>

            <small>
              Circular Low Earth Orbit profile
            </small>
          </div>
        </div>
      </div>
    </div>
  );
}

interface OperationsStepProps {
  form: MissionFormState;
  setForm: React.Dispatch<
    React.SetStateAction<MissionFormState>
  >;
}

function OperationsStep({
  form,
  setForm,
}: OperationsStepProps) {
  return (
    <div className="wizard-content">
      <WizardHeading
        eyebrow="04 · Simulation"
        title="Configure mission operations"
        description="Select the relationship between simulation time and real-world demonstration time."
      />

      <div className="simulation-speed-grid">
        {simulationSpeeds.map((speed) => (
          <button
            className={
              form.simulationSpeed === speed.value
                ? "simulation-speed-card selected"
                : "simulation-speed-card"
            }
            key={speed.value}
            type="button"
            onClick={() =>
              setForm((current) => ({
                ...current,
                simulationSpeed: speed.value,
              }))
            }
          >
            <Clock3 size={20} />

            <strong>{speed.label}</strong>
            <span>{speed.description}</span>

            {form.simulationSpeed ===
              speed.value && (
              <CheckCircle2 size={16} />
            )}
          </button>
        ))}
      </div>

      <div className="operations-note">
        <Gauge size={18} />

        <div>
          <strong>
            Simulation accuracy is preserved
          </strong>

          <p>
            Acceleration changes the relationship between
            simulation and real time. It does not alter
            the numerical integration model.
          </p>
        </div>
      </div>
    </div>
  );
}

interface ReviewStepProps {
  form: MissionFormState;
  spacecraft: Spacecraft | null;
}

function ReviewStep({
  form,
  spacecraft,
}: ReviewStepProps) {
  return (
    <div className="wizard-content">
      <WizardHeading
        eyebrow="05 · Final Review"
        title="Mission dossier"
        description="Review the mission definition before registering it with Mission Control."
      />

      <div className="mission-dossier">
        <div className="dossier-header">
          <div>
            <span>MISSION DESIGNATION</span>
            <h2>
              {form.name || "Unnamed Mission"}
            </h2>
          </div>

          <div className="dossier-status">
            <span />
            DRAFT CONFIGURATION
          </div>
        </div>

        <div className="dossier-grid">
          <DossierItem
            label="Mission"
            value="Low Earth Orbit"
          />

          <DossierItem
            label="Spacecraft"
            value={
              spacecraft?.name ?? "Not selected"
            }
          />

          <DossierItem
            label="Crew"
            value={`${form.crewCount}`}
          />

          <DossierItem
            label="Initial Orbit"
            value={`${formatNumber(
              form.initialAltitudeKm,
              0,
            )} km`}
          />

          <DossierItem
            label="Target Orbit"
            value={`${formatNumber(
              form.targetAltitudeKm,
              0,
            )} km`}
          />

          <DossierItem
            label="Minimum Fuel Reserve"
            value={`${formatNumber(
              form.minimumPropellantReservePercent,
              0,
            )}%`}
          />

          <DossierItem
            label="Simulation"
            value={`${form.simulationSpeed}×`}
          />

          <DossierItem
            label="Planned Start"
            value={
              form.plannedLaunchTime
                ? new Date(
                    form.plannedLaunchTime,
                  ).toLocaleString()
                : "Not scheduled"
            }
          />
        </div>

        {spacecraft && (
          <div className="dossier-resource-strip">
            <div>
              <Fuel size={16} />
              <span>
                <small>PROPELLANT</small>
                <strong>
                  {formatKilograms(
                    spacecraft.propellant_capacity_kg,
                  )}
                </strong>
              </span>
            </div>

            <div>
              <BatteryCharging size={16} />
              <span>
                <small>BATTERY</small>
                <strong>
                  {formatNumber(
                    spacecraft.battery_capacity_kwh,
                  )}{" "}
                  kWh
                </strong>
              </span>
            </div>

            <div>
              <Zap size={16} />
              <span>
                <small>ENGINE THRUST</small>
                <strong>
                  {formatKilonewtons(
                    spacecraft.engine_thrust_n,
                  )}
                </strong>
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

interface WizardHeadingProps {
  eyebrow: string;
  title: string;
  description: string;
}

function WizardHeading({
  eyebrow,
  title,
  description,
}: WizardHeadingProps) {
  return (
    <header className="wizard-heading">
      <span className="eyebrow">{eyebrow}</span>
      <h2>{title}</h2>
      <p>{description}</p>
    </header>
  );
}

interface VehicleSpecProps {
  icon: React.ReactNode;
  label: string;
  value: string;
}

function VehicleSpec({
  icon,
  label,
  value,
}: VehicleSpecProps) {
  return (
    <div className="vehicle-spec">
      {icon}

      <span>
        <small>{label}</small>
        <strong>{value}</strong>
      </span>
    </div>
  );
}

interface DossierItemProps {
  label: string;
  value: string;
}

function DossierItem({
  label,
  value,
}: DossierItemProps) {
  return (
    <div className="dossier-item">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}
