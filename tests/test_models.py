import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Product, Score, Tag
from app.models.score import CATEGORY_FIELDS, ALL_CAPABILITY_FIELDS


class TestScoreComputeTotals:
    def test_compute_totals_calculates_category_averages(self, db, sample_score):
        """compute_totals should set each category average from its capability values."""
        # Provide a minimal capabilities dict with no _min keys so total logic is exercised
        capabilities = {}
        sample_score.compute_totals(capabilities)

        for cat_key, fields in CATEGORY_FIELDS.items():
            values = [getattr(sample_score, f) for f in fields if getattr(sample_score, f) is not None]
            expected_avg = sum(values) / len(values) if values else 0
            assert getattr(sample_score, cat_key) == pytest.approx(expected_avg)

    def test_compute_totals_sets_total_from_mins(self, db, sample_score):
        """compute_totals should compute total as percentage of capabilities meeting their min."""
        # Set some _min thresholds
        capabilities = {"a1_min": 2, "a2_min": 3, "b1_min": 1}
        sample_score.compute_totals(capabilities)

        # Count how many actually meet the threshold
        met = 0
        for field_min_key, min_val in [("a1", 2), ("a2", 3), ("b1", 1)]:
            val = getattr(sample_score, field_min_key)
            if val is not None and val >= min_val:
                met += 1
        expected_total = (met / 3) * 100
        assert sample_score.total == pytest.approx(expected_total)

    def test_compute_totals_sets_latest_true(self, db, sample_score):
        sample_score.latest = False
        # Must pass at least one _min key; empty capabilities returns early before setting latest
        sample_score.compute_totals({"a1_min": 1})
        assert sample_score.latest is True


class TestScoreArrays:
    def test_get_capability_array_returns_42_values(self, db, sample_score):
        arr = sample_score.get_capability_array()
        assert len(arr) == 42

    def test_get_capability_array_values_are_ints(self, db, sample_score):
        arr = sample_score.get_capability_array()
        assert all(isinstance(v, int) for v in arr)

    def test_get_category_array_returns_5_values(self, db, sample_score):
        sample_score.compute_totals({})
        arr = sample_score.get_category_array()
        assert len(arr) == 5

    def test_get_category_array_with_no_computed_averages(self, db, sample_product):
        """When category averages are None, get_category_array should return zeros."""
        score = Score(product_id=sample_product.id, latest=True)
        db.add(score)
        db.commit()
        db.refresh(score)
        arr = score.get_category_array()
        assert arr == [0, 0, 0, 0, 0]


class TestProductLatestScore:
    def test_latest_score_returns_last_score_by_position(self, db, sample_product, sample_score):
        """latest_score returns the last score in the scores list (ordered by created_at)."""
        # sample_score is the only score, so it should be returned
        db.refresh(sample_product)
        assert sample_product.latest_score is not None
        assert sample_product.latest_score.id == sample_score.id

    def test_latest_score_returns_none_when_no_scores(self, db, sample_product):
        db.refresh(sample_product)
        assert sample_product.latest_score is None

    def test_latest_score_returns_last_not_first(self, db, sample_product):
        """With multiple scores, latest_score returns the last one (by order_by created_at)."""
        score1 = Score(product_id=sample_product.id, latest=False, a1=1)
        db.add(score1)
        db.commit()

        score2 = Score(product_id=sample_product.id, latest=True, a1=4)
        db.add(score2)
        db.commit()

        db.refresh(sample_product)
        # latest_score is the last element (ordered by created_at)
        assert sample_product.latest_score.id == score2.id


class TestTagUniqueConstraint:
    def test_duplicate_key_product_raises(self, db, sample_product):
        """Two tags with the same key + product_id should violate the unique constraint."""
        tag1 = Tag(key="env", value="prod", product_id=sample_product.id)
        tag2 = Tag(key="env", value="staging", product_id=sample_product.id)
        db.add(tag1)
        db.commit()

        db.add(tag2)
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

    def test_same_key_different_product_allowed(self, db, sample_product):
        """Same key on different products should be fine."""
        other = Product(name="Other", product_type="Component", is_active=True)
        db.add(other)
        db.commit()
        db.refresh(other)

        tag1 = Tag(key="env", value="prod", product_id=sample_product.id)
        tag2 = Tag(key="env", value="prod", product_id=other.id)
        db.add_all([tag1, tag2])
        db.commit()
        assert tag1.id is not None
        assert tag2.id is not None
