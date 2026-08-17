import { Orbit, Rocket } from "lucide-react";
import { motion } from "motion/react";

interface LaunchSequenceProps {
  missionName: string;
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
      />

      <motion.div
        className="launch-spacecraft"
        initial={{
          y: 150,
          opacity: 0,
        }}
        animate={{
          y: -120,
          opacity: [0, 1, 1],
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

        <span>MISSION LAUNCH AUTHORIZED</span>

        <h2>{missionName}</h2>

        <p>
          Orbital simulation initialized.
        </p>
      </motion.div>
    </motion.div>
  );
}
