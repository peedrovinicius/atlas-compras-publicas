from dental_procurement_intelligence.dashboard import render_dashboard


def test_render_dashboard_uses_real_overview_fields_and_escapes_content() -> None:
    html = render_dashboard(
        {
            "generated_at": "2026-09-27T20:00:00+00:00",
            "domains": [
                {
                    "id": "dental",
                    "label": "Odontologia",
                    "status": "active",
                }
            ],
            "quality": {
                "total_items": 10,
                "category_identified_items": 8,
                "fully_structured_items": 6,
                "average_quality_score": 0.812,
            },
            "category_prices": [
                {
                    "product_category": "<script>alert(1)</script>",
                    "item_count": 10,
                    "priced_item_count": 8,
                    "median_normalized_price": 12.5,
                    "min_normalized_price": 5,
                    "max_normalized_price": 30,
                }
            ],
            "awards": [],
            "anomalies": [],
        }
    )

    assert "Atlas de Compras Públicas" in html
    assert ">10<" in html
    assert ">8<" in html
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "Sinais estatísticos não constituem prova de irregularidade" in html
