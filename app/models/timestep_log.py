"""Timestep log model - detailed metrics recorded per simulation step"""

from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, JSON, Index, CheckConstraint
from app.models.base import Base


class TimestepLog(Base):
    """Database model for timestep execution logs with detailed metrics"""

    __tablename__ = "timestep_logs"

    # Indexes for performance
    __table_args__ = (
        Index("idx_timestep_log_sim_step", "simulation_id", "timestep"),
        Index("idx_timestep_log_created_at", "created_at"),
        CheckConstraint("timestep >= 0", name="ck_timestep_positive"),
        CheckConstraint("stability_score >= 0.0 AND stability_score <= 1.0", name="ck_ts_stability_range"),
        CheckConstraint("risk_level >= 0.0 AND risk_level <= 1.0", name="ck_ts_risk_range"),
        CheckConstraint("unmet_demand >= 0.0", name="ck_ts_unmet_positive"),
    )

    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id"), nullable=False)
    timestep = Column(Integer, nullable=False)

    # System state at this timestep
    power_available = Column(Float, nullable=False)
    water_available = Column(Float, nullable=False)
    power_allocated = Column(Float, default=0.0, nullable=False)
    water_allocated = Column(Float, default=0.0, nullable=False)

    # Metrics
    stability_score = Column(Float, nullable=False)
    risk_level = Column(Float, nullable=False)
    unmet_demand = Column(Float, default=0.0, nullable=False)
    allocation_efficiency = Column(Float, default=0.0, nullable=False)  # % of demand met
    fairness_score = Column(Float, default=0.0, nullable=False)  # 0.0 = unfair, 1.0 = fair

    # Count metrics
    total_agents = Column(Integer, default=0, nullable=False)
    agents_satisfied = Column(Integer, default=0, nullable=False)
    agents_critical = Column(Integer, default=0, nullable=False)  # Unmet demand > 50%

    # Event summary
    events_occurred = Column(Integer, default=0, nullable=False)
    events_summary = Column(JSON, default=list, nullable=False)  # [{"type": "...", "severity": 0.X}]

    # Bid summary (snapshot of negotiation)
    total_bids = Column(Integer, default=0, nullable=False)
    avg_utility_score = Column(Float, default=0.0, nullable=False)
    highest_utility_score = Column(Float, default=0.0, nullable=False)

    # Trust metrics snapshot
    avg_trust_score = Column(Float, default=0.5, nullable=False)
    min_trust_score = Column(Float, default=0.5, nullable=False)
    max_trust_score = Column(Float, default=0.5, nullable=False)

    # Allocation details by resource
    power_satisfaction_rate = Column(Float, default=0.0, nullable=False)  # How much was power demand met
    water_satisfaction_rate = Column(Float, default=0.0, nullable=False)  # How much was water demand met

    # Notes/explanations
    notes = Column(String(1000), nullable=True)  # Summary of significant events

    def __repr__(self):
        return f"<TimestepLog sim={self.simulation_id} step={self.timestep} stability={self.stability_score:.2f}>"
