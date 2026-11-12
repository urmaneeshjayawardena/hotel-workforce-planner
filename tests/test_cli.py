from hotel_workforce.cli import build_report, main


def test_report_shows_optimum_and_whole_plan():
    report = build_report(60)

    assert "Hotel with 60 rooms" in report
    assert "x* = 14.40, y* = 8.80" in report
    assert "14 housekeepers, 9 overtime hours" in report


def test_main_prints_report(capsys):
    main(["--rooms", "15"])

    assert "Hotel with 15 rooms" in capsys.readouterr().out
