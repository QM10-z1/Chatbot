def test_index_html_served(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    # 确保页面不包含敏感信息
    assert "sk-" not in response.text