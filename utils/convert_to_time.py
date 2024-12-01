def convert_to_time(time_string):
    """
    Konwertuje tekstowy zapis czasu na obiekt timedelta.
    Obsługuje formaty: godzina:minuta:sekunda, godzina:minuta,
    minuta:sekunda, oraz sytuacje z dodatkowymi spacjami i bardzo dużymi godzinami.
    """
    import re
    from datetime import timedelta

    # Usuń nadmiarowe spacje
    time_string = time_string.strip()

    # Wzorzec do rozdzielenia godziny, minut i sekund
    pattern = r'^\s*(\d+):(\d{1,2}):(\d{1,2})\s*$|^\s*(\d+):(\d{1,2})\s*$|^\s*(\d+):(\d{1,2})\s*$'
    match = re.match(pattern, time_string)

    if match:
        if match.group(1) and match.group(2) and match.group(3):  # Format godzina:minuta:sekunda
            hours = int(match.group(1))
            minutes = int(match.group(2))
            seconds = int(match.group(3))
        elif match.group(4) and match.group(5):  # Format godzina:minuta
            hours = int(match.group(4))
            minutes = int(match.group(5))
            seconds = 0
        elif match.group(6) and match.group(7):  # Format minuta:sekunda
            hours = 0
            minutes = int(match.group(6))
            seconds = int(match.group(7))
        else:
            raise ValueError(f"Nieprawidłowy format czasu: {time_string}")

        return timedelta(hours=hours, minutes=minutes, seconds=seconds)
    else:
        raise ValueError(f"Nieprawidłowy format czasu: {time_string}")
