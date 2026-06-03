from abc import ABC, abstractmethod

class TariffStrategy(ABC):
    @abstractmethod
    def calculate_price(self, distance_km: float) -> float:
        pass

class EconomyTariff(TariffStrategy):
    def calculate_price(self, distance_km: float) -> float:
        return distance_km * 50

class StandardTariff(TariffStrategy):
    def calculate_price(self, distance_km: float) -> float:
        return distance_km * 80

class ExpressTariff(TariffStrategy):
    def calculate_price(self, distance_km: float) -> float:
        return distance_km * 150