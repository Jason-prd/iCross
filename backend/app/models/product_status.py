# -*- coding: utf-8 -*-
"""
iCross Product Status Management
Defines product lifecycle states
"""

from enum import Enum


class ProductStatus(str, Enum):
    """Product status enum"""

    # Selection phase
    DRAFT = "draft"  # Draft/Not selected
    SELECTED = "selected"  # Selected (pending listing)

    # Listing phase
    LISTING = "listing"  # Listing in progress
    LISTED = "listed"  # Listed

    # Sales phase
    OUT_OF_STOCK = "out_of_stock"  # Out of stock
    ARCHIVED = "archived"  # Archived

    # Error
    ERROR = "error"  # Error


class ListingStatus(str, Enum):
    """Listing status"""

    NOT_LISTED = "not_listed"  # Not listed
    PENDING = "pending"  # Pending listing
    LISTING = "listing"  # Listing in progress
    LISTED = "listed"  # Listed
    DELISTED = "delisted"  # Delisted
    ARCHIVED = "archived"  # Archived


# Status display names
STATUS_DISPLAY = {
    "draft": "Not Selected",
    "selected": "Selected",
    "listing": "Listing",
    "listed": "Listed",
    "out_of_stock": "Out of Stock",
    "archived": "Archived",
    "error": "Error",
    "not_listed": "Not Listed",
    "pending": "Pending",
    "delisted": "Delisted",
}

# Status flow
STATUS_FLOW = {
    "draft": ["selected", "error"],
    "selected": ["listing", "archived", "error"],
    "listing": ["listed", "error"],
    "listed": ["out_of_stock", "delisted", "archived", "error"],
    "out_of_stock": ["listed", "archived"],
    "delisted": ["listed", "archived"],
    "archived": [],
    "error": ["draft", "selected"],
}


def can_transition(from_status: str, to_status: str) -> bool:
    """Check if status can transition"""
    allowed = STATUS_FLOW.get(from_status, [])
    return to_status in allowed


def get_display_status(status: str) -> str:
    """Get display name for status"""
    return STATUS_DISPLAY.get(status, status)
