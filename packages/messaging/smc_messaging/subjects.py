from enum import StrEnum


class SagaSubject(StrEnum):
    MISSION_PREPARE_REQUESTED = "mission.prepare.requested"
    MISSION_READY = "mission.ready"
    MISSION_PREPARATION_FAILED = "mission.preparation.failed"

    VEHICLE_RESERVE_REQUESTED = "vehicle.reserve.requested"
    VEHICLE_RESERVED = "vehicle.reserved"
    VEHICLE_RESERVATION_REJECTED = "vehicle.reservation.rejected"

    VEHICLE_RELEASE_REQUESTED = "vehicle.release.requested"
    VEHICLE_RELEASED = "vehicle.released"

    TRAJECTORY_PLAN_REQUESTED = "trajectory.plan.requested"
    TRAJECTORY_PLAN_CREATED = "trajectory.plan.created"
    TRAJECTORY_PLAN_REJECTED = "trajectory.plan.rejected"

    TRAJECTORY_PLAN_CANCEL_REQUESTED = "trajectory.plan.cancel.requested"
    TRAJECTORY_PLAN_CANCELLED = "trajectory.plan.cancelled"

    RESOURCES_VALIDATION_REQUESTED = "resources.validation.requested"
    RESOURCES_VALIDATED = "resources.validated"
    RESOURCES_VALIDATION_REJECTED = "resources.validation.rejected"

    COMMUNICATION_PROFILE_REQUESTED = "communication.profile.requested"
    COMMUNICATION_PROFILE_CREATED = "communication.profile.created"
    COMMUNICATION_PROFILE_REJECTED = "communication.profile.rejected"

    COMMUNICATION_PROFILE_REMOVE_REQUESTED = "communication.profile.remove.requested"
    COMMUNICATION_PROFILE_REMOVED = "communication.profile.removed"

    SIMULATION_INITIALIZE_REQUESTED = "simulation.initialize.requested"
    SIMULATION_INITIALIZED = "simulation.initialized"
    SIMULATION_INITIALIZATION_REJECTED = "simulation.initialization.rejected"


WORKFLOW_STREAM_NAME = "SMC_WORKFLOWS"

WORKFLOW_STREAM_SUBJECTS = [
    "mission.>",
    "vehicle.>",
    "trajectory.>",
    "resources.>",
    "communication.>",
    "simulation.>",
]
