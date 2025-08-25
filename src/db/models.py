# src/db/models.py
"""
ORM models for SmartHire Composer using SQLAlchemy.
"""
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, Boolean, UniqueConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData
from src.core.config import DB_SCHEMA
from .base import Base

metadata = MetaData(schema=DB_SCHEMA)
Base = declarative_base(metadata=metadata)

class JobFamily(Base):
    __tablename__ = "job_families"
    __table_args__ = {'extend_existing': True}

    family_id   = Column(Integer, primary_key=True, index=True)
    name        = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)

    job_descriptions = relationship("JobDescription", back_populates="family")

class JDTagMap(Base):
    __tablename__ = "jd_tag_map"
    __table_args__ = {'extend_existing': True}

    jd_id  = Column(Integer, ForeignKey("job_descriptions.jd_id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("jd_taxonomy_tags.tag_id"), primary_key=True)

# Expose the association table object for relationship(secondary=...) to resolve correctly
jd_tag_map = JDTagMap.__table__

class JDTag(Base):
    __tablename__ = "jd_taxonomy_tags"
    __table_args__ = {'extend_existing': True}

    tag_id        = Column(Integer, primary_key=True, index=True)
    tag_name      = Column(String, unique=True, nullable=False)
    description   = Column(Text, nullable=True)
    parent_tag_id = Column(Integer, ForeignKey("jd_taxonomy_tags.tag_id"), nullable=True)

    children = relationship(
        "JDTag",
        backref="parent",
        remote_side=[tag_id]
    )

    # Many-to-many with JobDescription via association table
    job_descriptions = relationship(
        "JobDescription",
        secondary=jd_tag_map,
        back_populates="tags"
    )

class JobDescription(Base):
    __tablename__ = "job_descriptions"
    __table_args__ = {"extend_existing": True}

    # PK is jd_id and ONLY jd_id
    jd_id = Column(Integer, primary_key=True, index=True)
    __mapper_args__ = {"primary_key": (jd_id,)}  # force mapper to use jd_id as PK

    job_code        = Column(String(50), unique=True, nullable=False)
    title           = Column(String, nullable=False)
    department      = Column(String, nullable=True)
    family_id       = Column(Integer, ForeignKey("job_families.family_id"))
    level           = Column(String(20), nullable=True)
    employment_type = Column(String(20), nullable=True)
    location        = Column(String, nullable=True)
    content_md      = Column(Text, nullable=False)
    version         = Column(Integer, default=1, nullable=False)
    created_by      = Column(String(50), nullable=True)
    created_at      = Column(DateTime, default=datetime.utcnow)
    updated_at      = Column(DateTime, nullable=True)

    family   = relationship("JobFamily", back_populates="job_descriptions")
    versions = relationship("JDVersion", back_populates="job_description")
    tags = relationship(
        "JDTag",
        secondary=jd_tag_map,
        back_populates="job_descriptions"
    )

class JDVersion(Base):
    __tablename__ = "jd_versions"
    __table_args__ = (
        UniqueConstraint("jd_id", "version_number", name="jd_versions_jd_id_version_number_key"),
        {'extend_existing': True},
    )

    version_id     = Column(Integer, primary_key=True, index=True)
    jd_id          = Column(Integer, ForeignKey("job_descriptions.jd_id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, nullable=False)
    content_md     = Column(Text, nullable=False)
    edited_by      = Column(String(50), nullable=False)
    edited_at      = Column(DateTime, default=datetime.utcnow, nullable=False)
    change_summary = Column(Text, nullable=True)

    job_description = relationship("JobDescription", back_populates="versions")

class UserRole(Base):
    __tablename__ = "user_roles"
    __table_args__ = {'extend_existing': True}

    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.role_id"), primary_key=True)

# Expose the association table for relationship(secondary=...) resolution
user_roles = UserRole.__table__

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    user_id   = Column(Integer, primary_key=True, index=True)
    username  = Column(String, unique=True, nullable=False)
    full_name = Column(String, nullable=True)
    email     = Column(String, unique=True, nullable=False)
    hashed_pw = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    roles = relationship(
        "Role",
        secondary=user_roles,
        back_populates="users"
    )

class Role(Base):
    __tablename__ = "roles"

    role_id   = Column(Integer, primary_key=True, index=True)
    role_name = Column(String, unique=True, nullable=False)

    users = relationship(
        "User",
        secondary=user_roles,
        back_populates="roles"
    )

class CandidateSkill(Base):
    __tablename__ = "candidate_skills"
    __table_args__ = {'extend_existing': True}

    candidate_id = Column(Integer, ForeignKey("candidate_profiles.candidate_id"), primary_key=True)
    skill_id     = Column(Integer, ForeignKey("skills_master.skill_id"), primary_key=True)

candidate_skills = CandidateSkill.__table__

class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"
    __table_args__ = {'extend_existing': True}

    candidate_id = Column(Integer, primary_key=True, index=True)
    full_name    = Column(String, nullable=False)
    email        = Column(String, unique=True, nullable=False)
    phone        = Column(String, nullable=True)
    resume_text  = Column(Text, nullable=False)
    created_at   = Column(DateTime, default=datetime.utcnow)

    skills = relationship(
        "Skill",
        secondary=candidate_skills,
        back_populates="candidates"
    )

class Skill(Base):
    __tablename__ = "skills_master"
    __table_args__ = {'extend_existing': True}

    skill_id   = Column(Integer, primary_key=True, index=True)
    skill_name = Column(String, unique=True, nullable=False)

    candidates = relationship(
        "CandidateProfile",
        secondary=candidate_skills,
        back_populates="skills"
    )


# {
#     "title": "Software Engineer",
#     "department": "Engineering",
#     "level": "Mid",
#     "job_family": "Backend"
# }