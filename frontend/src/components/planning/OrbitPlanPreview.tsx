import { Satellite } from "lucide-react";
import { motion } from "motion/react";

interface OrbitPlanPreviewProps {
  targetAltitudeKm: number;
}

export function OrbitPlanPreview({
  targetAltitudeKm,
}: OrbitPlanPreviewProps) {
  return (
    <div className="trajectory-orbit-card">
      <div className="trajectory-orbit-hud">
        <span>ECI REFERENCE FRAME</span>
        <span>NOMINAL TRAJECTORY</span>
      </div>

      <div className="trajectory-orbit-visual">
        <div className="trajectory-orbit-grid" />

        <div className="trajectory-earth">
          <div className="trajectory-earth-glow" />
          <span>EARTH</span>
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
              <Satellite size={15} />
            </div>
          </motion.div>
        </motion.div>

        <div className="trajectory-axis trajectory-axis-x" />
        <div className="trajectory-axis trajectory-axis-y" />
      </div>

      <div className="trajectory-orbit-footer">
        <div>
          <span>TARGET ALTITUDE</span>
          <strong>
            {targetAltitudeKm.toLocaleString()} km
          </strong>
        </div>

        <div>
          <span>ORBIT MODEL</span>
          <strong>2D Circular LEO</strong>
        </div>
      </div>
    </div>
  );
}
