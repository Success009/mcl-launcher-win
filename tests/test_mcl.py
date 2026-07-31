import unittest
import unittest.mock
import tempfile
import shutil
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mcl_launcher import config
from mcl_launcher import metadata_repair
from mcl_launcher import instance_manager
from mcl_launcher.cli import get_version_tuple

class TestMCLLauncherWin(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.test_dir)
        
    def test_metadata_repair(self):
        versions_dir = os.path.join(self.test_dir, "versions", "TestVer")
        os.makedirs(versions_dir)
        json_path = os.path.join(versions_dir, "TestVer.json")
        
        malformed_data = {
            "javaVersion": {
                "component": "java-runtime-alpha",
                "majorVersion": "21"
            }
        }
        with open(json_path, "w") as f:
            json.dump(malformed_data, f)
            
        repaired = metadata_repair.repair_version_metadata("TestVer", self.test_dir)
        self.assertTrue(repaired)
        
        with open(json_path, "r") as f:
            data = json.load(f)
        self.assertEqual(data["javaVersion"]["majorVersion"], 21)
        self.assertIsInstance(data["javaVersion"]["majorVersion"], int)
        
    def test_instance_manager(self):
        settings = {
            "isolate_instances": True,
            "isolate_saves": True,
            "isolate_resourcepacks": True
        }
        instance_dir = instance_manager.prepare_instance("TestVer", settings, self.test_dir)
        self.assertTrue(os.path.isdir(os.path.join(instance_dir, "mods")))
        self.assertTrue(os.path.isdir(os.path.join(instance_dir, "config")))

    def test_chronological_sorting(self):
        versions = [
            "Forge 1.8.9",
            "fabric-1.20.1-0.19.3",
            "1.21.4",
            "Fabric 1.21.4",
            "fabric-26.2-0.19.3"
        ]
        sorted_versions = sorted(versions, key=get_version_tuple, reverse=True)
        self.assertEqual(sorted_versions[0], "fabric-26.2-0.19.3")

if __name__ == "__main__":
    unittest.main()