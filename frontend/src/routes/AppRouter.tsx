import {
  Navigate,
  createBrowserRouter,
} from "react-router-dom";

import { AppLayout } from "../components/layout/AppLayout";
import { CreateMissionPage } from "../pages/CreateMissionPage";
import { DashboardPage } from "../pages/DashboardPage";
import { LoginPage } from "../pages/LoginPage";
import { MissionDetailsPage } from "../pages/MissionDetailsPage";
import { MissionsPage } from "../pages/MissionsPage";
import { ProtectedRoute } from "./ProtectedRoute";

export const router = createBrowserRouter([
  {
    path: "/login",
    element: <LoginPage />,
  },
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <AppLayout />,
        children: [
          {
            index: true,
            element: <DashboardPage />,
          },
          {
            path: "missions",
            element: <MissionsPage />,
          },
          {
            path: "missions/new",
            element: <CreateMissionPage />,
          },
          {
            path: "missions/:missionId",
            element: <MissionDetailsPage />,
          },
          {
            path: "*",
            element: <Navigate to="/" replace />,
          },
        ],
      },
    ],
  },
]);
