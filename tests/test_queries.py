from app.models import Product, Score
from app.models.score import ALL_CAPABILITY_FIELDS
from app.queries import get_active_product, get_org_summary


class TestGetActiveProduct:
    def test_returns_active_product(self, db, sample_product):
        result = get_active_product(db, sample_product.id)
        assert result is not None
        assert result.id == sample_product.id

    def test_returns_none_for_inactive_product(self, db, sample_product):
        sample_product.is_active = False
        db.commit()
        result = get_active_product(db, sample_product.id)
        assert result is None

    def test_returns_none_for_nonexistent_id(self, db):
        result = get_active_product(db, 99999)
        assert result is None


class TestGetOrgSummary:
    def test_returns_averages(self, db, sample_product, sample_score):
        """get_org_summary should return averages across all latest scores of active products."""
        # Compute totals so category averages are set
        sample_score.compute_totals({})
        db.commit()

        summary = get_org_summary(db)
        assert summary is not None
        assert summary.total is not None

        # With a single product the average should equal that product's values
        for cat in ["a", "b", "c", "d", "e"]:
            assert getattr(summary, cat) is not None

    def test_returns_none_total_when_no_scores(self, db):
        """With no products at all, summary total should be None."""
        summary = get_org_summary(db)
        assert summary.total is None

    def test_averages_multiple_products(self, db):
        """Averages should reflect all active products with latest scores."""
        p1 = Product(name="P1", product_type="Product", is_active=True, is_assessed=True)
        p2 = Product(name="P2", product_type="Product", is_active=True, is_assessed=True)
        db.add_all([p1, p2])
        db.commit()
        db.refresh(p1)
        db.refresh(p2)

        s1 = Score(product_id=p1.id, latest=True, a1=2, a2=4)
        s2 = Score(product_id=p2.id, latest=True, a1=4, a2=2)
        db.add_all([s1, s2])
        db.commit()

        summary = get_org_summary(db)
        # avg of a1: (2+4)/2 = 3, avg of a2: (4+2)/2 = 3
        assert summary.a1 == 3.0
        assert summary.a2 == 3.0
