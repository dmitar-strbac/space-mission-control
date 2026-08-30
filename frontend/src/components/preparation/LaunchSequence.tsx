import {
  Orbit,
  Rocket,
} from "lucide-react";

import {
  useMemo,
} from "react";

import {
  geoOrthographic,
  geoPath,
} from "d3-geo";

import { feature } from "topojson-client";

import worldLand from "world-atlas/land-110m.json";

import type {
  GeometryCollection,
  Topology,
} from "topojson-specification";

import { motion } from "motion/react";

interface LaunchSequenceProps {
  missionName: string;
}

type WorldLandTopology =
  Topology<{
    land: GeometryCollection;
  }>;

const WORLD_LAND =
  worldLand as unknown as
    WorldLandTopology;

function LaunchEarth() {
  const WIDTH = 1000;
  const HEIGHT = 430;

  const CENTER_X =
    WIDTH / 2;

  const CENTER_Y = 590;
  const RADIUS = 470;

  const land =
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

  const projection =
    useMemo(
      () =>
        geoOrthographic()
          .translate([
            CENTER_X,
            CENTER_Y,
          ])
          .scale(RADIUS)
          .rotate([
            -16,
            -3,
            0,
          ])
          .clipAngle(90)
          .precision(0.4),
      [CENTER_X],
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
      className="launch-earth-svg"
      viewBox={
        `0 0 ${WIDTH} ${HEIGHT}`
      }
      preserveAspectRatio="xMidYMid slice"
      aria-hidden="true"
    >
      <defs>
        <radialGradient
          id="launch-earth-ocean"
          cx="50%"
          cy="0%"
          r="78%"
        >
          <stop
            offset="0%"
            stopColor="#225d89"
          />

          <stop
            offset="23%"
            stopColor="#164568"
          />

          <stop
            offset="56%"
            stopColor="#092c48"
          />

          <stop
            offset="100%"
            stopColor="#041421"
          />
        </radialGradient>

        <linearGradient
          id="launch-earth-light"
          x1="0%"
          y1="0%"
          x2="0%"
          y2="100%"
        >
          <stop
            offset="0%"
            stopColor="#80d8ff"
            stopOpacity="0.13"
          />

          <stop
            offset="35%"
            stopColor="#2d86ba"
            stopOpacity="0.04"
          />

          <stop
            offset="100%"
            stopColor="#01060c"
            stopOpacity="0.46"
          />
        </linearGradient>

        <clipPath id="launch-earth-clip">
          <circle
            cx={CENTER_X}
            cy={CENTER_Y}
            r={RADIUS}
          />
        </clipPath>

        <filter
          id="launch-earth-atmosphere-glow"
          x="-30%"
          y="-30%"
          width="160%"
          height="160%"
        >
          <feGaussianBlur
            stdDeviation="8"
          />
        </filter>
      </defs>

      <circle
        className="launch-earth-atmosphere-glow"
        cx={CENTER_X}
        cy={CENTER_Y}
        r={RADIUS + 5}
      />

      <circle
        className="launch-earth-ocean"
        cx={CENTER_X}
        cy={CENTER_Y}
        r={RADIUS}
        fill="url(#launch-earth-ocean)"
      />

      <g
        clipPath="url(#launch-earth-clip)"
      >
        <path
          className="launch-earth-land"
          d={landPath}
        />

        <circle
          className="launch-earth-light"
          cx={CENTER_X}
          cy={CENTER_Y}
          r={RADIUS}
          fill="url(#launch-earth-light)"
        />
      </g>

      <circle
        className="launch-earth-limb"
        cx={CENTER_X}
        cy={CENTER_Y}
        r={RADIUS}
      />
    </svg>
  );
}

export function LaunchSequence({
  missionName,
}: LaunchSequenceProps) {
  return (
    <motion.div
      className="launch-sequence"
      initial={{
        opacity: 0,
      }}
      animate={{
        opacity: 1,
      }}
    >
      <div className="launch-stars" />

      <motion.div
        className="launch-earth-horizon"
        initial={{
          y: 70,
        }}
        animate={{
          y: 0,
        }}
        transition={{
          duration: 1,
        }}
      >
        <LaunchEarth />
      </motion.div>

      <motion.div
        className="launch-spacecraft"
        initial={{
          y: 150,
          opacity: 0,
        }}
        animate={{
          y: -120,
          opacity: [
            0,
            1,
            1,
          ],
        }}
        transition={{
          duration: 2.3,
          ease: "easeInOut",
        }}
      >
        <Rocket size={36} />
        <span />
      </motion.div>

      <motion.div
        className="launch-sequence-content"
        initial={{
          opacity: 0,
          y: 12,
        }}
        animate={{
          opacity: 1,
          y: 0,
        }}
        transition={{
          delay: 0.35,
        }}
      >
        <Orbit size={26} />

        <span>
          MISSION LAUNCH AUTHORIZED
        </span>

        <h2>{missionName}</h2>

        <p>
          Orbital simulation
          initialized.
        </p>
      </motion.div>
    </motion.div>
  );
}
