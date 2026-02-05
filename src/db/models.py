from datetime import datetime
from typing import Optional, List
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship, Column, BigInteger

# --- Enums for State Machines (Logic Flow Control) ---

class DealStatus(str, Enum):
    """
    Defines the lifecycle stages of an Escrow Deal.
    Used in `EscrowService` to control state transitions.
    """
    CREATED = "created"             # Initial state. Advertiser drafted.
    ACCEPTED = "accepted"           # Owner agreed to terms.
    DRAFT_SUBMITTED = "drafted"     # Owner submitted the content.
    REVISION_REQUESTED = "revision" # Advertiser asked for changes.
    AWAITING_PAYMENT = "awaiting"   # Advertiser approved draft AND paying.
    LOCKED = "locked"               # Funds confirmed on-chain.
    SCHEDULED = "scheduled"         # Scheduler picked it up.
    PUBLISHED = "published"         # Bot posted to channel.
    COMPLETED = "completed"         # Verification passed, funds released.
    CANCELLED = "cancelled"         # Refunded or aborted.
    REJECTED = "rejected"           # Deal rejected by owner.

class UserRole(str, Enum):
    """
    Role-based Access Control (RBAC).
    """
    ADVERTISER = "advertiser" # Can Buy Ads
    OWNER = "owner"           # Can clean/list channels
    ADMIN = "admin"           # System Admin

# --- Models ---

class User(SQLModel, table=True):
    """
    Represents a User identified by Telegram ID AND Wallet Address.
    Both are stored for robust identity tracking.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    telegram_id: int = Field(sa_column=Column(BigInteger, index=True, unique=True, nullable=False))
    username: Optional[str] = Field(default=None)
    wallet_address: Optional[str] = Field(default=None, index=True, description="TON wallet address")
    role: UserRole = Field(default=UserRole.ADVERTISER)
    
    channels: List["Channel"] = Relationship(back_populates="owner")
    managed_channels: List["ChannelManager"] = Relationship(back_populates="user")
    deals_as_advertiser: List["Deal"] = Relationship(back_populates="advertiser")

class Channel(SQLModel, table=True):
    """
    Represents a Telegram Channel listed on the marketplace.
    Includes verified metrics.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    channel_id: int = Field(sa_column=Column(BigInteger, index=True, unique=True, nullable=False))
    title: str
    username: Optional[str]
    
    # Ownership
    owner_id: int = Field(foreign_key="user.id", index=True) # [PERF] Index for fast "My Channels"
    owner: User = Relationship(back_populates="channels")
    
    # Verified Stats (Snapshots)
    subscribers: int = Field(default=0)
    avg_views: int = Field(default=0)
    language: str = Field(default="en")
    premium_ratio: float = Field(default=0.0)
    
    # Pricing (in TON)
    price_post: float = Field(default=100.0)
    
    verified: bool = Field(default=False, description="Bot confirmed admin rights")
    
    managers: List["ChannelManager"] = Relationship(back_populates="channel")
    deals: List["Deal"] = Relationship(back_populates="channel")

    # timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ChannelManager(SQLModel, table=True):
    """
    Many-to-Many relationship between Users and Channels for management.
    Supports PR Manager flow.
    """
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    channel_id: int = Field(foreign_key="channel.id", primary_key=True)
    
    user: User = Relationship(back_populates="managed_channels")
    channel: Channel = Relationship(back_populates="managers")

class Deal(SQLModel, table=True):
    """
    Represents an Escrow Deal between an Advertiser and a Channel.
    Tracks the lifecycle from Draft to Completion.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relationships
    advertiser_id: int = Field(foreign_key="user.id", index=True) # [PERF] Fast "My Deals" lookup
    advertiser: User = Relationship(back_populates="deals_as_advertiser")
    
    channel_id: int = Field(foreign_key="channel.id", index=True) # [PERF] Fast "Channel Deals" lookup
    channel: Channel = Relationship(back_populates="deals")
    
    # Deal Generic Data
    status: DealStatus = Field(default=DealStatus.CREATED)
    amount_ton: float = Field(default=0.0)
    
    # Content & Schedule
    ad_brief: str = Field(description="Initial instructions from advertiser")
    ad_draft: Optional[str] = Field(default=None, description="Draft submitted by owner")
    rejection_reason: Optional[str] = None
    
    scheduled_at: datetime = Field(nullable=True)
    published_at: Optional[datetime] = None
    
    # Escrow Data
    escrow_wallet: Optional[str] = Field(default=None, description="Temporary wallet for this deal")
    payment_tx_hash: Optional[str] = Field(default=None, unique=True, description="[SECURITY] Hash to prevent replay attacks")
    
    # Verification
    proof_link: Optional[str] = None # Link to the posted message
    
    # timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
