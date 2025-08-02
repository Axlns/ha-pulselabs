from ..const import PLAN_LIMITS
from ..sensors.ApiUsedSensor import ApiUsedSensor
from ..sensors.ApiRemainingSensor import ApiRemainingSensor
from ..sensors.ApiStatusSensor import ApiStatusSensor


async def build_sensors(hass, entry, coordinator):
    """Создаёт сенсоры, связанные с API аккаунтом."""
    sensors = []

    plan = entry.options.get("plan", "hobbyist").lower()
    limit = PLAN_LIMITS.get(plan, 4800)

    sensors.append(ApiUsedSensor(coordinator, entry))
    sensors.append(ApiRemainingSensor(coordinator, entry, limit, plan))

    return sensors


async def build_binary_sensors(hass, entry, coordinator):
    """Создаёт бинарные сенсоры, связанные с API аккаунтом."""
    return [
        ApiStatusSensor(coordinator,entry)
    ]
