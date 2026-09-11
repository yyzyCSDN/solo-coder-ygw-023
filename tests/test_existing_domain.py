import unittest
from powerprotocol.service import PowerProtocolService

class ExistingGatewayTests(unittest.TestCase):
    def setUp(self):
        self.s=PowerProtocolService()
        for asset,kind in [("c1","channel"),("s1","site"),("p1","point"),("d1","field_device"),("cmd1","control_command")]:self.s.baseline.register_asset(asset,kind)
    def tearDown(self):self.s.close()
    def test_frame_retention_records_sequence(self):self.assertEqual(self.s.domain.keep_frame("c1",b"abc",7)["sequence"],7)
    def test_mapping_and_fifo_are_current_behaviour(self):self.assertEqual(self.s.domain.map_point("p1",2,{"p1":{"scale":3}})["engineering_value"],6);self.assertEqual(self.s.domain.enqueue_fifo("s1",[{"v":1}])[0]["queue_order"],1)
    def test_source_scope_fails_closed(self):self.assertFalse(self.s.domain.source_allowed("master","s2",{"master":["s1"]}))
    def test_processing_job_is_persistent(self):self.assertEqual(self.s.domain.processing_job("x1",["c1"],"f1")["flow"],"frame_processing")
    def test_mapping_release_keeps_one_version(self):self.assertEqual(self.s.domain.mapping_release_job("m1",["s1"],3)["payload"]["version"],3)
    def test_remote_control_starts_requested(self):self.assertEqual(self.s.domain.remote_control_job("r1","cmd1","master")["payload"]["phase"],"requested")
    def test_channel_assessment_records_signal_and_job(self):self.assertEqual(self.s.domain.assess_channel("h1","c1",1,10)["payload"]["verdict"],"bad")
    def test_deduplication_is_a_durable_batch(self):self.assertEqual(len(self.s.domain.deduplicate_frames("d1","c1",[b"x",b"x",b"y"])["payload"]["kept"]),2)
    def test_retention_policy_is_versioned(self):self.assertEqual(self.s.domain.publish_retention(2,500)["version"],2)
    def test_presence_is_a_device_job(self):self.assertEqual(self.s.domain.presence_job("pjob","d1",31)["payload"]["state"],"offline")
    def test_point_quality_is_retained(self):self.assertEqual(self.s.domain.record_point_quality("p1",4,"bad")["quality"],"bad")
    def test_configuration_change_has_version_boundary(self):self.assertEqual(self.s.domain.configuration_change("cfg","s1","point_map",1,2)["payload"]["from_version"],1)
    def test_recall_is_idempotent(self):self.assertTrue(self.s.domain.recall_job("rec","s1",["p1"])["flow"]=="station_recall" and self.s.domain.recall_job("rec","s1",[])["duplicate"])
