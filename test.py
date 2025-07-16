import pytest

from process_to_csv import process_info, ProcessedInfo

@pytest.mark.parametrize(
    "input, expected",
    [
        (
            "Lanier, Louis 'Georgia Ridge Runner'; GA, USA,",
            ProcessedInfo(
                last_name="Lanier",
                first_name="Louis",
                trail_name="Georgia Ridge Runner",
                state="GA",
                country="USA",
                hike_type=None
            )
        ),
        (
            "F. Miller, George ''-'; '-, USA, -",
            ProcessedInfo(
                last_name="F. Miller",
                first_name="George",
                trail_name=None,
                state=None,
                country="USA",
                hike_type=None
            )
        ),
        (
            "Bradley, Adam '¡El Monstro!'; NV, USA, SOBO",
            ProcessedInfo(
                last_name="Bradley",
                first_name="Adam",
                trail_name="¡El Monstro!",
                state="NV",
                country="USA",
                hike_type="SOBO"
            )
        ),
        (
            "H. Shattuck, James ''-'; CT, USA, -",
            ProcessedInfo(
                last_name="H. Shattuck",
                first_name="James",
                trail_name=None,
                state="CT",
                country="USA",
                hike_type=None
            )
        ),
        (
            "McDonald, Brittany 'Puddin''; Virginia, United States, NOBO",
            ProcessedInfo(
                last_name="McDonald",
                first_name="Brittany",
                trail_name="Puddin'",
                state="Virginia",
                country="United States",
                hike_type="NOBO"
            )
        ),
        (
            "O'Keefe, Emily 'Emily O'Keefe'; VA, United States, NOBO",
            ProcessedInfo(
                last_name="O'Keefe",
                first_name="Emily",
                trail_name="Emily O'Keefe",
                state="VA",
                country="United States",
                hike_type="NOBO"
            )
        )
    ]
)
def test_process_info(
    input: str,
    expected: ProcessedInfo
):
    actual = process_info(info = input)
    assert actual == expected