def get_customized_mapping(cls):
    mapping = {
        "ccds": {
            "properties": {
                "ccds_id": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword",
                },
                "status": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword",
                },
                "match_type": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword",
                },
                "attribute": {"type": "text"},
            }
        }
    }
    return mapping