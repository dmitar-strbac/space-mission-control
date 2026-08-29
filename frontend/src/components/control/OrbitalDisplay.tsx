import {
  Crosshair,
  Satellite,
} from "lucide-react";

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import type {
  SimulationState,
} from "../../types/simulation";

import type {
  Maneuver,
  TrajectoryPlan,
} from "../../types/trajectory";

interface OrbitalDisplayProps {
  trajectory: TrajectoryPlan;
  maneuvers: Maneuver[];

  currentState:
    | SimulationState
    | undefined;

  missionStatus: string;
}

interface OrbitalPoint {
  x: number;
  y: number;
  elapsedTimeS: number;
}

interface SvgPoint {
  x: number;
  y: number;
}

const EARTH_RADIUS_M =
  6_371_000;

const VIEWBOX_SIZE = 600;
const CENTER =
  VIEWBOX_SIZE / 2;

function magnitude(
  vector: {
    x: number;
    y: number;
  },
) {
  return Math.hypot(
    vector.x,
    vector.y,
  );
}

function angleOf(
  vector: {
    x: number;
    y: number;
  },
) {
  return Math.atan2(
    vector.y,
    vector.x,
  );
}

function polarToSvg(
  radius: number,
  angle: number,
): SvgPoint {
  return {
    x:
      CENTER +
      Math.cos(angle) *
        radius,

    y:
      CENTER -
      Math.sin(angle) *
        radius,
  };
}

function statePositionToSvg(
  position: {
    x: number;
    y: number;
  },
  scale: number,
): SvgPoint {
  return {
    x:
      CENTER +
      position.x *
        scale,

    y:
      CENTER -
      position.y *
        scale,
  };
}

function pointsToPath(
  points: SvgPoint[],
) {
  if (
    points.length === 0
  ) {
    return "";
  }

  return points
    .map(
      (point, index) =>
        `${index === 0
          ? "M"
          : "L"} ` +
        `${point.x.toFixed(
          2,
        )} ` +
        `${point.y.toFixed(
          2,
        )}`,
    )
    .join(" ");
}

function getAngularRate(
  trajectory:
    TrajectoryPlan,
) {
  const position =
    trajectory
      .initial_state_vector
      .position;

  const velocity =
    trajectory
      .initial_state_vector
      .velocity;

  const radius =
    magnitude(position);

  if (radius <= 0) {
    return 0;
  }

  const tangentialSign =
    position.x *
      velocity.y -
    position.y *
      velocity.x;

  const speed =
    magnitude(velocity);

  const direction =
    tangentialSign < 0
      ? -1
      : 1;

  return (
    direction *
    speed /
    radius
  );
}

function getTransferPath(
  initialRadius: number,
  targetRadius: number,
  scale: number,
  initialAngle: number,
) {
  const pointCount = 80;

  const scaledInitialRadius =
    initialRadius * scale;

  const scaledTargetRadius =
    targetRadius * scale;

  const points = Array.from(
    { length: pointCount + 1 },
    (_, index) => {
      const progress =
        index / pointCount;

      const angle =
        initialAngle +
        Math.PI * progress;

      const interpolation =
        (1 -
          Math.cos(
            Math.PI *
              progress,
          )) /
        2;

      const radius =
        scaledInitialRadius +
        (scaledTargetRadius -
          scaledInitialRadius) *
          interpolation;

      return polarToSvg(
        radius,
        angle,
      );
    },
  );

  return pointsToPath(
    points,
  );
}

