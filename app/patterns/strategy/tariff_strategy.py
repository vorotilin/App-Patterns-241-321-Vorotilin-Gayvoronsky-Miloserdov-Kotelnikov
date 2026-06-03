from abc import ABC, abstractmethod

CARGO_MULTIPLIER = {'document': 1.0, 'package': 1.4}


class TariffStrategy(ABC):
    @abstractmethod
    def calculate_price(self, distance_km: float, cargo_type: str = 'document') -> float:
        pass


class EconomyTariff(TariffStrategy):
    def calculate_price(self, distance_km: float, cargo_type: str = 'document') -> float:
        return distance_km * 50 * CARGO_MULTIPLIER.get(cargo_type, 1.0)


class StandardTariff(TariffStrategy):
    def calculate_price(self, distance_km: float, cargo_type: str = 'document') -> float:
        return distance_km * 80 * CARGO_MULTIPLIER.get(cargo_type, 1.0)


class ExpressTariff(TariffStrategy):
    def calculate_price(self, distance_km: float, cargo_type: str = 'document') -> float:
        return distance_km * 150 * CARGO_MULTIPLIER.get(cargo_type, 1.0)