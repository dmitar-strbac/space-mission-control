import { useId } from "react";

export interface TelemetryChartSeries {
  label: string;
  values: Array<number | null>;
  variant?:
    | "primary"
    | "secondary"
    | "success"
    | "caution"
    | "critical";
}

interface TelemetryChartProps {
  title: string;
  subtitle: string;
  unit: string;

  series: TelemetryChartSeries[];

  height?: number;
}

interface Point {
  x: number;
  y: number;
}

const VIEWBOX_WIDTH = 640;
const VIEWBOX_HEIGHT = 220;

const PADDING_LEFT = 48;
const PADDING_RIGHT = 18;
const PADDING_TOP = 18;
const PADDING_BOTTOM = 32;

function getSeriesClass(
  variant:
    | TelemetryChartSeries["variant"]
    | undefined,
) {
  return (
    `telemetry-chart-line ` +
    `telemetry-chart-line-${
      variant ?? "primary"
    }`
  );
}

function buildPoints(
  values: Array<number | null>,
  minimum: number,
  maximum: number,
): Point[] {
  const validEntries = values
    .map((value, index) => ({
      value,
      index,
    }))
    .filter(
      (
        entry,
      ): entry is {
        value: number;
        index: number;
      } => entry.value !== null,
    );

  if (validEntries.length === 0) {
    return [];
  }

  const chartWidth =
    VIEWBOX_WIDTH -
    PADDING_LEFT -
    PADDING_RIGHT;

  const chartHeight =
    VIEWBOX_HEIGHT -
    PADDING_TOP -
    PADDING_BOTTOM;

  const denominator =
    Math.max(
      1,
      values.length - 1,
    );

  const range =
    Math.max(
      0.000001,
      maximum - minimum,
    );

  return validEntries.map(
    ({ value, index }) => {
      const x =
        PADDING_LEFT +
        (index / denominator) *
          chartWidth;

      const normalized =
        (value - minimum) /
        range;

      const y =
        PADDING_TOP +
        (1 - normalized) *
          chartHeight;

      return {
        x,
        y,
      };
    },
  );
}

function pointsToPath(
  points: Point[],
): string {
  if (points.length === 0) {
    return "";
  }

  return points
    .map(
      (point, index) =>
        `${index === 0 ? "M" : "L"} ` +
        `${point.x.toFixed(2)} ` +
        `${point.y.toFixed(2)}`,
    )
    .join(" ");
}

function formatAxisValue(
  value: number,
) {
  const absolute =
    Math.abs(value);

  if (absolute >= 1000) {
    return value.toFixed(0);
  }

  if (absolute >= 100) {
    return value.toFixed(1);
  }

  if (absolute >= 10) {
    return value.toFixed(2);
  }

  return value.toFixed(3);
}

