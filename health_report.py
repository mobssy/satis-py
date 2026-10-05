from dataclasses import dataclass, field
from html import escape

# 본문을 못 가져온 기사가 이 비율 이상이면 셀렉터가 깨진 것으로 보고 경고한다
MISSING_BODY_ALERT_RATIO = 0.5


@dataclass
class HealthReport:
    """실행 중 소스별 수집 결과를 모아, 스크래퍼가 조용히 깨진 경우를 찾아낸다"""
    warnings: list[str] = field(default_factory=list)

    def record_source(self, category: str, source: str, articles: list[dict]) -> None:
        if not articles:
            self.warnings.append(f"{category}/{source}: 기사 0개")
            return

        missing = sum(1 for a in articles if not a.get('content'))
        if missing / len(articles) >= MISSING_BODY_ALERT_RATIO:
            self.warnings.append(f"{category}/{source}: 본문 없는 기사 {missing}/{len(articles)}개")

    def record_error(self, category: str, source: str, error: Exception) -> None:
        self.warnings.append(f"{category}/{source}: 오류 - {error}")

    def format_alert(self) -> str | None:
        """경고가 있으면 텔레그램(HTML 모드)으로 보낼 메시지를, 없으면 None을 반환"""
        if not self.warnings:
            return None
        lines = ["⚠️ 뉴스봇 점검 필요", ""]
        lines.extend(f"- {escape(w)}" for w in self.warnings)
        return "\n".join(lines)
