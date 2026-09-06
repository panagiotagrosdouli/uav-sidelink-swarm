from tools.extract_5glena_bler import enrich_rows, extract_table1, extract_table1_bg1


SOURCE = r'''
static const NrEesmErrorModel::SimulatedBlerFromSINR BlerForSinr1 = {
    { // BG TYPE 1
     { // MCS 4
      {4096U, // SINR and BLER for CBS 4096
       NrEesmErrorModel::DoubleTuple{
           {5.300000e-01, 1.247500e+00, 1.730000e+00}, // SINR
           {1, 9.990385e-01, 4.936275e-01} // BLER
       }}},
     { // MCS 5
      {4096U, // SINR and BLER for CBS 4096
       NrEesmErrorModel::DoubleTuple{
           {1.600000e+00, 2.310000e+00}, // SINR
           {1, 9.498175e-01} // BLER
       }}}
    },
    { // BG TYPE 2
     { // MCS 0
      {120U, // SINR and BLER for CBS 120
       NrEesmErrorModel::DoubleTuple{
           {-6.0, -5.0, -4.0}, // SINR
           {1.0, 0.5, 0.0} // BLER
       }}}
    }
};
'''


def test_extract_table1_bg1_minimal_source():
    rows = extract_table1_bg1(SOURCE)
    assert len(rows) == 5
    assert rows[0] == {
        "mcs_index": 4,
        "base_graph": 1,
        "code_block_size": 4096,
        "sinr_db": 0.53,
        "bler": 1.0,
    }
    assert rows[-1]["mcs_index"] == 5
    assert rows[-1]["bler"] == 0.9498175


def test_extract_table1_includes_both_base_graphs():
    rows = extract_table1(SOURCE)
    assert len(rows) == 8
    bg2 = [r for r in rows if r["base_graph"] == 2]
    assert len(bg2) == 3
    assert bg2[0]["mcs_index"] == 0
    assert bg2[1]["bler"] == 0.5


def test_enriched_rows_keep_standard_and_source_metadata():
    rows = enrich_rows(
        extract_table1(SOURCE),
        source_version="v5.0",
        source_commit="47a3adc2",
        source_url="https://example.test/nr-eesm-t1.cc",
    )
    mcs4 = next(r for r in rows if r["mcs_index"] == 4)
    assert mcs4["modulation_order"] == 2
    assert mcs4["target_code_rate_x1024"] == 308
    assert mcs4["source_classification"] == "LINK_LEVEL_SIMULATION"
    assert mcs4["source_commit"] == "47a3adc2"
