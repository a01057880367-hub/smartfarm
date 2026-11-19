"""
services/auth_service.py
사용자 인증, 회원가입, 세션 관리 서비스
"""
from typing import Optional, Tuple, List
from models.user import User
from services.storage_service import StorageService


class AuthService:
    """회원가입, 로그인, 현재 로그인 세션을 관리하는 서비스 클래스"""

    def __init__(self, storage: StorageService):
        self.storage = storage
        self.current_user: Optional[User] = None

    def register(self, user_id: str, password: str, password_confirm: str) -> Tuple[bool, str]:
        """
        회원가입 처리
        - 빈칸 검사
        - 비밀번호 일치 검사
        - 아이디 중복 검사
        """
        user_id = user_id.strip()
        password = password.strip()
        password_confirm = password_confirm.strip()

        if not user_id:
            return False, "아이디를 입력해 주세요."
        if not password:
            return False, "비밀번호를 입력해 주세요."
        if not password_confirm:
            return False, "비밀번호 확인을 입력해 주세요."
        if password != password_confirm:
            return False, "두 비밀번호가 일치하지 않습니다. 다시 확인해 주세요."

        users = self.storage.get_users()
        for u in users:
            if u.user_id.lower() == user_id.lower():
                return False, f"이미 등록된 아이디 '{user_id}' 입니다. 다른 아이디를 사용해 주세요."

        new_user = User(user_id=user_id, password=password)
        users.append(new_user)
        self.storage.save_users(users)
        return True, "회원가입이 완료되었습니다. 로그인해 주세요."

    def login(self, user_id: str, password: str) -> Tuple[bool, str]:
        """
        로그인 처리
        - 아이디 및 비밀번호 검증
        - 성공 시 현재 세션 사용자(current_user) 설정
        """
        user_id = user_id.strip()
        password = password.strip()

        if not user_id or not password:
            return False, "아이디와 비밀번호를 모두 입력해 주세요."

        users = self.storage.get_users()
        for u in users:
            if u.user_id == user_id:
                if u.check_password(password):
                    self.current_user = u
                    return True, "로그인에 성공하였습니다."
                else:
                    return False, "비밀번호가 일치하지 않습니다. 다시 확인해 주세요."

        return False, "등록되지 않은 아이디입니다. 아이디를 확인하거나 회원가입을 진행해 주세요."

    def logout(self) -> None:
        """현재 세션 로그아웃"""
        self.current_user = None

    def get_current_user(self) -> Optional[User]:
        return self.current_user

    def is_logged_in(self) -> bool:
        return self.current_user is not None
