from src.report import main


def test_ftw_util():
    main(["--test-name", "unit-test-ftw", "--utils", "ftw"])

def test_locust_util():
    main(["--test-name", "unit-test-locust", "--utils", "locust"])

def test_cAdvisor_util():
    main(["--test-name", "unit-test-cAdvisor", "--utils", "cAdvisor"])
