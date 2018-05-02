def test_sha():
    from pyknow_rt.utils import sha
    res = 'b2213295d564916f89a6a42455567c87c3f480fcd7a1c15e220f17d7169a790b'
    assert sha('foo') == res
