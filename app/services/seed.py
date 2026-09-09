"""Kigali-flavoured demo seed. Educational simulation only."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.security import hash_password
from app.config import get_settings
from app.models.assignment import Assignment
from app.models.enums import (
    AssignmentStatus,
    IncidentSeverity,
    IncidentStatus,
    IncidentType,
    ResourceStatus,
    ResourceType,
    Role,
)
from app.models.incident import Incident
from app.models.notification import Notification
from app.models.resource import Resource
from app.models.user import User

logger = logging.getLogger("nexusone.seed")

# Approximate Kigali landmarks around -1.95, 30.06
KIGALI = {
    "nyabugogo": (-1.9397, 30.0444, "Nyabugogo bus park"),
    "kacyiru": (-1.9442, 30.0781, "Kacyiru"),
    "remera": (-1.9578, 30.1124, "Remera"),
    "kimironko": (-1.9494, 30.1252, "Kimironko market"),
    "nyamirambo": (-1.9801, 30.0398, "Nyamirambo"),
    "gikondo": (-1.9754, 30.0752, "Gikondo"),
    "kanombe": (-1.9685, 30.1348, "Kanombe"),
    "nyarugenge": (-1.9439, 30.0612, "Nyarugenge"),
    "kicukiro": (-1.9780, 30.1002, "Kicukiro"),
    "convention": (-1.9546, 30.0935, "Kigali Convention Centre"),
    "chuk": (-1.9588, 30.0589, "CHUK / Nyarugenge hospital area"),
    "amahoro": (-1.9520, 30.1120, "Amahoro Stadium, Remera"),
}


def seed_if_empty(db: Session) -> None:
    settings = get_settings()
    if not settings.seed_demo_data:
        return
    if db.scalar(select(User.id).limit(1)) is not None:
        return

    password = hash_password(settings.app_seed_password)
    now = datetime.now(timezone.utc)

    citizen = User(
        email="citizen@nexusone.local",
        hashed_password=password,
        full_name="Amahoro Uwase",
        phone="+250788010001",
        role=Role.CITIZEN,
        created_at=now,
    )
    dispatcher = User(
        email="dispatcher@nexusone.local",
        hashed_password=password,
        full_name="Jean-Claude Dispatch",
        phone="+250788010002",
        role=Role.DISPATCHER,
        created_at=now,
    )
    responder = User(
        email="responder@nexusone.local",
        hashed_password=password,
        full_name="Marie First-Responder",
        phone="+250788010003",
        role=Role.RESPONDER,
        created_at=now,
    )
    admin = User(
        email="admin@nexusone.local",
        hashed_password=password,
        full_name="Nexus Admin",
        phone="+250788010004",
        role=Role.ADMIN,
        created_at=now,
    )
    db.add_all([citizen, dispatcher, responder, admin])
    db.flush()

    resources = [
        Resource(
            name="CHUK Emergency Desk",
            resource_type=ResourceType.CLINIC,
            capacity=40,
            current_load=12,
            latitude=KIGALI["chuk"][0],
            longitude=KIGALI["chuk"][1],
            location_name=KIGALI["chuk"][2],
            status=ResourceStatus.AVAILABLE,
            contact_phone="+250788111001",
            notes="Public referral hospital. Simulation only.",
        ),
        Resource(
            name="King Faisal Ambulance",
            resource_type=ResourceType.AMBULANCE,
            capacity=4,
            current_load=1,
            latitude=KIGALI["kacyiru"][0],
            longitude=KIGALI["kacyiru"][1],
            location_name="King Faisal Hospital, Kacyiru",
            status=ResourceStatus.AVAILABLE,
            contact_phone="+250788111002",
        ),
        Resource(
            name="Remera Ambulance 2",
            resource_type=ResourceType.AMBULANCE,
            capacity=2,
            current_load=2,
            latitude=KIGALI["remera"][0],
            longitude=KIGALI["remera"][1],
            location_name=KIGALI["remera"][2],
            status=ResourceStatus.BUSY,
            contact_phone="+250788111003",
            notes="Currently on a transfer — ranks lower in DispatchRanker.",
        ),
        Resource(
            name="Nyarugenge Fire Unit",
            resource_type=ResourceType.FIRE_UNIT,
            capacity=8,
            current_load=0,
            latitude=KIGALI["nyarugenge"][0],
            longitude=KIGALI["nyarugenge"][1],
            location_name=KIGALI["nyarugenge"][2],
            status=ResourceStatus.AVAILABLE,
            contact_phone="+250788111004",
        ),
        Resource(
            name="Nyabugogo City Bus Standby",
            resource_type=ResourceType.BUS,
            capacity=45,
            current_load=6,
            latitude=KIGALI["nyabugogo"][0],
            longitude=KIGALI["nyabugogo"][1],
            location_name=KIGALI["nyabugogo"][2],
            status=ResourceStatus.AVAILABLE,
            contact_phone="+250788111005",
            notes="Evacuation lift for flood / missing-person sweeps.",
        ),
        Resource(
            name="Amahoro Shelter",
            resource_type=ResourceType.SHELTER,
            capacity=200,
            current_load=40,
            latitude=KIGALI["amahoro"][0],
            longitude=KIGALI["amahoro"][1],
            location_name=KIGALI["amahoro"][2],
            status=ResourceStatus.AVAILABLE,
            contact_phone="+250788111006",
        ),
        Resource(
            name="Gikondo Warehouse Shelter",
            resource_type=ResourceType.SHELTER,
            capacity=80,
            current_load=80,
            latitude=KIGALI["gikondo"][0],
            longitude=KIGALI["gikondo"][1],
            location_name=KIGALI["gikondo"][2],
            status=ResourceStatus.BUSY,
            notes="At capacity.",
        ),
        Resource(
            name="Rwanda Red Cross Volunteers",
            resource_type=ResourceType.VOLUNTEER_TEAM,
            capacity=24,
            current_load=4,
            latitude=KIGALI["convention"][0],
            longitude=KIGALI["convention"][1],
            location_name=KIGALI["convention"][2],
            status=ResourceStatus.AVAILABLE,
            contact_phone="+250788111007",
        ),
        Resource(
            name="Kimironko Search Team",
            resource_type=ResourceType.VOLUNTEER_TEAM,
            capacity=12,
            current_load=0,
            latitude=KIGALI["kimironko"][0],
            longitude=KIGALI["kimironko"][1],
            location_name=KIGALI["kimironko"][2],
            status=ResourceStatus.AVAILABLE,
            contact_phone="+250788111008",
        ),
        Resource(
            name="Kanombe Clinic Night Desk",
            resource_type=ResourceType.CLINIC,
            capacity=16,
            current_load=3,
            latitude=KIGALI["kanombe"][0],
            longitude=KIGALI["kanombe"][1],
            location_name=KIGALI["kanombe"][2],
            status=ResourceStatus.AVAILABLE,
            contact_phone="+250788111009",
        ),
        Resource(
            name="Kicukiro Fire Reserve",
            resource_type=ResourceType.FIRE_UNIT,
            capacity=6,
            current_load=0,
            latitude=KIGALI["kicukiro"][0],
            longitude=KIGALI["kicukiro"][1],
            location_name=KIGALI["kicukiro"][2],
            status=ResourceStatus.OFFLINE,
            notes="Offline for maintenance — DispatchRanker marks ineligible.",
        ),
    ]
    db.add_all(resources)
    db.flush()

    incidents = [
        Incident(
            title="Nyabugogo drainage overflow",
            description="Knee-deep water at the taxi park. Pedestrians stranded on the median. Simulation.",
            incident_type=IncidentType.FLOOD,
            status=IncidentStatus.OPEN,
            severity=IncidentSeverity.HIGH,
            latitude=KIGALI["nyabugogo"][0],
            longitude=KIGALI["nyabugogo"][1],
            location_name=KIGALI["nyabugogo"][2],
            reporter_id=citizen.id,
            created_at=now - timedelta(minutes=42),
            updated_at=now - timedelta(minutes=42),
        ),
        Incident(
            title="Medical collapse near CHUK gate",
            description="Adult unresponsive at the hospital roundabout. Bystander CPR in progress. Simulation.",
            incident_type=IncidentType.MEDICAL,
            status=IncidentStatus.ASSIGNED,
            severity=IncidentSeverity.CRITICAL,
            latitude=KIGALI["chuk"][0],
            longitude=KIGALI["chuk"][1],
            location_name=KIGALI["chuk"][2],
            reporter_id=citizen.id,
            created_at=now - timedelta(minutes=18),
            updated_at=now - timedelta(minutes=10),
        ),
        Incident(
            title="Nyamirambo market stall fire",
            description="Smoke from a charcoal stall cluster. Crowd forming on the main road. Simulation.",
            incident_type=IncidentType.FIRE,
            status=IncidentStatus.OPEN,
            severity=IncidentSeverity.HIGH,
            latitude=KIGALI["nyamirambo"][0],
            longitude=KIGALI["nyamirambo"][1],
            location_name=KIGALI["nyamirambo"][2],
            reporter_id=citizen.id,
            created_at=now - timedelta(minutes=9),
            updated_at=now - timedelta(minutes=9),
        ),
        Incident(
            title="Missing child last seen Kimironko",
            description="Eight-year-old last seen near the fabric rows. Blue school jumper. Simulation.",
            incident_type=IncidentType.MISSING_PERSON,
            status=IncidentStatus.OPEN,
            severity=IncidentSeverity.MEDIUM,
            latitude=KIGALI["kimironko"][0],
            longitude=KIGALI["kimironko"][1],
            location_name=KIGALI["kimironko"][2],
            reporter_id=citizen.id,
            created_at=now - timedelta(hours=1, minutes=5),
            updated_at=now - timedelta(hours=1, minutes=5),
        ),
        Incident(
            title="Gikondo industrial drain flood",
            description="Workshop street flooded after overnight rain. Two families requesting lift. Simulation.",
            incident_type=IncidentType.FLOOD,
            status=IncidentStatus.RESOLVED,
            severity=IncidentSeverity.MEDIUM,
            latitude=KIGALI["gikondo"][0],
            longitude=KIGALI["gikondo"][1],
            location_name=KIGALI["gikondo"][2],
            reporter_id=citizen.id,
            created_at=now - timedelta(hours=6),
            updated_at=now - timedelta(hours=2),
            resolved_at=now - timedelta(hours=2),
        ),
    ]
    db.add_all(incidents)
    db.flush()

    medical = incidents[1]
    ambulance = next(r for r in resources if r.name == "King Faisal Ambulance")
    db.add(
        Assignment(
            incident_id=medical.id,
            resource_id=ambulance.id,
            assigned_by_id=dispatcher.id,
            responder_id=responder.id,
            status=AssignmentStatus.EN_ROUTE,
            notes="Seed assignment — DispatchRanker recommended this unit.",
            ranker_score=91.0,
            ranker_reason="Ambulance ↔ MEDICAL, 1.9 km, available, spare capacity",
            assigned_at=now - timedelta(minutes=10),
            updated_at=now - timedelta(minutes=10),
        )
    )
    ambulance.current_load = min(ambulance.capacity, ambulance.current_load + 1)

    db.add_all(
        [
            Notification(
                user_id=dispatcher.id,
                title="New flood report — Nyabugogo",
                body="HIGH flood at Nyabugogo bus park. DispatchRanker has not assigned a unit yet.",
                incident_id=incidents[0].id,
                created_at=now - timedelta(minutes=40),
            ),
            Notification(
                user_id=responder.id,
                title="You are assigned — CHUK gate",
                body="King Faisal Ambulance is en route to a CRITICAL medical incident (simulation).",
                incident_id=medical.id,
                created_at=now - timedelta(minutes=10),
            ),
            Notification(
                user_id=citizen.id,
                title="Report received",
                body="Your Nyamirambo fire report is on the live board. This is a simulation.",
                incident_id=incidents[2].id,
                created_at=now - timedelta(minutes=8),
            ),
        ]
    )
    db.commit()
    logger.info("Seeded NexusOne demo users, Kigali resources, and incidents")
