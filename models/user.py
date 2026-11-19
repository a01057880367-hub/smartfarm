"""
models/user.py
사용자 계정 도메인 엔티티
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """사용자 계정 정보 모델"""
    user_id: str
    password: str
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def check_password(self, password: str) -> bool:
        """비밀번호 일치 여부 확인"""
        return self.password == password

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(
            user_id=data["user_id"],
            password=data["password"],
            created_at=data.get("created_at", "")
        )
