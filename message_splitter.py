def split_message(message: str, limit: int) -> list[str]:
    """메시지를 줄 단위로 묶어 limit자 이하의 파트로 분할

    limit보다 긴 줄은 강제로 잘라내며, 빈 파트는 만들지 않는다.
    """
    parts = []
    current_part = ""

    for line in message.split('\n'):
        # 남은 줄에 개행을 붙여도 limit을 넘지 않도록 limit 이상인 줄은 먼저 잘라낸다
        while len(line) >= limit:
            if current_part:
                parts.append(current_part)
                current_part = ""
            parts.append(line[:limit])
            line = line[limit:]

        if current_part and len(current_part) + len(line) + 1 > limit:
            parts.append(current_part)
            current_part = ""

        current_part += line + '\n'

    if current_part.strip():
        parts.append(current_part)

    return parts
