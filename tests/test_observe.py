from pathlib import Path

from smb3_agent.observe import build_state_trace, write_state_trace
from smb3_agent.review import parse_log_events


def test_build_state_trace_samples_ticks_and_progress_events(tmp_path: Path) -> None:
    log_path = tmp_path / "route.log"
    log_path.write_text(
        "\n".join(
            [
                "frame=0 event=attempt_1_start x=24 y=384 form=0 lives=4",
                "frame=5 event=tick x=30 y=384 form=0 lives=4",
                "frame=15 event=tick x=100 y=384 form=0 lives=4",
                "frame=30 event=tick x=200 y=384 form=0 lives=4",
                "frame=40 event=attempt_1_reached_end_x x=2501 y=336 form=0 lives=4",
                "frame=50 event=attempt_1_success_course_clear x=8192 y=0 form=0 lives=4",
            ]
        )
    )

    snapshots = build_state_trace(parse_log_events(log_path), segment="world_1_1_clear", sample_frames=15)

    assert snapshots[0].progress == "start"
    assert any(snapshot.progress == "progress" for snapshot in snapshots)
    assert snapshots[-1].progress == "success"
    assert snapshots[-1].final is True
    assert snapshots[0].lives == 4


def test_write_state_trace_jsonl(tmp_path: Path) -> None:
    log_path = tmp_path / "route.log"
    log_path.write_text("frame=0 event=attempt_1_start x=24 y=384 form=0\n")
    snapshots = build_state_trace(parse_log_events(log_path), segment="world_1_1_clear", sample_frames=15)
    trace_path = tmp_path / "state_trace.jsonl"

    write_state_trace(trace_path, snapshots)

    assert trace_path.read_text().count("\n") == 1
    assert '"segment": "world_1_1_clear"' in trace_path.read_text()


def test_build_state_trace_marks_done_after_success_as_final_success(tmp_path: Path) -> None:
    log_path = tmp_path / "route.log"
    log_path.write_text(
        "\n".join(
            [
                "frame=0 event=attempt_1_start x=24 y=384 form=0",
                "frame=50 event=attempt_1_success_course_clear x=8192 y=0 form=0",
                "frame=60 event=attempt_1_done x=8192 y=0 form=0",
            ]
        )
    )

    snapshots = build_state_trace(parse_log_events(log_path), segment="world_1_1_clear", sample_frames=15)

    assert snapshots[-1].event == "attempt_1_done"
    assert snapshots[-1].progress == "success"
    assert snapshots[-1].final is True
