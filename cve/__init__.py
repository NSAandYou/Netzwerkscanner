import json
import requests


def get_cve_json(cpe: str) -> json:
    ##return json.loads(requests.get("https://services.nvd.nist.gov/rest/json/cves/2.0?cpeName=cpe:2.3:o:microsoft:windows_10:1607").text)
    return json.loads(requests.get("https://services.nvd.nist.gov/rest/json/cves/2.0?cpeName=" + cpe).text)
