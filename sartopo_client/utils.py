def assert_res(res):
    assert res.status_code == 200 and res.json()['status'] == 'ok'
    return res.json()['result']