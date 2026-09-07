import importlib.util
from pathlib import Path
from unittest.mock import Mock, patch
import numpy as np
import pytest

@pytest.fixture
def api():
    path = Path(__file__).resolve().parents[1] / 'flask_model_server.py'
    spec = importlib.util.spec_from_file_location('sales_server', path)
    module = importlib.util.module_from_spec(spec)
    with patch('joblib.load', return_value=Mock(predict=Mock(return_value=np.array([123.8])))):
        spec.loader.exec_module(module)
    module.model = Mock(predict=Mock(return_value=np.array([123.8])))
    module.app.config.update(TESTING=True, MAIL_SUPPRESS_SEND=True)
    return module, module.app.test_client()

def features():
    return dict(Store=1,Dept=1,Temperature=55,MarkDown1=0,MarkDown2=0,MarkDown4=0,MarkDown5=0,Size=1000,Type_A=1,Type_B=0,Type_C=0,Month=1,Day=1,isHoliday=0)

def test_valid_prediction_preserves_feature_order(api):
    module,client=api
    response=client.post('/predict',json=features())
    assert response.status_code==200
    assert response.json=={'prediction':123}
    np.testing.assert_array_equal(module.model.predict.call_args.args[0],[[1,1,55,0,0,0,0,1000,1,0,0,1,1,0]])

@pytest.mark.parametrize('payload',[{},[],{'Store':1},dict(features(),Type_B=1),dict(features(),isHoliday=2),dict(features(),Month=13),dict(features(),Temperature='nan')])
def test_invalid_prediction_returns_400_without_model_call(api,payload):
    module,client=api
    response=client.post('/predict',json=payload)
    assert response.status_code==400
    assert 'error' in response.json
    module.model.predict.assert_not_called()

def test_inventory_is_independent_of_working_directory(api,tmp_path,monkeypatch):
    _,client=api
    monkeypatch.chdir(tmp_path)
    response=client.get('/get_data?store_number=1&dept_number=1')
    assert response.status_code==200
    assert isinstance(response.json,list)
    assert response.json and response.json[0]['Store']=='1'

def test_missing_inventory_selection_returns_400(api):
    _,client=api
    assert client.get('/get_data').status_code==400

@pytest.mark.parametrize('payload',[{},[],{'email':'reviewer@example.com','inventoryData':None},{'email':'reviewer@example.com','inventoryData':[{}]}])
def test_malformed_email_payload_is_rejected_without_sending(api,payload):
    module,client=api
    with patch.object(module.mail,'send') as send:
        assert client.post('/send-email',json=payload).status_code==400
        send.assert_not_called()
