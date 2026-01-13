from osuscrob import OsuScrob
import tempfile
import os


def test_init_without_config():
    """
    On the very first startup, OsuScrob's init should create an empty config
    file and return `False` (but not crash!)
    """
    with tempfile.TemporaryDirectory() as config_dir:
        o = OsuScrob()

        # Return false (but not crash)
        assert not o.init(config_dir=config_dir)

        # Config file should be non-empty
        assert os.path.exists(o.config_path)
        with open(o.config_path, "r") as f:
            assert len(f.read()) > 0
