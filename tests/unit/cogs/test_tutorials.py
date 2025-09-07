import pytest

from cogs.tutorials import make_human_readable_list


@pytest.mark.parametrize(
    "items, expected",
    [
        pytest.param([], "", id="[]"),
        pytest.param(["A"], "A", id='["A"]'),
        pytest.param(["A", "B"], "A and B", id='["A", "B"]'),
        pytest.param(["A", "B", "C"], "A, B and C", id='["A", "B", "C"]'),
        pytest.param(["A", "B", "C", "D"], "A, B, C and D", id='["A", "B", "C", "D"]'),
        pytest.param(
            ["A", "B", "C", "D", "E"],
            "A, B, C, D and E",
            id='["A", "B", "C", "D", "E"]',
        ),
    ],
)
def test_make_human_readable_list(items, expected):
    output = make_human_readable_list(items)
    print("\n", items, "-> ", repr(output))
    assert output == expected
