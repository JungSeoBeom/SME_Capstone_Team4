"""
차량 생성 및 도착 프로세스를 관리하는 모듈입니다.
"""
import simpy
import random
from typing import List, Callable, Optional

from src.config import NUM_NORMAL, NUM_EV
from src.utils.helpers import sample_interarrival
from src.utils.logger import SimulationLogger
from src.models.vehicle import Vehicle


class VehicleGenerator:
    """
    시뮬레이션 동안 차량을 생성하는 클래스입니다.
    """
    
    def __init__(self, 
                 env: simpy.Environment, 
                 parking_res: simpy.Resource, 
                 charger_res: simpy.Resource,
                 logger: SimulationLogger):
        """
        차량 생성기를 초기화합니다.
        
        Args:
            env: SimPy 환경 객체
            parking_res: 일반 주차면 리소스
            charger_res: EV 충전소 리소스
            logger: 이벤트 로깅을 위한 로거 객체
        """
        self.env = env
        self.parking_res = parking_res
        self.charger_res = charger_res
        self.logger = logger
        
        # 차량 ID 초기화
        self.next_id = 0
    
    def generate_vehicle(self, vtype: str) -> None:
        """
        주어진 유형의 차량을 생성하고 시뮬레이션에 추가합니다.
        
        Args:
            vtype: 차량 유형 ("normal" 또는 "ev")
        """
        vehicle = Vehicle(
            vid=self.next_id,
            vtype=vtype,
            env=self.env,
            parking_res=self.parking_res,
            charger_res=self.charger_res,
            logger=self.logger
        )
        
        self.next_id += 1
        self.env.process(vehicle.process())
    
    def run(self) -> None:
        """
        지정된 수의 일반 차량과 전기차를 생성하는 프로세스를 시작합니다.
        차량은 지수 분포에 따라 도착합니다.
        """
        # 모든 차량(일반 + 전기차)을 랜덤 순서로 생성
        total_vehicles = self.normal_count + self.ev_count
        vehicle_types = ["normal"] * self.normal_count + ["ev"] * self.ev_count
        random.shuffle(vehicle_types)  # 차량 유형 순서를 랜덤하게 섞음
        
        # 랜덤 순서로 차량 생성
        for vtype in vehicle_types:
            yield self.env.timeout(self.interarrival_func())
            self.generate_vehicle(vtype)


class CustomVehicleGenerator(VehicleGenerator):
    """
    사용자 정의 분포나 도착 패턴을 적용할 수 있는 확장된 차량 생성기입니다.
    """
    
    def __init__(self, 
                 env: simpy.Environment, 
                 parking_res: simpy.Resource, 
                 charger_res: simpy.Resource,
                 logger: SimulationLogger,
                 interarrival_func: Optional[Callable[[], float]] = None,
                 normal_count: int = NUM_NORMAL,
                 ev_count: int = NUM_EV):
        """
        사용자 정의 차량 생성기를 초기화합니다.
        
        Args:
            env: SimPy 환경 객체
            parking_res: 일반 주차면 리소스
            charger_res: EV 충전소 리소스
            logger: 이벤트 로깅을 위한 로거 객체
            interarrival_func: 도착 시간 간격을 샘플링하는 함수
            normal_count: 생성할 일반 차량 수
            ev_count: 생성할 전기차 수
        """
        super().__init__(env, parking_res, charger_res, logger)
        # interarrival_func가 None이면 기본 함수 사용
        self.interarrival_func = interarrival_func if interarrival_func is not None else sample_interarrival
        self.normal_count = normal_count
        self.ev_count = ev_count
    
    def run(self) -> None:
        """
        사용자 정의 분포에 따라 차량을 생성합니다.
        """
        # 모든 차량(일반 + 전기차)을 랜덤 순서로 생성
        total_vehicles = self.normal_count + self.ev_count
        vehicle_types = ["normal"] * self.normal_count + ["ev"] * self.ev_count
        random.shuffle(vehicle_types)  # 차량 유형 순서를 랜덤하게 섞음
        
        # 랜덤 순서로 차량 생성
        for vtype in vehicle_types:
            yield self.env.timeout(self.interarrival_func())
            self.generate_vehicle(vtype) 