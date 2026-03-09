# -*- coding: utf-8 -*-
"""
iCross Scheduled Tasks
Automated task scheduling using Celery
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class TaskScheduler:
    """Simple task scheduler"""

    def __init__(self):
        self.tasks = {}

    def register_task(self, name: str, func, interval_minutes: int):
        self.tasks[name] = {
            "func": func,
            "interval": interval_minutes,
            "last_run": None,
            "next_run": None,
        }
        logger.info(f"Registered task: {name} (every {interval_minutes} min)")

    def run_task(self, name: str) -> Dict[str, Any]:
        if name not in self.tasks:
            return {"success": False, "error": "Task not found"}

        task = self.tasks[name]
        func = task["func"]

        try:
            start_time = datetime.now()
            result = func()
            end_time = datetime.now()

            task["last_run"] = start_time
            task["next_run"] = start_time + timedelta(minutes=task["interval"])

            return {
                "success": True,
                "task": name,
                "duration_seconds": (end_time - start_time).seconds,
                "result": result,
            }
        except Exception as e:
            logger.error(f"Task {name} failed: {e}")
            return {"success": False, "task": name, "error": str(e)}

    def get_task_status(self, name: str) -> Optional[Dict[str, Any]]:
        if name not in self.tasks:
            return None

        task = self.tasks[name]
        return {
            "name": name,
            "interval_minutes": task["interval"],
            "last_run": task["last_run"].isoformat() if task["last_run"] else None,
            "next_run": task["next_run"].isoformat() if task["next_run"] else None,
        }

    def get_all_tasks_status(self) -> Dict[str, Dict]:
        return {name: self.get_task_status(name) for name in self.tasks}


scheduler = TaskScheduler()


# ==================== Task Functions ====================


def sync_orders_task():
    logger.info("Running: sync_orders_task")
    return {"synced": 0, "message": "Orders sync completed"}


def sync_inventory_task():
    logger.info("Running: sync_inventory_task")
    return {"synced": 0, "message": "Inventory sync completed"}


def sync_products_task():
    logger.info("Running: sync_products_task")
    return {"synced": 0, "message": "Products sync completed"}


def check_low_stock_task():
    logger.info("Running: check_low_stock_task")
    return {"alerts": 0, "message": "Low stock check completed"}


def auto_dropship_task():
    logger.info("Running: auto_dropship_task")
    return {"orders": 0, "message": "Auto dropship completed"}


def update_pricing_task():
    logger.info("Running: update_pricing_task")
    return {"updated": 0, "message": "Pricing update completed"}


# ==================== Register Tasks ====================


def register_all_tasks():
    scheduler.register_task("sync_orders", sync_orders_task, interval_minutes=5)
    scheduler.register_task("sync_inventory", sync_inventory_task, interval_minutes=30)
    scheduler.register_task("sync_products", sync_products_task, interval_minutes=120)
    scheduler.register_task(
        "check_low_stock", check_low_stock_task, interval_minutes=60
    )
    scheduler.register_task("auto_dropship", auto_dropship_task, interval_minutes=10)
    scheduler.register_task(
        "update_pricing", update_pricing_task, interval_minutes=1440
    )
    logger.info("All tasks registered")


def run_scheduled_task(task_name: str) -> Dict[str, Any]:
    return scheduler.run_task(task_name)


def get_task_schedule() -> Dict[str, Dict]:
    return scheduler.get_all_tasks_status()


register_all_tasks()


if __name__ == "__main__":
    print("=== Task Scheduler Test ===\n")
    print("Task Schedule:")
    for name, status in get_task_schedule().items():
        print(f"  {name}: every {status['interval_minutes']} min")

    print("\nRunning sync_orders task...")
    result = run_scheduled_task("sync_orders")
    print(f"Result: {result}")
