import { useQuery } from "@tanstack/react-query";

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  getMissionAlerts,
  getRecentTelemetry,
  getTelemetryWebSocketUrl,
} from "../api/telemetryApi";

import type {
  MissionAlert,
  TelemetryPoint,
  TelemetrySocketMessage,
  TelemetrySocketStatus,
} from "../types/telemetry";

const MAX_TELEMETRY_POINTS = 180;

export function useMissionTelemetry(
  missionId: string | undefined,
) {
  const telemetryQuery = useQuery({
    queryKey: ["mission-telemetry", missionId],

    queryFn: () =>
      getRecentTelemetry(
        missionId!,
        MAX_TELEMETRY_POINTS,
      ),

    enabled: Boolean(missionId),
  });

  const alertsQuery = useQuery({
    queryKey: ["mission-alerts", missionId],

    queryFn: () =>
      getMissionAlerts(missionId!),

    enabled: Boolean(missionId),
  });

  const [
    liveTelemetry,
    setLiveTelemetry,
  ] = useState<TelemetryPoint[]>([]);

  const [
    liveAlerts,
    setLiveAlerts,
  ] = useState<MissionAlert[]>([]);

  const [
    socketStatus,
    setSocketStatus,
  ] =
    useState<TelemetrySocketStatus>(
      "disconnected",
    );

  useEffect(() => {
    setLiveTelemetry([]);
    setLiveAlerts([]);

    if (!missionId) {
      setSocketStatus("disconnected");
      return;
    }

    const socketUrl =
      getTelemetryWebSocketUrl(missionId);

    if (!socketUrl) {
      setSocketStatus("error");
      return;
    }

    setSocketStatus("connecting");

    const socket =
      new WebSocket(socketUrl);

    socket.onopen = () => {
      setSocketStatus("connected");
    };

    socket.onmessage = (event) => {
      try {
        const message = JSON.parse(
          event.data as string,
        ) as TelemetrySocketMessage;

        if (message.type === "telemetry") {
          setLiveTelemetry((current) =>
            [
              ...current,
              message.data,
            ].slice(
              -MAX_TELEMETRY_POINTS,
            ),
          );

          return;
        }

        setLiveAlerts((current) => {
          const withoutDuplicate =
            current.filter(
              (alert) =>
                alert.id !==
                message.data.id,
            );

          return [
            message.data,
            ...withoutDuplicate,
          ].slice(0, 100);
        });
      } catch {
        setSocketStatus("error");
      }
    };

    socket.onerror = () => {
      setSocketStatus("error");
    };

    socket.onclose = () => {
      setSocketStatus((current) =>
        current === "error"
          ? current
          : "disconnected",
      );
    };

    return () => {
      socket.close();
    };
  }, [missionId]);

  const telemetry = useMemo(() => {
    const combined = [
      ...(telemetryQuery.data ?? []),
      ...liveTelemetry,
    ];

    const unique =
      new Map<string, TelemetryPoint>();

    for (const point of combined) {
      unique.set(
        `${point.simulation_session_id}:${point.simulation_time_s}`,
        point,
      );
    }

    return [...unique.values()]
      .sort(
        (left, right) =>
          left.simulation_time_s -
          right.simulation_time_s,
      )
      .slice(-MAX_TELEMETRY_POINTS);
  }, [
    telemetryQuery.data,
    liveTelemetry,
  ]);

  const alerts = useMemo(() => {
    const unique =
      new Map<string, MissionAlert>();

    for (const alert of [
      ...liveAlerts,
      ...(alertsQuery.data ?? []),
    ]) {
      if (!unique.has(alert.id)) {
        unique.set(
          alert.id,
          alert,
        );
      }
    }

    return [...unique.values()].sort(
      (left, right) =>
        new Date(
          right.last_seen_at,
        ).getTime() -
        new Date(
          left.last_seen_at,
        ).getTime(),
    );
  }, [
    alertsQuery.data,
    liveAlerts,
  ]);

  return {
    telemetry,

    latestTelemetry:
      telemetry.at(-1) ?? null,

    alerts,
    socketStatus,

    isLoading:
      telemetryQuery.isLoading ||
      alertsQuery.isLoading,
  };
}
