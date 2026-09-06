from pathlib import Path

import numpy as np
import pandas as pd

from src.experiments.campaign_utils import evaluate_snapshot, summarize_groups
from src.experiments.system_evaluation import annotate_nr_link_metrics
from src.sidelink.bler_io import load_bler_curves
from src.sidelink.resource_grid import thesis_profile_50mhz_30khz
from src.sidelink.tb_link_model import select_tbs_aware_mcs
from src.swarm_system import SwarmConfig


def _fixture():
    return load_bler_curves(
        Path("data/reference/5glena_table1_bg1_cbs4096_subset.csv"),
        source="5G-LENA fixture",
    )


def test_tbs_aware_adaptation_returns_supported_choice():
    choice = select_tbs_aware_mcs(_fixture(), 3.0, thesis_profile_50mhz_30khz())
    assert choice is not None
    assert choice.mcs_index in {4, 5, 6}
    assert choice.tbs_bits > 0
    assert 0.0 <= choice.transport_block_bler <= 1.0
    assert choice.expected_first_tx_goodput_mbps >= 0.0


def test_unified_link_annotation_adds_harq_metrics():
    links = pd.DataFrame([{"tx": 0, "rx": 1, "sinr_db": 3.0}])
    out = annotate_nr_link_metrics(
        links,
        _fixture(),
        thesis_profile_50mhz_30khz(),
        harq_attempts=2,
        feedback_and_retx_gap_slots=2,
    )
    assert out.link_model_status.iloc[0] == "ok"
    assert out.harq_success_probability.iloc[0] >= out.first_tx_success_probability.iloc[0]
    assert out.harq_latency_ms.iloc[0] >= 0.5


def test_campaign_snapshot_is_reproducible():
    cfg = SwarmConfig(n_uavs=20, seed=7, activity_probability=1.0)
    kwargs = dict(curves=_fixture(), grid=thesis_profile_50mhz_30khz(), n_resources=4, resource_algorithm="graph")
    a, links_a, pos_a = evaluate_snapshot(cfg, **kwargs)
    b, links_b, pos_b = evaluate_snapshot(cfg, **kwargs)
    assert a == b
    assert links_a.equals(links_b)
    assert np.array_equal(pos_a, pos_b)


def test_summary_handles_optional_grouping_column():
    frame = pd.DataFrame([
        {"kind": "a", "metric": 1.0},
        {"kind": "a", "metric": 2.0},
    ])
    summary = summarize_groups(frame, ["kind", "optional"], ["metric"])
    assert summary.optional.iloc[0] == "not_applicable"
    assert np.isclose(summary.metric_mean.iloc[0], 1.5)
