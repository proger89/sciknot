import yaml


def test_model_config_has_no_real_secret():
    config = yaml.safe_load(open("config/models.yml", encoding="utf-8"))
    assert "{YANDEX_FOLDER_ID}" in config["default_generator"]
    assert config["default_generator"].endswith("/yandexgpt-5.1")
    assert "AQVN0" not in str(config)

