from pathlib import Path

from smb3_agent.review import compare_logs, review_log


def test_review_log_reports_successful_gate(tmp_path: Path) -> None:
    log_path = tmp_path / "pass.log"
    log_path.write_text(
        "\n".join(
            [
                "frame=10 event=attempt_1_success_course_clear x=8192 y=0",
                "frame=20 event=post_probe_1_airship_stage_bridge x=219 y=192",
                "frame=30 event=post_probe_1_airship_success_king x=432 y=4192 form=0",
            ]
        )
    )

    report = review_log(log_path, expected_attempts=1)

    assert report.failure_class == "none"
    assert report.failed_segment == "none"
    assert report.last_event == "post_probe_1_airship_success_king"
    assert "No repair needed" in report.next_experiment
    assert "final_snapshot=" in report.to_text()


def test_review_log_classifies_bad_state_as_state_detection(tmp_path: Path) -> None:
    log_path = tmp_path / "bad_state.log"
    log_path.write_text(
        "\n".join(
            [
                "frame=10 event=attempt_1_start x=24 y=384",
                "frame=50 event=attempt_1_bad_state x=512 y=320 form=0",
            ]
        )
    )

    report = review_log(log_path, expected_attempts=1)

    assert report.failure_class == "state_detection"
    assert report.failed_segment == "world_1_1_clear"
    assert "guard screenshot" in report.next_experiment


def test_review_log_classifies_post_probe_failure_as_wrong_route_state(tmp_path: Path) -> None:
    log_path = tmp_path / "wrong_route.log"
    log_path.write_text(
        "\n".join(
            [
                "frame=10 event=attempt_1_success_course_clear x=8192 y=0",
                "frame=50 event=post_probe_1_4_after x=640 y=320 form=0",
            ]
        )
    )

    report = review_log(log_path, expected_attempts=1)

    assert report.failure_class == "wrong_route_state"
    assert report.failed_segment == "world_1_4_clear"
    assert "precondition check" in report.next_experiment


def test_review_log_classifies_bridge_failure(tmp_path: Path) -> None:
    log_path = tmp_path / "bridge.log"
    log_path.write_text(
        "\n".join(
            [
                "frame=10 event=attempt_1_success_course_clear x=8192 y=0",
                "frame=50 event=post_probe_1_airship_stage_bridge x=219 y=192",
            ]
        )
    )

    report = review_log(log_path, expected_attempts=1)

    assert report.failure_class == "bridge_failure"
    assert report.failed_segment == "world_1_airship_to_king"
    assert "bridge preconditions" in report.next_experiment


def test_compare_logs_calls_out_watch_or_capture_timing_risk(tmp_path: Path) -> None:
    passing = tmp_path / "pass.log"
    passing.write_text(
        "\n".join(
            [
                "frame=10 event=attempt_1_success_course_clear x=8192 y=0",
                "frame=30 event=post_probe_1_airship_success_king x=432 y=4192",
            ]
        )
    )
    failing = tmp_path / "fail.log"
    failing.write_text(
        "\n".join(
            [
                "frame=10 event=attempt_1_success_course_clear x=8192 y=0",
                "frame=40 event=post_probe_1_4_after x=700 y=320",
            ]
        )
    )

    report = compare_logs(passing, failing)

    assert "timing/capture overhead" in report.explanation
    assert "right_failure_class=wrong_route_state" in report.to_text()
