import { useQuery } from "@tanstack/react-query";
import {
  Orbit,
  Plus,
  Search,
} from "lucide-react";
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { getMissions } from "../api/missionApi";
import { MissionCard } from "../components/mission/MissionCard";
import type { MissionStatus } from "../types/mission";

const filters: Array<{
  label: string;
  value: MissionStatus | "ALL";
}> = [
  {
    label: "All",
    value: "ALL",
  },
  {
    label: "Draft",
    value: "DRAFT",
  },
  {
    label: "Preparing",
    value: "PREPARING",
  },
  {
    label: "Ready",
    value: "READY",
  },
  {
    label: "Active",
    value: "IN_PROGRESS",
  },
  {
    label: "Completed",
    value: "COMPLETED",
  },
];

export function MissionsPage() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] =
    useState<MissionStatus | "ALL">("ALL");

  const {
    data,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["missions"],
    queryFn: () =>
      getMissions({
        limit: 100,
      }),
  });

  const missions = useMemo(() => {
    const items = data?.items ?? [];

    return items.filter((mission) => {
      const matchesSearch = mission.name
        .toLowerCase()
        .includes(search.toLowerCase());

      const matchesStatus =
        statusFilter === "ALL" ||
        mission.status === statusFilter;

      return matchesSearch && matchesStatus;
    });
  }, [data, search, statusFilter]);

  return (
    <div className="missions-page">
      <section className="page-heading">
        <div>
          <span className="eyebrow">
            Mission Registry
          </span>

          <h1>Orbital missions</h1>

          <p>
            Review mission definitions, preparation state
            and operational lifecycle across the platform.
          </p>
        </div>

        <Link
          className="primary-button page-action-button"
          to="/missions/new"
        >
          <Plus size={17} />
          New Mission
        </Link>
      </section>

      <section className="mission-toolbar">
        <div className="mission-search">
          <Search size={16} />

          <input
            value={search}
            onChange={(event) =>
              setSearch(event.target.value)
            }
            placeholder="Search missions..."
          />
        </div>

        <div className="mission-filter-list">
          {filters.map((filter) => (
            <button
              key={filter.value}
              className={
                statusFilter === filter.value
                  ? "mission-filter active"
                  : "mission-filter"
              }
              type="button"
              onClick={() =>
                setStatusFilter(filter.value)
              }
            >
              {filter.label}
            </button>
          ))}
        </div>
      </section>

      {isLoading && (
        <div className="mission-loading-grid">
          {Array.from({ length: 6 }).map(
            (_, index) => (
              <div
                className="mission-card-skeleton"
                key={index}
              />
            ),
          )}
        </div>
      )}

      {isError && (
        <div className="content-error-state">
          <Orbit size={28} />
          <strong>
            Mission registry unavailable
          </strong>
          <p>
            The Mission Service could not be reached
            through the API Gateway.
          </p>
        </div>
      )}

      {!isLoading &&
        !isError &&
        missions.length === 0 && (
          <div className="content-empty-state">
            <Orbit size={32} />

            <strong>No missions found</strong>

            <p>
              Create a new orbital mission or adjust the
              current filters.
            </p>
          </div>
        )}

      {!isLoading &&
        !isError &&
        missions.length > 0 && (
          <>
            <div className="mission-results-heading">
              <span>
                {missions.length} mission
                {missions.length === 1 ? "" : "s"}
              </span>
            </div>

            <div className="mission-grid">
              {missions.map((mission) => (
                <MissionCard
                  key={mission.id}
                  mission={mission}
                />
              ))}
            </div>
          </>
        )}
    </div>
  );
}
