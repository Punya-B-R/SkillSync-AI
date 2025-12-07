"""
Data module for verified resources and other static data
"""

from .verified_resources import (
    VERIFIED_RESOURCES,
    TECH_TO_CATEGORY,
    get_resources_for_tech,
    get_resources_for_topics,
    get_all_resources_for_techs
)

__all__ = [
    'VERIFIED_RESOURCES',
    'TECH_TO_CATEGORY',
    'get_resources_for_tech',
    'get_resources_for_topics',
    'get_all_resources_for_techs'
]

