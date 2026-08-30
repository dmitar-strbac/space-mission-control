import {
  useMemo,
} from "react";

import {
  geoOrthographic,
  geoPath,
} from "d3-geo";

import {
  feature,
} from "topojson-client";

import worldLand from "world-atlas/land-110m.json";

import type {
  GeometryCollection,
  Topology,
} from "topojson-specification";

import { Satellite } from "lucide-react";
import { motion } from "motion/react";

interface OrbitPlanPreviewProps {
  targetAltitudeKm: number;
}

type WorldLandTopology =
  Topology<{
    land: GeometryCollection;
  }>;

const WORLD_LAND =
  worldLand as unknown as
    WorldLandTopology;

const EARTH_VIEWBOX_SIZE = 120;
const EARTH_CENTER =
  EARTH_VIEWBOX_SIZE / 2;
const EARTH_RADIUS = 48;

export function OrbitPlanPreview({
  targetAltitudeKm,
}: OrbitPlanPreviewProps) {
  const earthLand =
    useMemo(
      () =>
        feature(
          WORLD_LAND,
          WORLD_LAND
            .objects
            .land,
        ),
      [],
    );

  const earthProjection =
    useMemo(
      () =>
        geoOrthographic()
          .translate([
            EARTH_CENTER,
            EARTH_CENTER,
          ])
          .scale(
            EARTH_RADIUS,
          )
          .rotate([
            -14,
            -9,
            0,
          ])
          .clipAngle(90)
          .precision(0.45),
      [],
    );

  const earthLandPath =
    useMemo(
      () =>
        geoPath(
          earthProjection,
        )(
          earthLand,
        ) ?? "",
      [
        earthProjection,
        earthLand,
      ],
    );

  return (
    <div className="trajectory-orbit-card">
      <div className="trajectory-orbit-hud">
        <span>
          ECI REFERENCE FRAME
        </span>

        <span>
          NOMINAL TRAJECTORY
        </span>
      </div>

      <div className="trajectory-orbit-visual">
        <div className="trajectory-orbit-grid" />

        <div className="trajectory-earth">
          <svg
            className="trajectory-earth-svg"
            viewBox={
              `0 0 ` +
              `${EARTH_VIEWBOX_SIZE} ` +
              `${EARTH_VIEWBOX_SIZE}`
            }
            aria-hidden="true"
          >
            <defs>
              <radialGradient
                id="trajectory-earth-ocean"
                cx="31%"
                cy="25%"
                r="78%"
              >
                <stop
                  offset="0%"
                  stopColor="#225c80"
                />

                <stop
                  offset="35%"
                  stopColor="#15445f"
                />

                <stop
                  offset="65%"
                  stopColor="#0b2d44"
                />

                <stop
                  offset="87%"
                  stopColor="#061d2e"
                />

                <stop
                  offset="100%"
                  stopColor="#03111d"
                />
              </radialGradient>

              <linearGradient
                id="trajectory-earth-land"
                x1="20%"
                y1="10%"
                x2="80%"
                y2="90%"
              >
                <stop
                  offset="0%"
                  stopColor="#6f8373"
                />

                <stop
                  offset="40%"
                  stopColor="#586f62"
                />

                <stop
                  offset="72%"
                  stopColor="#3d5b52"
                />

                <stop
                  offset="100%"
                  stopColor="#27443f"
                />
              </linearGradient>

              <radialGradient
                id="trajectory-earth-shadow"
                cx="26%"
                cy="22%"
                r="92%"
              >
                <stop
                  offset="0%"
                  stopColor="#00040a"
                  stopOpacity="0"
                />

                <stop
                  offset="52%"
                  stopColor="#00040a"
                  stopOpacity="0.05"
                />

                <stop
                  offset="76%"
                  stopColor="#000309"
                  stopOpacity="0.33"
                />

                <stop
                  offset="100%"
                  stopColor="#000106"
                  stopOpacity="0.78"
                />
              </radialGradient>

              <clipPath id="trajectory-earth-clip">
                <circle
                  cx={EARTH_CENTER}
                  cy={EARTH_CENTER}
                  r={EARTH_RADIUS}
                />
              </clipPath>
            </defs>

            <circle
              className="trajectory-earth-atmosphere"
              cx={EARTH_CENTER}
              cy={EARTH_CENTER}
              r={
                EARTH_RADIUS +
                3
              }
            />

            <circle
              className="trajectory-earth-ocean"
              cx={EARTH_CENTER}
              cy={EARTH_CENTER}
              r={EARTH_RADIUS}
              fill="url(#trajectory-earth-ocean)"
            />

            <g
              clipPath="url(#trajectory-earth-clip)"
            >
              <path
                className="trajectory-earth-land"
                d={earthLandPath}
                fill="url(#trajectory-earth-land)"
              />

              <circle
                className="trajectory-earth-shadow"
                cx={EARTH_CENTER}
                cy={EARTH_CENTER}
                r={EARTH_RADIUS}
                fill="url(#trajectory-earth-shadow)"
              />
            </g>

            <circle
              className="trajectory-earth-limb"
              cx={EARTH_CENTER}
              cy={EARTH_CENTER}
              r={EARTH_RADIUS}
            />

            <g className="trajectory-earth-origin">
              <line
                x1={
                  EARTH_CENTER -
                  4
                }
                x2={
                  EARTH_CENTER +
                  4
                }
                y1={EARTH_CENTER}
                y2={EARTH_CENTER}
              />

              <line
                x1={EARTH_CENTER}
                x2={EARTH_CENTER}
                y1={
                  EARTH_CENTER -
                  4
                }
                y2={
                  EARTH_CENTER +
                  4
                }
              />

              <circle
                cx={EARTH_CENTER}
                cy={EARTH_CENTER}
                r="1.4"
              />
            </g>
          </svg>
        </div>

        <motion.div
          className="trajectory-ring"
          initial={{
            opacity: 0,
            scale: 0.94,
          }}
          animate={{
            opacity: 1,
            scale: 1,
          }}
          transition={{
            duration: 0.7,
          }}
        >
          <motion.div
            className="trajectory-spacecraft"
            animate={{
              rotate: 360,
            }}
            transition={{
              duration: 16,
              repeat: Infinity,
              ease: "linear",
            }}
          >
            <div>
              <Satellite
                size={15}
              />
            </div>
          </motion.div>
        </motion.div>

        <div className="trajectory-axis trajectory-axis-x" />

        <div className="trajectory-axis trajectory-axis-y" />
      </div>

      <div className="trajectory-orbit-footer">
        <div>
          <span>
            TARGET ALTITUDE
          </span>

          <strong>
            {targetAltitudeKm.toLocaleString()}{" "}
            km
          </strong>
        </div>

        <div>
          <span>
            ORBIT MODEL
          </span>

          <strong>
            2D Circular LEO
          </strong>
        </div>
      </div>
    </div>
  );
}
