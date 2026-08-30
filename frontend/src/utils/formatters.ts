export function formatDateTime(
  value: string | null | undefined,
): string {
  if (!value) {
    return "Not scheduled";
  }

  const date = new Date(value);

  return new Intl.DateTimeFormat("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

export function formatNumber(
  value: number,
  maximumFractionDigits = 1,
): string {
  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits,
  }).format(value);
}

export function formatKilograms(value: number): string {
  return `${formatNumber(value)} kg`;
}

export function formatKilonewtons(value: number): string {
  return `${formatNumber(value / 1000)} kN`;
}

export function formatLabel(value: string): string {
  return value
    .toLowerCase()
    .split("_")
    .map(
      (part) =>
        part.charAt(0).toUpperCase() + part.slice(1),
    )
    .join(" ");
}