export function TelemetryChart({
  title,
  subtitle,
  unit,
  series,
  height = 220,
}: TelemetryChartProps) {
  const gradientId = useId()
    .replaceAll(":", "");

  const allValues =
    series.flatMap(
      (item) =>
        item.values.filter(
          (
            value,
          ): value is number =>
            value !== null,
        ),
    );

  const hasData =
    allValues.length > 0;

  let minimum =
    hasData
      ? Math.min(...allValues)
      : 0;

  let maximum =
    hasData
      ? Math.max(...allValues)
      : 1;

  if (minimum === maximum) {
    const padding =
      Math.max(
        Math.abs(minimum) * 0.05,
        1,
      );

    minimum -= padding;
    maximum += padding;
  } else {
    const padding =
      (maximum - minimum) * 0.08;

    minimum -= padding;
    maximum += padding;
  }

  const horizontalLines =
    Array.from(
      { length: 5 },
      (_, index) => {
        const ratio =
          index / 4;

        const y =
          PADDING_TOP +
          ratio *
            (
              VIEWBOX_HEIGHT -
              PADDING_TOP -
              PADDING_BOTTOM
            );

        const value =
          maximum -
          ratio *
            (
              maximum -
              minimum
            );

        return {
          y,
          value,
        };
      },
    );

  return (
    <article className="telemetry-chart-card">
      <div className="telemetry-chart-heading">
        <div>
          <span className="eyebrow">
            {subtitle}
          </span>

          <h3>{title}</h3>
        </div>

        <span className="telemetry-chart-window">
          LIVE BUFFER
        </span>
      </div>

      <div className="telemetry-chart-legend">
        {series.map(
          (item) => (
            <span
              key={item.label}
              className={
                `telemetry-chart-legend-item ` +
                `telemetry-chart-legend-${
                  item.variant ??
                  "primary"
                }`
              }
            >
              <i />

              {item.label}
            </span>
          ),
        )}
      </div>

      <div className="telemetry-chart-visual">
        {!hasData && (
          <div className="telemetry-chart-empty">
            Waiting for live telemetry
          </div>
        )}

        <svg
          viewBox={
            `0 0 ` +
            `${VIEWBOX_WIDTH} ` +
            `${VIEWBOX_HEIGHT}`
          }
          style={{
            height,
          }}
          role="img"
          aria-label={`${title} telemetry chart`}
        >
          <defs>
            <linearGradient
              id={gradientId}
              x1="0"
              x2="0"
              y1="0"
              y2="1"
            >
              <stop
                offset="0%"
                stopColor="currentColor"
                stopOpacity="0.18"
              />

              <stop
                offset="100%"
                stopColor="currentColor"
                stopOpacity="0"
              />
            </linearGradient>
          </defs>

          {horizontalLines.map(
            ({ y, value }) => (
              <g key={y}>
                <line
                  className="telemetry-chart-grid-line"
                  x1={PADDING_LEFT}
                  x2={
                    VIEWBOX_WIDTH -
                    PADDING_RIGHT
                  }
                  y1={y}
                  y2={y}
                />

                <text
                  className="telemetry-chart-axis-label"
                  x={
                    PADDING_LEFT -
                    8
                  }
                  y={y + 3}
                  textAnchor="end"
                >
                  {formatAxisValue(
                    value,
                  )}
                </text>
              </g>
            ),
          )}

          <line
            className="telemetry-chart-axis"
            x1={PADDING_LEFT}
            x2={PADDING_LEFT}
            y1={PADDING_TOP}
            y2={
              VIEWBOX_HEIGHT -
              PADDING_BOTTOM
            }
          />

          <line
            className="telemetry-chart-axis"
            x1={PADDING_LEFT}
            x2={
              VIEWBOX_WIDTH -
              PADDING_RIGHT
            }
            y1={
              VIEWBOX_HEIGHT -
              PADDING_BOTTOM
            }
            y2={
              VIEWBOX_HEIGHT -
              PADDING_BOTTOM
            }
          />

          {series.map(
            (item) => {
              const points =
                buildPoints(
                  item.values,
                  minimum,
                  maximum,
                );

              const path =
                pointsToPath(
                  points,
                );

              if (!path) {
                return null;
              }

              const lastPoint =
                points.at(-1);

              return (
                <g
                  key={
                    item.label
                  }
                  className={
                    getSeriesClass(
                      item.variant,
                    )
                  }
                >
                  <path
                    d={path}
                    fill="none"
                    vectorEffect="non-scaling-stroke"
                  />

                  {lastPoint && (
                    <>
                      <circle
                        className="telemetry-chart-live-pulse"
                        cx={
                          lastPoint.x
                        }
                        cy={
                          lastPoint.y
                        }
                        r="7"
                      />

                      <circle
                        className="telemetry-chart-live-point"
                        cx={
                          lastPoint.x
                        }
                        cy={
                          lastPoint.y
                        }
                        r="3"
                      />
                    </>
                  )}
                </g>
              );
            },
          )}

          <text
            className="telemetry-chart-unit"
            x={
              VIEWBOX_WIDTH -
              PADDING_RIGHT
            }
            y={
              VIEWBOX_HEIGHT -
              8
            }
            textAnchor="end"
          >
            {unit}
          </text>
        </svg>
      </div>
    </article>
  );
}
