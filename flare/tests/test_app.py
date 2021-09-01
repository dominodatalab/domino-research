from typing import Optional
from flare.examples import (
    generate_example_dataframe,
    EXAMPLE_DF_NULL_PERCENTS,
    EXAMPLE_DF_STRING_DOMAINS,
)

from flare.types import FeatureType
from flare.generators import gen_constraints

from flare.constraints import Constraints
from flare.constraints import Feature as ConstraintsFeature


def test_type_inference():
    test_df = generate_example_dataframe()
    constraints = gen_constraints(test_df)

    # Integer column with no missing values is
    # detected as Integral
    assert test_df["int_1"].isna().sum() == 0
    int_1_feature = fetch_constrain_feature("int_1", constraints)
    assert int_1_feature.inferred_type == FeatureType.INTEGRAL.value

    # Integer column with missing values is
    # detected as Fractional
    assert test_df["int_0"].isna().sum() > 0
    int_0_feature = fetch_constrain_feature("int_0", constraints)
    assert int_0_feature.inferred_type == FeatureType.FRACTIONAL.value

    # Fractional column with missing values is
    # detected as Fractional and has correct completeness
    assert test_df["float_0"].isna().sum() > 0
    float_0_feature = fetch_constrain_feature("float_0", constraints)
    assert float_0_feature.inferred_type == FeatureType.FRACTIONAL.value

    # Mixed-type column is detected as unknown
    assert len(set(map(type, test_df["mixed_0"].dropna()))) > 1
    mixed_0_feature = fetch_constrain_feature("mixed_0", constraints)
    assert mixed_0_feature.inferred_type == FeatureType.UNKNOWN.value

    # String column with missing is detected as String
    assert test_df["str_0"].isna().sum() > 0
    str_0_feature = fetch_constrain_feature("str_0", constraints)
    assert str_0_feature.inferred_type == FeatureType.STRING.value


def test_completeness_inference():
    test_df = generate_example_dataframe()
    constraints = gen_constraints(test_df)

    float_0_feature = fetch_constrain_feature("float_0", constraints)

    assert (
        float_0_feature.completeness
        - (1 - EXAMPLE_DF_NULL_PERCENTS["float_0"])
        <= 0.1  # allow some room for rounding
    )


def test_string_constraints_inference():
    test_df = generate_example_dataframe()
    constraints = gen_constraints(test_df)

    str_0_feature = fetch_constrain_feature("str_0", constraints)

    assert set(str_0_feature.string_constraints.domains) == set(
        EXAMPLE_DF_STRING_DOMAINS
    )


def test_numerical_constraints():
    test_df = generate_example_dataframe()
    constraints = gen_constraints(test_df)

    int_0_feature = fetch_constrain_feature("int_0", constraints)
    pos_int_0_feature = fetch_constrain_feature("positive_int_0", constraints)

    assert test_df["int_0"].dropna().min() < 0
    assert not int_0_feature.num_constraints.is_non_negative

    assert test_df["positive_int_0"].dropna().min() >= 0
    assert pos_int_0_feature.num_constraints.is_non_negative


def fetch_constrain_feature(
    feature_name: str, constraints: Constraints
) -> Optional[ConstraintsFeature]:

    feature: Optional[ConstraintsFeature] = next(
        filter(lambda x: x.name == feature_name, constraints.features)
    )

    return feature
