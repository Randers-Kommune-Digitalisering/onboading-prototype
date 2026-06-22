import os

import controllers.user_controller as user_controller


class _FakeAzureClient:
    def __init__(self, *_args, **_kwargs):
        pass

    def get_all_users(self):
        return [{"displayName": "Test User", "mail": "test@example.com", "onPremisesSamAccountName": "DQ1234"}]


def test_get_and_save_azure_ad_data_handles_dot_in_directory(monkeypatch):
    captured = {}

    def fake_df_to_csv(_df, filename):
        captured["filename"] = filename

    monkeypatch.setattr(user_controller, "AZURE_CLIENTID", "client")
    monkeypatch.setattr(user_controller, "AZURE_CLIENTSECRET", "secret")
    monkeypatch.setattr(user_controller, "AZURE_TENANTID", "tenant")
    monkeypatch.setattr(user_controller, "AZURE_CSV_PATH", r"U:\.ENV\onboarding-prototype\users.csv")
    monkeypatch.setattr(user_controller, "AzureClient", _FakeAzureClient)
    monkeypatch.setattr(user_controller, "df_to_csv", fake_df_to_csv)

    assert user_controller.get_and_save_azure_ad_data() is True
    assert captured["filename"] == r"U:\.ENV\onboarding-prototype\users"


def test_ensure_azure_ad_data_fresh_does_not_refetch_recent_file(monkeypatch, tmp_path):
    azure_csv_path = tmp_path / ".ENV" / "users.csv"
    azure_csv_path.parent.mkdir(parents=True, exist_ok=True)
    azure_csv_path.write_text("displayName,mail,onPremisesSamAccountName\n", encoding="utf-8")

    def fail_if_called():
        raise AssertionError("Azure refetch should not be called for fresh CSV")

    monkeypatch.setattr(user_controller, "AZURE_CSV_PATH", str(azure_csv_path))
    monkeypatch.setattr(user_controller, "get_and_save_azure_ad_data", fail_if_called)

    assert user_controller.ensure_azure_ad_data_fresh(max_age_hours=24) is True
    assert os.path.exists(str(azure_csv_path))
