"""
Base Agent Class
----------------
Har naya agent is class ko inherit karta hai.
Isme common functionality hai: logging, retry logic, status tracking.
"""

import time
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional
from datetime import datetime


@dataclass
class AgentResult:
    """Har agent ka output is standard format mein hoga."""
    agent_name: str
    success: bool
    data: Any = None
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    execution_time_sec: float = 0.0


class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    
    Nayi agent banana ho toh:
    1. Is class ko inherit karo
    2. `run()` method implement karo
    3. Orchestrator mein register karo
    """

    MAX_RETRIES = 3
    RETRY_DELAY_SEC = 2  # exponential backoff ke liye base delay

    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"agent.{name}")

    def execute(self, *args, **kwargs) -> AgentResult:
        """
        Public entry point. Retry logic yahan handle hoti hai.
        Directly `run()` mat call karo.
        """
        start_time = time.time()

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                self.logger.info(f"[{self.name}] Attempt {attempt}/{self.MAX_RETRIES} starting...")
                data = self.run(*args, **kwargs)
                elapsed = round(time.time() - start_time, 2)
                self.logger.info(f"[{self.name}] SUCCESS in {elapsed}s")
                return AgentResult(
                    agent_name=self.name,
                    success=True,
                    data=data,
                    execution_time_sec=elapsed
                )

            except Exception as e:
                wait = self.RETRY_DELAY_SEC ** attempt  # exponential: 2s, 4s, 8s
                self.logger.warning(
                    f"[{self.name}] Attempt {attempt} failed: {e}. "
                    f"{'Retrying in ' + str(wait) + 's...' if attempt < self.MAX_RETRIES else 'All retries exhausted.'}"
                )
                if attempt < self.MAX_RETRIES:
                    time.sleep(wait)

        elapsed = round(time.time() - start_time, 2)
        error_msg = f"[{self.name}] failed after {self.MAX_RETRIES} attempts."
        self.logger.error(error_msg)
        return AgentResult(
            agent_name=self.name,
            success=False,
            error=error_msg,
            execution_time_sec=elapsed
        )

    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        """
        Har agent apna actual logic yahan likhega.
        Agar kuch galat ho toh Exception raise karo — base class handle kar lega.
        """
        raise NotImplementedError