export function OrbitalDisplay({
  trajectory,
  maneuvers,
  currentState,
  missionStatus,
}: OrbitalDisplayProps) {
  const [
    actualTrack,
    setActualTrack,
  ] = useState<
    OrbitalPoint[]
  >([]);

  const initialPosition =
    trajectory
      .initial_state_vector
      .position;

  const targetPosition =
    trajectory
      .target_state_vector
      .position;

  const initialRadius =
    magnitude(
      initialPosition,
    );

  const targetRadius =
    magnitude(
      targetPosition,
    );

  const currentRadius =
    currentState
      ? magnitude(
          currentState.position,
        )
      : initialRadius;

  const maximumPhysicalRadius =
    Math.max(
      initialRadius,
      targetRadius,
      currentRadius,
      EARTH_RADIUS_M +
        1_000_000,
    );

  const orbitalDisplayRadius =
    CENTER - 42;

  const scale =
    orbitalDisplayRadius /
    maximumPhysicalRadius;

  const earthRadius =
    EARTH_RADIUS_M *
    scale;

  const initialDisplayRadius =
    initialRadius *
    scale;

  const targetDisplayRadius =
    targetRadius *
    scale;

  const initialAngle =
    angleOf(
      initialPosition,
    );

  const angularRate =
    getAngularRate(
      trajectory,
    );

  useEffect(() => {
    setActualTrack([
      {
        x:
          initialPosition.x,

        y:
          initialPosition.y,

        elapsedTimeS:
          trajectory
            .initial_state_vector
            .elapsed_time_s,
      },
    ]);
  }, [
    trajectory.id,
    initialPosition.x,
    initialPosition.y,
    trajectory.initial_state_vector.elapsed_time_s,
  ]);

  useEffect(() => {
    if (!currentState) {
      return;
    }

    setActualTrack(
      (current) => {
        const next: OrbitalPoint = {
          x:
            currentState
              .position.x,

          y:
            currentState
              .position.y,

          elapsedTimeS:
            currentState
              .elapsed_time_s,
        };

        const previous =
          current.at(-1);

        if (
          previous &&
          previous.elapsedTimeS ===
            next.elapsedTimeS
        ) {
          return current;
        }

        return [
          ...current,
          next,
        ];
      },
    );
  }, [currentState]);

  const actualPath =
    useMemo(
      () =>
        pointsToPath(
          actualTrack.map(
            (point) =>
              statePositionToSvg(
                point,
                scale,
              ),
          ),
        ),
      [
        actualTrack,
        scale,
      ],
    );

  const currentPosition =
    statePositionToSvg(
      currentState
        ?.position ??
        initialPosition,
      scale,
    );

  const targetPoint =
    polarToSvg(
      targetDisplayRadius,
      initialAngle +
        Math.PI,
    );

  const transferPath =
    getTransferPath(
      initialRadius,
      targetRadius,
      scale,
      initialAngle,
    );

  const maneuverMarkers =
    maneuvers.map(
      (maneuver) => {
        const angle =
          initialAngle +
          angularRate *
            maneuver
              .planned_offset_s;

        const radius =
          maneuver.sequence ===
          1
            ? initialDisplayRadius
            : targetDisplayRadius;

        return {
          maneuver,
          point:
            polarToSvg(
              radius,
              angle,
            ),
        };
      },
    );

  const altitudeKm =
    (
      currentRadius -
      EARTH_RADIUS_M
    ) / 1000;

  return (
    <article className="orbital-display-card">
      <div className="orbital-display-heading">
        <div>
          <span className="eyebrow">
            Orbital Visualization
          </span>

          <h2>
            Earth-centered
            inertial frame
          </h2>
        </div>

        <div className="orbital-display-live">
          <i />

          {missionStatus ===
          "IN_PROGRESS"
            ? "LIVE FLIGHT"
            : "FLIGHT PLAN"}
        </div>
      </div>

      <div className="orbital-display-stage">
        <svg
          viewBox={
            `0 0 ` +
            `${VIEWBOX_SIZE} ` +
            `${VIEWBOX_SIZE}`
          }
          role="img"
          aria-label="Live orbital mission visualization"
        >
          <defs>
            <radialGradient
              id="earth-surface"
              cx="35%"
              cy="30%"
            >
              <stop
                offset="0%"
                stopColor="#238cd5"
              />

              <stop
                offset="55%"
                stopColor="#0c497d"
              />

              <stop
                offset="100%"
                stopColor="#041b34"
              />
            </radialGradient>

            <radialGradient
              id="earth-atmosphere"
            >
              <stop
                offset="70%"
                stopColor="#50d8ff"
                stopOpacity="0.08"
              />

              <stop
                offset="100%"
                stopColor="#50d8ff"
                stopOpacity="0"
              />
            </radialGradient>

            <filter id="spacecraft-glow">
              <feGaussianBlur
                stdDeviation="3"
                result="blur"
              />

              <feMerge>
                <feMergeNode
                  in="blur"
                />

                <feMergeNode
                  in="SourceGraphic"
                />
              </feMerge>
            </filter>
          </defs>

          <g className="orbital-coordinate-grid">
            {[
              80,
              140,
              200,
              260,
            ].map(
              (radius) => (
                <circle
                  key={radius}
                  cx={CENTER}
                  cy={CENTER}
                  r={radius}
                />
              ),
            )}

            <line
              x1="30"
              x2="570"
              y1={CENTER}
              y2={CENTER}
            />

            <line
              x1={CENTER}
              x2={CENTER}
              y1="30"
              y2="570"
            />
          </g>

          <circle
            className="orbital-earth-atmosphere"
            cx={CENTER}
            cy={CENTER}
            r={
              earthRadius +
              18
            }
            fill="url(#earth-atmosphere)"
          />

          <circle
            className="orbital-earth"
            cx={CENTER}
            cy={CENTER}
            r={earthRadius}
            fill="url(#earth-surface)"
          />

          <g className="orbital-earth-details">
            <path
              d={
                `M ${
                  CENTER -
                  earthRadius *
                    0.55
                } ${
                  CENTER -
                  earthRadius *
                    0.15
                } ` +
                `Q ${CENTER} ${
                  CENTER -
                  earthRadius *
                    0.62
                } ${
                  CENTER +
                  earthRadius *
                    0.48
                } ${
                  CENTER -
                  earthRadius *
                    0.12
                }`
              }
            />

            <path
              d={
                `M ${
                  CENTER -
                  earthRadius *
                    0.42
                } ${
                  CENTER +
                  earthRadius *
                    0.28
                } ` +
                `Q ${
                  CENTER +
                  earthRadius *
                    0.05
                } ${
                  CENTER +
                  earthRadius *
                    0.58
                } ${
                  CENTER +
                  earthRadius *
                    0.5
                } ${
                  CENTER +
                  earthRadius *
                    0.2
                }`
              }
            />
          </g>

          <text
            className="orbital-earth-label"
            x={CENTER}
            y={
              CENTER + 4
            }
            textAnchor="middle"
          >
            EARTH
          </text>

          <circle
            className="orbital-reference-orbit orbital-reference-initial"
            cx={CENTER}
            cy={CENTER}
            r={
              initialDisplayRadius
            }
          />

          <circle
            className="orbital-reference-orbit orbital-reference-target"
            cx={CENTER}
            cy={CENTER}
            r={
              targetDisplayRadius
            }
          />

          <path
            className="orbital-transfer-path"
            d={transferPath}
          />

          {actualPath && (
            <path
              className="orbital-actual-path"
              d={actualPath}
            />
          )}

          <g
            className="orbital-target-point"
            transform={
              `translate(` +
              `${targetPoint.x} ` +
              `${targetPoint.y})`
            }
          >
            <circle
              r="13"
            />

            <circle
              r="4"
            />

            <Crosshair
              x={-7}
              y={-7}
              size={14}
            />
          </g>

          {maneuverMarkers.map(
            ({
              maneuver,
              point,
            }) => (
              <g
                className="orbital-maneuver-marker"
                key={
                  maneuver.id
                }
                transform={
                  `translate(` +
                  `${point.x} ` +
                  `${point.y})`
                }
              >
                <circle r="9" />

                <text
                  x="0"
                  y="3"
                  textAnchor="middle"
                >
                  {
                    maneuver.sequence
                  }
                </text>
              </g>
            ),
          )}

          <g
            className="orbital-spacecraft-live"
            transform={
              `translate(` +
              `${currentPosition.x} ` +
              `${currentPosition.y})`
            }
            filter="url(#spacecraft-glow)"
          >
            <circle r="13" />

            <Satellite
              x={-8}
              y={-8}
              size={16}
            />
          </g>
        </svg>

        <div className="orbital-hud orbital-hud-left">
          <span>
            ACTUAL STATE
          </span>

          <strong>
            {altitudeKm.toFixed(
              2,
            )}{" "}
            km
          </strong>

          <small>
            ALTITUDE
          </small>
        </div>

        <div className="orbital-hud orbital-hud-right">
          <span>
            ECI POSITION
          </span>

          <strong>
            X{" "}
            {(
              (
                currentState
                  ?.position.x ??
                initialPosition.x
              ) / 1000
            ).toFixed(0)}
          </strong>

          <strong>
            Y{" "}
            {(
              (
                currentState
                  ?.position.y ??
                initialPosition.y
              ) / 1000
            ).toFixed(0)}
          </strong>

          <small>km</small>
        </div>
      </div>

      <div className="orbital-display-footer">
        <div>
          <i className="orbit-key orbit-key-initial" />

          <span>
            Initial orbit
          </span>
        </div>

        <div>
          <i className="orbit-key orbit-key-target" />

          <span>
            Target orbit
          </span>
        </div>

        <div>
          <i className="orbit-key orbit-key-transfer" />

          <span>
            Nominal transfer
          </span>
        </div>

        <div>
          <i className="orbit-key orbit-key-actual" />

          <span>
            Actual trajectory
          </span>
        </div>

        <div className="orbital-footer-spacer" />

        <span className="orbital-reference-label">
          {
            trajectory
              .reference_frame
          }
        </span>
      </div>
    </article>
  );
}
