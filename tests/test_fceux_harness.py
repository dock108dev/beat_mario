from pathlib import Path

from PIL import Image

from smb3_agent.fceux_images import convert_gd_directory, write_contact_sheet
from smb3_agent.fceux_harness import parse_fceux_log


def test_parse_fceux_log_counts_successes(tmp_path: Path) -> None:
    log_path = tmp_path / "route.log"
    log_path.write_text(
        "\n".join(
            [
                "frame=10 event=attempt_1_start x=24 y=384",
                "frame=20 event=agent_tick x=100 y=384",
                "frame=30 event=attempt_1_reached_end_x x=2501 y=336",
                "frame=40 event=attempt_1_goal_area x=2801 y=384",
                "frame=50 event=attempt_1_success_course_clear x=8192 y=0",
                "frame=60 event=attempt_2_start x=24 y=384",
                "frame=70 event=agent_tick x=900 y=384",
                "frame=80 event=attempt_2_bad_state x=8192 y=0",
                "frame=90 event=post_probe_1_2_progress_x_512 x=512 y=320",
                "frame=100 event=post_probe_1_2_done x=490 y=320",
            ]
        )
    )

    summary = parse_fceux_log(log_path, expected_attempts=2)

    assert summary.success_count == 1
    assert summary.bad_state_count == 1
    assert summary.attempts[0].max_x == 2801
    assert summary.attempts[0].reached_end is True
    assert summary.attempts[0].goal_area is True
    assert summary.attempts[1].max_x == 900
    assert summary.attempts[1].bad_state is True
    assert summary.post_probe_max_x == 512
    assert summary.post_probe_last_event == "post_probe_1_2_done"


def test_convert_gd_directory_and_contact_sheet(tmp_path: Path) -> None:
    image_dir = tmp_path / "gd"
    image_dir.mkdir()
    gd_path = image_dir / "000001_probe.gd"
    pixel = bytes([0, 10, 20, 30])
    gd_path.write_bytes(b"FCEUXGD0000"[:11] + pixel * (256 * 224))

    output_dir = tmp_path / "png"
    converted = convert_gd_directory(image_dir, output_dir)
    sheet_path = write_contact_sheet(converted, tmp_path / "sheet.png", columns=1)

    assert len(converted) == 1
    with Image.open(converted[0]) as converted_image:
        assert converted_image.size == (256, 224)
    with Image.open(sheet_path) as sheet:
        assert sheet.size == (256, 242)
