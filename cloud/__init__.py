"""
Cloud and Microservices Architecture Module

This module provides cloud-native and microservices capabilities for HackGPT,
including Docker containerization, Kubernetes deployment, and service decomposition.
"""

from .docker_manager import DockerManager
from .kubernetes_manager import KubernetesManager
from .service_registry import ServiceRegistry
from .microservice_base import MicroserviceBase
from .load_balancer import LoadBalancer

__version__ = "1.0.0"

__all__ = [
    "DockerManager",
    "KubernetesManager",
    "ServiceRegistry",
    "MicroserviceBase",
    "LoadBalancer",
]
