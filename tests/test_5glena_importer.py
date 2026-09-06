from tools.extract_5glena_bler import extract_table1_bg1


def test_extract_table1_bg1_minimal_source():
    source = r'''
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
    }
};
'''
    rows = extract_table1_bg1(source)
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
